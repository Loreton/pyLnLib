#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 19-07-2026 17.25.59
#
# ruff: noqa: I001 - Import block is un-sorted or un-formatted
#
from __future__ import annotations

import os
import platform
import socket
import sys
from dataclasses import dataclass, field
from pathlib import Path
# from typing import Any  # , TYPE_CHECKING

from .colors import Colors

# if TYPE_CHECKING:
# from .logger import lnLogger  # per permettere di definitre il type di context_vars
# from .lndict import lnDict  # per permettere di definitre il type di context_vars
from .lndict import lnDict  # per permettere di definitre il type di context_vars

@dataclass
class GlobalVars_V2:
    """Solo dati di configurazione - NESSUN LOGGER QUI!"""
    def __init__(self, name: str | None = None, tmp_dir: str | None = None, version: str | None = None) -> None:
        # creo una classe dove metto tutte le variabili del mio ambiente.
        # il tutto sarà sotto self.main
        self.main: lnDict = lnDict()

        # Sistema
        self.main.hostname = socket.gethostname().split()[0]
        self.main.op_sys = platform.system()

        # Project
        self.main.name = name or os.environ.get("LN_PROJECT_NAME", "dummy_project")
        self.main.root = self._find_project_root()
        self.main.temp_dir = tmp_dir or f"/tmp/{self.main.name}"
        self.main.log_dir = self.get_log_dir()
        self.main.config_dir = self.get_config_dir()

        self.main.version = version or "0.0.1"


    # def set_project_name(self, name: str) -> None:
    #     self.main.project_name = name
    #     self.main.temp_dir = f"/tmp/{name}"
        # print(f"Project name: {self.project_name}")

    def get_context_vars(self, keypath: str | None = None) -> lnDict:
        """Restituisce i context_vars (già lnDict)."""
        # if not self.main.context_vars:
            # self.main.context_vars = lnDict()
        if keypath:
            return self.main[keypath]
        return self.main

    def _find_project_root(self, max_depth: int = 10) -> Path:
        """Trova la root del progetto."""
        # import pdb; pdb.set_trace();  # by Loreto
        main_prg = Path(sys.argv[0])
        current = main_prg.resolve().parent
        if main_prg.suffix in [".zip", ".pyz"]:
            return current

        for _ in range(max_depth):
            if ( (current / "conf").exists() or (current / "pyproject.toml").exists() or (current / "src").exists() ):
                return current
            if current.parent == current:
                break
            current = current.parent

        if not current or str(current) in ["/"]:
            sys.exit(f"\t[context.py] Project root: {current} not found")
        return current

    def get_temp_path(self, subdir: str | None = None) -> Path:
        """Restituisce il path temporaneo."""
        temp_path = Path(self.main.temp_dir)
        if subdir:
            temp_path = temp_path / subdir
            temp_path.mkdir(parents=True, exist_ok=True)
        return temp_path

    def get_log_dir(self) -> Path:
        """Restituisce il path per i log."""
        return self.get_temp_path("logs")

    def get_conf_dir_(self) -> Path:
        """Restituisce la directory conf oppure exit"""
        if self.main.root:
            conf = self.main.root / "conf"
            if conf.exists():
                return conf
            else:
                sys.exit(f"Conf directory: {conf} not found")
        else:
            sys.exit(f"Project root: {self.main.root} not found")

    # def get_conf_dir_solo_per_zed(self) -> Path:
    def get_config_dir(self) -> Path:
        """Restituisce la directory conf oppure exit"""
        if self.main.root:
            conf = self.main.root / "conf"
            if conf.exists():
                return conf
            else:  # vale per zed (non so perché self.project_root è sbagliato)
                if os.environ.get("ZED_TERM"):
                    print(f"Conf directory: {conf} not found")
                    current = self._find_project_root()
                    conf = current / "conf"
                    if conf.exists():
                        return conf
                    else:
                        sys.exit(f"Conf directory: {conf} not found")
                else:
                    sys.exit(f"Conf directory: {conf} not found")
        else:
            sys.exit(f"Project root: {self.main.root} not found")

    def to_dict(self) -> dict[str, any]:
        """Converte l'oggetto in un dizionario."""
        result: dict[str, any] = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_") and key not in ["colors", "project_root"]:
                if isinstance(value, (Path, Colors)):
                    result[key] = str(value)
                else:
                    result[key] = value
        return result


# Istanza globale
# gVars = GlobalVars()
# ctx = GlobalVars_V2()


# Funzione comoda per ottenere i context_vars
def init_context(name: str | None = None, tmp_dir: Path | str | None = None, version: str | None = None) -> lnDict:
    """Funzione comoda per ottenere i context_vars."""
    global _ctx
    _ctx = GlobalVars_V2(name, Path(tmp_dir), version)
    return _ctx.main

def get_context(keypath: str | None = None) -> lnDict:
    """Funzione comoda per ottenere i context_vars."""
    return _ctx.get_context_vars(keypath)
