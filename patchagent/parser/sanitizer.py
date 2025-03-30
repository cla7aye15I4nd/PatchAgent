from enum import StrEnum
from pathlib import Path
from typing import List, Tuple, Union

from patchagent.parser.cwe import CWE


class Sanitizer(StrEnum):
    UnknownSanitizer = "UnknownSanitizer"
    AddressSanitizer = "AddressSanitizer"
    LeakAddressSanitizer = "LeakAddressSanitizer"
    UndefinedBehaviorSanitizer = "UndefinedBehaviorSanitizer"
    MemorySanitizer = "MemorySanitizer"
    ThreadSanitizer = "ThreadSanitizer"
    JazzerSanitizer = "JazzerSanitizer"


class SanitizerReport:
    def __init__(
        self,
        sanitizer: Sanitizer,
        content: str,
        cwe: CWE,
        stacktrace: List[Tuple[str, Path, int, int]],
    ):

        self.sanitizer: Sanitizer = sanitizer
        self.content: str = content
        self.cwe: CWE = cwe
        self.stacktrace: List[Tuple[str, Path, int, int]] = stacktrace

    @property
    def summary(self) -> str:
        return self.content

    @property
    def stacktraces(self) -> List[List[Tuple[str, Path, int, int]]]:
        return [self.stacktrace]

    @staticmethod
    def parse(raw_content: str, *args, **kwargs) -> Union[None, "SanitizerReport"]:
        raise NotImplementedError("parse method must be implemented in child class")
