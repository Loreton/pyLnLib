#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 18-05-2026 19.11.31
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
my_TRACE_value    =  9
my_NOTIFY_value   = 21
my_FUNCTION_value = 22


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
                    # show_caller: bool=False,
                    max_name_len: int=15,  # <<<--- Lunghezza totale del campo [nome:1234]
                    threads: bool=False
                    ):
        self.logger = logging.getLogger(name)
        # Evita handler duplicati
        if self.logger.handlers:
            return


        self.add_custom_levels()
        self.logger.setLevel(logging.TRACE)
        self.logger.propagate = False
        self.name = name
        self.test = testLogger


        self.max_name_len = max_name_len
        self.show_caller = False
        self.setNameLength(max_name_len)
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
        def notify(self_logger, msg, *args, **kwargs):
            self_logger._log(logging.NOTIFY, msg, args, **kwargs)
        logging.NOTIFY = my_NOTIFY_value
        logging.addLevelName(logging.NOTIFY, "NOTIFY")
        logging.Logger.notify = notify

        # --- Livello custom TRACE ---
        def trace(self_logger, msg, *args, **kwargs):
            self_logger._log(logging.TRACE, msg, args, **kwargs)
        logging.TRACE = my_TRACE_value
        logging.addLevelName(logging.TRACE, "TRACE")
        logging.Logger.trace = trace

        # --- Livello custom FUNCTION ---
        def function(self_logger, msg, *args, **kwargs):
            self_logger._log(logging.FUNCTION, msg, args, **kwargs)
        logging.FUNCTION = my_FUNCTION_value
        logging.addLevelName(logging.FUNCTION, "FUNCTION")
        logging.Logger.function = function


    # -------------------------------
    # Logger console
    # -------------------------------
    def setConsoleLogger(self):
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
            f"%(asctime)s - [{self.threads_str}%(module_formatted)s%(caller_formatted)s [%(levelname)4.4s]: %(message)s"
        )
        fh.setFormatter(formatter)
        return fh


    def setConsoleLoggerLevel(self, level: str):
        self.consoleHandler.setLevel(level.upper())
        self.notify("console log level has been set to: %s", level.upper())




    # -------------------------------
    #
    # -------------------------------
    def setNameLength(self, max_len: int=0, show_caller: bool=False):
        """
        Imposta la lunghezza dei nomi dei moduli
        sia per il caller che per il modulo
        """
        # print(max_len)

        if max_len < self.max_name_len:
            max_len=self.max_name_len

        self.lineno_len = 4  # Larghezza fissa per il numero di linea
        self.name_len = max_len - self.lineno_len - 1  # -1 per i due punti
        self.show_caller = show_caller


    def _format_name(self, name: str, lineno: int) -> str:
        """
        Formatta nome e numero di linea come [nome:1234]
        con troncamento e padding appropriati
        """
        # Tronca il nome se necessario
        # import pdb; pdb.set_trace(); # by Loreto
        # print(name, len(name))
        if len(name) >= self.name_len:
            name = name[:self.name_len-2] + "." ### per far capire che è troncato
            # print("trunc", len(name))

        # print(name, len(name))

        # Padding del nome con spazi a destra
        name = f"{name}:".ljust(self.name_len)
        # print(name, len(name))
        # Formatta il numero di linea con padding a sinistra
        return f"[{name}{lineno:4d}]"


    def _caller(self):
        """Recupera informazioni sul chiamante e le formatta"""
        f = inspect.currentframe()
        # skip levels: _caller() -> _log() -> metodo pubblico -> chiamante originale
        for _ in range(4):
            if f is not None:
                f = f.f_back
            else:
                break

        if f is None:
            return self._format_name("unknown", 0)

        filename = Path(os.path.basename(f.f_code.co_filename)).stem
        lineno = f.f_lineno
        func = f.f_code.co_name
        if func == '<module>':
            func = 'main'

        caller_name = filename  # default

        return self._format_name(caller_name, lineno)


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

            # Ottieni le informazioni del chiamante originale per module_formatted
            f = inspect.currentframe()
            for _ in range(3):  # Salta fino al chiamante reale
                if f is not None:
                    f = f.f_back
                else:
                    break

            if f is not None:
                module_name = Path(os.path.basename(f.f_code.co_filename)).stem
                lineno = f.f_lineno
                module_formatted = self._format_name(module_name, lineno)
            else:
                module_formatted = self._format_name("unknown", 0)

            # Calcola caller formattato se necessario
            caller_formatted = ""
            if showCaller or self.show_caller:
                caller_formatted = self._caller()

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
                "module_formatted": module_formatted,  # <<<--- modulo formattato
                "caller_formatted": caller_formatted,  # <<<--- caller formattato
            })
            kwargs["extra"] = extra

            self.logger.log(level_value, msg, *args, **kwargs)
            if forceExit:
                sys.exit(1)


    #########################################################################
    # API pubbliche
    #########################################################################
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
    print(f"--- Logger name: {logger.name} (max_len={logger.max_len})")
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

    print("\n--- test con nome lungo ---")
    logger.info("Test con nome modulo lungo", show_caller=True)

    print("\n")


# -------------------------------
# Test
# -------------------------------
if __name__ == "__main__":
    # Test con diverse lunghezze
    print("=== Test con max_len=15 ===")
    logger1 = lnLoggerColored(
        name="test_logger",
        console_logger_level="debug",
        show_caller=True,
        max_len=15
    )
    testLogger(logger1)

    print("\n=== Test con max_len=20 ===")
    logger2 = lnLoggerColored(
        name="test_logger",
        console_logger_level="debug",
        show_caller=True,
        max_len=20
    )
    testLogger(logger2)