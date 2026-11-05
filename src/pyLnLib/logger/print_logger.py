#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
#
#  ruff: noqa: E402 Module level import not at top of file (Ruff E402)
#  ruff: noqa: E701 Multiple statements on one line (colon) (Ruff E701)

import sys
from webbrowser import get; sys.dont_write_bytecode=True;
from pathlib import Path
from datetime import datetime
import inspect

from ..colors import get_colors

class PrintLogger:
    def __init__(self, name: str="PrintLogger", console_logger_level: str="info", time_caller_prefix: bool=False):
        self.Colors = get_colors() # per chi volesse prelevare i Colori (per dargli un nome parlante))
        self.C = self.Colors # per questa classe

        self.LEVELS = {
            "trace":     (5,  "TRACE", self.C.trace),
            "debug":     (10, "DEBUG", self.C.debug),
            "info":      (20, "INFO ", self.C.info),
            "notify":    (25, "NOTFY", self.C.notify),
            "warning":   (30, "WARN ", self.C.warning),
            "error":     (40, "ERROR", self.C.error),
            "critical":  (50, "CRIT ", self.C.critical),
        }

        self.level = self.LEVELS[console_logger_level.lower()][0]
        self.name = name
        self.show_caller = True
        self.module = True
        self.function = False
        self.time_caller_prefix = time_caller_prefix

    # ==========================================================
    def setMaxLevel(self, level):
        self.level = self.LEVELS[level.lower()][0]


    # ==========================================================
    def _caller(self):
        f = inspect.currentframe()
        for _ in range(3):  # salta stack interno logger
            f = f.f_back  # type: ignore

        filename = Path(f.f_code.co_filename).stem # type: ignore
        lineno = f.f_lineno # type: ignore
        func = f.f_code.co_name # type: ignore
        if func=='<module>': func='main'
        caller=f":{lineno}"
        if self.module:
            caller=f"{filename}{caller}"
        if self.function:
            caller=f"{func}{caller}"

        return caller
        return f"{filename}.{func}:{lineno}"


    # ==========================================================
    def _log(self, lvl, msg, *args, **kwargs):
        lvl_num, tag, default_color = self.LEVELS[lvl.lower()]
        if lvl_num < self.level:
            return

        if args:
            try:
                msg = msg % args
            except Exception:
                msg = f"{msg} {args}"

        # extract kwargs arguments
        time_caller_prefix = kwargs.get("time_caller_prefix", self.time_caller_prefix)
        color       = kwargs.get("color", default_color)
        # nel caso abbiamo qualche substring videnziata con altro colore
        if self.C.reset in msg:
            msg = msg.replace(self.C.reset, color)

        # se si vuole datetime + caller ...
        if time_caller_prefix:
            now = datetime.now().strftime("%H:%M:%S")
            caller = f"{self._caller()}" if self.show_caller else ""
            prefix = f"{self.C.blue}{now} [{caller}] [{tag}]: {color}"
        else:
            prefix = f"{color}"

        print(f"{prefix}{msg}{self.C.reset}")

    # ==========================================================
    def trace(self,     msg, *args, **kwargs): self._log("trace",    msg, *args, **kwargs)
    def notify(self,    msg, *args, **kwargs): self._log("notify",   msg, *args, **kwargs)
    def debug(self,     msg, *args, **kwargs): self._log("debug",    msg, *args, **kwargs)
    def info (self,     msg, *args, **kwargs): self._log("info",     msg, *args, **kwargs)
    def warning(self,   msg, *args, **kwargs): self._log("warning",  msg, *args, **kwargs)
    def error(self,     msg, *args, **kwargs): self._log("error",    msg, *args, **kwargs)
    def critical(self,  msg, *args, **kwargs): self._log("critical", msg, *args, **kwargs)





##################################################################
#
##################################################################
if __name__ == '__main__':
    C = PrintLogger.Color
    # logger=PrintLogger()
    log = PrintLogger(name="prova", console_logger_level="warning", time_caller_prefix=True)
    # log = PrintLogger(level="WARN", show_caller=True)
    log.info("non lo vedi")
    log.error("questo sì")

    log.setMaxLevel("trace")
    log.debug("ora sì: %s", "ok")
    log.info("Ciao: %s", "loreto", color=C.magentaH)
    log.error("Ciao")
    log.trace("Ciao")
    log.trace("Ciao", color=C.yellow, time_caller_prefix=True)
    log.notify("Ciao")
