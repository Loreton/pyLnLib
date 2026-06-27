#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 27-06-2026 10.20.22
#
import sys
sys.dont_write_bytecode = True  # (vedi pyproject.oml per notifica "E402")

from typing import Any, Optional, List, Dict, Union
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
    red: str = "\033[31m"
    redH: str = "\033[91m"
    green: str = "\033[32m"
    greenH: str = "\033[92m"
    yellow: str = "\033[33m"
    yellowH: str = "\033[93m"
    blue: str = "\033[34m"
    blueH: str = "\033[94m"
    purple: str = "\033[35m"
    purpleH: str = "\033[95m"
    magenta: str = "\033[35m"
    magentaH: str = "\033[95m"
    cyan: str = "\033[36m"
    cyanH: str = "\033[96m"
    white: str = "\033[37m"
    whiteH: str = "\033[97m"
    reset: str = "\033[0m"

    # Costanti per stili aggiuntivi
    bold: str = "\033[1m"
    underline: str = "\033[4m"
    blink: str = "\033[5m"
    reverse: str = "\033[7m"
    hidden: str = "\033[8m"

    # Background colors
    bg_red: str = "\033[41m"
    bg_green: str = "\033[42m"
    bg_yellow: str = "\033[43m"
    bg_blue: str = "\033[44m"
    bg_magenta: str = "\033[45m"
    bg_cyan: str = "\033[46m"
    bg_white: str = "\033[47m"


@dataclass
class GlobalVars:
    """
    Classe per le variabili globali dell'applicazione.

    Per le variabili mutabili (liste, dizionari, ecc.), usa default_factory.
    In questo modo, ogni istanza ottiene una nuova copia invece di condividere la stessa.
    """

    # Attributi base

    project_name: str = os.environ.get("LN_PROJECT_NAME", "dummy_prj_name")
    # project_name: str = ""
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
    logger: Optional[lnColoredLogger] = None  # Usa il logger personalizzato
    test_logger: bool = False

    # Liste e dizionari (usando default_factory)
    log_levels: List[str] = field(default_factory=lambda: ["INFO", "WARNING", "ERROR"])
    config: Dict[str, Any] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)

    # Opzionali
    yaml_engine: Any = None
    environment: Optional[str] = None

    def __post_init__(self) -> None:
        """Inizializza i campi che dipendono da altri valori."""
        if not self.temp_dir:
            self.temp_dir = f"/tmp/{self.project_name}" if self.project_name else "/tmp/ln_app"

        # Crea la directory temporanea se non esiste
        if self.temp_dir:
            os.makedirs(self.temp_dir, exist_ok=True)

        # Inizializza il logger se non è già stato fatto
        if self.logger is None:
            self._init_logger()

    def _init_logger(self) -> None:
        """
        Inizializza il logger usando lnColoredLogger.
        """
        try:
            # Crea il logger con il nome del progetto
            log_dir = Path(self.temp_dir) / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            # import pdb; pdb.set_trace(); # by Loreto
            self.logger = lnColoredLogger(
                name=self.project_name or "ln_app",
                console_logger_level="INFO",
                file_logger_level="DEBUG",
                logging_dir=str(log_dir),
                threads=False,
            )

            # Test del logger se richiesto
            if self.test_logger:
                self.logger.test(self.logger)

        except Exception as e:
            # Fallback: stampa a console
            print(f"ERROR initializing logger: {e}")
            self.logger = None

    def get_logger(self) -> Optional[lnColoredLogger]:
        """
        Restituisce il logger inizializzato.
        Se il logger non esiste, lo crea.

        Returns:
            Istanza di lnColoredLogger o None se non disponibile
        """
        if self.logger is None:
            self._init_logger()
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

    def reset_log_levels(self, levels: Optional[List[str]] = None) -> None:
        """Resetta i livelli di log."""
        if levels is None:
            self.log_levels = ["INFO", "WARNING", "ERROR"]
        else:
            self.log_levels = levels

    def add_log_level(self, level: str) -> None:
        """Aggiunge un livello di log."""
        if level not in self.log_levels:
            self.log_levels.append(level)

    def remove_log_level(self, level: str) -> None:
        """Rimuove un livello di log."""
        if level in self.log_levels:
            self.log_levels.remove(level)

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

def get_logger() -> Optional[lnColoredLogger]:
    """
    Funzione di comodo per ottenere il logger globale.

    Returns:
        Istanza di lnColoredLogger o None se non disponibile

    Examples:
        >>> logger = get_logger()
        >>> if logger:
        ...     logger.info("Messaggio di info")
    """
    return gVars.get_logger()


# ============================================================
# ISTANZA GLOBALE
# ============================================================

# Crea l'istanza globale
gVars = GlobalVars()

# Inizializza il logger
gVars.get_logger()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    # Test del logger
    logger = get_logger()
    if logger:
        print("Logger inizializzato!")
        logger.info("Questo è un test dal context.py")
        logger.debug("Debug message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.notify("Notify message")
        logger.function("Function message")
    else:
        print("Logger non disponibile")

    print(f"\nProject: {gVars.project_name}")
    print(f"Temp dir: {gVars.temp_dir}")
    print(f"Log dir: {gVars.get_log_dir()}")
