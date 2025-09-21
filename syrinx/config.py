from __future__ import annotations
from typing import Any, Optional
from os.path import isfile


class SyrinxConfiguration:
    domain: Optional[str]
    verbose: bool
    environment: str


def configure(args: Any) -> SyrinxConfiguration:
    config = SyrinxConfiguration()
    return config
