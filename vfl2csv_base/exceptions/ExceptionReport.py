from dataclasses import dataclass


@dataclass
class ExceptionReport:
    exception: Exception
    traceback: str
