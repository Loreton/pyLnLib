#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 07-07-2026 12.15.44
#

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import sys
# from unittest.main import main; sys.dont_write_bytecode = True

# import pyLnLib

import os
from pyLnLib import gVars, init_logger, get_logger
from pyLnLib import  test02


def main_01():
    from pyLnLib.context import gVars as ctx, get_logger, get_colors
    # from pyLnLib.logger import lnLogger
    C=get_colors()
    logger = get_logger(test=True)
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


def context_logger_separated():
    # 1. Imposta il nome del progetto
    os.environ["LN_PROJECT_NAME"] = "logger_TEST"

    # 2. Importa context e logger_setup
    # 2. Importa context e logger

    # 3. Inizializza il logger (SUBITO, prima di importare altri moduli)
    logger = init_logger(logger_name="logger_TEST", test=False)

    # 4. Ora importa gli altri moduli (che possono usare get_logger())
    # from lnsync.core.parse_input import ParseInput
    # from lnsync.core.lnsync_class import LnSync

    logger.info("Main started")
    logger.info(f"logger name:  {logger.name}")
    logger.info(f"Project:      {gVars.project_name}")
    logger.info(f"Temp dir:     {gVars.temp_dir}")
    logger.info(f"Log dir:      {gVars.get_log_dir()}")

        # ... resto del codice

# -------------------------------
# Test
# -------------------------------
if __name__ == "__main__":
    # main_01()
    context_logger_separated()
    test02()
