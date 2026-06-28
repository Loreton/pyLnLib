# pyLnLib/lndict/__init__.py
#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 22-06-2026 21.14.28
#
# import os

print(f"\t{__name__} - start loading")

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

# Per debug
print(f"\t{__name__} - end loading")
