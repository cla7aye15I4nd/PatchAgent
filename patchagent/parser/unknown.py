from patchagent.parser.cwe import CWE
from patchagent.parser.sanitizer import Sanitizer, SanitizerReport


class UnknownSanitizerReport(SanitizerReport):
    def __init__(self, stdout: str, stderr: str):
        super().__init__(Sanitizer.UnknownSanitizer, "", CWE.UNKNOWN, [])
        self.stdout = stdout
        self.stderr = stderr

    @property
    def summary(self):
        return (
            "The sanitizer detected an unknown vulnerability. \n"
            "Here is the stdout: \n\n"
            f"{self.stdout}\n\n"
            "Here is the stderr: \n\n"
            f"{self.stderr}\n\n"
            "Please check the logs for more information."
        )
