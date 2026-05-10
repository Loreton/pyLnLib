#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 10-05-2026 10.24.01
#

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys; sys.dont_write_bytecode = True
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

from pyLnLib import Color, lnLogger, testLogger, DummyPrintLogger


# -------------------------------
# Test
# -------------------------------
if __name__ == "__main__":
    logger=lnLogger(name="test_log",
                            console_logger_level="info", ### --- default
                            file_logger_level="warning",
                            logging_dir=None, # no filehandler
                            threads=False)

    print("\n"*2)
    print("*"*60)
    print("--- LnLogger ---")
    print("*"*60)

    testLogger(logger=logger)




    print("\n"*2)
    print("*"*60)
    print("--- DummyPrintLogger ---")
    print("*"*60)


    logger=DummyPrintLogger(level="INFO",
                            show_caller=True,
                            module=False,
                            function=True
                            )


    testLogger(logger=logger)

    print("\n"*2)



