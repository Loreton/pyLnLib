#!/usr/bin/env python3
# ruff: noqa: PLE1205 Too many arguments for `logging` format string (Ruff PLE1205
# ruff: noqa: BLE001 Do not catch blind exception: `Exception`
#
from __future__ import annotations

import inspect
import logging
# import emoji
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
# from typing import any, Callable

# from webbrowser import get
from ..colors import get_colors

C = get_colors()
# Type aliases
LevelName = str
Message = str
ColorCode = str
StackLevel = int
LoggerName = str

sys.dont_write_bytecode = True


"""
    Level       Numeric value What it means / When to use it
"""
my_NOTSET_value: int = 0
my_TRACE_value: int = 9
my_DEBUG_value: int = 10
my_FUNCTION_value: int = 15
my_INFO_value: int = 20
my_NOTIFY_value: int = 21
my_WARNING_value: int = 30
my_ERROR_value: int = 40
my_CRITICAL_value: int = 50


# -------------------------------
# Formatter semplice + safe + TTY
# -------------------------------
class ColorFormatter(logging.Formatter):
    def __init__(
        self, fmt: str, datefmt: str | None = None, use_color: bool = True
    ) -> None:
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
    def __init__( self, name: str) -> None:
        self.LEVEL_COLORS: dict[str, str] = {
            "trace": C.debug,
            "debug": C.debug,
            "function": C.debug,
            "info": C.info,
            "notify": C.notify,
            "warning": C.warning,
            "error": C.error,
            "critical": C.critical,
        }
        # - config di base
        self.logger: logging.Logger = logging.getLogger(name)
        # Evita handler duplicati
        if self.logger.handlers:
            return
        self.add_custom_levels()
        self.logger.setLevel(logging.TRACE)  # type: ignore
        self.logger.propagate = False

        # - parametri
        self.name: str = name
        # self.test: Callable = testLogger


        self.initialize(name=name, console_logger_level="info", f_temporary=True)




    #############################################################
    # Args:
    #   name: Nome del logger
    #   console_level: Livello per console
    #   file_level: Livello per file
    #   log_dir: Directory per i log
    #
    # Returns:
    #   Logger configurato
    #############################################################
    def initialize( self, name: str, *,
            console_logger_level: str | None = None,
            file_logger_level: str = "warning",
            logging_dir: str | Path | None = None,
            threads: bool = False,
            f_temporary: bool=False,
        ) -> None:

        self.name = name
        self.threads_str: str = "%(threadName)-5.5s." if threads else ""
        self.logging_dir = Path(logging_dir) if logging_dir else None

        self.consoleHandler: logging.Handler | None = None
        self.fileHandler: logging.Handler | None = None

        # rimuoviventuali handler creati durante la fase di __init__
        # altrimenti scrive due volte le log lines
        self._clear_handlers()
        # breakpoint()


        if console_logger_level:
            # self.addHandler(console_handler)
            # self.addHandler(file_handler)
            self.consoleHandler = self.setConsoleLogger()
            self.consoleHandler.setLevel( getattr(logging, console_logger_level.upper(), logging.INFO) )
            self.logger.addHandler(self.consoleHandler)

        if self.logging_dir:
            self.fileHandler = self.setRotatingLogger()
            self.fileHandler.setLevel( getattr(logging, file_logger_level.upper(), logging.WARNING) )
            self.logger.addHandler(self.fileHandler)

        self.module_name_len: int = 0
        self.lineno_len = 4
        self.name_function: bool = True  # come nome modulo melle module_name.func_name
        self.show_caller = False
        self.setNameLength(dynamic=True, length=0)
        if False:
            self.dump_handlers()
        if not f_temporary:
            # breakpoint()
            self.warning(f"Logger {C.white}{self.name}{C.warning} inizializzato!...")


    # metodo di pulizia handlers
    def _clear_handlers(self):
        if self.logger.handlers:
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
                handler.close()

    # metodo di debug
    def dump_handlers(self):
        print(f"Logger: {self.name}")
        print(f"Handlers: {len(self.logger.handlers)}")
        for h in self.logger.handlers:
            print(f"  {type(h).__name__} level={logging.getLevelName(h.level)}")

    def add_custom_levels(self) -> None:
        # --- Livello custom NOTIFY ---
        def notify(
            self_logger: logging.Logger, msg: str, *args: any, **kwargs: any
        ) -> None:
            self_logger._log(logging.NOTIFY, msg, args, **kwargs)  # type: ignore

        logging.NOTIFY = my_NOTIFY_value  # type: ignore
        logging.addLevelName(logging.NOTIFY, "NOTIFY")  # type: ignore
        logging.Logger.notify = notify  # type: ignore

        # --- Livello custom TRACE ---
        def trace(
            self_logger: logging.Logger, msg: str, *args: any, **kwargs: any
        ) -> None:
            self_logger._log(logging.TRACE, msg, args, **kwargs)  # type: ignore

        logging.TRACE = my_TRACE_value  # type: ignore
        logging.addLevelName(logging.TRACE, "TRACE")  # type: ignore
        logging.Logger.trace = trace  # type: ignore

        # --- Livello custom FUNCTION ---
        def function(
            self_logger: logging.Logger, msg: str, *args: any, **kwargs: any
        ) -> None:
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
            f"{C.cyan}%(asctime)s "
            f"{C.blue}%(module_formatted)s"  # <--- Usa il campo formattato
            f"{C.magenta}%(caller_formatted)s"  # <--- Usa il campo formattato
            f"{C.reset}"
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
    def setRotatingLogger(self) -> logging.Handler:
        # if self.logging_dir is None:
        #     self.logging_dir = f"/tmp/{self.name.lower()}/log"

        logging_file = f"{self.logging_dir}/{self.name.lower()}.log"
        if not self.logging_dir or not os.path.exists(self.logging_dir):
            os.makedirs(str(self.logging_dir), exist_ok=True)

        fh = RotatingFileHandler(logging_file, maxBytes=5 * 1000 * 1000, backupCount=5)
        formatter = logging.Formatter(
            f"%(asctime)s - [{self.threads_str}%(module_formatted)s%(caller_formatted)s [%(levelname)4.4s]: %(message)s"
        )
        fh.setFormatter(formatter)
        return fh

    def setConsoleLoggerLevel(self, level: str) -> None:
        if self.consoleHandler is not None:
            self.consoleHandler.setLevel(level.upper())
            self.debug("console log level has been set to: %s", level.upper())

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

    def get_log_levels(self) -> list[str]:
        """
        Restituisce un dizionario con tutti i livelli di logging correnti.

        Returns:
            Dizionario con {'console': 'INFO', 'file': 'DEBUG', ...}
        """
        return list(self.LEVEL_COLORS.keys())
        # return {
        #     'console': self.getConsoleLoggerLevel(),
        #     'file': self.getFileLoggerLevel(),
        #     'logger': logging.getLevelName(self.logger.level),
        # }

    def showMaxLength(self) -> int:
        self.notify(
            "name_len: %s, lineno_len: %s (total+[]: %s)",
            self.module_name_len,
            self.lineno_len,
            self.module_name_len + self.lineno_len + 1 + 2,
        )
        return self.module_name_len + self.lineno_len + 1

    # def setLinenoLength(self, len: int) -> None:
    #     self.lineno_len = len
    #     # self.notify("lineno length set to: %s", self.lineno_len)

    def setShowCaller(self, show_caller: bool) -> None:
        self.show_caller = show_caller
        self.notify("showCaller set to: %s", self.show_caller, stacklevel=1)

    ###########################################################
    #
    ###########################################################
    def setNameLength( self, dynamic: bool, length: int, f_name_function: bool = True ) -> None:
        self.name_function = f_name_function
        if dynamic or length == 0:
            self.dynamic_name_lentgh = True
            self.module_name_len = 0
            self.debug("name length set to dynamic", stacklevel=2)
        else:
            self.dynamic_name_lentgh = False
            length = max(length, 15)
            self.module_name_len = length
            self.debug(
                "name length set to: %s (dynamic: %s)",
                self.module_name_len,
                self.dynamic_name_lentgh,
                stacklevel=2,
            )

    def _format_name(self, name: str, lineno: int, function: str) -> str:
        """
        Formatta nome e numero di linea come [nome:1234]
        con troncamento e padding appropriati
        """
        fDEBUG = False
        # Tronca il nome se necessario
        if fDEBUG:
            print(f"before: {self.module_name_len = } {len(name) = }")
        if self.dynamic_name_lentgh:
            # if len(name) >= self.module_name_len:
                # self.module_name_len = len(name)
            self.module_name_len = max(self.module_name_len, len(name))
        else:
            if len(name) >= self.module_name_len:
                name = (
                    name[: self.module_name_len - 2] + "."
                )  ### per far capire che è troncato

        # Padding del nome con spazi a destra
        if fDEBUG:
            print(f"after:  {self.module_name_len = } {len(name) = }")
        # name = f"{name}:".ljust(self.module_name_len)
        name = f"{name}".ljust(self.module_name_len)

        # Formatta il numero di linea con padding a sinistra
        return f"[{name}:{lineno:-04d} ({function:10.10})]"
        return f"[{name}.{function:10.10}:{lineno:-04d})]"

    def _format_name_func(self, name: str, lineno: int, function: str) -> str:
        """
        Formatta nome e numero di linea come [nome:1234]
        con troncamento e padding appropriati
        """
        fDEBUG = False
        # Tronca il nome se necessario
        if fDEBUG:
            print(
                f"before: {self.module_name_len = } {len(name) = } {len(function) = }"
            )

        my_name = name.strip() + "." + function.strip()
        my_len = len(my_name)
        if self.dynamic_name_lentgh:
            # if my_len >= self.module_name_len:
            #     self.module_name_len = my_len
            self.module_name_len = max(self.module_name_len, my_len)
        else:
            if my_len >= self.module_name_len:
                name = (
                    my_name[: self.module_name_len - 2] + "."
                )  ### per far capire che è troncato

        # Padding del nome con spazi a destra
        if fDEBUG:
            print(f"after:  {self.module_name_len = } {len(my_name) = }")
        # name = f"{name}:".ljust(self.module_name_len)
        name = f"{my_name}".ljust(self.module_name_len)

        # Formatta il numero di linea con padding a sinistra
        return f"[{name}:{lineno:-04d}]"
        # return f"[{name}.{function:10.10}:{lineno:-04d})]"

    # ######################################################
    # 0  _caller() - la funzione corrente
    # 2  _log()
    # 3  info() / debug() / etc. (metodo pubblico)
    # 4  chiamante originale (test function)
    # ######################################################
    def _caller(self, stacklevel: int, show_stack: bool = False) -> tuple[str, str]:
        """Restituisce (module_formatted, caller_formatted)

        Args:
            stacklevel: Livello base da cui partire (default 1)
                       1 = chiamante di _log (metodo pubblico)
                       2 = chiamante originale
        """
        frames: list[inspect.FrameInfo] = inspect.stack()
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

        # Calcola gli indici (evitando di andare out of range)
        module_idx = min(stacklevel, n_levels - 1)
        module_frame = frames[module_idx]
        module_filename = module_frame.filename
        module_name = Path(module_frame.filename).stem
        module_lineno = module_frame.lineno
        module_func = module_frame.function

        if n_levels - stacklevel <= 1:
            caller_filename = "out_of_index"
            caller_name = "out_of_index"
            caller_lineno = 0
            caller_func = "out_of_index"
            caller_frame = "no_frame"
            caller_idx = min(module_idx + 1, n_levels - 1)  # module_idx+1
        else:
            caller_idx = min(module_idx + 1, n_levels - 1)  # module_idx+1
            caller_frame = frames[caller_idx]
            caller_filename = caller_frame.filename
            caller_name = Path(caller_frame.filename).stem
            caller_lineno = caller_frame.lineno
            caller_func = caller_frame.function

        if show_stack:
            print("-" * 40)
            print("module:", module_idx, module_filename, module_lineno, module_func)
            print("caller:", caller_idx, caller_filename, caller_lineno, caller_func)
            print("-" * 40)

        # self.name_function: bool=True
        if self.name_function:
            return (
                self._format_name_func(module_name, module_lineno, module_func),
                self._format_name_func(caller_name, caller_lineno, caller_func),
            )
        else:
            return (
                self._format_name(module_name, module_lineno, module_func),
                self._format_name(caller_name, caller_lineno, caller_func),
            )

    ################################################################
    # supporta sia %s che {}
    #   msg1 = "moving version:\n %s\nto %s"  # Stile %
    #   msg2 = "moving version:\n {}\nto {}"  # Stile format()
    ################################################################
    def _write_log_line(
                        self,
                        level_value: int,
                        msg: str,
                        *args: any,
                        color: str | None = None,
                        **kwargs: any,
                    ) -> None:
        extra = kwargs["extra"]

        try:
            trim_line = extra.get("trim_line", False)
            msg_dry_run = extra["msg_dry_run"]

            # Prova a formattare il messaggio
            if args:
                try:
                    # Primo tentativo: stile %
                    formatted_msg = msg % args
                except (TypeError, ValueError):
                    try:
                        # Secondo tentativo: stile format()
                        formatted_msg = msg.format(*args)
                    except (IndexError, KeyError):
                        # Fallback: usa il messaggio originale
                        formatted_msg = msg
                        _level_value = getattr(logging, "WARNING", logging.WARNING)
                        self.logger.log(_level_value, f"Formatting failed for: {msg}")
            else:
                formatted_msg = msg


            # Dividi in righe
            # Usa splitlines() per robustezza
            # lines = formatted_msg.split('\n')
            lines = formatted_msg.splitlines()

            for i, line in enumerate(lines):
                if i > 0:
                    # Aggiungi indentazione per le righe successive
                    if trim_line:
                        line = line.strip()
                    line = f"\t{line}" if line else ""

                    extra["msg_color"] = C.logger_second_line
                else:
                    if len(lines) > 1:
                        extra["msg_color"] = C.logger_first_line

                if level_value in [logging.ERROR, logging.CRITICAL]:
                    extra["msg_color"] = extra["level_color"]

                if line:  # Logga solo se non vuota
                    if C.reset in line:
                        line = line.replace(C.reset, extra["msg_color"])  # Sostituisci il reset con il colore secondario
                    self.logger.log(level_value, f"{msg_dry_run}{line}", **kwargs)
            # if isinstance(msg, str) and msg.startswith("processItems called"):
                # breakpoint()

        except Exception as e:
            # Fallback: logga il messaggio originale in caso di errori
            extra["msg_color"] = C.error
            error_level_value = getattr(logging, "ERROR", logging.ERROR)
            print(f"{error_level_value = }")
            self.logger.log(error_level_value, f"Error in logging: {msg}", **kwargs)
            self.logger.log(error_level_value, f"Error details:    {e}", **kwargs)

    # -------------------------------
    # Core logging
    # -------------------------------
    def _prepare_for_logging( self,
                                level_name: str,
                                msg: str,
                                *args: any,
                                color: str | None = None,
                                **kwargs: any,
                            ) -> dict:
        ### ok processiamo la linea
        stacklevel: int = kwargs.pop("stacklevel", 0)
        showCaller: bool = kwargs.pop("show_caller", False)
        show_stack: bool = kwargs.pop("show_stack", False)
        dry_run: bool = kwargs.pop("dry_run", False)
        trim_line = kwargs.pop("trim_line", False)

        kwargs["stacklevel"] = stacklevel + 4

        # Calcola caller formattato se necessario
        module_formatted, caller_formatted = self._caller(
            stacklevel=kwargs["stacklevel"], show_stack=show_stack
        )

        if showCaller or self.show_caller:
            ...
        else:
            caller_formatted = ""

        level_color = self.LEVEL_COLORS.get(level_name.lower(), C.white)

        # ----------------------
        # - override colors
        # ----------------------


        if color and level_name not in ["ERROR", "EXCEPTION", "CRITICAL"]:
            msg_color = color
            level_color = color
        elif dry_run:
            msg_color = C.magentaH
        else:
            msg_color = level_color

        msg_dry_run = f"{C.white}[dry-run]{msg_color}" if dry_run else ""
        # extract extra from kwargs
        extra = kwargs.pop("extra", {})

        extra.update(
            {
                "msg_color": msg_color,
                "level_color": level_color,
                "2nd_line_color": C.blue,
                "reset": C.reset,
                "module_formatted": module_formatted,  # <<<--- modulo formattato
                "caller_formatted": caller_formatted,  # <<<--- caller formattato
                "msg_dry_run": msg_dry_run,
                "trim_line": trim_line,
            }
        )
        # add updated extra to kwargs
        kwargs["extra"] = extra
        return kwargs  # sono obbligato altrimenti lo perdo

    # -------------------------------
    # - check if level is valid
    # -------------------------------
    def _is_valid_level(self, level_value: int, forceLog: bool) -> bool:
        if not self.consoleHandler:
            return False

        # if level_value < self.consoleHandler.level:
        #     print(f"level_value: {level_value} < consoleHandler.level: {self.consoleHandler.level}")
        #     print(f"{level_value = }")
        #     print(f"{self.getConsoleLoggerLevel() = }")
        #     _curr_name=logging.getLevelName(level_value)
        #     print(f"{_curr_name = }")

        return level_value >= self.consoleHandler.level or forceLog

    # -------------------------------
    # Core logging
    # -------------------------------
    def _log_multiline( self,
                        level_name: str,
                        msg: str|list,
                        *args: any,
                        color: str | None = None,
                        **kwargs: any,
                    ) -> None:
        forceExit: bool = kwargs.pop("exit", False)
        forceLog: bool = kwargs.pop("force_log", False)

        level_value = getattr(logging, level_name, logging.INFO)
        if not self._is_valid_level(level_value, forceLog):
            return

        ### ok processiamo la linea
            # convert in string with '\n' on each item and the index of each item
        if isinstance(msg, list):
            msg = f"list items ({len(msg)}):\n" + "\n".join(f"{i+1}. {item}" for i, item in enumerate(msg))

        kwargs = self._prepare_for_logging( level_name, msg, *args, color=color, **kwargs )
        self._write_log_line(level_value, msg, *args, color=color, **kwargs)

        if forceExit:
            sys.exit(1)

    #########################################################################
    # API pubbliche
    #########################################################################
    def trace( self, msg: str|list, *args: any, color: str | None = None, **kwargs: any ) -> None:
        self._log_multiline("TRACE", msg, *args, color=color, **kwargs)

    def debug( self, msg: str|list, *args: any, color: str | None = None, **kwargs: any ) -> None:
        self._log_multiline("DEBUG", msg, *args, color=color, **kwargs)

    def info( self, msg: str|list, *args: any, color: str | None = None, **kwargs: any ) -> None:
        self._log_multiline("INFO", msg, *args, color=color, **kwargs)

    def warning( self, msg: str|list, *args: any, color: str | None = None, **kwargs: any ) -> None:
        self._log_multiline("WARNING", f"⚠️ {msg}", *args, color=color, **kwargs)

    def error( self, msg: str|list, *args: any, color: str | None = None, **kwargs: any ) -> None:
        self._log_multiline("ERROR", f"🔴 {msg}", *args, color=color, **kwargs)

    def critical( self, msg: str|list, *args: any, color: str | None = None, **kwargs: any ) -> None:
        self._log_multiline("CRITICAL", f"💀 {msg}", *args, color=color, **kwargs)

    # def exception( self, msg: str|list, *args: any, color: str | None = None, **kwargs: any ) -> None:
    #     self._log_multiline("ERROR", msg, *args, exc_info=True, exit=True, **kwargs) da una riga dirrore:  NoneType: None

    def notify( self, msg: str|list, *args: any, color: str | None = None, **kwargs: any ) -> None:
        self._log_multiline("NOTIFY", msg, *args, color=color, **kwargs)
        # self._log_multiline("NOTIFY", f"👉-{msg}", *args, color=color, **kwargs)

    def function( self, msg: str|list, *args: any, color: str | None = None, **kwargs: any ) -> None:
        self._log_multiline( "FUNCTION", msg, *args, color=color, **kwargs )

    # - EXTR
    def success( self, msg: str|list, *args: any, color: str | None = None, **kwargs: any ) -> None:
        self._log_multiline( "INFO", f"✔️ {msg}", *args, color=color, **kwargs )





def testLogger(logger: any) -> None:
    print("\n--- base colors ---")
    logger.trace("TRACE default")
    logger.debug("DEBUG default")
    logger.function("FUNCTION default")
    logger.info("INFO default")
    logger.notify("NOTIFY default")
    logger.warning("WARNING default")
    logger.error("ERROR default")
    logger.critical("CRITICAL default")

    # saved_level = logger.getConsoleLoggerLevel()
    # logger.setConsoleLoggerLevel("WARNING")
    print("\n--- base colors forzando level to WARNING---")
    logger.trace("TRACE default")
    logger.debug("DEBUG default")
    logger.function("FUNCTION default")
    logger.info("INFO default")
    logger.notify("NOTIFY default")
    logger.warning("WARNING default")
    logger.error("ERROR default")
    logger.critical("CRITICAL default")
    logger.notify("NOTIFY default")
    # logger.setConsoleLoggerLevel(saved_level)

    print("\n--- modifying default colors ---")
    logger.info("INFO in magenta", color=C.magenta)
    logger.warning("WARNING in cyan", color=C.cyan)
    logger.error("ERROR in yellowH", color=C.yellowH)

    logger.info("This shows caller info", show_caller=True)

    logger.info("Test con nome modulo lungo", show_caller=True)

    logger.info("This shows caller info + stacklevel=1", show_caller=True, stacklevel=1)

    logger.info(
        "Test con nome modulo lungo + stacklevel=1", show_caller=True, stacklevel=1
    )


# Variabile globale per il logger singleton
my_logger = None


def get_logger( name: str="TEMPORARY_LOGGER" ) -> lnColoredLogger:
    """
    Inizializza il logger temporaneo per l'inizializzazione dei moduli.
    il main program provvederà ad eseguire logger.configure() per impostare quello di lavoro

    """
    global my_logger
    # Lazy initialization: crea un logger temporaneo se get_logger() viene chiamato
    # prima di init_logger(). Questo risolve il problema dell'ordine di importazione
    # nei moduli. Quando init_logger() verrà chiamato, sostituirà questo logger
    # temporaneo con quello configurato correttamente.
    if not my_logger:
        # Crea il logger
        my_logger = lnColoredLogger(name="TEMPORARY_LOGGER")
        my_logger.warning( f"Logger {C.white}{my_logger.name}{C.warning} in attesa di init_logger()...", exit=False, )
    # - questa riga per indicare i moduli che la caricano prima di initialize()
    my_logger.debug("my_logger.name: %s", my_logger.name, stacklevel=1    )
    return my_logger
