#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 10-05-2026 15.36.19
#

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys; sys.dont_write_bytecode = True
import os
# import logging
# from logging.handlers import RotatingFileHandler
# from typing import Optional
from pathlib import Path




from pyLnLib import gVars as ctx
from pyLnLib import lnLogger, DummyPrintLogger, lnYamlEnvironment, lnDict


# -------------------------------
# Test
# -------------------------------
if __name__ == "__main__":
    logger=lnLogger(name=Path(__file__).stem, console_logger_level="trace")
    ctx.logger=logger
    logger.test(logger=logger)

    # ctx.search_paths = ["conf"]
    env = lnYamlEnvironment(logger=logger, search_paths=["conf"], recursive=True)
    config_data = env.yaml_engine.load("/home/loreto/filu/lnEnv/pyScripts/ssh_tunnel_watchdog/conf/config.yaml")
    config: dict = lnDict(data=config_data)
    print(config)