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
from dataclasses import dataclass
from pathlib import Path

# from typing import Any  # , TYPE_CHECKING

from .colors import Colors
"""
    messo solo per permettere di fare un ctx.get_logger()
    potrebbessere rimosso se dovesse dare problemi
    perché ogni modulo può benissimo fare l'import di: from pyLnLib.logger import get_logger
"""
from .logger.ln_colored_logger import get_logger, lnColoredLogger


from .lndict import lnDict  # per permettere di definitre il type di context_vars

@dataclass
class lnContext:
    """Solo dati di configurazione - NESSUN LOGGER QUI!"""
    # def __init__(self, name: str | None = None, tmp_dir: str | None = None, version: str | None = None) -> None:
    def __init__(self) -> None:
        # creo una classe dove metto tutte le variabili del mio ambiente.
        # il tutto sarà sotto self.main
        # self.main: lnDict = lnDict()

        # Sistema
        self.hostname = socket.gethostname().split()[0]
        self.op_sys = platform.system()

        self.version = "0.0.1"

    def initialize(self, project_name: str,  version: str, *,
                        project_root: Path | None = None,
                        project_temp_dir: str | None = None,
                        project_log_dir: str | None = None,
                        project_config_dir: str | None = None,
                        ) -> None:
        self.project_name = project_name
        self.version = version
        self.config: lnDict = lnDict()
        self.input_args: lnDict = lnDict()

        self.project_root = Path(project_root) if project_root else self._find_project_root()
        self.project_temp_dir = Path(project_temp_dir) if project_temp_dir else self._set_temp_path(req_top_dir="/tmp")
        self.project_log_dir = Path(project_log_dir) if project_log_dir else self._set_log_dir(req_top_dir=self.project_temp_dir)
        self.project_config_dir = Path(project_config_dir) if project_config_dir else self._set_config_dir(top_dir=self.project_root)



    def get_logger(self) -> lnColoredLogger:
        """Restituisce il logger."""
        return get_logger()

    def get_context_vars(self, keypath: str) -> lnDict:
        """Restituisce i context_vars (già lnDict)."""
        _my = lnDict(self.to_dict())
        if keypath in _my:
            return _my[keypath]
        return lnDict()

    def _find_project_root(self, max_depth: int = 10) -> Path:
        """Trova la root del progetto."""
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
        # self.project_root = current
        return current

    def _set_temp_path(self, req_top_dir: str|Path) -> Path:
        """Restituisce il path temporaneo."""
        top_dir = Path(req_top_dir).resolve()

        if top_dir.exists():
            temp_path = top_dir / self.project_name
            temp_path.mkdir(parents=True, exist_ok=True)
        else:
            sys.exit(f"[{__name__}]: top_dir directory: {req_top_dir} not found")
        return temp_path

    def _set_log_dir(self, req_top_dir: str | Path) -> Path:
        """Restituisce il path per i log."""
        top_dir = Path(req_top_dir).resolve()
        if top_dir.exists():
            log_dir = top_dir / "logs"
        else:
            log_dir = self.project_temp_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        # self.project_log_dir = log_dir
        return log_dir

    def _set_config_dir(self, top_dir: str|Path) -> Path:
        """Restituisce la directory conf oppure exit"""
        top_dir = Path(top_dir).resolve()
        if top_dir.exists():
            conf = top_dir / "conf"
        else:
            conf = Path(self.project_root) / "conf"
        if conf.exists():
            return conf
        else:
            sys.exit(f"[{__name__}]: Conf directory: {conf} not found")

    def to_dict(self) -> dict[str, any]:
        """Converte l'oggetto in un dizionario."""
        result: dict[str, any] = {}
        for key, value in self.__dict__.items():
            # if not key.startswith("_") and key not in ["colors", "project_root"]:
            if not key.startswith("_") and key not in ["colors"]:
                if isinstance(value, (Path, Colors)):
                    result[key] = str(value)
                else:
                    result[key] = value
        return result




# Istanza globale
ctx = lnContext()


# Funzione comoda per ottenere i context_vars
# def init_context(name: str | None = None, tmp_dir: str | None = None, version: str | None = None) -> lnDict:
#     """Funzione comoda per ottenere i context_vars."""
#     global ctx
#     ctx = GlobalVars(name, tmp_dir=(tmp_dir), version=version)
#     return ctx.main


# def get_context_prev(keypath: str | None = None) -> lnDict:
#     """Funzione comoda per ottenere i context_vars."""
#     return ctx.get_context_vars(keypath)


# def get_context(keypath: str | None = None) -> lnDict:
#     """Funzione comoda per ottenere i context_vars."""
#     # return ctx.get_context_vars(keypath)
#     return ctx
