#!/usr/bin/env python3
# ruff: noqa: I001 - Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
# updated by ...: Loreto Notarantonio
# Date .........: 11-07-2026 18.12.21
#
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import os
import yaml
import zipfile
from pathlib import Path

from .file_utils import searchFileOnFS
from .zip_file_utils import searchFileInZip
from ..context import ctx
from ..logger import get_logger

logger = get_logger()
# ctx = get_context()

#################################
# --- Riferimento globale all'engine ---
#################################
_yaml_engine: 'YamlEngine' | None = None

def set_yaml_engine(engine: YamlEngine) -> None:
    """Imposta il riferimento globale all'engine YAML."""
    global _yaml_engine
    _yaml_engine = engine

def get_yaml_engine_instance() -> YamlEngine | None:
    """Recupera il riferimento globale all'engine YAML."""
    return _yaml_engine

#################################
# --- Loader Personalizzato ---
#################################
class lnYamlLoader(yaml.FullLoader):
    """Loader che mantiene un riferimento all'oggetto di ambiente per i tag custom."""
    # Non serve più env_ref, usiamo il riferimento globale
    pass

#################################
# --- Costruttori dei Tag ---
#################################
def yaml_include_constructor(loader, node):
    """Costruttore per il tag !include."""
    engine = get_yaml_engine_instance()
    if engine is None:
        raise ValueError("YAML engine not initialized. Call get_yaml_engine() first.")
    return engine.load(node.value)

def yaml_constructor_include_merge(loader, node):
    """Costruttore per il tag !include_merge."""
    engine = get_yaml_engine_instance()
    if engine is None:
        raise ValueError("YAML engine not initialized. Call get_yaml_engine() first.")

    items = loader.construct_sequence(node)
    final_dict = {}
    for filename in items:
        res = engine.load(filename)
        if isinstance(res, dict):
            final_dict.update(res)
    return final_dict

def yaml_constructor_list_merge(loader, node):
    """Costruttore per il tag !list_merge."""
    engine = get_yaml_engine_instance()
    if engine is None:
        raise ValueError("YAML engine not initialized. Call get_yaml_engine() first.")

    items = loader.construct_sequence(node)
    final_list = []
    for filename in items:
        res = engine.load(filename)
        if isinstance(res, list):
            final_list.extend(res)
        elif res is not None:
            final_list.append(res)
    return final_list

def join_path(loader, node):
    """Costruttore per il tag !join_path."""
    return os.path.join(*loader.construct_sequence(node))

def join_str(loader, node):
    """Costruttore per il tag !join_str."""
    return ''.join([str(i) for i in loader.construct_sequence(node)])

# ----------------------
# Registrazione Tag
# ----------------------
lnYamlLoader.add_constructor('!include', yaml_include_constructor)
lnYamlLoader.add_constructor('!include_merge', yaml_constructor_include_merge)
lnYamlLoader.add_constructor('!list_merge', yaml_constructor_list_merge)
lnYamlLoader.add_constructor('!join_path', join_path)
lnYamlLoader.add_constructor('!join_str', join_str)

#################################
# --- YamlEngine Class ---
#################################
class YamlEngine:
    #################################
    # - Costruttore
    #################################
    def __init__(self, search_paths: list[Path|str] | None = None, recursive: bool = False):
        # self.logger = get_logger()
        self.logger = logger
        self.recursive = recursive

        # Prepara i percorsi di ricerca
        if search_paths is None:
            try:
                search_paths = [ctx.get_config_dir()]
            except (ImportError, AttributeError):
                search_paths = ["conf"]

        # Rimuovi duplicati mantenendo l'ordine
        self.search_paths = list(dict.fromkeys(search_paths))

        # Identifica se stiamo girando da un .pyz o .zip
        self.script_path = sys.argv[0]
        self.isZIP = zipfile.is_zipfile(self.script_path)
        if self.isZIP:
            self.zipFname = self.script_path
            with zipfile.ZipFile(self.zipFname, 'r') as z:
                self.zip_contents = z.namelist()

        # Imposta il riferimento globale a questo engine
        set_yaml_engine(self)

    #################################
    # - find_file
    #################################
    def find_file(self, filename: str) -> str | None:
        """Cerca un file nei percorsi di ricerca."""
        result = searchFileOnFS(
            filename=filename,
            search_paths=self.search_paths,
            recursive=self.recursive
        )

        if not result.filepath:
            if zipfile.is_zipfile(sys.argv[0]):
                result = searchFileInZip(
                    filename=filename,
                    archive_file=sys.argv[0],
                    search_paths=self.search_paths,
                    recursive=self.recursive
                )
                if not result.filepath:
                    self.logger.error(
                        "filename: %s not found on filesystem neither in zipfile",
                        filename,
                        exit=True
                    )
            else:
                self.logger.error(
                    "filename: %s not found on fileSystem",
                    filename,
                    exit=True
                )

        return result.content

    #################################
    # - _get_keypath
    #################################
    def _get_keypath(self, data: dict[str, any], keypath: str) -> any:
        """Recupera un valore da un dizionario usando un percorso di chiavi."""
        current_data = data
        try:
            for key in keypath.split('.'):
                if isinstance(current_data, dict):
                    current_data = current_data.get(key)
                    if current_data is None:
                        break
                else:
                    break
        except Exception as e:
            self.logger.error(f"Error accessing keypath '{keypath}': {e}")

        return current_data

    #################################
    # - load
    #################################
    def load(self, filename_with_pointer: str) -> any:
        """
        Carica un file YAML con supporto per:
        - !include, !include_merge, !list_merge
        - !join_path, !join_str
        - keypath con # (es: 'file.yaml#key.subkey')
        """
        # Estrai keypath se presente
        if '#' in filename_with_pointer:
            target_file, keypath = filename_with_pointer.split('#', 1)
        else:
            target_file, keypath = filename_with_pointer, None

        self.logger.info("trying to load file: %s", target_file)

        # Cerca il file
        content: str | None = self.find_file(target_file)
        if not content:
            self.logger.error(
                "filename: %s is empty or not found",
                target_file,
                show_stack=True,
                exit=True
            )

        # Espandi variabili d'ambiente
        content = os.path.expandvars(str(content))

        # Carica il contenuto YAML
        data = yaml.load(content, Loader=lnYamlLoader)

        # Estrai keypath se specificato
        if keypath:
            file_data = self._get_keypath(data, keypath)
            if file_data is None:
                self.logger.error(
                    "Key '%s' not found in file: %s",
                    keypath,
                    target_file
                )
                file_data = data  # Fallback al dato completo
        else:
            file_data = data

        return file_data

#################################
# --- Funzione Factory ---
#################################
def get_yaml_engine( search_paths: list[Path|str] | None = None, recursive: bool = True ) -> YamlEngine:
    """
    Crea e restituisce un'istanza di YamlEngine.

    Args:
        search_paths: Lista di percorsi dove cercare i file YAML
        recursive: Se cercare ricorsivamente nelle sottodirectory

    Returns:
        Un'istanza configurata di YamlEngine
    """
    # Se non ci sono percorsi, usa il default
    if search_paths is None:
        try:
            search_paths = [ctx.get_config_dir()]
        except (ImportError, AttributeError):
            search_paths = ["conf"]

    # Crea l'engine (il costruttore imposta automaticamente il riferimento globale)
    engine = YamlEngine(search_paths=search_paths, recursive=recursive)

    return engine
