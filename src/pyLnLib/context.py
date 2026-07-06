#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 06-07-2026 14.25.04
#

import sys ; sys.dont_write_bytecode=True
#!/usr/bin/env python3
import os
import socket
import platform
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional

from colors import Colors

@dataclass
class GlobalVars:
    """Solo dati di configurazione - NESSUN LOGGER QUI!"""

    # Variabili d'ambiente
    project_name: str = field(default_factory=lambda:
        os.environ.get("LN_PROJECT_NAME", "dummy_project")
    )

    # Path
    temp_dir: str = field(default_factory=lambda:
        f"/tmp/{os.environ.get('LN_PROJECT_NAME', 'dummy_project')}"
    )

    # Sistema
    hostname: str = field(default_factory=lambda: socket.gethostname().split()[0])
    op_sys: str = field(default_factory=lambda: platform.system())

    # Altri dati
    version: str = "0.0.1"
    args: Any = None
    config: dict = field(default_factory=dict)

    # Colori
    colors: Colors = field(default_factory=Colors)

    # Project root (opzionale, per trovare file di config)
    project_root: Optional[Path] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Inizializza il project root."""
        if self.project_root is None:
            self.project_root = self._find_project_root()

    def _find_project_root(self, max_depth: int = 10) -> Optional[Path]:
        """Trova la root del progetto."""
        current = Path(__file__).resolve().parent

        for _ in range(max_depth):
            if (current / 'conf').exists() or (current / 'pyproject.toml').exists():
                return current
            if current.parent == current:
                break
            current = current.parent
        return None

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

    def get_conf_dir(self) -> Optional[Path]:
        """Restituisce la directory conf."""
        if self.project_root:
            conf = self.project_root / 'conf'
            if conf.exists():
                return conf
        return None

    def get_colors(self) -> Colors:
        return self.colors

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