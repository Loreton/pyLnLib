#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 22-05-2026 16.30.31
#



import sys; sys.dont_write_bytecode = True
import os
import logging
import inspect
import traceback
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class Color:
    red        = '\033[31m'; redH       = '\033[91m'
    green      = '\033[32m'; greenH     = '\033[92m'
    yellow     = '\033[33m'; yellowH    = '\033[93m'
    blue       = '\033[34m'; blueH      = '\033[94m'
    magenta    = '\033[35m'; magentaH   = '\033[95m'
    cyan       = '\033[36m'; cyanH      = '\033[96m'
    white      = '\033[37m'; whiteH     = '\033[97m'
    reset      = '\033[0m'

    purple = magenta
    purpleH = magentaH

# from ..colors import Color

'''
    Level       Numeric value What it means / When to use it
'''
my_NOTSET_value   =  0   #   When set on a logger, indicates that ancestor loggers are to be consulted to determine the effective level. If that still resolves to NOTSET, then all events are logged. When set on a handler, all events are handled.
my_TRACE_value    =  9   #  loreto.
my_DEBUG_value    = 10   #  Detailed information, typically only of interest to a developer trying to diagnose a problem.
my_INFO_value     = 20   #  Confirmation that things are working as expected.
my_NOTIFY_value   = 21   #  loreto
my_FUNCTION_value = 22   #  loreto
my_WARNING_value  = 30   #  An indication that something unexpected happened, or that a problem might occur in the near future (e.g. ‘disk space low’). The software is still working as expected.
my_ERROR_value    = 40   #  Due to a more serious problem, the software has not been able to perform some function.
my_CRITICAL_value = 50   #  A serious error, indicating that the program itself may be unable to continue running.



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
class lnColoredLogger:

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

        self.setNameLength(dynamic=False, length=10)
        self.setLinenoLength(len=4)
        self.setShowCaller(show_caller=False)
        # self.setDynNameLength(dynamic=False)


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


    def getMaxLength(self):
        return self.name_len + self.lineno_len + 1


    def setLinenoLength(self, len: int):
        self.lineno_len=len

    def setShowCaller(self, show_caller: bool):
        self.show_caller=show_caller

    ###########################################################
    # if
    ###########################################################
    def setNameLength(self, dynamic: bool, length: int):
        if dynamic or length==0:
            self.dynamic_name_lentgh=True
            self.name_len=0
        else:
            self.dynamic_name_lentgh=False
            if length<8:
                length=8
            self.name_len=length



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
                name = name[:self.name_len-2] + "." ### per far capire che è troncato


        # Padding del nome con spazi a destra
        name = f"{name}:".ljust(self.name_len)

        # Formatta il numero di linea con padding a sinistra
        return f"[{name}{lineno:4d}]"




    def _callerMIO(self, stacklevel: int=1):
        fDEBUG=True
        _stacks=inspect.stack() # changed:  27-02-2024
        n_stacks=len(_stacks) # changed:  27-02-2024

        # if stacklevel ==4:
        #     import pdb; pdb.set_trace(); # by Loreto
        if stacklevel>=n_stacks-1:
            module_stacklevel= n_stacks-1
            caller_stacklevel= -99
        else:
            module_stacklevel = stacklevel
            caller_stacklevel = module_stacklevel+1



        if fDEBUG:
            x=traceback.extract_stack()

            print('-'*40)
            for i in range(len(x)):
                filename = inspect.stack()[i].filename
                function = inspect.stack()[i].function
                lineno = inspect.stack()[i].lineno
                print(i, filename, lineno)


        caller = inspect.stack()[caller_stacklevel]
        module = inspect.stack()[module_stacklevel]

        if fDEBUG:
            print('-'*40)
            print("module:", module_stacklevel, module.filename, module.lineno)
            print("caller:", caller_stacklevel, caller.filename, caller.lineno)
            print('-'*40)

        caller_name = Path(caller.filename).stem
        module_name = Path(module.filename).stem

        return self._format_name(module_name, module.lineno), self._format_name(caller_name, caller.lineno)


    # ######################################################
    # 0  _caller() - la funzione corrente
    # 2  _log()
    # 3  info() / debug() / etc. (metodo pubblico)
    # 4  chiamante originale (test function)
    # ######################################################
    def _caller(self, stacklevel: int = 1):
        fDEBUG=False
        """Restituisce (module_formatted, caller_formatted)

        Args:
            stacklevel: Livello base da cui partire (default 1)
                       1 = chiamante di _log (metodo pubblico)
                       2 = chiamante originale
        """

        frames = inspect.stack()
        n_levels = len(frames)
        # ---------------------------
        # - lvl: 0 self._caller()
        # - lvl: 1 self._log()
        # - lvl: 2 self.info()...self.trace()...
        # - lvl: 3 call to log
        # - lvl: 4 caller of lev.3
        # ---------------------------
        if fDEBUG:
            x=traceback.extract_stack()
            print('-'*40)
            for i in range(len(x)):
                filename = inspect.stack()[i].filename
                function = inspect.stack()[i].function
                lineno = inspect.stack()[i].lineno
                print(i, filename, lineno)




        # Calcola gli indici (evitando di andare otut of range)
        module_idx    = min(stacklevel, n_levels - 1)
        module_frame  = frames[module_idx]
        module_filename   = module_frame.filename
        module_name   = Path(module_frame.filename).stem
        module_lineno = module_frame.lineno

        if n_levels - stacklevel <= 1:
            caller_filename = "out_of_index"
            caller_name     = "out_of_index"
            caller_lineno   = 0
            caller_frame    = "no_frame"
            caller_idx      = min(module_idx + 1, n_levels - 1) # module_idx+1
        else:
            caller_idx      = min(module_idx + 1, n_levels - 1) # module_idx+1
            caller_frame    = frames[caller_idx]
            caller_filename = caller_frame.filename
            caller_name     = Path(caller_frame.filename).stem
            caller_lineno   = caller_frame.lineno


        if fDEBUG:
            print('-'*40)
            print("module:", module_idx, module_filename, module_lineno)
            print("caller:", caller_idx, caller_filename, caller_lineno)
            print('-'*40)


        return (self._format_name(module_name, module_lineno),
                self._format_name(caller_name, caller_lineno))



    def _caller_BAD(self, additional_levels=0):
        """Recupera informazioni sul chiamante e le formatta
        Args:
            additional_levels: Numero di livelli extra da saltare nello stack
        """
        f = inspect.currentframe()
        # additional_levels permette di saltare ulteriori livelli
        for _ in range(4 + additional_levels):
            print(_, f.f_code.co_filename, f.f_lineno)
            # print(f.f_back)
            if f is not None:
                f = f.f_back
            else:
                break

        if f is None:
            return self._format_name("unknown", 0), "dummy"

        filename = Path(os.path.basename(f.f_code.co_filename)).stem
        lineno = f.f_lineno
        func = f.f_code.co_name
        if func == '<module>':
            func = 'main'

        caller_name = filename  # default

        return self._format_name(caller_name, lineno), "dummy"


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

            # Calcola caller formattato se necessario
            # Il caller deve essere il chiamante del metodo pubblico (un livello sopra)
            # module_formatted, caller_formatted = self._callerMIO(stacklevel=3+stacklevel)
            module_formatted, caller_formatted = self._caller(stacklevel=3+stacklevel)

            if showCaller or self.show_caller:
                ...
            else:
                caller_formatted = ""
            #     caller_formatted = self._caller(additional_levels=1)  # <<<--- Salta un livello extra!


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


    # logger.setDynNameLength()
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

    logger.info("This shows caller info", show_caller=True)

    logger.info("Test con nome modulo lungo", show_caller=True)

    logger.info("This shows caller info + stacklevel=1", show_caller=True, stacklevel=1)

    logger.info("Test con nome modulo lungo + stacklevel=1", show_caller=True, stacklevel=1)

    # print("\n")


# # -------------------------------
# # Test
# # -------------------------------
# if __name__ == "__main__":
#     # Test con diverse lunghezze
#     print("=== Test con max_len=15 ===")
#     logger1 = lnColoredLogger(
#         name="test_logger",
#         console_logger_level="debug",
#         show_caller=True,
#         max_len=15
#     )
#     testLogger(logger1)

#     print("\n=== Test con max_len=20 ===")
#     logger2 = lnColoredLogger(
#         name="test_logger",
#         console_logger_level="debug",
#         show_caller=True,
#         max_len=20
#     )
#     testLogger(logger2)