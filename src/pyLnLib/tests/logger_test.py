#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 27-06-2026 18.54.20
#

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import sys
# from unittest.main import main; sys.dont_write_bytecode = True

# import pyLnLib
from pyLnLib.context import gVars as ctx
from pyLnLib.logger import lnLogger
C=ctx.get_colors()
# logger = ctx.get_logger()


def main_02():
    # Caso 0: Non creare se non esiste
    logger = ctx.get_logger()
    if logger is None:
        print("Logger non esiste ancora")

    # Caso 1: Logger automatico (create=True di default)
    logger = ctx.get_logger(create=True, logger_name="test_logger")  # Crea automaticamente
    if logger:
        logger.info("Logger creato automaticamente. (name: %s)", logger.name)


    # Caso 4: Ottenere il logger esistente (senza creare)
    logger = ctx.get_logger()
    if logger:
        logger.setNameLength(dynamic=True, length=0)
        logger.info("Logger personalizzato (name: %s)", logger.name)


def main_01():
    # Caso 0: Non creare se non esiste
    logger = ctx.get_logger()
    if logger is None:
        print("Logger non esiste ancora")

    # Caso 1: Logger automatico (create=True di default)
    logger = ctx.get_logger(create=True, logger_name="test_logger")  # Crea automaticamente
    if logger:
        logger.info("Logger creato automaticamente. (name: %s)", logger.name)


    # Caso 2: Non creare se non esiste
    logger = ctx.get_logger()
    if logger is None:
        print("Logger non esiste ancora")

    # Caso 3: Logger personalizzato
    custom_logger = lnLogger(
        name="custom_logger",
        console_logger_level="INFO",
        file_logger_level="DEBUG",
        logging_dir=ctx.get_log_dir(),
        threads=False,
    )
    ctx.set_logger(custom_logger)

    # Caso 4: Ottenere il logger esistente (senza creare)
    logger = ctx.get_logger()
    if logger:
        logger.setNameLength(dynamic=True, length=0)
        logger.info("Logger personalizzato (name: %s)", logger.name)

    # Caso 5: In un modulo che non vuole creare automaticamente
    logger = ctx.get_logger(create=False)
    if logger is None:
        print("Attenzione: logger non inizializzato, uso fallback")
    else:
        logger.info("Logger disponibile (name: %s)", logger.name)




# -------------------------------
# Test
# -------------------------------
if __name__ == "__main__":
    # main_01()
    main_02()
