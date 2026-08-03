#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
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


# generics
from .keyboard_prompt import keyboardPrompt
from .ln_utils import flatten_and_filter, flatten_nested_list
from .beep import BeepPlayer
from .colors import get_colors


# files
from .files.write_file import writeFile
from .files.yaml_loader_class import get_yaml_engine
from .files.zip_file_utils import searchFileInZip, zipDir
from .files.file_utils import get_file_list, searchFile, searchFileOnFS, scan_directory, unique_filename
from .files.ini_file import loadIni, updateIniKey, writeIni


# git
from .git.pyproject_class import PyProjectManager
from .git.changelog_class import ChangeLogManager


# lndict
from .lndict.ln_dict_class import lnDict
from .lndict.ln_dict_resolver_class import LnDictResolver


# system
from .system.acquire_lock import acquire_lock
from .system.ln_run import lnRun
from .system.ln_run_stream_class import lnRunStream_Class as lnRunStream
from .system.signal_handler import signalHandler, start_signal_handler
from .system.clean_doc import clean_doc

# regex
from .regex.ln_regex import replace, and_search, or_search, search_term

# pub
from .epub.epub_manager import EpubProcessor

# calibre
from .calibre.calibre_metadata_reader import CalibreMetadataReader, test_calibre



# ============================================================
# ESPORTAZIONE PER `from pyLnLib import *`
# ============================================================
__all__ = [
    # logger
    "lnLogger",
    "get_logger",
    "testLogger",


    # generics
    "BeepPlayer",
    "acquire_lock",
    "get_colors",
    "keyboardPrompt",

    # lndict
    "lnDict",
    "LnDictResolver",

    # ln_utils
    "flatten_and_filter",
    "flatten_nested_list",


    # regex
    "and_search",
    "or_search",
    "replace",
    "search_term",

    # git
    "ChangeLogManager",
    "PyProjectManager",

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

    # epub
    "EpubProcessor",

    # calibre
    "CalibreMetadataReader",
    "test_calibre",

    # system
    "clean_doc",
    "lnRun",
    "lnRunStream",
    "signalHandler",
    "start_signal_handler",
    "zipDir",
]

if __INIT__PY__DEBUG == "True":
    print(f"{__name__} - end loading")
