# /home/loreto/filu/Programming/gitREPO/pyLnLib/src/pyLnLib/sqLite/__init__.py
# updated by ...: Loreto Notarantonio#


"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""

import os

__INIT__PY__DEBUG = os.environ.get("__INIT__PY__DEBUG", "False") == "True"
if __INIT__PY__DEBUG:
    print(f"{__name__} - start loading")


from .SQLite_Class_LnNew import Table, Database

__all__ = [
    "Database",
    "Table",
]


if __INIT__PY__DEBUG:
    print(f"{__name__} - end loading")
