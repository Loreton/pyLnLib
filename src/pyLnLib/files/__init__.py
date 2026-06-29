# pyLnLib/files/f__init__.py
#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 22-06-2026 21.15.31
#

"""
pyLnLib - libreria personale di utility Python
Autore: Loreto Notarantonio
"""
import os
__INIT__PY__DEBUG = os.environ.get("__INIT__PY__DEBUG", "False") == "True"
if __INIT__PY__DEBUG:
    print(f"{__name__} - start loading")


from .file_utils_new        import searchFile, searchFileOnFS, dirList
from .ini_file          import loadIni, writeIni
from .write_file        import writeFile
from .yaml_loader_class import lnYamlEnvironment
from .zip_file_utils    import searchFileInZip


# Definisci cosa esportare quando si fa "from pyLnLib.logger import *"
__all__ = [
    'searchFile',
    'searchFileOnFS',
    'dirList',
    'loadIni',
    'writeIni',
    'writeFile',
    'lnYamlEnvironment',
    'searchFileInZip',
]


if __INIT__PY__DEBUG == "True":
    print(f"{__name__} - end loading")
