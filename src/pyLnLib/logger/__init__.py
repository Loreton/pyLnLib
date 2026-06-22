# pyLnLib/logger/__init__.py
#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 22-06-2026 21.06.07
#


"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""



from .dummy_logger   import DummyPrintLogger
from .ln_colored_logger import lnColoredLogger as lnLogger, testLogger

# Definisci cosa esportare quando si fa "from pyLnLib.logger import *"
__all__ = [
    'DummyPrintLogger',
    'lnLogger',
    'testLogger',
]

# Per debug
print(f"Logger sub-package loaded: {__name__}")