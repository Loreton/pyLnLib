# pyLnLib/__init__.py
#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 11-07-2026 14.25.10
#

"""
pyLnLib - Libreria di utility per Python
"""


import os
os.environ["__INIT__PY__DEBUG"] = "False"

__INIT__PY__DEBUG = os.environ.get("__INIT__PY__DEBUG", "False")
if __INIT__PY__DEBUG == "True":
    print(f"{__name__} - start loading")

__version__ = "0.0.1"
__author__ = "Loreto Notarantonio"


# ✅ Import dal package principale (usa pyLnLib/__init__.py)
# ============================================================
# IMPORT DAL SOTTO-PACKAGE logger (messo per primo in modo che venga caricato prima di altri sotto-package)
# ============================================================
from .logger.ln_colored_logger import (
                                        lnColoredLogger as lnLogger,
                                        init_logger,
                                        get_logger,
                                        testLogger,
                                    )


# ============================================================
# IMPORT DAL SOTTO-PACKAGE  system
# ============================================================
from .system.acquire_lock           import acquire_lock
from .system.ln_run                 import lnRun
from .system.ln_run_stream_class    import lnRunStream_Class as lnRunStream
from .system.signal_handler         import signalHandler

# ============================================================
# IMPORT DAL SOTTO-PACKAGE files
# ============================================================
from .files.write_file              import writeFile
from .files.yaml_loader_class       import get_yaml_engine
from .files.zip_file_utils          import searchFileInZip, zipDir
from .files.file_utils              import searchFile, searchFileOnFS, dirList
from .files.ini_file                import loadIni, writeIni, updateIniKey


# ============================================================
# IMPORT DAL SOTTO-PACKAGE lndict
# ============================================================
from .lndict.ln_dict_class          import lnDict
from .lndict.ln_dict_resolver_class import LnDictResolver

# ============================================================
# IMPORT DA ALTRI MODULI
# ============================================================
from .keyboard_prompt               import keyboardPrompt
from .beep                          import playBeep, play_success_sound, play_error_sound, play_notification_sound, get_beep_types
from .context                       import gVars,  get_project_vars
from .ln_utils                      import flatten_nested_list, flatten_and_filter
from .colors                        import get_colors

# ============================================================
# IMPORT DAL SOTTO-PACKAGE  git
# ============================================================
from .git.pyproject_class           import PyProjectManager
from .git.changelog_class           import ChangeLogManager

# =========================================================
# ============================================================
# ESPORTAZIONE PER `from pyLnLib import *`
# ============================================================

__all__ = [
    'get_colors',

    # git
    'PyProjectManager',
    'ChangeLogManager',

    # Logger
    'lnLogger',
    'init_logger',
    'get_logger',
    'testLogger',
    'get_project_vars',

    # Beep
    'playBeep',
    'play_success_sound',
    'play_error_sound',
    'play_notification_sound',

    # Context
    'gVars',
    # 'Colors',
    # 'get_yaml_engine',
    'get_colors',
    'dirList',
    'get_logger',
    'get_beep_types',

    # lnDict
    'lnDict',
    'LnDictResolver',

    # files
    'writeFile',
    'searchFileInZip',
    'searchFile',
    'searchFileOnFS',
    'dirList',
    'loadIni',
    'writeIni',
    'updateIniKey',
    'zipDir',
    'get_yaml_engine',

    # system
    'lnRun',
    'lnRunStream',
    'signalHandler',
    'acquire_lock',

    # Utils
    'flatten_nested_list',
    'flatten_and_filter',

    # Keyboard
    'keyboardPrompt',

    # Version
    '__version__',
    '__author__',
]

if __INIT__PY__DEBUG == "True":
    print(f"{__name__} - end loading")
