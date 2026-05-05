#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 03-05-2026 20.17.07
#

import sys; sys.dont_write_bytecode=True;
import os
import yaml
import zipfile
from typing import Any, List, Optional, Tuple


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
    def __init__(self, environment, search_paths: List[str] = None, recursive: bool = False):
        self.env = environment
        lnYamlLoader.env_ref = environment
        self.logger = environment.logger
        self.recursive = recursive

        ### - prepare search paths
        s_paths = search_paths or [".", "conf"]
        s_paths.extend(['.', 'conf'])
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
    def find_file(self, filename: str) -> Tuple[Optional[str], bool]:
        """
        Cerca il file prima nel filesystem esterno, poi dentro il .pyz.
        Ritorna: (path_o_nome, is_inside_zip)
        """
        # --- 1. Ricerca Esterna (Filesystem) ---
        for base_path in self.search_paths:
            if os.path.exists(base_path):
                self.logger.debug("searching file: %s/%s on Filesystem", base_path, filename)
                if self.recursive:
                    for root, _, files in os.walk(base_path):
                        if filename in files:
                            return os.path.join(root, filename), False
                else:
                    full_path = os.path.join(base_path, filename)
                    if os.path.exists(full_path):
                        return full_path, False



        # --- 2. Ricerca Interna (ZIP/PYZ) ---
        if self.isZIP:
            # Cerchiamo nei search_paths interni allo zip
            for base_path in self.search_paths:
                self.logger.debug("searching file: %s/%s inside zip: %s", base_path, filename, self.script_path)
                # Normalizziamo il path interno (niente drive letter, slash avanti)
                target_in_zip = os.path.join(base_path, filename).replace('\\', '/')
                if target_in_zip in self.zip_contents:
                    return target_in_zip, True

                # Se ricorsivo, cerchiamo corrispondenze parziali
                if self.recursive:
                    for member in self.zip_contents:
                        if member.startswith(base_path) and member.endswith(filename):
                            return member, True

        return None, False

    #################################
    # -
    #################################
    def _get_keypath(self, data: Any, keypath: str) -> Any:
        try:
            for key in keypath.split('.'):
                if isinstance(data, dict):
                    data = data.get(key)
                else:
                    return None
            return data
        except Exception:
            return None

    #################################
    # -
    #################################
    def load(self, filename_with_pointer: str) -> Any:
        if '#' in filename_with_pointer:
            target_file, keypath = filename_with_pointer.split('#', 1)
        else:
            target_file, keypath = filename_with_pointer, None

        # Ricerca file (ritorna path e flag zip)
        filepath, is_in_zip = self.find_file(target_file)

        if filepath:
            self.logger.info("file: %s FOUND (in_zip: %s)", filepath, is_in_zip)
        else:
            self.logger.error("File '%s' non trovato (Esterno o PYZ)", target_file)
            return {}

        ### - lettura del contenuto
        try:
            if is_in_zip:
                # Lettura da ZIP
                with zipfile.ZipFile(self.script_path, 'r') as z:
                    with z.open(filepath) as f:
                        content = f.read().decode('utf-8')
                self.logger.trace("Caricato dallo ZIP: %s", filepath)
            else:
                # Lettura da Filesystem
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.logger.trace("Caricato dal Filesystem: %s", filepath)

            content = os.path.expandvars(content)
            data = yaml.load(content, Loader=lnYamlLoader)

            return self._get_keypath(data, keypath) if keypath else data

        except Exception as e:
            self.logger.error("Errore nel caricamento di %s: %s", target_file, str(e))
            return {}


#################################
# -
#################################
class lnYamlEnvironment:
    def __init__(self, logger, paths: list=["conf"], recursive=True):
        self.logger = logger

        # Inizializziamo l'engine con i parametri richiesti
        self.yaml_engine = YamlEngine(self, search_paths=paths, recursive=recursive)

# Test
if __name__ == "__main__":
    # --- Logger Personalizzato ---
    class DummyLogger:
        def critical(self, msg, *args): print(f"CRITICAL: {msg % args if args else msg}")
        def error(self, msg, *args):    print(f"ERROR:    {msg % args if args else msg}")
        def warning(self, msg, *args):  print(f"WARNING:  {msg % args if args else msg}")
        def info(self, msg, *args):     print(f"INFO:     {msg % args if args else msg}")
        def debug(self, msg, *args):    print(f"DEBUG:    {msg % args if args else msg}")
        def function(self, msg, *args): print(f"FUNCTION: {msg % args if args else msg}")
        def notify(self, msg, *args):   print(f"NOTIFY:   {msg % args if args else msg}")
        def trace(self, msg, *args):    print(f"TRACE:    {msg % args if args else msg}")


    # Esempio di chiamata
    env = lnYamlEnvironment(logger=DummyLogger, paths=["conf", "conf/profiles"], recursive=False)
    config = env.yaml_engine.load("@lnSync_config.yaml#myDirs")

    print(config)