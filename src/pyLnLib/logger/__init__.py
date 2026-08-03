# pyLnLib/logger/__init__.py
#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio

#


"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""
import os
__INIT__PY__DEBUG=os.environ.get("__INIT__PY__DEBUG", "False") == "True"
if __INIT__PY__DEBUG:
    print(f"{__name__} - start loading")


# from .dummy_logger   import DummyPrintLogger
from .ln_colored_logger import lnColoredLogger as lnLogger, testLogger, get_logger

# Definisci cosa esportare quando si fa "from pyLnLib.logger import *"
__all__ = [
    # 'DummyPrintLogger',
    'get_logger',
    'lnLogger',
    'testLogger',
]

if __INIT__PY__DEBUG:
    print(f"{__name__} - end loading")
