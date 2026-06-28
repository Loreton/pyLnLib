#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 27-06-2026 18.41.26
#
import pdb
import sys; sys.dont_write_bytecode = True  # (vedi pyproject.oml per notifica "E402")

from typing import Any, Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import platform
import socket
import zipfile
import os


# Import del logger
from .logger.ln_colored_logger import lnColoredLogger


@dataclass(frozen=True)  # "frozen" rende i colori non modificabili per errore
class Colors:
    """Classe per i codici colore ANSI per il terminale."""
    red: str        = "\033[31m"
    redH: str       = "\033[91m"
    green: str      = "\033[32m"
    greenH: str     = "\033[92m"
    yellow: str     = "\033[33m"
    yellowH: str    = "\033[93m"
    blue: str       = "\033[34m"
    blueH: str      = "\033[94m"
    purple: str     = "\033[35m"
    purpleH: str    = "\033[95m"
    magenta: str    = "\033[35m"
    magentaH: str   = "\033[95m"
    cyan: str       = "\033[36m"
    cyanH: str      = "\033[96m"
    white: str      = "\033[37m"
    whiteH: str     = "\033[97m"
    reset: str      = "\033[0m"

    # Costanti per stili aggiuntivi
    bold: str       = "\033[1m"
    underline: str  = "\033[4m"
    blink: str      = "\033[5m"
    reverse: str    = "\033[7m"
    hidden: str     = "\033[8m"

    # Background colors
    bg_red: str     = "\033[41m"
    bg_green: str   = "\033[42m"
    bg_yellow: str  = "\033[43m"
    bg_blue: str    = "\033[44m"
    bg_magenta: str = "\033[45m"
    bg_cyan: str    = "\033[46m"
    bg_white: str   = "\033[47m"


class _DummyLogger:
    """
    Logger di fallback quando lnColoredLogger non è disponibile.
    """
    def __init__(self):
        import logging
        self._logger = logging.getLogger('dummy')
        self._logger.setLevel(logging.DEBUG)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def debug(self, msg: str, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)

    def notify(self, msg: str, *args, **kwargs):
        self._logger.info(f"NOTIFY: {msg}", *args, **kwargs)

    def function(self, msg: str, *args, **kwargs):
        self._logger.debug(f"FUNCTION: {msg}", *args, **kwargs)

    def trace(self, msg: str, *args, **kwargs):
        self._logger.debug(f"TRACE: {msg}", *args, **kwargs)

    def test(self, *args, **kwargs):
        print("DummyLogger: test chiamato")


@dataclass
class GlobalVars:
    """
    Classe per le variabili globali dell'applicazione.

    Per le variabili mutabili (liste, dizionari, ecc.), usa default_factory.
    In questo modo, ogni istanza ottiene una nuova copia invece di condividere la stessa.
    """

    # Attributi base
    Colors = Colors # inerisco la classe Colors nelle variabili
    project_name: str|None = os.environ.get("LN_PROJECT_NAME", None)
    version: str = "0.0.1"

    # Path
    script_path: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    temp_dir: str = ""  # Verrà impostato in __post_init__

    # Sistema
    hostname: str = field(default_factory=lambda: socket.gethostname().split()[0])
    op_sys: str = field(default_factory=lambda: platform.system())
    now_str: str = field(default_factory=lambda: datetime.now().strftime("%d-%m-%Y_%H:%M"))

    # Esecuzione
    args: Any = None
    fExecute: bool = False
    isZIP: bool = field(default_factory=lambda: zipfile.is_zipfile(sys.argv[0]))

    # Logging e colori
    colors: Colors = field(default_factory=Colors)
    _logger: Any = field(default=None, repr=False)  # Logger privato
    test_logger: bool = False

    # Liste e dizionari
    log_levels: List[str] = field(default_factory=lambda: ["INFO", "WARNING", "ERROR"])
    config: Dict[str, Any] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)

    # Opzionali
    yaml_engine: Any = None
    environment: Optional[str] = None


    def __post_init__(self) -> None:
        """Inizializza i campi che dipendono da altri valori."""
        if self.project_name:
            self.set_project_name(name=self.project_name)


    def set_temp_dir(self) -> None:
        if not self.temp_dir:
            self.temp_dir = f"/tmp/{self.project_name}"
        if self.temp_dir:
            os.makedirs(self.temp_dir, exist_ok=True)


    def set_project_name(self, name: str) -> None:
        self.project_name = name
        self.set_temp_dir()
        self._init_logger()

    def _init_logger(self) -> None:
        """
        Inizializza il logger usando lnColoredLogger.
        Se fallisce, usa un logger dummy.
        """

        try:
            log_dir = Path(self.temp_dir) / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            self._logger = lnColoredLogger(
                name=self.project_name or "ln_app",
                console_logger_level="INFO",
                file_logger_level="DEBUG",
                logging_dir=str(log_dir),
                threads=False,
            )
            self._logger.setNameLength(dynamic=True, length=0)
            if self.test_logger and hasattr(self._logger, 'test'):
                self._logger.test(self._logger)

        except Exception as e:
            print(f"WARNING: Errore nell'inizializzazione del logger: {e}")
            print("Uso logger dummy di fallback")
            self._logger = _DummyLogger()

    @property
    def logger(self) -> Any:
        """
        Property per accedere al logger.
        Garantisce che logger non sia mai None.
        """
        if self._logger is None:
            self._init_logger()
        return self._logger

    # @logger.setter
    # def logger(self, value: Any) -> None:
    #     """Permette di impostare un logger personalizzato."""
    #     self._logger = value

    def get_logger(self) -> Any:
        """Restituisce il logger inizializzato. Non è mai None."""
        return self.logger

    def get_temp_path(self, subdir: Optional[str] = None) -> Path:
        """Restituisce il path temporaneo."""
        temp_path = Path(self.temp_dir)
        if subdir:
            temp_path = temp_path / subdir
            temp_path.mkdir(parents=True, exist_ok=True)
        return temp_path

    def get_log_dir(self) -> Path:
        """Restituisce il path per i log."""
        return self.get_temp_path("logs")

    def get_config_dir(self) -> Path:
        """Restituisce il path per le configurazioni."""
        return self.get_temp_path("conf")

    def to_dict(self) -> Dict[str, Any]:
        """Converte l'oggetto in un dizionario."""
        result: Dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_") and key != "logger":
                if isinstance(value, (Path, Colors)):
                    result[key] = str(value)
                else:
                    result[key] = value
        return result


# ============================================================
# FUNZIONE DI UTILITY PER ACCEDERE AL LOGGER
# ============================================================

def get_logger() -> Any:
    """
    Funzione di comodo per ottenere il logger globale.
    Garantisce che non sia mai None.
    """
    return gVars.get_logger()


# ============================================================
# ISTANZA GLOBALE
# ============================================================

gVars = GlobalVars()




# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    logger = get_logger()
    print("Logger inizializzato!")
    logger.info("Questo è un test dal context.py")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.notify("Notify message")
    logger.function("Function message")

    print(f"\nProject: {gVars.project_name}")
    print(f"Temp dir: {gVars.temp_dir}")
    print(f"Log dir: {gVars.get_log_dir()}")
