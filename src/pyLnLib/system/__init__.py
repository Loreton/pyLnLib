#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio#


"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""

import os

__INIT__PY__DEBUG = os.environ.get("__INIT__PY__DEBUG", "False") == "True"
if __INIT__PY__DEBUG:
    print(f"{__name__} - start loading")


from .acquire_lock import acquire_lock
from .ln_run import lnRun
from .ln_run_stream_class import lnRunStream_Class as lnRunStream
from .signal_handler import signalHandler, start_signal_handler
from .clean_doc import clean_doc

all = [
    acquire_lock,
    lnRun,
    lnRunStream,
    signalHandler,
    clean_doc,
    start_signal_handler
]


if __INIT__PY__DEBUG:
    print(f"{__name__} - end loading")
