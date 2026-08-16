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
from .varie.keyboard_prompt import keyboardPrompt
from .varie.ln_utils import flatten_and_filter, flatten_nested_list
from .varie.beep import BeepPlayer

from .colors import get_colors
from .emoji import get_emoji
from .context import ctx, pVars


# files
from .files.write_file import writeFile
from .files.yaml_loader_class import get_yaml_engine
from .files.zip_file_utils import searchFileInZip, zipDir
from .files.file_utils import get_file_list, searchFile, searchFileOnFS, scan_directory, get_unique_filename
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
from .epub.epub_manager import EpubProcessor, get_epub_processor, manage_epub_processor
from .epub.author_registry import AuthorRegistry

# calibre
from .calibre.calibre_metadata_reader import CalibreMetadataReader, calibre_test

# varie
from .varie.menu_from_list import menu_select_from_list



# ============================================================
# ESPORTAZIONE PER `from pyLnLib import *`
# ============================================================
__all__ = [
    # logger
    "lnLogger",
    "get_logger",
    "testLogger",


    # generics
    "ctx",
    "pVars",

    "BeepPlayer",
    "acquire_lock",
    "get_colors",
    "get_emoji",
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
    "get_unique_filename",
    "updateIniKey",
    "writeFile",
    "writeIni",

    # epub
    "EpubProcessor",
    "get_epub_processor",
    "manage_epub_processor",
    "AuthorRegistry",

    # calibre
    "CalibreMetadataReader",
    "calibre_test",

    # system
    "clean_doc",
    "lnRun",
    "lnRunStream",
    "signalHandler",
    "start_signal_handler",
    "zipDir",

    # varie
    "menu_select_from_list",
]

if __INIT__PY__DEBUG == "True":
    print(f"{__name__} - end loading")
