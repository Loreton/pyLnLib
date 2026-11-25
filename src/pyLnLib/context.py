#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
#
# ruff: noqa: I001 - Import block is un-sorted or un-formatted
#
from __future__ import annotations

import inspect
import platform
import socket
import sys
from dataclasses import dataclass
from pathlib import Path

# from src.pyLnLib.git.pyproject_class import PyProjectManager

# from pyLnLib.epub.epub_manager import EpubProcessor

# from build.lib.pyLnLib.epub import epub_manager

# from typing import Any  # , TYPE_CHECKING

# from .colors import Colors
# """
#     messo solo per permettere di fare un ctx.get_logger()
#     potrebbessere rimosso se dovesse dare problemi
#     perché ogni modulo può benissimo fare l'import di: from pyLnLib.logger import get_logger
# """
# from .logger.ln_colored_logger import get_logger, lnColoredLogger


from .lndict import lnDict  # per permettere di definitre il type di context_vars
from .system.signal_handler import start_signal_handler


@dataclass(frozen=False)
class lnContext:
    """Solo dati di configurazione - NESSUN LOGGER QUI se non quello passato all'initializzazione!"""
    # def __init__(self, name: str|None = None, tmp_dir: str|None = None, version: str|None = None) -> None:
    def __init__(self) -> None:
        # creo una classe dove metto tutte le variabili del mio ambiente.
        # il tutto sarà sotto self.main
        # self.main: lnDict = lnDict()

        # Sistema
        self.hostname = socket.gethostname().split()[0]
        self.op_sys = platform.system()
        self.project_vars: lnDict = lnDict()

        self.version = "0.0.1"

    def initialize(self, project_name: str,
                        *,
                        version: str,
                        logger: object,
                        project_root: Path|None = None,
                        project_temp_dir: str|None = None,
                        project_log_dir: str|None = None,
                        project_config_dir: str|None = None,
                        ) -> None:

        self.project_name = project_name
        self.project_root = Path(project_root) if project_root else self._find_project_root()
        self.project_temp_dir = Path(project_temp_dir) if project_temp_dir else self._set_temp_path(req_top_dir="/tmp")
        self.project_log_dir = Path(project_log_dir) if project_log_dir else self._set_log_dir(req_top_dir=self.project_temp_dir)
        self.project_config_dir = Path(project_config_dir).resolve() if project_config_dir else self._set_config_dir(top_dir=self.project_root)
        self.logger = logger


        # Variabili del progetto
        self.project_vars.update( {
                "root_dir": self.project_root,
                "temp_dir": self.project_temp_dir,
                "log_dir": self.project_log_dir,
                "config_dir": self.project_config_dir,
                "project_name": project_name,
                "version": version,
                "config": lnDict(),
                "args": lnDict(), # input args
                "logger": logger,
            }
        )

    @property
    def temp_dir(self) -> Path:
        return self.project_temp_dir

    @property
    def log_dir(self) -> Path:
        return self.project_log_dir

    @property
    def config_dir(self) -> Path:
        return self.project_config_dir

    @property
    def prj_root_dir(self) -> Path:
        return self.project_root




    # ======================================================================
    def get_function_name(self) -> str:
        """Restituisce i context_vars (già lnDict)."""
        return inspect.currentframe().f_back.f_code.co_name





    # ======================================================================
    def get_context_vars(self, keypath: str) -> lnDict:
        """Restituisce i context_vars (già lnDict)."""
        _my = lnDict(self.to_dict())
        if keypath in _my:
            return _my[keypath]
        return lnDict()




    # ======================================================================
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



    # ======================================================================
    def _set_temp_path(self, req_top_dir: str|Path) -> Path:
        """Restituisce il path temporaneo."""
        top_dir = Path(req_top_dir).resolve()

        if top_dir.exists():
            temp_path = top_dir / self.project_name
            temp_path.mkdir(parents=True, exist_ok=True)
        else:
            sys.exit(f"[{__name__}]: top_dir directory: {req_top_dir} not found")
        return temp_path



    # ======================================================================
    def _set_log_dir(self, req_top_dir: str|Path) -> Path:
        """Restituisce il path per i log."""
        top_dir = Path(req_top_dir).resolve()
        if top_dir.exists():
            log_dir = top_dir / "logs"
        else:
            log_dir = self.project_temp_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        # self.project_log_dir = log_dir
        return log_dir




    # ======================================================================
    def _set_config_dir(self, top_dir: str|Path) -> Path:
        """Restituisce la directory conf oppure la root del progetto"""
        top_dir = Path(top_dir).resolve()

        if top_dir.exists():
            conf = top_dir / "conf"
        else:
            conf = Path(self.project_root) / "conf"

        if conf.exists():
            return conf
        else:
            return top_dir

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



    ###################################################################
    # Read Configuration
    ###################################################################
    def read_yaml_configuration(self,
                                config_file_name: str,
                                # logger: object,
                                bootstrap_key: str|None=None,
                                log_action: int=0,
                            ) -> lnDict:
        """
             read application configuration file
             Args:
                 configuration file name
             return:
                 configuration (lnDict)
        """
        from .yaml.yaml_loader import get_yamlEngine

        # --- class instance
        myYaml=get_yamlEngine(logger=self.logger)

        # --- read bootstrap variables
        # if bootstrap_key:
        myYaml.bootstrap(config_file_name, main_key=bootstrap_key, log_action=log_action)

        # --- read configuration data
        config_data=myYaml.load(config_file_name)

        # --- remove bootstrap section
        if bootstrap_key and isinstance(config_data, dict):
            _bootstrat=config_data.pop(bootstrap_key)

        # --- remove bootstrap section
        myYaml.save_yaml(filepath=self.temp_dir / Path(config_file_name).stem, indent=4, log_action=log_action)

        return lnDict(config_data)



# Istanza globale
ctx = lnContext()
pVars = ctx.project_vars
project_vars = ctx.project_vars
