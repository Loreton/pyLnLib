#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 05-05-2026 10.49.02
#

import sys; sys.dont_write_bytecode=True;
# utils/logger_types.py
from typing import Protocol, Any, Optional

from datetime import datetime






# # class DummyLogger:
# class DummyPrintLogger():
#     from datetime import datetime
#     class Color:
#         # purple     = '\033[35m'; purpleH    = '\033[95m'
#         red        = '\033[31m'; redH       = '\033[91m'
#         green      = '\033[32m'; greenH     = '\033[92m'
#         yellow     = '\033[33m'; yellowH    = '\033[93m'
#         blue       = '\033[34m'; blueH      = '\033[94m'
#         magenta    = '\033[35m'; magentaH   = '\033[95m'
#         cyan       = '\033[36m'; cyanH      = '\033[96m'
#         white      = '\033[37m'; whiteH     = '\033[97m'
#         reset      = '\033[0m'


#     """Fallback logger semplice che stampa su stdout con colore opzionale."""
#     def trace(self,     msg, *args, dry_run: bool=False, color: Optional[str] = Color.whiteH,   **kwargs): self._print("TRAC", msg, color, *args)
#     def debug(self,     msg, *args, dry_run: bool=False, color: Optional[str] = Color.cyanH,    **kwargs): self._print("DEBU", msg, color, *args)
#     def info(self,      msg, *args, dry_run: bool=False, color: Optional[str] = Color.greenH,   **kwargs): self._print("INFO", msg, color, *args)
#     def notify(self,    msg, *args, dry_run: bool=False, color: Optional[str] = Color.blueH,    **kwargs): self._print("NOTI", msg, color, *args)
#     def warning(self,   msg, *args, dry_run: bool=False, color: Optional[str] = Color.yellowH,  **kwargs): self._print("WARN", msg, color, *args)
#     def error(self,     msg, *args, dry_run: bool=False, color: Optional[str] = Color.redH,     **kwargs): self._print("ERRO", msg, color, *args)
#     def critical(self,  msg, *args, dry_run: bool=False, color: Optional[str] = Color.magentaH, **kwargs): self._print("CRIT", msg, color, *args)

#     def _print(self, level, msg, color, *args):
#         # now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         now=datetime.now().strftime("%H:%M:%S")

#         if args:
#             try:
#                 msg = msg % args
#             except Exception:
#                 # fallback sicuro
#                 msg = f"{msg} {args}"

#         if color:
#             print(f"{color}{now} - {level}: {msg}{self.Color.reset}") # qui vuole il self
#         else:
#             print(msg)



class DummyLogger:
    # class C:
    #     R='\033[0m'
    #     G='\033[92m'; Y='\033[93m'; Rr='\033[91m'
    #     B='\033[94m'; Cc='\033[96m'; M='\033[95m'; W='\033[97m'
    class Color:
        # purple     = '\033[35m'; purpleH    = '\033[95m'
        red        = '\033[31m'; redH       = '\033[91m'
        green      = '\033[32m'; greenH     = '\033[92m'
        yellow     = '\033[33m'; yellowH    = '\033[93m'
        blue       = '\033[34m'; blueH      = '\033[94m'
        magenta    = '\033[35m'; magentaH   = '\033[95m'
        cyan       = '\033[36m'; cyanH      = '\033[96m'
        white      = '\033[37m'; whiteH     = '\033[97m'
        reset      = '\033[0m'

    LEVELS = {
        "TRACE": ("TRAC", Color.whiteH),
        "DEBUG": ("DEBU", Color.cyanH),
        "INFO":  ("INFO", Color.greenH),
        "WARN":  ("WARN", Color.yellowH),
        "ERROR": ("ERRO", Color.redH),
        "CRIT":  ("CRIT", Color.magentaH),
    }

    def _log(self, lvl, msg, *args, color=None):
        tag, default_color = self.LEVELS[lvl]
        color = color or default_color

        if args:
            try:
                msg = msg % args
            except Exception:
                msg = f"{msg} {args}"

        now = datetime.now().strftime("%H:%M:%S")
        print(f"{color}{now} - {tag}: {msg}{self.Color.reset}")

    def trace(self,     msg, *args, color=None, **kwargs): self._log("TRACE",  msg, *args, color=color)
    def debug(self,     msg, *args, color=None, **kwargs): self._log("DEBUG",  msg, *args, color=color)
    def info (self,     msg, *args, color=None, **kwargs): self._log("INFO",   msg, *args, color=color)
    def warning(self,   msg, *args, color=None, **kwargs): self._log("WARN",   msg, *args, color=color)
    def error(self,     msg, *args, color=None, **kwargs): self._log("ERROR",  msg, *args, color=color)
    def critical(self,  msg, *args, color=None, **kwargs): self._log("CRIT",   msg, *args, color=color)




if __name__ == '__main__':
    C = DummyLogger.Color
    # logger=DummyPrintLogger()
    logger=DummyLogger()
    logger.info("Ciao: %s", "loreto", color=C.magentaH)
    logger.error("Ciao")
    logger.trace("Ciao", color=C.blue)