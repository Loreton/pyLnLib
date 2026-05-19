#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 18-05-2026 14.40.38
#

import sys; sys.dont_write_bytecode = True
import os
import logging
import inspect
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

### - project modules
from ..colors import Color

'''
    Level       Numeric value What it means / When to use it
'''
# logging.NOTSET   =  0   #   When set on a logger, indicates that ancestor loggers are to be consulted to determine the effective level. If that still resolves to NOTSET, then all events are logged. When set on a handler, all events are handled.
my_TRACE_value    =  9   #  loreto.
# logging.DEBUG    = 10   #  Detailed information, typically only of interest to a developer trying to diagnose a problem.
# logging.INFO     = 20   #  Confirmation that things are working as expected.
my_NOTIFY_value   = 21   #  loreto
my_FUNCTION_value = 22   #  loreto
# logging.WARNING  = 30   #  An indication that something unexpected happened, or that a problem might occur in the near future (e.g. ‘disk space low’). The software is still working as expected.
# logging.ERROR    = 40   #  Due to a more serious problem, the software has not been able to perform some function.
# logging.CRITICAL = 50   #  A serious error, indicating that the program itself may be unable to continue running.


'''
Logger che mi permette di fare override del colore su ogni comando
'''

logger_config=''' NOT used
    name: loreto_logger
    console:
        enable: true
        colors:
            DEBUG:     cyanH
            INFO:      greenH
            WARNING:   yellowH
            ERROR:     redH
            CRITICAL:  magentaH
            NOTIFY:    blueH

        formatter:
            asci_time:   "{Color.cyan}%(asctime)s
            module:      "{Color.blue}[%(module)s:%(lineno)4s]
            caller:      "{Color.magenta}[%(caller)-10.10s]
            level:       "%(level_color)s[%(levelname)4.4s]%(reset)s
            message:     "%(msg_color)s%(message)s%(reset)s"
            time_format: "%H:%M:%S"

    rotating_file:
        enable: true
        logging_dir: /tmp
        max_bytes: 5*1000*1000
        backup_counter: 5

'''


# -------------------------------
# Formatter semplice + safe + TTY
# -------------------------------
class ColorFormatter(logging.Formatter):
    def __init__(self, fmt, datefmt=None, use_color=True):
        super().__init__(fmt, datefmt)
        self.use_color = use_color

    def format(self, record):
        # Safe fallback (evita errori se mancano attributi)
        for attr in ("msg_color", "level_color", "reset", "caller"):
            if not hasattr(record, attr):
                setattr(record, attr, "")

        # Disabilita colori se necessario
        if not self.use_color:
            record.msg_color = ""
            record.level_color = ""
            record.reset = ""

        return super().format(record)


# -------------------------------
# Logger principale
# -------------------------------
class lnLoggerColored:

    LEVEL_COLORS = {
        "DEBUG":     Color.cyan,
        "INFO":      Color.green,
        "WARNING":   Color.yellow,
        "ERROR":     Color.red,
        "CRITICAL":  Color.magenta,
        "NOTIFY":    Color.blue,
    }


    def __init__(self, name: str,
                    console_logger_level: str=None,
                    file_logger_level: str="warning",
                    logging_dir: str=None,
                    show_caller: bool=False,
                    threads: bool=False
                    ):
        self.logger = logging.getLogger(name)
        self.add_custom_levels()
        self.logger.setLevel(logging.TRACE)
        self.logger.propagate = False
        self.name = name
        self.test = testLogger
        # self.show_caller = show_caller
        self.caller_len = 0
        self.show_module = True
        self.show_function = False

        # Evita handler duplicati
        if self.logger.handlers:
            return

        self.threads_str="%(threadName)-5.5s." if threads else ''

        if console_logger_level:
            self.consoleHandler = self.setConsoleLogger()
            self.consoleHandler.setLevel(getattr(logging, console_logger_level.upper(), logging.INFO))
            self.logger.addHandler(self.consoleHandler)

        if logging_dir:
            self.fileHandler = self.setRotatingLogger(name=name, logging_dir=logging_dir)
            self.fileHandler.setLevel(getattr(logging, file_logger_level.upper(), logging.WARNING))
            self.logger.addHandler(self.fileHandler)


    def add_custom_levels(self):
        # --- Livello custom NOTIFY ---
        logging.NOTIFY = my_NOTIFY_value
        logging.addLevelName(logging.NOTIFY, "NOTIFY")

        def notify(self_logger, msg, *args, **kwargs):
            self_logger._log(logging.NOTIFY, msg, args, **kwargs)
        logging.Logger.notify = notify

        # --- Livello custom TRACE ---
        logging.TRACE = my_TRACE_value
        logging.addLevelName(logging.TRACE, "TRACE")

        def trace(self_logger, msg, *args, **kwargs):
            self_logger._log(logging.TRACE, msg, args, **kwargs)
        logging.Logger.trace = trace

        # --- Livello custom FUNCTION ---
        logging.FUNCTION = my_FUNCTION_value
        logging.addLevelName(logging.FUNCTION, "FUNCTION")

        def function(self_logger, msg, *args, **kwargs):
            self_logger._log(logging.FUNCTION, msg, args, **kwargs)
        logging.Logger.function = function


    # -------------------------------
    # Logger console
    # -------------------------------
    def setConsoleLogger(self):
        ch = logging.StreamHandler()
        use_color = hasattr(ch.stream, "isatty") and ch.stream.isatty()

        formatter = ColorFormatter(
            f"{Color.cyan}%(asctime)s "
            f"{Color.blue}[%(module)-10.10s:%(lineno)4s]"
            f"{Color.magenta}%(caller)s"  # <<<--- caller inserito qui!
            "%(level_color)s[%(levelname)4.4s]%(reset)s "
            "%(msg_color)s%(message)s%(reset)s",
            "%H:%M:%S",
            use_color=use_color
        )

        ch.setFormatter(formatter)
        return ch


    # -------------------------------
    # Rotating Logger
    # -------------------------------
    def setRotatingLogger(self, name: str, logging_dir: str=None, create_logging_dir: bool=True):
        logging_file = f"{logging_dir}/{name.lower()}.log"
        if not os.path.exists(logging_dir) and create_logging_dir:
            os.makedirs(logging_dir)

        fh = RotatingFileHandler(logging_file, maxBytes=5*1000*1000, backupCount=5)
        formatter = logging.Formatter(
            f"%(asctime)s - [{self.threads_str}%(module)s:%(lineno)4.4s][%(caller)] [%(levelname)4.4s]: %(message)s"
        )
        fh.setFormatter(formatter)
        return fh


    def setConsoleLoggerLevel(self, level: str):
        self.consoleHandler.setLevel(level.upper())
        self.notify("console log level has been set to: %s", level.upper())



    # -------------------------------
    # Logger console
    # -------------------------------
    def setCallerLength(self, lentgh: int):
        # self.show_caller = int(lentgh)
        self.caller_len = int(lentgh)


    def _caller(self):
        """Recupera informazioni sul chiamante"""
        f = inspect.currentframe()
        # skip levels: _caller() -> _log() -> metodo pubblico (info, debug, etc.) -> chiamante originale
        for _ in range(4):
            if f is not None:
                f = f.f_back
            else:
                break

        if f is None:
            return "unknown:0"

        filename = Path(os.path.basename(f.f_code.co_filename)).stem
        lineno = f.f_lineno
        func = f.f_code.co_name
        if func == '<module>':
            func = 'main'


        _lineno    = f"{lineno:4}"
        rest_len   = self.caller_len-4 ### lineno_length
        module_len = f"{rest_len}.{rest_len}"

        caller = ''
        if self.show_module:
            module = f"{filename}:"
            caller = f"[{module:{module_len}}{_lineno}]"
        # if self.show_function:
        #     caller = f"{func}{caller}"

        return caller


    # -------------------------------
    # Core logging
    # -------------------------------
    def _log(self, level_name: str, msg: str, *args, color: Optional[str] = None, **kwargs):
        level_value = getattr(logging, level_name, logging.INFO)
        stacklevel  = kwargs.pop("stacklevel", 0)
        forceLog    = kwargs.pop("force_log", False)
        forceExit   = kwargs.pop("exit", False)
        showCaller  = kwargs.pop("show_caller", False)

        if level_value >= self.consoleHandler.level or forceLog:
            kwargs["stacklevel"] = stacklevel + 3

            # Calcola caller se necessario
            caller = ""
            if showCaller or self.caller_len > 8:
                caller = self._caller()

            level_color = self.LEVEL_COLORS.get(level_name, Color.white)

            dry_run = kwargs.pop("dry_run", False)
            if dry_run:
                msg = f"[dry-run] {msg}"

            # override colore
            if color:
                msg_color = color
                level_color = color
            elif dry_run:
                msg_color = Color.magentaH
            else:
                msg_color = level_color

            extra = kwargs.pop("extra", {})
            extra.update({
                "msg_color": msg_color,
                "level_color": level_color,
                "reset": Color.reset,
                "caller": caller,  # <<<--- caller passato attraverso extra
            })
            kwargs["extra"] = extra

            # Il msg rimane pulito, il formatter userà %(caller)s
            self.logger.log(level_value, msg, *args, **kwargs)
            if forceExit:
                sys.exit(1)


    #########################################################################
    # API pubbliche
    #########################################################################
    def getLogLevels(self):
        return self.logLevels


    # -------------------------------
    # API standard
    # -------------------------------
    def trace(self, msg: str, *args, color: Optional[str] = None, **kwargs):
        self._log("TRACE", msg, *args, color=color, **kwargs)

    def debug(self, msg: str, *args, color: Optional[str] = None, **kwargs):
        self._log("DEBUG", msg, *args, color=color, **kwargs)

    def info(self, msg: str, *args, color: Optional[str] = None, **kwargs):
        self._log("INFO", msg, *args, color=color, **kwargs)

    def warning(self, msg: str, *args, color: Optional[str] = None, **kwargs):
        self._log("WARNING", msg, *args, color=color, **kwargs)

    def error(self, msg: str, *args, color: Optional[str] = None, **kwargs):
        self._log("ERROR", msg, *args, color=color, **kwargs)

    def critical(self, msg: str, *args, color: Optional[str] = None, **kwargs):
        self._log("CRITICAL", msg, *args, color=color, **kwargs)

    def notify(self, msg: str, *args, color: Optional[str] = None, **kwargs):
        self._log("NOTIFY", msg, *args, color=color, **kwargs)

    def function(self, msg: str, *args, color: Optional[str] = None, **kwargs):
        self._log("FUNCTION", msg, *args, color=color, show_caller=True, **kwargs)


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

    print("\n--- caller test ---")
    logger.info("This shows caller info", show_caller=True)
    print("\n")


# -------------------------------
# Test
# -------------------------------
if __name__ == "__main__":
    # Esempio di utilizzo
    logger = lnLoggerColored(
        name="test_logger",
        console_logger_level="debug",
        show_caller=True  # Abilita caller globalmente
    )
    testLogger(logger)