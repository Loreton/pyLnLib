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
                                        # init_logger,
                                        get_logger,
                                        testLogger,
                                    )

from .beep import BeepPlayer
from .colors import get_colors
from .context import init_context, get_context

# ============================================================
# import dal sotto-package files
# ============================================================
from .files.write_file import writeFile
from .files.yaml_loader_class import get_yaml_engine
from .files.zip_file_utils import searchFileInZip, zipDir
from .files.file_utils import get_file_list, searchFile, searchFileOnFS, scan_directory, unique_filename
from .files.ini_file import loadIni, updateIniKey, writeIni

# ============================================================
# import dal sotto-package  git
# ============================================================
from .git.pyproject_class import PyProjectManager
from .git.changelog_class import ChangeLogManager

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
from .system.clean_doc import clean_doc


from .regex.ln_regex import replace, and_search, or_search, search_term

# ============================================================
# ESPORTAZIONE PER `from pyLnLib import *`
# ============================================================
__all__ = [
    # logger
    "lnLogger",
    "get_logger",
    # "init_logger",
    "testLogger",


    "get_context",
    "BeepPlayer",
    "ChangeLogManager",
    "PyProjectManager",
    "acquire_lock",
    "ctx",

    # lndict
    "lnDict",
    "LnDictResolver",

    # ln_utils
    "init_context",
    "flatten_and_filter",
    "flatten_nested_list",

    "get_colors",
    "get_project_vars",
    "keyboardPrompt",
    "lnRun",
    "lnRunStream",

    # regex
    "and_search",
    "or_search",
    "replace",
    "search_term",
    # "multi_near_words",
    # "multi_near_words_any_order",
    # "search_anywhere",
    # "multi_near_words_token_based",

    # files
    "get_yaml_engine",
    "get_file_list",
    "loadIni",
    "scan_directory",
    "searchFile",
    "searchFileInZip",
    "searchFileOnFS",
    "unique_filename",
    "updateIniKey",
    "writeFile",
    "writeIni",

    # system
    "clean_doc",
    "signalHandler",
    "zipDir",
]

if __INIT__PY__DEBUG == "True":
    print(f"{__name__} - end loading")
