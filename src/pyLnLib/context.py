#!/usr/bin/env python3
# import sys
import os
import socket
import platform
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any #,  TYPE_CHECKING

# if TYPE_CHECKING:
from pyLnLib.logger import lnLogger


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






@dataclass
class GlobalVars:
    """Solo dati, niente logica di inizializzazione pesante."""

    # Variabili d'ambiente
    project_name: str = field(default_factory=lambda:  os.environ.get("LN_PROJECT_NAME", "dummy_project") )

    # Path
    temp_dir: str = field(default_factory=lambda:  f"/tmp/{os.environ.get('LN_PROJECT_NAME', 'dummy_project')}" )

    # Sistema
    hostname: str = field(default_factory=lambda: socket.gethostname().split()[0])
    op_sys: str = field(default_factory=lambda: platform.system())

    # Logging e colori
    colors: Colors = field(default_factory=Colors)
    # my_logger: Any = None  # Verrà settato dall'esterno
    # my_logger: Any = field(default=None, repr=False)  # Logger privato
    # test_logger: bool = False

    # Altri dati
    version: str = "0.0.1"
    args: Any = None
    config: dict = field(default_factory=dict)



    ############# LOGGER
    my_logger: 'lnLogger | None' = field(default=None, repr=False)

    def get_logger(self, create: bool = False, logger_name: str | None = None) -> 'lnLogger | None':
        """
        Ottieni il logger.

        Args:
            create: Se True e il logger non esiste, lo crea automaticamente.
                   Se False, restituisce None se il logger non esiste.
            logger_name: Nome del logger (se None, usa il nome del progetto).

        Returns:
            Il logger se esiste (o viene creato), altrimenti None
        """
        if self.my_logger is None and create:
            self._init_logger(logger_name)
        return self.my_logger

    def _init_logger(self, logger_name: str | None = None) -> None:
        """Inizializza il logger con i valori di default."""
        # from pyLnLib.logger import lnLogger  # Import lazy

        log_dir: Path | str | None = self.get_log_dir()
        if log_dir is not None:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)

        self.my_logger = lnLogger(
            name=logger_name or self.project_name,
            console_logger_level="INFO",
            file_logger_level="DEBUG",
            logging_dir=str(log_dir),
            threads=False,
        )
        self.my_logger.setNameLength(dynamic=True, length=0)

    def set_logger(self, logger: 'lnLogger') -> None:
        """Imposta un logger esterno (override di quello automatico)."""
        self.my_logger = logger

    def get_log_dir(self) -> str|Path|None:
        """Restituisce il path per i log."""
        return self.get_temp_path("logs")



    # def get_logger(self, create: bool = False) -> 'lnLogger | None':
    #     """Ottieni il logger. Se non esiste, lo crea solo se create è True."""
    #     if self.my_logger is None and create:
    #         self._init_logger()
    #     return self.my_logger

    # def get_logger_or_raise(self) -> 'lnLogger':
    #     """Ottieni il logger o solleva eccezione se non inizializzato."""
    #     if self.my_logger is None:
    #         raise RuntimeError("Logger not initialized")
    #     return self.my_logger


    # def get_logger(self) -> 'lnLogger':
    #     """Ottieni il logger. Se non inizializzato, lo crea automaticamente."""
    #     if self.my_logger is None:
    #         # Inizializzazione lazy - crea il logger al primo utilizzo
    #         self._init_logger()
    #     return self.my_logger

    # def _init_logger(self) -> None:
    #     """Inizializza il logger con i valori di default."""
    #     from pyLnLib.logger import lnLogger  # Import lazy

    #     log_dir = self.get_log_dir()
    #     log_dir.mkdir(parents=True, exist_ok=True)

    #     self.my_logger = lnLogger(
    #         name=self.project_name,
    #         console_logger_level="INFO",
    #         file_logger_level="DEBUG",
    #         logging_dir=str(log_dir),
    #         threads=False,
    #     )
    #     self.my_logger.setNameLength(dynamic=True, length=0)

    # def set_logger(self, logger: 'lnLogger') -> None:
    #     """Imposta un logger esterno (override di quello automatico)."""
    #     self.my_logger = logger

    # def get_log_dir(self) -> str|Path:
    #     """Restituisce il path per i log."""
    #     return self.get_temp_path("logs")

    ############# LOGGER
    #
    def get_temp_path(self, subdir: str | None = None) -> Path:
        """Restituisce il path temporaneo."""
        temp_path = Path(self.temp_dir)
        if subdir:
            temp_path = temp_path / subdir
            temp_path.mkdir(parents=True, exist_ok=True)
        return temp_path


    def get_colors(self) -> Colors:
        return self.colors

    def to_dict(self) -> dict[str, Any]:
        """Converte l'oggetto in un dizionario."""
        result: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_") and key != "logger":
                if isinstance(value, (Path, Colors)):
                    result[key] = str(value)
                else:
                    result[key] = value
        return result


# Istanza globale
gVars = GlobalVars()

def get_logger(create: bool = False, logger_name: str | None = None) -> 'lnLogger | None':
    """Funzione comoda per ottenere il logger."""
    return gVars.get_logger(create=create, logger_name=logger_name)
