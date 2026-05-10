#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 10-05-2026 10.00.36
#


import  sys; sys.dont_write_bytecode=True
import os






### --------------------
### --- project modules
### --------------------
from ..context    import gVars as gv
from .file_utils import getFileContent




###############################################
#    I N I   - I N I   - I N I   -
###############################################

############  INI Files ###############################
def _iniSet():
    import configparser
    ini_config=configparser.ConfigParser(
                        allow_no_value=False,
                        delimiters=('=', ':'),
                        comment_prefixes=('#',';'),
                        inline_comment_prefixes=(';',),
                        strict=True,          # True: impone unique key/session
                        empty_lines_in_values=False,
                        default_section='DEFAULT',
                        # "interpolation": configparser.ExtendedInterpolation() # mi dà errore con le variabili
                        interpolation=configparser.BasicInterpolation()
                    )

    ini_config.optionxform = str        # mantiene il case nei nomi delle section e delle Keys (Assicurarsi che i riferimenti a vars interne siano case-sensitive)

    return ini_config

###############################################
#
###############################################
def loadIni(filepath: str=None, content: str=None, search_paths: list=[], exit_on_error: bool=True):
    # from .file_utils import getFileContent

    my_serarch_paths = search_paths + gv.search_paths
    ini_dict = {}

    if not content: ### read contetn
        if not (content := getFileContent(filename=filepath, search_paths=my_serarch_paths)):
            gv.logger.error(f"File not found: {filepath}", exc_info=exit_on_error)


    if content:
        content = os.path.expandvars(content)
        ### -----------------------------
        ### if it's a ini file
        ### -----------------------------
        ini_config=_iniSet()
        ini_config.read_string(content)
        for section in ini_config.sections():
            ini_dict[section] = {}
            for option in ini_config.options(section):
                ini_dict[section][option] = ini_config.get(section, option)

    return ini_dict

