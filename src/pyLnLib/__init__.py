#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 11-07-2026 14.25.10
#
# ruff: noqa: I001 Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
# ruff: noqa: I022
# ruff: noqa: RUF022 `__all__` is not sorted help: Apply an isort-style sorting to `__all__` (Ruff RUF022)

"""
pyLnLib - Libreria di utility per Python
"""

import os

os.environ["__INIT__PY__DEBUG"] = "False"

__INIT__PY__DEBUG = os.environ.get("__INIT__PY__DEBUG", "False")
if __INIT__PY__DEBUG == "True":
    print(f"{__name__} - start loading")


# ✅ Import dal package principale (usa pyLnLib/__init__.py)
# ============================================================
# IMPORT  logger (messo per primo in modo che venga caricato prima di altri sotto-package)
# ============================================================
from .logger.ln_colored_logger import (
                                        lnColoredLogger as lnLogger,
                                        init_logger,
                                        get_logger,
                                        testLogger,
                                    )

from .beep import BeepPlayer
from .colors import get_colors
from .context import ctx, get_project_vars
from .context_V2 import init_context, get_context
from .files.file_utils import get_file_list, searchFile, searchFileOnFS, scan_directory, unique_filename
from .files.ini_file import loadIni, updateIniKey, writeIni

# ============================================================
# import dal sotto-package files
# ============================================================
from .files.write_file import writeFile
from .files.yaml_loader_class import get_yaml_engine
from .files.zip_file_utils import searchFileInZip, zipDir
from .git.changelog_class import ChangeLogManager

# ============================================================
# import dal sotto-package  git
# ============================================================
from .git.pyproject_class import PyProjectManager

# ============================================================
# import da altri moduli
# ============================================================
from .keyboard_prompt import keyboardPrompt
from .ln_utils import flatten_and_filter, flatten_nested_list

# ============================================================
# import dal sotto-package lndict
# ============================================================
from .lndict.ln_dict_class import lnDict
from .lndict.ln_dict_resolver_class import LnDictResolver


# ============================================================
# IMPORT DAL SOTTO-PACKAGE  system
# ============================================================
from .system.acquire_lock import acquire_lock
from .system.ln_run import lnRun
from .system.ln_run_stream_class import lnRunStream_Class as lnRunStream
from .system.signal_handler import signalHandler

# ============================================================
# ESPORTAZIONE PER `from pyLnLib import *`
# ============================================================
__all__ = [
    "lnLogger",
    "get_logger",

    "BeepPlayer",
    "ChangeLogManager",
    "LnDictResolver",
    "PyProjectManager",
    "acquire_lock",
    "ctx",
    # "GlobalVars_V2",
    "init_context",
    "get_context",
    "get_file_list",
    "flatten_and_filter",
    "flatten_nested_list",
    # "get_beep_types",
    "get_colors",
    "get_project_vars",
    "get_yaml_engine",
    "init_logger",
    "keyboardPrompt",
    "lnDict",
    "lnRun",
    "lnRunStream",
    "loadIni",
    # "playBeep",
    # "play_error_sound",
    # "play_notification_sound",
    # "play_success_sound",
    "searchFile",
    "searchFileInZip",
    "searchFileOnFS",
    "scan_directory",
    "signalHandler",
    "testLogger",
    "updateIniKey",
    "unique_filename",
    "writeFile",
    "writeIni",
    "zipDir",
]

if __INIT__PY__DEBUG == "True":
    print(f"{__name__} - end loading")
