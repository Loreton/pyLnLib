# pyLnLib/__init__.py
#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 22-06-2026 21.32.40
#

"""
pyLnLib - Libreria di utility per Python
"""

__version__ = "0.0.1"
__author__ = "Loreto Notarantonio"


# ✅ Import dal package principale (usa pyLnLib/__init__.py)

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
from .files.yaml_loader_class       import lnYamlEnvironment
from .files.zip_file_utils          import searchFileInZip
from .files.file_utils              import searchFile, searchFileOnFS, dirList
from .files.ini_file                import loadIni, writeIni, updateIniKey

# ============================================================
# IMPORT DAL SOTTO-PACKAGE logger
# ============================================================
from .logger.dummy_logger           import DummyPrintLogger
from .logger.ln_colored_logger      import lnColoredLogger as lnLogger, testLogger


# ============================================================
# IMPORT DAL SOTTO-PACKAGE lndict
# ============================================================
from .lndict.ln_dict_class          import lnDict
from .lndict.ln_dict_resolver_class import LnDictResolver

# ============================================================
# IMPORT DA ALTRI MODULI
# ============================================================
from .keyboard_prompt               import keyboardPrompt
from .beep                          import playBeep, play_success_sound, play_error_sound, play_notification_sound
from .context                       import gVars, Colors
from .ln_utils                      import flatten_nested_list, flatten_and_filter


# ============================================================
# ESPORTAZIONE PER `from pyLnLib import *`
# ============================================================

# __all__ = [
#     # Logger
#     'lnLogger',
#     'testLogger',
#     'DummyPrintLogger',

#     # Beep
#     'playBeep',
#     'play_success_sound',
#     'play_error_sound',
#     'play_notification_sound',

#     # Context
#     'gVars',
#     'Colors',
#     'lnLib.dirList',

#     # Utils
#     'flatten_nested_list',
#     'flatten_and_filter',

#     # Keyboard
#     'keyboardPrompt',

#     # Version
#     '__version__',
#     '__author__',
# ]

print(f"Logger primary package loaded: {__name__}")