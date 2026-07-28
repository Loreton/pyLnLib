#!/usr/bin/env python3
# ruff: noqa: I001 Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
# ruff: noqa: RUF022 `__all__` is not sorted help: Apply an isort-style sorting to `__all__` (Ruff RUF022)
# ruff_: noqa: E402 Module level import not at top of file (Ruff E402)
# updated by ...: Loreto Notarantonio
# Date .........: 11-07-2026 10.34.14
#

"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""

import os

__INIT__PY__DEBUG = os.environ.get("__INIT__PY__DEBUG", "False") == "True"
if __INIT__PY__DEBUG:
    print(f"{__name__} - start loading")


from .file_utils import get_file_list, searchFile, searchFileOnFS, scan_directory
from .ini_file import loadIni, writeIni
from .write_file import writeFile
from .yaml_loader_class import get_yaml_engine  # YamlEngine
from .zip_file_utils import searchFileInZip, zipDir

# Definisci cosa esportare quando si fa "from pyLnLib.logger import *"
__all__ = [
    "searchFile",
    "searchFileOnFS",
    "get_file_list",
    "loadIni",
    "writeIni",
    "writeFile",
    # 'YamlEngine',
    "get_yaml_engine",
    "searchFileInZip",
    "zipDir",
    "scan_directory",
]

if __INIT__PY__DEBUG:
    print(f"{__name__} - end loading")
