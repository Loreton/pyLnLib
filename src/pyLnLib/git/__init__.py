# pyLnLib/files/f__init__.py
#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio

#

"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""
import os
__INIT__PY__DEBUG = os.environ.get("__INIT__PY__DEBUG", "False") == "True"
if __INIT__PY__DEBUG:
    print(f"{__name__} - start loading")


from .changelog_class        import ChangeLogManager
from .pyproject_class        import PyProjectManager


# Definisci cosa esportare quando si fa "from pyLnLib.logger import *"
__all__ = [
    'ChangeLogManager',
    'PyProjectManager',
]

if __INIT__PY__DEBUG:
    print(f"{__name__} - end loading")
