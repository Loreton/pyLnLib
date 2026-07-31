#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 10-05-2026 15.16.45
#

import sys; sys.dont_write_bytecode=True;
import os
# utils/logger_types.py
from typing import Protocol, Any, Optional
from pathlib import Path
from datetime import datetime
import inspect



class DummyPrintLogger:
    class Color:
        red        = '\033[31m'; redH       = '\033[91m'
        green      = '\033[32m'; greenH     = '\033[92m'
        yellow     = '\033[33m'; yellowH    = '\033[93m'
        blue       = '\033[34m'; blueH      = '\033[94m'
        magenta    = '\033[35m'; magentaH   = '\033[95m'
        cyan       = '\033[36m'; cyanH      = '\033[96m'
        white      = '\033[37m'; whiteH     = '\033[97m'
        reset      = '\033[0m'

    LEVELS = {
        "TRACE": (5,  "TRAC", Color.white),
        "DEBUG": (10, "DEBU", Color.cyan),
        "INFO":  (20, "INFO", Color.green),
        "NTFY":  (25, "NTFY", Color.greenH),
        "WARN":  (30, "WARN", Color.yellow),
        "ERROR": (40, "ERRO", Color.red),
        "CRIT":  (50, "CRIT", Color.magenta),
    }


    def __init__(self, name: str="DummyPrintLogger", console_logger_level="info"):
        self.level = self.LEVELS[console_logger_level.upper()][0]
        self.name = name
        self.show_caller = True
        self.module = True
        self.function = False
        self.test = testLogger

    def setLevel(self, level):
        self.level = self.LEVELS[level.upper()][0]


    def _caller(self):
        f = inspect.currentframe()
        for _ in range(3):  # salta stack interno logger
            f = f.f_back
        filename = Path(os.path.basename(f.f_code.co_filename)).stem
        lineno = f.f_lineno
        func = f.f_code.co_name
        if func=='<module>': func='main'
        caller=f":{lineno}"
        if self.module:
            caller=f"{filename}{caller}"
        if self.function:
            caller=f"{func}{caller}"
        # if modules: caller=f"{module}:{lineno}"

        return caller
        return f"{filename}.{func}:{lineno}"

    def _log(self, lvl, msg, *args, color=None):
        lvl_num, tag, default_color = self.LEVELS[lvl]

        if lvl_num < self.level:
            return

        color = color or default_color

        if args:
            try:
                msg = msg % args
            except Exception:
                msg = f"{msg} {args}"

        now = datetime.now().strftime("%H:%M:%S")
        caller = f"{self._caller()}" if self.show_caller else ""

        print(f"{color}{now} [{caller}] {tag}: {msg}{self.Color.reset}")

    def trace(self,     msg, *args, color=None, **kwargs): self._log("TRACE",  msg, *args, color=color)
    def notify(self,    msg, *args, color=None, **kwargs): self._log("NTFY",  msg, *args, color=color)

    def debug(self,     msg, *args, color=None, **kwargs): self._log("DEBUG",  msg, *args, color=color)
    def info (self,     msg, *args, color=None, **kwargs): self._log("INFO",   msg, *args, color=color)
    def warning(self,   msg, *args, color=None, **kwargs): self._log("WARN",   msg, *args, color=color)
    def error(self,     msg, *args, color=None, **kwargs): self._log("ERROR",  msg, *args, color=color)
    def critical(self,  msg, *args, color=None, **kwargs): self._log("CRIT",   msg, *args, color=color)



def testLogger(logger):
    print("\n")
    print("*"*60)
    print(f"--- Logger name: {logger.name}")
    print("*"*60)

    print("\n--- base colors ---")
    logger.debug("DEBUG default")
    logger.info("INFO default")
    logger.warning("WARNING default")
    logger.error("ERROR default")
    logger.critical("CRITICAL default")
    logger.notify("NOTIFY default")


    print("\n--- custom colors ---")
    logger.info("INFO in magenta", color=Color.magenta)
    logger.warning("WARNING in cyan", color=Color.cyan)
    logger.error("ERROR in yellowH", color=Color.yellowH)
    print("\n")




if __name__ == '__main__':
    C = DummyPrintLogger.Color
    # logger=DummyPrintLogger()
    log = DummyPrintLogger(level="WARN", show_caller=True, module=True, function=False)
    # log = DummyPrintLogger(level="WARN", show_caller=True)
    log.info("non lo vedi")
    log.error("questo sì")

    log.setLevel("TRACE")
    log.debug("ora sì: %s", "ok")
    log.info("Ciao: %s", "loreto", color=C.magentaH)
    log.error("Ciao")
    log.trace("Ciao")
    log.trace("Ciao", color=C.blue)
    log.notify("Ciao")
