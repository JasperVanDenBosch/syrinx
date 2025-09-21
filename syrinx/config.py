from __future__ import annotations
from typing import Any, Optional
from os.path import isfile


class SyrinxConfiguration:
    domain: Optional[str]


def configure(root_dir: str, args: Any) -> SyrinxConfiguration:
    config = SyrinxConfiguration()
    return config
