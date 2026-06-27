#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 27-06-2026 18.53.52
#

import inspect
import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# Type aliases
LevelName = str
Message = str
ColorCode = str
StackLevel = int
LoggerName = str

sys.dont_write_bytecode = True


class Color:
    red: str      = "\033[31m"
    redH: str     = "\033[91m"
    green: str    = "\033[32m"
    greenH: str   = "\033[92m"
    yellow: str   = "\033[33m"
    yellowH: str  = "\033[93m"
    blue: str     = "\033[34m"
    blueH: str    = "\033[94m"
    magenta: str  = "\033[35m"
    magentaH: str = "\033[95m"
    cyan: str     = "\033[36m"
    cyanH: str    = "\033[96m"
    white: str    = "\033[37m"
    whiteH: str   = "\033[97m"
    reset: str    = "\033[0m"

    purple: str   = magenta
    purpleH: str  = magentaH


"""
    Level       Numeric value What it means / When to use it
"""
my_NOTSET_value: int   = 0
my_TRACE_value: int    = 9
my_DEBUG_value: int    = 10
my_INFO_value: int     = 20
my_NOTIFY_value: int   = 21
my_FUNCTION_value: int = 22
my_WARNING_value: int  = 30
my_ERROR_value: int    = 40
my_CRITICAL_value: int = 50


# -------------------------------
# Formatter semplice + safe + TTY
# -------------------------------
class ColorFormatter(logging.Formatter):
    def __init__(self, fmt: str, datefmt: Optional[str] = None, use_color: bool = True ) -> None:
        super().__init__(fmt, datefmt)
        self.use_color: bool = use_color

    def format(self, record: logging.LogRecord) -> str:
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
class lnColoredLogger:
    LEVEL_COLORS: Dict[str, str] = {
        "DEBUG": Color.cyan,
        "INFO": Color.green,
        "WARNING": Color.yellow,
        "ERROR": Color.red,
        "CRITICAL": Color.magenta,
        "NOTIFY": Color.blue,
    }

    def __init__(self, name: str,
                        console_logger_level: Optional[str] = None,
                        file_logger_level: str = "warning",
                        logging_dir: Optional[str] = None,
                        threads: bool = False,
                ) -> None:
        self.logger: logging.Logger = logging.getLogger(name)
        # Evita handler duplicati
        if self.logger.handlers:
            return

        self.add_custom_levels()
        self.logger.setLevel(logging.TRACE)  # type: ignore
        self.logger.propagate = False
        self.name: str = name
        self.test: Callable = testLogger

        self.setNameLength(dynamic=False, length=10)
        self.setLinenoLength(len=4)
        self.setShowCaller(show_caller=False)
        # self.setDynNameLength(dynamic=False)

        self.threads_str: str = "%(threadName)-5.5s." if threads else ""

        self.consoleHandler: Optional[logging.Handler] = None
        self.fileHandler: Optional[logging.Handler] = None

        if console_logger_level:
            self.consoleHandler = self.setConsoleLogger()
            self.consoleHandler.setLevel(
                getattr(logging, console_logger_level.upper(), logging.INFO)
            )
            self.logger.addHandler(self.consoleHandler)

        if logging_dir:
            self.fileHandler = self.setRotatingLogger(
                name=name, logging_dir=logging_dir
            )
            self.fileHandler.setLevel(
                getattr(logging, file_logger_level.upper(), logging.WARNING)
            )
            self.logger.addHandler(self.fileHandler)

    def add_custom_levels(self) -> None:
        # --- Livello custom NOTIFY ---
        def notify(self_logger: logging.Logger, msg: str, *args: Any, **kwargs: Any ) -> None:
            self_logger._log(logging.NOTIFY, msg, args, **kwargs)  # type: ignore

        logging.NOTIFY = my_NOTIFY_value  # type: ignore
        logging.addLevelName(logging.NOTIFY, "NOTIFY")  # type: ignore
        logging.Logger.notify = notify  # type: ignore

        # --- Livello custom TRACE ---
        def trace(self_logger: logging.Logger, msg: str, *args: Any, **kwargs: Any ) -> None:
            self_logger._log(logging.TRACE, msg, args, **kwargs)  # type: ignore

        logging.TRACE = my_TRACE_value  # type: ignore
        logging.addLevelName(logging.TRACE, "TRACE")  # type: ignore
        logging.Logger.trace = trace  # type: ignore

        # --- Livello custom FUNCTION ---
        def function(self_logger: logging.Logger, msg: str, *args: Any, **kwargs: Any ) -> None:
            self_logger._log(logging.FUNCTION, msg, args, **kwargs)  # type: ignore

        logging.FUNCTION = my_FUNCTION_value  # type: ignore
        logging.addLevelName(logging.FUNCTION, "FUNCTION")  # type: ignore
        logging.Logger.function = function  # type: ignore

    # -------------------------------
    # Logger console
    # -------------------------------
    def setConsoleLogger(self) -> logging.Handler:
        ch = logging.StreamHandler()
        use_color = hasattr(ch.stream, "isatty") and ch.stream.isatty()

        formatter = ColorFormatter(
            f"{Color.cyan}%(asctime)s "
            f"{Color.blue}%(module_formatted)s"  # <--- Usa il campo formattato
            f"{Color.magenta}%(caller_formatted)s"  # <--- Usa il campo formattato
            f"{Color.reset}"
            "%(level_color)s[%(levelname)4.4s]%(reset)s "
            "%(msg_color)s%(message)s%(reset)s",
            "%H:%M:%S",
            use_color=use_color,
        )

        ch.setFormatter(formatter)
        return ch

    # -------------------------------
    # Rotating Logger
    # -------------------------------
    def setRotatingLogger(self, name: str, logging_dir: Optional[str] = None, create_logging_dir: bool = True, ) -> logging.Handler:
        if logging_dir is None:
            logging_dir = "logs"

        logging_file = f"{logging_dir}/{name.lower()}.log"
        if not os.path.exists(logging_dir) and create_logging_dir:
            os.makedirs(logging_dir)

        fh = RotatingFileHandler(logging_file, maxBytes=5 * 1000 * 1000, backupCount=5)
        formatter = logging.Formatter(
            f"%(asctime)s - [{self.threads_str}%(module_formatted)s%(caller_formatted)s [%(levelname)4.4s]: %(message)s"
        )
        fh.setFormatter(formatter)
        return fh

    def setConsoleLoggerLevel(self, level: str) -> None:
        if self.consoleHandler is not None:
            self.consoleHandler.setLevel(level.upper())
            self.notify("console log level has been set to: %s", level.upper())


    def getConsoleLoggerLevel(self) -> str:
        """
        Restituisce il livello di logging corrente per la console.

        Returns:
            Stringa con il nome del livello (es. 'INFO', 'DEBUG', etc.)
        """
        if self.consoleHandler is not None:
            level_value = self.consoleHandler.level
            return logging.getLevelName(level_value)
        return "NOTSET"

    def getFileLoggerLevel(self) -> str:
        """
        Restituisce il livello di logging corrente per il file.

        Returns:
            Stringa con il nome del livello (es. 'INFO', 'DEBUG', etc.)
        """
        if self.fileHandler is not None:
            level_value = self.fileHandler.level
            return logging.getLevelName(level_value)
        return "NOTSET"

    def get_all_log_levels(self) -> Dict[str, str]:
        """
        Restituisce un dizionario con tutti i livelli di logging correnti.

        Returns:
            Dizionario con {'console': 'INFO', 'file': 'DEBUG', ...}
        """
        return {
            'console': self.getConsoleLoggerLevel(),
            'file': self.getFileLoggerLevel(),
            'logger': logging.getLevelName(self.logger.level),
        }

    def getMaxLength(self) -> int:
        return self.name_len + self.lineno_len + 1

    def setLinenoLength(self, len: int) -> None:
        self.lineno_len = len

    def setShowCaller(self, show_caller: bool) -> None:
        self.show_caller = show_caller

    ###########################################################
    # if
    ###########################################################
    def setNameLength(self, dynamic: bool, length: int) -> None:
        self.dynamic_name_lentgh: bool = False
        self.name_len: int = 0

        if dynamic or length == 0:
            self.dynamic_name_lentgh = True
            self.name_len = 0
        else:
            self.dynamic_name_lentgh = False
            if length < 8:
                length = 8
            self.name_len = length

    def _format_name(self, name: str, lineno: int) -> str:
        """
        Formatta nome e numero di linea come [nome:1234]
        con troncamento e padding appropriati
        """
        # Tronca il nome se necessario
        if self.dynamic_name_lentgh:
            if len(name) >= self.name_len:
                self.name_len = len(name)
        else:
            if len(name) >= self.name_len:
                name = (
                    name[: self.name_len - 2] + "."
                )  ### per far capire che è troncato

        # Padding del nome con spazi a destra
        name = f"{name}:".ljust(self.name_len)

        # Formatta il numero di linea con padding a sinistra
        return f"[{name}{lineno:4d}]"

    # ######################################################
    # 0  _caller() - la funzione corrente
    # 2  _log()
    # 3  info() / debug() / etc. (metodo pubblico)
    # 4  chiamante originale (test function)
    # ######################################################
    def _caller(self, stacklevel: int, show_stack: bool = False) -> Tuple[str, str]:
        """Restituisce (module_formatted, caller_formatted)

        Args:
            stacklevel: Livello base da cui partire (default 1)
                       1 = chiamante di _log (metodo pubblico)
                       2 = chiamante originale
        """
        frames: List[inspect.FrameInfo] = inspect.stack()
        n_levels = len(frames)
        # ---------------------------
        # - lvl: 0 self._caller()
        # - lvl: 1 self._log()
        # - lvl: 2 self.info()...self.trace()...
        # - lvl: 3 call to log
        # - lvl: 4 caller of lev.3
        # ---------------------------
        if show_stack:
            x = traceback.extract_stack()
            print("-" * 40)
            print(f"required stacklevel: {stacklevel}")
            for i in range(len(x)):
                filename = inspect.stack()[i].filename
                _function = inspect.stack()[i].function
                lineno = inspect.stack()[i].lineno
                print(i, filename, lineno)

        # Calcola gli indici (evitando di andare otut of range)
        module_idx = min(stacklevel, n_levels - 1)
        module_frame = frames[module_idx]
        module_filename = module_frame.filename
        module_name = Path(module_frame.filename).stem
        module_lineno = module_frame.lineno

        if n_levels - stacklevel <= 1:
            caller_filename = "out_of_index"
            caller_name = "out_of_index"
            caller_lineno = 0
            caller_frame = "no_frame"
            caller_idx = min(module_idx + 1, n_levels - 1)  # module_idx+1
        else:
            caller_idx = min(module_idx + 1, n_levels - 1)  # module_idx+1
            caller_frame = frames[caller_idx]
            caller_filename = caller_frame.filename
            caller_name = Path(caller_frame.filename).stem
            caller_lineno = caller_frame.lineno

        if show_stack:
            print("-" * 40)
            print("module:", module_idx, module_filename, module_lineno)
            print("caller:", caller_idx, caller_filename, caller_lineno)
            print("-" * 40)

        return (
            self._format_name(module_name, module_lineno),
            self._format_name(caller_name, caller_lineno),
        )

    # -------------------------------
    # Core logging
    # -------------------------------
    def _log(self, level_name: str, msg: str, *args: Any, color: Optional[str] = None, **kwargs: Any, ) -> None:
        level_value = getattr(logging, level_name, logging.INFO)
        stacklevel: int = kwargs.pop("stacklevel", 0)
        # print(f"....required stacklevel: {stacklevel}")
        forceLog: bool = kwargs.pop("force_log", False)
        forceExit: bool = kwargs.pop("exit", False)
        showCaller: bool = kwargs.pop("show_caller", False)
        showStack: bool = kwargs.pop("show_stack", False)

        if level_value >= self.consoleHandler.level or forceLog:  # type: ignore
            kwargs["stacklevel"] = stacklevel + 3

            # Calcola caller formattato se necessario
            # Il caller deve essere il chiamante del metodo pubblico (un livello sopra)
            # module_formatted, caller_formatted = self._callerMIO(stacklevel=3+stacklevel)
            module_formatted, caller_formatted = self._caller(
                stacklevel=kwargs["stacklevel"], show_stack=showStack
            )

            if showCaller or self.show_caller:
                ...
            else:
                caller_formatted = ""
            #     caller_formatted = self._caller(additional_levels=1)  # <<<--- Salta un livello extra!

            level_color = self.LEVEL_COLORS.get(level_name, Color.white)

            dry_run: bool = kwargs.pop("dry_run", False)
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
            extra.update( {
                    "msg_color": msg_color,
                    "level_color": level_color,
                    "reset": Color.reset,
                    "module_formatted": module_formatted,  # <<<--- modulo formattato
                    "caller_formatted": caller_formatted,  # <<<--- caller formattato
                }
            )
            kwargs["extra"] = extra

            self.logger.log(level_value, msg, *args, **kwargs)
            if forceExit:
                sys.exit(1)

    #########################################################################
    # API pubbliche
    #########################################################################
    def trace(self, msg: str, *args: Any, color: Optional[str] = None, **kwargs: Any ) -> None:
        self._log("TRACE", msg, *args, color=color, **kwargs)

    def debug(self, msg: str, *args: Any, color: Optional[str] = None, **kwargs: Any ) -> None:
        self._log("DEBUG", msg, *args, color=color, **kwargs)

    def info(self, msg: str, *args: Any, color: Optional[str] = None, **kwargs: Any ) -> None:
        self._log("INFO", msg, *args, color=color, **kwargs)

    def warning(self, msg: str, *args: Any, color: Optional[str] = None, **kwargs: Any ) -> None:
        self._log("WARNING", msg, *args, color=color, **kwargs)

    def error(self, msg: str, *args: Any, color: Optional[str] = None, **kwargs: Any ) -> None:
        self._log("ERROR", msg, *args, color=color, **kwargs)

    def critical(self, msg: str, *args: Any, color: Optional[str] = None, **kwargs: Any ) -> None:
        self._log("CRITICAL", msg, *args, color=color, **kwargs)

    def notify(self, msg: str, *args: Any, color: Optional[str] = None, **kwargs: Any ) -> None:
        self._log("NOTIFY", msg, *args, color=color, **kwargs)

    def function(self, msg: str, *args: Any, color: Optional[str] = None, **kwargs: Any ) -> None:
        self._log("FUNCTION", msg, *args, color=color, show_caller=True, **kwargs)


def testLogger(logger: lnColoredLogger) -> None:
    print("\n--- base colors ---")
    logger.debug("DEBUG default")
    logger.info("INFO default")
    logger.warning("WARNING default")
    logger.error("ERROR default")
    logger.critical("CRITICAL default")
    logger.notify("NOTIFY default")

    save_level = logger.getConsoleLoggerLevel()
    logger.setConsoleLoggerLevel("WARNING")
    print("\n--- base colors forzando level to WARNING---")
    logger.debug("DEBUG default")
    logger.info("INFO default")
    logger.warning("WARNING default")
    logger.error("ERROR default")
    logger.critical("CRITICAL default")
    logger.notify("NOTIFY default")
    logger.setConsoleLoggerLevel(save_level)

    print("\n--- custom colors ---")
    logger.info("INFO in magenta", color=Color.magenta)
    logger.warning("WARNING in cyan", color=Color.cyan)
    logger.error("ERROR in yellowH", color=Color.yellowH)

    logger.info("This shows caller info", show_caller=True)

    logger.info("Test con nome modulo lungo", show_caller=True)

    logger.info("This shows caller info + stacklevel=1", show_caller=True, stacklevel=1)

    logger.info(
        "Test con nome modulo lungo + stacklevel=1", show_caller=True, stacklevel=1
    )
