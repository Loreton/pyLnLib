#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 11-05-2026 09.50.22
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

    logger.test(logger=logger)

    logger=DummyPrintLogger(name="DummyPrintLogger",
                            console_logger_level="trace"
                            )


    testLogger(logger=logger)

    print("\n"*2)



