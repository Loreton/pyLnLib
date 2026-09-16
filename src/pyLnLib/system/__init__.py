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
from .timing import timing_base, timing_logger

__all__ = [
    "acquire_lock",
    "clean_doc",
    "lnRun",
    "lnRunStream",
    "signalHandler",
    "start_signal_handler",
    "timing_base",
    "timing_logger",
]


if __INIT__PY__DEBUG:
    print(f"{__name__} - end loading")
