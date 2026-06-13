#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 13-06-2026 14.00.47
#
import os

#!/usr/bin/env python3
"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""
'''
	uv remove pyLnLib
	uv pip uninstall pyLnLib

	- per i progetti strutturati python:
	uv add /home/loreto/filu/Programming/gitREPO/pyLnLib
	- per altri progetti:
	uv pip install -e  /home/loreto/filu/Programming/gitREPO/pyLnLib

	test: python -c "import pyLnLib.system; print('OK')"
	test: python -c "import pyLnLib.system; print(pyLnLib.system)"
'''


print("ci sono")
# ---- system
from   .system.acquire_lock        import acquire_lock
from   .system.ln_run              import lnRun
from   .system.ln_run_stream_class import lnRunStream_Class as lnRunStream
from   .system.signal_handler             import signalHandler

# ---- files
from   .files.write_file                 import writeFile
from   .files.yaml_loader_class          import lnYamlEnvironment
from   .files.zip_file_utils             import searchFileInZip
from   .files.file_utils                 import searchFile, searchFileOnFS, dirList
from   .files.ini_file                   import loadIni, writeIni, updateIniKey


# ---- logger
from   .logger.dummy_logger               import DummyPrintLogger
from   .logger.ln_colored_logger           import lnColoredLogger as lnLogger, testLogger


# ---- lndict
from   .lndict.ln_dict_class              import lnDict
from   .lndict.ln_dict_resolver_class     import LnDictResolver

# ---- others
from   .colors                     import Color
from   .beep                       import playBeep as Beep
from   .context                    import gVars
from   .keyboard_prompt            import keyboardPrompt

# logger di default pronto all’uso
project_name=os.environ.get("PROJECT_NAME")
# log = DummyPrintLogger(name="test_log", console_logger_level="TRACE")