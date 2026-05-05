#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 03-05-2026 17.16.55
#
import sys; sys.dont_write_bytecode=True
from dataclasses import dataclass
from datetime import datetime
import socket
import platform
import yaml
import zipfile
from pathlib import Path

# from .yaml_loader_class import YamlEngine, AppEnvironment

@dataclass(frozen=True) # "frozen" rende i colori non modificabili per errore
class Colors:
    red: str    = '\033[31m'; redH: str    = '\033[91m'
    green: str  = '\033[32m'; greenH: str  = '\033[92m'
    yellow: str = '\033[33m'; yellowH: str = '\033[93m'
    blue: str   = '\033[34m'; blueH: str   = '\033[94m'
    purple: str = '\033[35m'; purpleH: str = '\033[95m'
    magenta: str = '\033[35m'; magentaH: str = '\033[95m'
    cyan: str   = '\033[36m'; cyanH: str   = '\033[96m'
    white: str  = '\033[37m'; whiteH: str  = '\033[97m'
    reset: str  = '\033[0m'


# @dataclass
class GlobalVars:
    # project_name: str = "git_commit"
    script_path = Path(__file__).resolve().parent
    args: any = None
    fExecute: bool = False

    hostname: str = socket.gethostname().split()[0]
    op_sys: str   = platform.system()
    now_str: str  = datetime.now().strftime("%d-%m-%Y_%H:%M")

    colors: Colors = Colors()
    logger: any = None
    isZIP = zipfile.is_zipfile(sys.argv[0]) ### - siamo in un .zip o .pyz


    # Inizializziamo il motore YAML
    # my_yaml = YamlEngine(self)

    # def load_yaml(self, path: str):
    #     """ Metodo scorciatoia che delega al motore YAML """
    #     return self.yaml.load(path)


    # def __post_init__(self):
    #     # Inizializziamo il motore YAML
    #     # from .yaml_loader_class import YamlEngine
    #     self.yaml = YamlEngine(self)

# 👉 ISTANZA VERA
gVars = GlobalVars()



# env = AppEnvironment(logger=gVars.logger, paths=["conf", "conf/profiles"], recursive=False)
# gVars.yamlEngine = env.yaml_engine


