from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import Callable, Generator, List, Optional, Tuple

from patchagent.agent.base import BaseAgent
from patchagent.builder import Builder
from patchagent.builder.utils import BuilderProcessError, BuilderTimeoutError
from patchagent.context import Context
from patchagent.parser import SanitizerReport


class ValidationResult(Enum):
    BugFree = "Bug free"
    BugDetected = "Bug detected"

    InvalidPatchFormat = "Invalid patch format"
    BuildFailed = "Build failed"
    BuildTimeout = "Build timeout"
    ReplayFailed = "Replay failed"
    ReplayTimeout = "Replay timeout"
    FunctionTestFailed = "Function test failed"
    FunctionTestTimeout = "Function test timeout"


class PatchTask:
    def __init__(
        self,
        poc_paths: List[Path],
        harness_name: str,
        builder: Builder,
    ):
        self.poc_paths: List[Path] = poc_paths
        self.harness_name: str = harness_name
        self.builder: Builder = builder
        self.project: str = self.builder.project
        self.contexts: List[Context] = []

        self._report: Optional[SanitizerReport] = None

    def initialize(self) -> Tuple[ValidationResult, str]:
        try:
            self.builder.build()
        except BuilderProcessError as e:
            return ValidationResult.BuildFailed, str(e)
        except BuilderTimeoutError as e:
            return ValidationResult.BuildTimeout, str(e)

        try:
            for poc_path in self.poc_paths:
                report = self.builder.replay(self.harness_name, poc_path)
                if report is not None:
                    self._report = report
                    return ValidationResult.BugDetected, report.summary
        except BuilderProcessError as e:
            return ValidationResult.ReplayFailed, str(e)
        except BuilderTimeoutError as e:
            return ValidationResult.ReplayTimeout, str(e)

        return ValidationResult.BugFree, ""

    @cached_property
    def report(self) -> SanitizerReport:
        assert self._report is not None, "Please initialize the task first"
        return self._report

    @property
    def patch(self) -> Optional[str]:
        if len(self.contexts) > 0:
            return self.contexts[-1].patch

    @property
    def current_context(self) -> Context:
        return self.contexts[-1]

    def new_context(self) -> Context:
        context = Context()
        self.contexts.append(context)
        return context

    def validate(self, patch: str) -> Tuple[ValidationResult, str]:
        try:
            self.builder.check_patch(patch)
        except BuilderProcessError as e:
            return ValidationResult.InvalidPatchFormat, str(e)

        try:
            self.builder.build(patch)
        except BuilderProcessError as e:
            return ValidationResult.BuildFailed, str(e)
        except BuilderTimeoutError as e:
            return ValidationResult.BuildTimeout, str(e)

        try:
            for poc_path in self.poc_paths:
                report = self.builder.replay(self.harness_name, poc_path, patch)
                if report is not None:
                    return ValidationResult.BugDetected, report.summary
        except BuilderProcessError as e:
            return ValidationResult.ReplayFailed, str(e)
        except BuilderTimeoutError as e:
            return ValidationResult.ReplayTimeout, str(e)

        try:
            self.builder.function_test(patch)
        except BuilderProcessError as e:
            return ValidationResult.FunctionTestFailed, str(e)
        except BuilderTimeoutError as e:
            return ValidationResult.FunctionTestTimeout, str(e)

        return ValidationResult.BugFree, ""

    def repair(self, agent_generator: Callable[["PatchTask"], Generator[BaseAgent, None, None]]) -> Optional[str]:
        for agent in agent_generator(self):
            if (patch := agent()) is not None:
                return patch
