#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 11-07-2026 17.30.19
#

import sys
import os
import socket
import platform
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from .lndict import lnDict  # per permettere di definitre il type di project_vars




from .colors import Colors

@dataclass
class GlobalVars:
    """Solo dati di configurazione - NESSUN LOGGER QUI!"""

    # Variabili d'ambiente
    project_name: str = field(default_factory=lambda: os.environ.get("LN_PROJECT_NAME", "dummy_project") )

    # Path
    temp_dir: str = field(default_factory=lambda: f"/tmp/{os.environ.get('LN_PROJECT_NAME', 'dummy_project')}" )

    # Sistema
    hostname: str = field(default_factory=lambda: socket.gethostname().split()[0])
    op_sys: str = field(default_factory=lambda: platform.system())

    # Altri dati
    version: str = "0.0.1"
    # args: Any = None
    config: dict = field(default_factory=dict)

    # Colori
    # colors: Colors = field(default_factory=Colors)

    # Project root (opzionale, per trovare file di config)
    project_root: Path|None = field(default=None, repr=False)

    project_vars: 'dict' = field(default_factory=dict)
    # yaml_env: 'lnYamlEnvironment' = field(default_factory=lnYamlEnvironment)

    def __post_init__(self) -> None:
        """Inizializza il project root."""
        if self.project_root is None:
            self.project_root = self._find_project_root()


    def set_project_name(self, name: str) -> None:
        self.project_name = name
        self.temp_dir = f"/tmp/{name}"

    def get_project_vars(self, keypath: str|None=None) -> dict:
        """Restituisce i project_vars (già lnDict)."""
        from .lndict import lnDict  # ← Import reale a runtime
        if not self.project_vars:
            self.project_vars=lnDict()
        if keypath:
            return self.project_vars[keypath]
        return self.project_vars



    def _find_project_root(self, max_depth: int = 10) -> Path:
        """Trova la root del progetto."""
        current = Path(sys.argv[0]).resolve().parent
        for _ in range(max_depth):
            if (current / 'conf').exists() or (current / 'pyproject.toml').exists() or (current / 'src').exists():
                return current
            if current.parent == current:
                break
            current = current.parent

        if not current or str(current) in ['/']:
            sys.exit(f"\t[context.py] Project root: {current} not found")
        return current

    def get_temp_path(self, subdir: str | None = None) -> Path:
        """Restituisce il path temporaneo."""
        temp_path = Path(self.temp_dir)
        if subdir:
            temp_path = temp_path / subdir
            temp_path.mkdir(parents=True, exist_ok=True)
        return temp_path

    def get_log_dir(self) -> Path:
        """Restituisce il path per i log."""
        return self.get_temp_path("logs")

    def get_conf_dir(self) -> Path:
        """Restituisce la directory conf oppure exit"""
        if self.project_root:
            conf = self.project_root / 'conf'
            if conf.exists():
                return conf
            else:
                sys.exit(f"Conf directory: {conf} not found")
        else:
            sys.exit(f"Project root: {self.project_root} not found")

    # def get_colors(self) -> Colors:
    #     return self.colors

    def to_dict(self) -> dict[str, Any]:
        """Converte l'oggetto in un dizionario."""
        result: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_") and key not in ["colors", "project_root"]:
                if isinstance(value, (Path, Colors)):
                    result[key] = str(value)
                else:
                    result[key] = value
        return result


# Istanza globale
gVars = GlobalVars()



# Funzione comoda per ottenere i project_vars
def get_project_vars(keypath: str|None=None) -> lnDict:
    """Funzione comoda per ottenere i project_vars."""
    return gVars.get_project_vars(keypath)
