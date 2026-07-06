#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 06-07-2026 14.16.41
#

import sys ; sys.dont_write_bytecode=True
import os
import socket
import platform
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any


from typing import TYPE_CHECKING  # TYPE_CHECKING - La soluzione per import circolari

from .logger import lnLogger, testLogger
from .colors import Colors

if TYPE_CHECKING:
    from .lndict import lnDict

def _default_lnDict():
    """Factory function per creare un lnDict vuoto."""
    from .lndict import lnDict  # ← Import reale a runtime
    return lnDict()


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
    config: dict = field(default_factory=dict)
    project_vars: 'lnDict' = field(default_factory=_default_lnDict)

    # Colori
    colors: Colors = field(default_factory=Colors)
    config_search_paths: list[str] = field(default_factory=list)
    project_root: Path|None = field(default=None, repr=False)

    # Logger - inizializzato in __post_init__
    my_logger: Any = field(default=None, repr=False)

    # ==========================================================
    # = Post-init
    # ==========================================================
    def __post_init__(self) -> None:
        """Inizializza il logger dopo la creazione dell'istanza."""
        self._init_logger()


        """Inizializza il project root."""
        if self.project_root is None:
            self.project_root = self._find_project_root()

        """Inizializza il config_search_paths."""
        self.config_search_paths.append('conf')  # default conf dir
        if self.project_root:
            if (self.project_root / 'conf').exists():
                self.config_search_paths.append(str(self.project_root / 'conf'))


    # ==========================================================
    # = find project root
    # ==========================================================
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



    # ==========================================================
    # = initialize logger
    # ==========================================================
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

    def get_project_vars(self) -> 'lnDict':
        """Restituisce i project_vars (già lnDict)."""
        # from .lndict import lnDict  # ← Import reale a runtime
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
def get_project_vars() -> 'lnDict':
    """Funzione comoda per ottenere i project_vars."""
    return gVars.get_project_vars()
