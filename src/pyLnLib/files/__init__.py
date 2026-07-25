#!/usr/bin/env python3
# ruff: noqa: E402 Module level import not at top of file (Ruff E402)
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


from .file_utils import dirList, searchFile, searchFileOnFS
from .ini_file import loadIni, writeIni
from .write_file import writeFile
from .yaml_loader_class import get_yaml_engine  # YamlEngine
from .zip_file_utils import searchFileInZip, zipDir

# Definisci cosa esportare quando si fa "from pyLnLib.logger import *"
__all__ = [
    "searchFile",
    "searchFileOnFS",
    "dirList",
    "loadIni",
    "writeIni",
    "writeFile",
    # 'YamlEngine',
    "get_yaml_engine",
    "searchFileInZip",
    "zipDir",
]

if __INIT__PY__DEBUG:
    print(f"{__name__} - end loading")
