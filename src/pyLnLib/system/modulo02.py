#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 07-07-2026 12.11.48
#


import sys

sys.dont_write_bytecode = True
### - project modules
from ..context import get_colors
from pyLnLib.logger import get_logger

C = get_colors()
logger = get_logger()


# ##################################################
# # lnRun
# ##################################################
def test02():
    # logger = get_logger()
    print(C.redH, "ciao sono il secondo modulo", C.reset)
    logger.info("ciao sono il secondo modulo")
