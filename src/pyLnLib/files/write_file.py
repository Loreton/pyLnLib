#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 10-05-2026 10.02.18
#

import sys; sys.dont_write_bytecode=True; this=sys.modules[__name__]
import os
from pathlib import Path
from datetime import datetime
from types import SimpleNamespace




### --------------------
### --- project modules
### --------------------
from ..context  import gVars as gv; logger = gv.logger


##############################################################
# - WRITE - FILE
# - writeFile version: 18-07-2023 12.54.30
##############################################################
def writeFile(data: (str, list, dict), filepath: (str, os.PathLike), *, replace: bool=False, write_datetime: bool=True, **kwargs) -> bool:
    gv.logger.function(__name__, force_log=False)
    fout=Path(filepath).resolve()
    stacklevel = kwargs.pop("stacklevel", 1)
    gv.logger.debug('writing file: %s', fout)
    ret_code = False


    # else:

    is_list_in_list = any(isinstance(el, list) for el in data)

    _data = '\n'.join(data) if isinstance(data, list) else data

    comment_char='# '
    if fout.suffix == '.json':
        comment_char='// '



    if write_datetime:
        date_time=datetime.now().strftime("%d-%m-%Y %H:%M")
        _data=f"{comment_char}\n{comment_char} Write time: {date_time}\n{comment_char}\n" + _data

    if not _data.endswith('\n'):
        _data+="\n"

    if not fout.parent.exists():
        os.makedirs(fout.parent,  exist_ok=True)

    if not fout.exists() or replace:
        try:
            with open(fout, "w") as f:
                f.write(_data)
            gv.logger.notify('file %s has been written', fout, stacklevel=stacklevel+1 )
            ret_code = True

        except (Exception) as e:
            gv.logger.error('error writing file: %s', fout )
            gv.logger.error(e)

    else:
        gv.logger.error('file %s already exists. No changes', fout )

    return ret_code


