import os
import shutil
import subprocess
from functools import cached_property
from hashlib import md5
from pathlib import Path
from typing import Optional

import yaml

from patchagent.builder import Builder
from patchagent.builder.utils import (
    BuilderProcessError,
    DockerUnavailableError,
    safe_subprocess_run,
)
from patchagent.lang import Lang
from patchagent.logger import logger
from patchagent.lsp.hybridc import HybridCServer
from patchagent.lsp.java import JavaLanguageServer
from patchagent.lsp.language import LanguageServer
from patchagent.parser import Sanitizer, SanitizerReport, parse_sanitizer_report
from patchagent.parser.unknown import UnknownSanitizerReport
from patchagent.utils import bear_path, subprocess_none_pipe


class OSSFuzzBuilder(Builder):
    SANITIZER_MAP = {
        Sanitizer.AddressSanitizer: "address",
        Sanitizer.UndefinedBehaviorSanitizer: "undefined",
        Sanitizer.LeakAddressSanitizer: "address",
        Sanitizer.MemorySanitizer: "memory",
        Sanitizer.ThreadSanitizer: "thread",
        # OSS-Fuzz maps Jazzer to AddressSanitizer for JVM projects
        # Reference:
        #   - https://github.com/google/oss-fuzz/blob/master/projects/hamcrest/project.yaml
        #   - https://github.com/google/oss-fuzz/blob/master/projects/apache-commons-bcel/project.yaml
        #   - https://github.com/google/oss-fuzz/blob/master/projects/threetenbp/project.yaml
        Sanitizer.JazzerSanitizer: "address",
    }

    def __init__(
        self,
        project: str,
        source_path: Path,
        fuzz_tooling_path: Path,
        sanitizer: Optional[Sanitizer] = None,
        workspace: Optional[Path] = None,
        clean_up: bool = True,
        replay_poc_timeout: int = 60,
    ):
        super().__init__(project, source_path, workspace, clean_up)
        self.project = project
        self.org_fuzz_tooling_path = fuzz_tooling_path

        match sanitizer, self.language:
            case None, Lang.CLIKE:
                self.sanitizer = Sanitizer.LeakAddressSanitizer
            case None, Lang.JVM:
                self.sanitizer = Sanitizer.JazzerSanitizer
            case _:
                self.sanitizer = sanitizer

        self.replay_poc_timeout = replay_poc_timeout

    @cached_property
    def fuzz_tooling_path(self) -> Path:
        target_path = self.workspace / "immutable" / self.org_fuzz_tooling_path.name
        if not target_path.is_dir():
            shutil.copytree(self.org_fuzz_tooling_path, target_path, symlinks=True)

        return target_path

    def hash_patch(self, patch: str) -> str:
        return md5(patch.encode()).hexdigest()

    def build_finish_indicator(self, patch: str) -> Path:
        return self.workspace / self.hash_patch(patch) / ".build"

    def _build_image(self, fuzz_tooling_path: Path, tries: int = 3) -> None:
        for _ in range(tries):
            process = subprocess.Popen(
                ["infra/helper.py", "build_image", "--pull", self.project],
                cwd=fuzz_tooling_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            _, stderr = process.communicate()
            if process.returncode == 0:
                return

            logger.warning(f"[🔥] Failed to build image for {self.project}: {stderr.decode(errors='ignore')}")

        raise DockerUnavailableError(stderr.decode(errors="ignore"))

    def build(self, patch: str = "") -> None:
        if self.build_finish_indicator(patch).is_file():
            return

        logger.info(f"[🧱] Building {self.project} with patch {self.hash_patch(patch)}")
        workspace = self.workspace / self.hash_patch(patch)
        source_path = workspace / self.org_source_path.name
        fuzz_tooling_path = workspace / self.org_fuzz_tooling_path.name

        shutil.rmtree(workspace, ignore_errors=True)
        shutil.copytree(self.source_path, source_path, symlinks=True)
        shutil.copytree(self.fuzz_tooling_path, fuzz_tooling_path, symlinks=True)

        safe_subprocess_run(["patch", "-p1"], source_path, input=patch.encode())

        self._build_image(fuzz_tooling_path)

        safe_subprocess_run(
            [
                "infra/helper.py",
                "build_fuzzers",
                "--sanitizer",
                self.SANITIZER_MAP[self.sanitizer],
                "--clean",
                self.project,
                source_path,
            ],
            fuzz_tooling_path,
        )

        safe_subprocess_run(
            [
                "infra/helper.py",
                "check_build",
                self.project,
            ],
            fuzz_tooling_path,
        )

        self.build_finish_indicator(patch).write_text(patch)

    def replay(self, harness_name: str, poc_path: Path, patch: str = "") -> Optional[SanitizerReport]:
        self.build(patch)

        assert poc_path.is_file(), "PoC file does not exist"
        assert self.build_finish_indicator(patch).is_file(), "Build failed"

        logger.info(f"[🔄] Replaying {self.project}/{harness_name} with PoC {poc_path} and patch {self.hash_patch(patch)}")

        try:
            safe_subprocess_run(
                [
                    "infra/helper.py",
                    "reproduce",
                    self.project,
                    harness_name,
                    poc_path,
                ],
                self.workspace / self.hash_patch(patch) / self.fuzz_tooling_path.name,
                timeout=self.replay_poc_timeout,
            )
        except BuilderProcessError as e:
            for report in [e.stdout, e.stderr]:
                if (
                    report := parse_sanitizer_report(
                        report,
                        self.sanitizer,
                        source_path=self.source_path,
                    )
                ) is not None:
                    return report

            return UnknownSanitizerReport(e.stdout, e.stderr)

    @cached_property
    def language(self) -> Lang:
        project_yaml = self.fuzz_tooling_path / "projects" / self.project / "project.yaml"
        assert project_yaml.is_file(), "project.yaml not found"
        yaml_data = yaml.safe_load(project_yaml.read_text())
        return Lang.from_string(yaml_data.get("language", "c"))

    @cached_property
    def language_server(self) -> LanguageServer:
        match self.language:
            case Lang.CLIKE:
                return self.construct_c_language_server()
            case Lang.JVM:
                return self.construct_java_language_server()

    def construct_c_language_server(self) -> HybridCServer:
        ctags_source = self.workspace / "ctags"
        if not ctags_source.is_dir():
            shutil.copytree(self.source_path, ctags_source, symlinks=True)

        clangd_workdir = self.workspace / "clangd"
        os.makedirs(clangd_workdir, exist_ok=True)

        clangd_source = clangd_workdir / self.source_path.name
        clangd_fuzz_tooling = clangd_workdir / self.fuzz_tooling_path.name
        if not clangd_source.is_dir():
            shutil.copytree(self.source_path, clangd_source, symlinks=True)
        if not clangd_fuzz_tooling.is_dir():
            shutil.copytree(self.fuzz_tooling_path, clangd_fuzz_tooling, symlinks=True)

        compile_commands = clangd_source / "compile_commands.json"
        if not compile_commands.is_file():
            logger.info("[🔋] Generating compile_commands.json")
            self._build_image(clangd_fuzz_tooling)

            shutil.copy2(bear_path() / "helper.py", clangd_fuzz_tooling / "infra/helper.py")
            shutil.copytree(bear_path(), clangd_source / ".bear", symlinks=True)

            subprocess.run(
                ["infra/helper.py", "bear", self.project, clangd_source],
                cwd=clangd_fuzz_tooling,
                stdout=subprocess_none_pipe(),
                stderr=subprocess_none_pipe(),
            )

            dotpwd = clangd_source / ".pwd"
            assert dotpwd.is_file(), ".pwd not found"
            assert compile_commands.is_file(), "compile_commands.json not found"

            workdir = dotpwd.read_text().strip()
            compile_commands.write_text(
                compile_commands.read_text().replace(
                    workdir,
                    clangd_source.as_posix(),
                ),
            )

        return HybridCServer(ctags_source, clangd_source)

    def construct_java_language_server(self) -> JavaLanguageServer:
        return JavaLanguageServer(self.source_path)
