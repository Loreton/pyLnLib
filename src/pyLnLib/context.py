#!/usr/bin/env python3
import sys ; sys.dont_write_bytecode=True
import os
import socket
import platform
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any



from pyLnLib.logger import lnLogger, testLogger
# from pyLnLib.lndict import lnDict


@dataclass(frozen=True)
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
    bold: str = "\033[1m"
    underline: str = "\033[4m"
    blink: str = "\033[5m"
    reverse: str = "\033[7m"
    hidden: str = "\033[8m"
    bg_red: str = "\033[41m"
    bg_green: str = "\033[42m"
    bg_yellow: str = "\033[43m"
    bg_blue: str = "\033[44m"
    bg_magenta: str = "\033[45m"
    bg_cyan: str = "\033[46m"
    bg_white: str = "\033[47m"




@dataclass
class GlobalVars:
    """Solo dati, niente logica di inizializzazione pesante."""

    # Variabili d'ambiente
    project_name: str = field(default_factory=lambda: os.environ.get("LN_PROJECT_NAME", "dummy_project"))

    # Path
    temp_dir: str = field(default_factory=lambda: f"/tmp/{os.environ.get('LN_PROJECT_NAME', 'dummy_project')}")

    # Sistema
    hostname: str = field(default_factory=lambda: socket.gethostname().split()[0])
    op_sys: str = field(default_factory=lambda: platform.system())

    # Altri dati
    version: str = "0.0.1"
    args: Any = None
    config: dict = field(default_factory=dict)
    project_vars: dict = field(default_factory=dict)

    # Colori
    colors: Colors = field(default_factory=Colors)
    config_search_paths: list[str] = field(default_factory=list)
    project_root: Path|None = field(default=None, repr=False)

    # Logger - inizializzato in __post_init__
    my_logger: Any = field(default=None, repr=False)

    def __post_init__(self) -> None:
        # from .lndict import lnDict
        """Inizializza il logger dopo la creazione dell'istanza."""
        # self.project_vars=lnDict()
        # Crea il logger
        self._init_logger()

        """Inizializza il project root."""
        if self.project_root is None:
            self.project_root = self._find_project_root()

        """Inizializza il config_search_paths."""
        self.config_search_paths.append('conf')  # default conf dir
        if self.project_root:
            if (self.project_root / 'conf').exists():
                self.config_search_paths.append(str(self.project_root / 'conf'))


    def _find_project_root(self, max_depth: int = 10) -> Path | None:
        """Trova la root del progetto."""
        # Usa il percorso del modulo corrente
        # current = Path(__file__).resolve().parent
        # Usa il percorso del modulo chiamante
        current = Path(sys.argv[0]).parent
        for _ in range(max_depth):
            # Cerca conf/ o pyproject.toml
            if (current / 'conf').exists() or (current / 'pyproject.toml').exists():
                return current
            if current.parent == current:
                break
            current = current.parent
        return None



    def _init_logger(self) -> None:
        """Inizializza il logger con i valori di default."""
        # Ottieni la directory dei log
        log_dir = self.get_log_dir()
        log_dir.mkdir(parents=True, exist_ok=True)

        # Crea il logger
        self.my_logger = lnLogger(
            name=self.project_name,
            console_logger_level="INFO",
            file_logger_level="DEBUG",
            logging_dir=str(log_dir),
            threads=False,
        )

        print("*" * 20)
        print("logger inizializzato")
        print("*" * 20)

        # Configura il logger
        self.my_logger.setNameLength(dynamic=True, length=0)

    def get_logger(self, test: bool = False) -> Any:
        """Restituisce il logger."""
        if self.my_logger is None:
            self._init_logger()
        if test:
            testLogger(self.my_logger)
        return self.my_logger

    def set_logger(self, logger: Any) -> None:
        """Imposta un logger esterno."""
        self.my_logger = logger

    def get_log_dir(self) -> Path:
        """Restituisce il path per i log."""
        return self.get_temp_path("logs")

    def get_temp_path(self, subdir: str | None = None) -> Path:
        """Restituisce il path temporaneo."""
        temp_path = Path(self.temp_dir)
        if subdir:
            temp_path = temp_path / subdir
            temp_path.mkdir(parents=True, exist_ok=True)
        return temp_path

    def get_colors(self) -> Colors:
        return self.colors

    # def init_project_vars(self) -> dict[str, Any]:
    #     from pyLnLib.lndict import lnDict
    #     self.project_vars = lnDict()
    #     return self.project_vars

    def get_project_vars(self, init: bool=False) -> dict[str, Any]:
        from .lndict import lnDict
        if init and not self.project_vars:
            self.project_vars = lnDict()
        return self.project_vars

    def get_config_search_paths(self) -> list[str]:
        return self.config_search_paths

    def to_dict(self) -> dict[str, Any]:
        """Converte l'oggetto in un dizionario."""
        result: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_") and key != "my_logger":
                if isinstance(value, (Path, Colors)):
                    result[key] = str(value)
                else:
                    result[key] = value
        return result


# Istanza globale
gVars = GlobalVars()

# Funzione comoda per ottenere il logger
def get_logger(test: bool=False) -> Any:
    """Funzione comoda per ottenere il logger."""
    return gVars.get_logger(test=test)

# Funzione comoda per ottenere i Colors
def get_colors() -> Colors:
    """Funzione comoda per ottenere i Colors."""
    return gVars.get_colors()

# Funzione comoda per ottenere i project_vars
def get_project_vars(init: bool=False) -> dict[str, Any]:
    """Funzione comoda per ottenere i project_vars."""
    return gVars.get_project_vars(init=init)
