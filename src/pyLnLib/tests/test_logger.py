#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 20-05-2026 21.28.26
#

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys; sys.dont_write_bytecode = True
import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from pyLnLib import Color, lnLogger, testLogger, DummyPrintLogger


# -------------------------------
# Test
# -------------------------------
if __name__ == "__main__":
    logger=lnLogger(name=Path(__file__).stem,
                            console_logger_level="trace", ### --- default
                            file_logger_level="warning",
                            logging_dir=None, # no filehandler
                            threads=False)


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



