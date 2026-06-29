#!/usr/bin/env python3
import os
import socket
import platform
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional, Dict

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

    # Logger - solo un riferimento, non lo creiamo qui
    my_logger: Any = None  # Verrà settato dall'esterno

    # Altri dati
    version: str = "0.0.1"
    args: Any = None
    config: Dict = field(default_factory=dict)

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

    def get_logger(self):
        return self.my_logger


# Istanza globale
gVars = GlobalVars()
