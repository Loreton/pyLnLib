#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 11-05-2026 09.40.53
#
import os

#!/usr/bin/env python3
"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""

# ---- system
from   .system.acquire_lock        import acquire_lock
from   .system.ln_run              import lnRun
from   .system.ln_run_stream_class import lnRunStream_Class as lnRunStream
from   .system.signal_handler             import signalHandler

# ---- files
from   .files.write_file                 import writeFile
from   .files.yaml_loader_class          import lnYamlEnvironment
from   .files.zip_file_utils             import searchFileInZip
from   .files.file_utils                 import searchFile, searchFileOnFS
from   .files.ini_loader                 import loadIni


# ---- logger
from   .logger.dummy_logger               import DummyPrintLogger
from   .logger.logger_colored            import lnLoggerColored as lnLogger, testLogger


# ---- lndict
from   .lndict.ln_dict_class              import lnDict
from   .lndict.ln_dict_resolver_class     import LnDictResolver

# ---- others
from   .colors                     import Color
from   .context                    import gVars
from   .keyboard_prompt            import keyboardPrompt

# logger di default pronto all’uso
project_name=os.environ.get("PROJECT_NAME")
# log = DummyPrintLogger(name="test_log", console_logger_level="TRACE")