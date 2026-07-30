# pyLnLib/regex/__init__.py


import os

"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""

__INIT__PY__DEBUG=os.environ.get("__INIT__PY__DEBUG", "False") == "True"
if __INIT__PY__DEBUG:
    print(f"{__name__} - start loading")


from .ln_regex import replace, and_search, or_search

# Definisci cosa esportare quando si fa "from pyLnLib.regex import *"
__all__ = [
    'and_search',
    'or_search',
    'replace',
    # 'multi_near_words',
    # 'multi_near_words_any_order',
    # 'search_anywhere',
    # 'multi_near_words_token_based',
]

if __INIT__PY__DEBUG:
    print(f"{__name__} - end loading")
