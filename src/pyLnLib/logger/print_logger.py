#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
#
#  ruff: noqa: E402 Module level import not at top of file (Ruff E402)
#  ruff: noqa: E701 Multiple statements on one line (colon) (Ruff E701)

import sys; sys.dont_write_bytecode=True;
from pathlib import Path
from datetime import datetime
import inspect


class PrintLogger:
    class Color:
        red        = '\033[31m'; redH       = '\033[91m'
        green      = '\033[32m'; greenH     = '\033[92m'
        yellow     = '\033[33m'; yellowH    = '\033[93m'
        blue       = '\033[34m'; blueH      = '\033[94m'
        magenta    = '\033[35m'; magentaH   = '\033[95m'
        cyan       = '\033[36m'; cyanH      = '\033[96m'
        white      = '\033[37m'; whiteH     = '\033[97m'
        reset      = '\033[0m'



    def __init__(self, name: str="PrintLogger", console_logger_level: str="info", time_caller_prefix: bool=False):
        self.LEVELS = {
            "trace":     (5,  "TRACE", self.Color.white),
            "debug":     (10, "DEBUG", self.Color.cyan),
            "info":      (20, "INFO ", self.Color.green),
            "notify":    (25, "NOTFY", self.Color.greenH),
            "warning":   (30, "WARN ", self.Color.yellow),
            "error":     (40, "ERROR", self.Color.red),
            "critical":  (50, "CRIT ", self.Color.magenta),
        }

        self.level = self.LEVELS[console_logger_level.lower()][0]
        self.name = name
        self.show_caller = True
        self.module = True
        self.function = False
        # self.test = testLogger
        self.time_caller_prefix = time_caller_prefix

    # ==========================================================
    def setMaxLevel(self, level):
        self.level = self.LEVELS[level.lower()][0]


    # ==========================================================
    def _caller(self):
        f = inspect.currentframe()
        for _ in range(3):  # salta stack interno logger
            f = f.f_back  # type: ignore
        # breakpoint()
        # filename = Path(os.path.basename(f.f_code.co_filename)).stem # type: ignore
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
        if self.Color.reset in msg:
            msg = msg.replace(self.Color.reset, color)

        # se si vuole datetime + caller ...
        if time_caller_prefix:
            now = datetime.now().strftime("%H:%M:%S")
            caller = f"{self._caller()}" if self.show_caller else ""
            prefix = f"{color}{now} [{caller}] [{tag}]: "
        else:
            prefix = f"{color}"

        print(f"{prefix}{msg}{self.Color.reset}")

    # ==========================================================
    def trace(self,     msg, *args, **kwargs): self._log("trace",  msg, *args, **kwargs)
    def notify(self,    msg, *args, **kwargs): self._log("notify",   msg, *args, **kwargs)
    def debug(self,     msg, *args, **kwargs): self._log("debug",  msg, *args, **kwargs)
    def info (self,     msg, *args, **kwargs): self._log("info",   msg, *args, **kwargs)
    def warning(self,   msg, *args, **kwargs): self._log("warning",   msg, *args, **kwargs)
    def error(self,     msg, *args, **kwargs): self._log("error",  msg, *args, **kwargs)
    def critical(self,  msg, *args, **kwargs): self._log("critical",   msg, *args, **kwargs)





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
