#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 27-06-2026 18.54.20
#

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys; sys.dont_write_bytecode = True

# import pyLnLib
from pyLnLib.context import gVars as ctx
from pyLnLib.logger import testLogger
from logger.ln_colored_logger import lnColoredLogger

C=ctx.Colors
logger=ctx.get_logger()


# -------------------------------
# Test
# -------------------------------
if __name__ == "__main__":
    # Crea il logger
    logger = lnColoredLogger(
        name=__name__,
        console_logger_level="INFO",
        file_logger_level="DEBUG",
        logging_dir=ctx.get_log_dir(),
        threads=False,
    )
    logger.setNameLength(dynamic=True, length=0)

    # Salva il logger nel context
    ctx.logger = logger

    # logger = get_logger()
    print("Logger inizializzato!")
    logger.info("Questo è un test dal context.py")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.notify("Notify message")
    logger.function("Function message")


    print(f"\nProject: {ctx.project_name}")
    print(f"Temp dir: {ctx.temp_dir}")
    print(f"Log dir: {ctx.get_log_dir()}")

    print(ctx.to_dict())

    # logger=lnLogger(name=Path(__file__).stem,
    #                         console_logger_level="trace", ### --- default
    #                         file_logger_level="warning",
    #                         logging_dir=None, # no filehandler
    #                         threads=False)


    dynamic_length=False
    logger.setNameLength(dynamic=False, length=10)
    print("\n")
    print("*"*60)
    print(f"--- Logger name: {logger.name} {dynamic_length = }")
    print("*"*60)
    testLogger(logger)



    dynamic_length=True
    logger.setNameLength(dynamic=True, length=0)
    print("\n")
    print("*"*60)
    print(f"--- Logger name: {logger.name} {dynamic_length = }")
    print("*"*60)
    testLogger(logger)



    print("\n"*2)
