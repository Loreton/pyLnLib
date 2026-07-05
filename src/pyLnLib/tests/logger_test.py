#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 05-07-2026 14.18.31
#

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import sys
# from unittest.main import main; sys.dont_write_bytecode = True

# import pyLnLib
from pyLnLib.context import gVars as ctx, get_logger, get_colors
# from pyLnLib.logger import lnLogger
C=get_colors()
logger = get_logger(test=True)


def main_01():
    logger.info("Logger creato automaticamente. (name: %s)", logger.name)
    logger.setNameLength(dynamic=True, length=0)
    logger.info("Logger personalizzato (name: %s)", logger.name)
    logger.setConsoleLoggerLevel(level='debug')
    logger1 = get_logger(test=True)
    logger1.info("Logger test (name: %s)", logger.name)

    # Esempio di log dinamico
    logger.debug("Debug dinamico!", color=C.cyan)
    logger.info("Informazione importante", color=C.green)
    logger.warning("Attenzione!", color=C.yellow)
    logger.error("Errore!", color=C.red)
    logger.critical("Critico!", color=C.magenta)
    logger.notify("Notifica speciale", color=C.blue)


# -------------------------------
# Test
# -------------------------------
if __name__ == "__main__":
    main_01()
