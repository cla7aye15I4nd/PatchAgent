from typing import Optional

from openai import APIError
from pydantic_core import ValidationError

from patchagent.logger import logger


class AgentStopException(Exception): ...


class PatchFoundException(Exception): ...


class BaseAgent:
    def __init__(self, retry: int = 3):
        self.retry = retry

    def _run_once(self):
        try:
            return self.apply()
        except ValidationError as e:
            logger.info(f"[🛑] Validation error: {e}")
        except AgentStopException as e:
            logger.info(f"[🛑] Agent stopped because {e}")
        except PatchFoundException as e:
            logger.info("[🎉] Patch is found")
            return str(e)

    def __call__(self) -> Optional[str]:
        for _ in range(self.retry):
            try:
                return self._run_once()
            except APIError as e:
                logger.info(f"[🛑] API error: {e}")

        return self._run_once()

    def apply(self):
        raise NotImplementedError
