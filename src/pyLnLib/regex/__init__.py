# pyLnLib/regex/__init__.py


import os

"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""

__INIT__PY__DEBUG=os.environ.get("__INIT__PY__DEBUG", "False") == "True"
if __INIT__PY__DEBUG:
    print(f"{__name__} - start loading")


from .ln_regex import multi_near_words, multi_near_words_any_order

# Definisci cosa esportare quando si fa "from pyLnLib.regex import *"
__all__ = [
    'multi_near_words',
    'multi_near_words_any_order',
    # 'multi_near_words_token_based',
]

if __INIT__PY__DEBUG:
    print(f"{__name__} - end loading")
