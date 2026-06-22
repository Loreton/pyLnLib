#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 21-06-2026 17.31.37
#

import os
import platform
import socket
import sys
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.dont_write_bytecode = True


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
    project_name: str = ""
    version: str = "0.0.1"

    # Path
    script_path: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    temp_dir: str = ""  # Verrà impostato in __post_init__

    # Sistema
    hostname: str = field(default_factory=lambda: socket.gethostname().split()[0])
    op_sys: str = field(default_factory=lambda: platform.system())
    now_str: str = field(
        default_factory=lambda: datetime.now().strftime("%d-%m-%Y_%H:%M")
    )

    # Esecuzione
    args: Any = None
    fExecute: bool = False
    isZIP: bool = field(default_factory=lambda: zipfile.is_zipfile(sys.argv[0]))

    # Logging e colori
    colors: Colors = field(default_factory=Colors)
    logger: Any = None
    test_logger: bool = False

    # Liste e dizionari (usando default_factory)
    log_levels: List[str] = field(default_factory=lambda: ["INFO", "WARNING", "ERROR"])
    config: Dict[str, Any] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)

    # Opzionali
    yaml_engine: Any = None
    environment: Optional[str] = None

    def __post_init__(self) -> None:
        """
        Inizializza i campi che dipendono da altri valori.
        """
        # Imposta temp_dir se non è già impostato
        if not self.temp_dir:
            self.temp_dir = (
                f"/tmp/{self.project_name}" if self.project_name else "/tmp/ln_app"
            )

        # Crea la directory temporanea se non esiste
        if self.temp_dir:
            os.makedirs(self.temp_dir, exist_ok=True)

    def get_temp_path(self, subdir: Optional[str] = None) -> Path:
        """
        Restituisce il path temporaneo, opzionalmente con una sottodirectory.

        Args:
            subdir: Sottodirectory opzionale

        Returns:
            Path completo per la directory temporanea
        """
        temp_path: Path = Path(self.temp_dir)
        if subdir:
            temp_path = temp_path / subdir
            temp_path.mkdir(parents=True, exist_ok=True)
        return temp_path

    def get_log_dir(self) -> Path:
        """
        Restituisce il path per i log.

        Returns:
            Path per la directory dei log
        """
        log_dir: Path = self.get_temp_path("logs")
        return log_dir

    def get_config_dir(self) -> Path:
        """
        Restituisce il path per le configurazioni.

        Returns:
            Path per la directory delle configurazioni
        """
        return self.get_temp_path("conf")

    def reset_log_levels(self, levels: Optional[List[str]] = None) -> None:
        """
        Resetta i livelli di log.

        Args:
            levels: Nuova lista di livelli, o None per default
        """
        if levels is None:
            self.log_levels = ["INFO", "WARNING", "ERROR"]
        else:
            self.log_levels = levels

    def add_log_level(self, level: str) -> None:
        """
        Aggiunge un livello di log.

        Args:
            level: Livello da aggiungere
        """
        if level not in self.log_levels:
            self.log_levels.append(level)

    def remove_log_level(self, level: str) -> None:
        """
        Rimuove un livello di log.

        Args:
            level: Livello da rimuovere
        """
        if level in self.log_levels:
            self.log_levels.remove(level)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte l'oggetto in un dizionario.

        Returns:
            Dizionario con tutti gli attributi
        """
        result: Dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                if isinstance(value, (Path, Colors)):
                    result[key] = str(value)
                else:
                    result[key] = value
        return result


# Versione alternativa con tipo più specifico per temp_dir
@dataclass
class GlobalVarsStrict:
    """Versione con tipi più stretti."""

    project_name: str = ""
    version: str = "0.0.1"
    script_path: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    temp_dir: Path = field(default_factory=lambda: Path("/tmp/ln_app"))

    hostname: str = field(default_factory=lambda: socket.gethostname().split()[0])
    op_sys: str = field(default_factory=lambda: platform.system())
    now_str: str = field(
        default_factory=lambda: datetime.now().strftime("%d-%m-%Y_%H:%M")
    )

    args: Any = None
    fExecute: bool = False
    isZIP: bool = field(default_factory=lambda: zipfile.is_zipfile(sys.argv[0]))

    colors: Colors = field(default_factory=Colors)
    logger: Any = None
    test_logger: bool = False

    log_levels: List[str] = field(default_factory=lambda: ["INFO", "WARNING", "ERROR"])
    config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Crea le directory necessarie."""
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Se project_name è impostato, aggiorna temp_dir
        if self.project_name:
            self.temp_dir = Path(f"/tmp/{self.project_name}")
            self.temp_dir.mkdir(parents=True, exist_ok=True)


# 👉 ISTANZA VERA (singleton)
gVars: GlobalVars = GlobalVars()


# Funzione per ottenere l'istanza globale
def get_global_vars() -> GlobalVars:
    """
    Restituisce l'istanza globale di GlobalVars.

    Returns:
        Istanza GlobalVars
    """
    return gVars


# Funzione per reimpostare l'istanza (utile per test)
def reset_global_vars(project_name: Optional[str] = None) -> GlobalVars:
    """
    Reimposta l'istanza globale (utile per test).

    Args:
        project_name: Nuovo nome del progetto

    Returns:
        Nuova istanza GlobalVars
    """
    global gVars
    if project_name:
        gVars = GlobalVars(project_name=project_name)
    else:
        gVars = GlobalVars()
    return gVars


# Context manager per temporanee modifiche
class GlobalVarsContext:
    """
    Context manager per modifiche temporanee alle variabili globali.

    Example:
        with GlobalVarsContext(project_name="test"):
            # gVars.project_name è "test"
            ...
        # gVars torna allo stato precedente
    """

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs: Dict[str, Any] = kwargs
        self.original_values: Dict[str, Any] = {}

    def __enter__(self) -> GlobalVars:
        """Salva i valori originali e applica le modifiche."""
        for key, value in self.kwargs.items():
            if hasattr(gVars, key):
                self.original_values[key] = getattr(gVars, key)
                setattr(gVars, key, value)
        return gVars

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Ripristina i valori originali."""
        for key, value in self.original_values.items():
            setattr(gVars, key, value)


# Utility per logging
def log_info(message: str) -> None:
    """Log di info se il logger è disponibile."""
    if gVars.logger and hasattr(gVars.logger, "info"):
        gVars.logger.info(message)
    else:
        print(f"INFO: {message}")


def log_error(message: str) -> None:
    """Log di errore se il logger è disponibile."""
    if gVars.logger and hasattr(gVars.logger, "error"):
        gVars.logger.error(message)
    else:
        print(f"ERROR: {message}")


""" Esempio di utilizzo
    from .context import gVars, get_global_vars, GlobalVarsContext

    # Uso normale
    logger = gVars.logger
    temp_path = gVars.get_temp_path("subdir")

    # Context manager per test
    with GlobalVarsContext(project_name="test_app"):
        print(gVars.project_name)  # "test_app"
        # Esegui operazioni di test
        ...
    # Torna al valore originale
"""

if __name__ == "__main__":
    print(f"{gVars.project_name = }")
    print(f"{gVars.script_path = }")
    print(f"{gVars.temp_dir = }")
    print(f"{gVars.hostname = }")
    print(f"Colors: {gVars.colors.green}Green text{gVars.colors.reset}")
    print(f"{gVars.log_levels = }")
