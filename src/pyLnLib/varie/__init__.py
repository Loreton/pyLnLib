# pyLnLib/files/f__init__.py
#

"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""
import os
__INIT__PY__DEBUG = os.environ.get("__INIT__PY__DEBUG", "False") == "True"
if __INIT__PY__DEBUG:
    print(f"{__name__} - start loading")


from .menu_from_list        import  select_from_list
from .beep        import BeepPlayer
from .keyboard_prompt import keyboardPrompt
from .ln_utils import flatten_and_filter, flatten_nested_list


# Definisci cosa esportare quando si fa "from pyLnLib.logger import *"
__all__ = [
    "BeepPlayer",
    "flatten_and_filter",
    "flatten_nested_list",
    "keyboardPrompt",
    "select_from_list",
]

if __INIT__PY__DEBUG:
    print(f"{__name__} - end loading")
