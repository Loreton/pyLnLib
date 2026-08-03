# pyLnLib/lndict/__init__.py
#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio

#
# import os
import os
__INIT__PY__DEBUG=os.environ.get("__INIT__PY__DEBUG", "False") == "True"
if __INIT__PY__DEBUG:
    print(f"{__name__} - start loading")

"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""
from   .ln_dict_class              import lnDict
from   .ln_dict_resolver_class     import LnDictResolver

# Definisci cosa esportare quando si fa "from pyLnLib.logger import *"
__all__ = [
    'lnDict',
    'LnDictResolver',
]


if __INIT__PY__DEBUG:
    print(f"{__name__} - end loading")
