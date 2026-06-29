#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 11-05-2026 10.47.44
#

import sys; sys.dont_write_bytecode=True

import os
import yaml
import zipfile
from typing import Any


from .file_utils_new     import searchFileOnFS
from .zip_file_utils import searchFileInZip
from ..context import gVars as ctx
# C=ctx.colors
# logger=ctx.get_logger()

#################################
# --- Loader Personalizzato ---
#################################
class lnYamlLoader(yaml.FullLoader):
    """Loader che mantiene un riferimento all'oggetto di ambiente per i tag custom."""
    env_ref = None

#################################
# --- Costruttori dei Tag ---
#################################
def yaml_include_constructor(loader, node):
    # Usa il riferimento all'ambiente per ricaricare un file
    return loader.env_ref.yaml_engine.load(node.value)

#################################
# --- Costruttori dei Tag ---
#################################
def yaml_constructor_include_merge(loader, node):
    items = loader.construct_sequence(node)
    final_dict = {}
    for filename in items:
        res = loader.env_ref.yaml_engine.load(filename)
        if isinstance(res, dict): final_dict.update(res)
    return final_dict

#################################
# --- Costruttori dei Tag ---
#################################
def yaml_constructor_list_merge(loader, node):
    items = loader.construct_sequence(node)
    final_list = []
    for filename in items:
        res = loader.env_ref.yaml_engine.load(filename)
        if isinstance(res, list): final_list.extend(res)
        elif res is not None: final_list.append(res)
    return final_list

#################################
# --- Costruttori dei Tag ---
#################################
def join_path(loader, node):
    return os.path.join(*loader.construct_sequence(node))

#################################
# --- Costruttori dei Tag ---
#################################
def join_str(loader, node):
    return ''.join([str(i) for i in loader.construct_sequence(node)])

# ----------------------
# Registrazione Tag
# ----------------------
lnYamlLoader.add_constructor('!include', yaml_include_constructor)
lnYamlLoader.add_constructor('!include_merge', yaml_constructor_include_merge)
lnYamlLoader.add_constructor('!list_merge', yaml_constructor_list_merge)
lnYamlLoader.add_constructor('!join_path', join_path)
lnYamlLoader.add_constructor('!join_str', join_str)



class YamlEngine:
    #################################
    # -
    #################################
    def __init__(self, environment, search_paths: list[str] = [], recursive: bool = False):
        self.env = environment
        lnYamlLoader.env_ref = environment
        # self.logger = environment.logger
        self.logger = ctx.get_logger()
        self.recursive = recursive

        ### - prepare search paths
        s_paths = search_paths or ["conf"] ### non mettere '.'
        self.search_paths = list(dict.fromkeys(s_paths))


        # Identifichiamo se stiamo girando da un .pyz o .zip
        # self.main_zip_path = sys.argv[0]

        self.script_path = sys.argv[0]
        self.isZIP = zipfile.is_zipfile(self.script_path)
        if self.isZIP:
            self.zipFname=self.script_path
            with zipfile.ZipFile(self.zipFname, 'r') as z:
                self.zip_contents = z.namelist()







    #################################
    # -
    #################################
    # def find_file(self, filename: str) -> tuple[str, bool]:
    def find_file(self, filename: str) -> str|None:
        result = searchFileOnFS(filename=filename, search_paths=self.search_paths, recursive=self.recursive)
        if not result.filepath:
            if zipfile.is_zipfile(sys.argv[0]):
                result = searchFileInZip(filename=filename, archive_file=sys.argv[0], search_paths=self.search_paths, recursive=self.recursive)
                if not result.filepath:
                    self.logger.error("filename: %s not found on filesysten neither in zipfile", filename, exit=True)
            else:
                self.logger.error("filename: %s not found on fileSystem", filename, exit=True)

        return result.content


    #################################
    # -
    #################################
    # def _get_keypath(self, data: Any, keypath: str) -> Any:
    #     try:
    #         for key in keypath.split('.'):
    #             if isinstance(data, dict):
    #                 data = data.get(key)
    #             else:
    #     return result.content


    #################################
    # -
    #################################
    def _get_keypath(self, data: dict, keypath: str) -> Any:
        try:
            for key in keypath.split('.'):
                if isinstance(data, dict):
                    data = data.get(key)
                    break

        except Exception as e:
            self.logger.error(str(e))

        return data

    #################################
    # -
    #################################
    def load(self, filename_with_pointer: str) -> Any:
        if '#' in filename_with_pointer:
            target_file, keypath = filename_with_pointer.split('#', 1)
        else:
            target_file, keypath = filename_with_pointer, None

        content = self.find_file(target_file)
        content = os.path.expandvars(content)
        data = yaml.load(content, Loader=lnYamlLoader)

        # file_data = self._get_keypath(data, keypath) if keypath else data
        if keypath:
            file_data = self._get_keypath(data, keypath)
            if file_data is None:
                self.logger.error("Key %s not found in file: %s:", keypath, target_file)
                self.logger.exception("Key %s not found in file: %s:", keypath, target_file)
                # raise ValueError(f"Key not found: {keypath}")
                # sys.exit(1)
        else:
            file_data = data

        return file_data



#################################
# -
#################################
class lnYamlEnvironment:
    def __init__(self, search_paths: list=["conf"], recursive=True):
        # self.logger = logger

        # Inizializziamo l'engine con i parametri richiesti
        self.yaml_engine = YamlEngine(self, search_paths=search_paths, recursive=recursive)


# Test
if __name__ == "__main__":
    ...
