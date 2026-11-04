# pyLnLib/regex/__init__.py

# ruff: noqa: I001
import os

"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""

__INIT__PY__DEBUG=os.environ.get("__INIT__PY__DEBUG", "False") == "True"
if __INIT__PY__DEBUG:
    print(f"{__name__} - start loading")


# from .ln_regex import replace, and_search, or_search, search_term, mergeOccurrencies
from . import ln_regex
# Definisci cosa esportare quando si fa "from pyLnLib.regex import *"
# ruff: noqa: RUF022 - `__all__` is not sorted help: Apply an isort-style sorting to `__all__`
__all__ = [
    # 'and_search',
    # 'mergeOccurrencies',
    # 'or_search',
    # 'replace',
    # 'search_term',
    'ln_regex',
]

if __INIT__PY__DEBUG:
    print(f"{__name__} - end loading")
