#!/usr/bin/env python3
# ruff: noqa: I001 Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
# ruff: noqa: RUF022 `__all__` is not sorted help: Apply an isort-style sorting to `__all__` (Ruff RUF022)
# ruff_: noqa: E402 Module level import not at top of file (Ruff E402)
# updated by ...: Loreto Notarantonio

#

"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""

import os

__INIT__PY__DEBUG = os.environ.get("__INIT__PY__DEBUG", "False") == "True"
if __INIT__PY__DEBUG:
    print(f"{__name__} - start loading")


from .yaml_loader import lnYamlLoader, YamlEngine


# Definisci cosa esportare quando si fa "from pyLnLib.logger import *"
__all__ = [
    "YamlEngine",
    "lnYamlLoader",
]

if __INIT__PY__DEBUG:
    print(f"{__name__} - end loading")
