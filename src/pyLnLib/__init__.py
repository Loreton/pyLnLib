# pyLnLib/__init__.py
#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 07-07-2026 09.54.38
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
# IMPORT DAL SOTTO-PACKAGE  system
# ============================================================
from .system.acquire_lock           import acquire_lock
from .system.ln_run                 import lnRun
from .system.modulo02                 import test02
from .system.ln_run_stream_class    import lnRunStream_Class as lnRunStream
from .system.signal_handler         import signalHandler

# ============================================================
# IMPORT DAL SOTTO-PACKAGE files
# ============================================================
from .files.write_file              import writeFile
from .files.yaml_loader_class       import lnYamlEnvironment
from .files.zip_file_utils          import searchFileInZip
from .files.file_utils_new              import searchFile, searchFileOnFS, dirList
from .files.ini_file                import loadIni, writeIni, updateIniKey

# ============================================================
# IMPORT DAL SOTTO-PACKAGE logger
# ============================================================
# from .logger.dummy_logger           import DummyPrintLogger
# from .logger.ln_colored_logger      import lnColoredLogger as lnLogger, testLogger
from pyLnLib.logger.ln_colored_logger import (
    init_logger,
    lnColoredLogger as lnLogger,
    get_logger,
    # set_logger,
    # is_logger_initialized,
    # reset_logger,
    # testLogger,
)
# pyLnLib/__init__.py
"""
pyLnLib - Libreria di utility per Python
"""



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
# from .context                       import gVars, get_logger, get_colors, get_project_vars
from .context                       import gVars, get_colors, get_project_vars
from .ln_utils                      import flatten_nested_list, flatten_and_filter
from .colors                      import Colors


# ============================================================
# ESPORTAZIONE PER `from pyLnLib import *`
# ============================================================

__all__ = [
    'Colors',

    # Logger
    'lnLogger',
    # 'lnColoredLogger',
    'init_logger',
    'get_logger',
    # 'set_logger',
    # 'is_logger_initialized',
    # 'reset_logger',
    # 'testLogger',

    # 'lnLogger',
    # 'testLogger',
    # 'get_logger',
    # 'get_colors',
    'get_project_vars',
    # 'DummyPrintLogger',

    # Beep
    'playBeep',
    'play_success_sound',
    'play_error_sound',
    'play_notification_sound',

    # Context
    'gVars',
    # 'Colors',
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


