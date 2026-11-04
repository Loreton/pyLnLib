#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 02-05-2026 18.04.29
#
import os
import yaml
import zipfile
from typing import Any, List, Optional



# --- Loader Personalizzato ---
class lnYamlLoader(yaml.FullLoader):
    """Loader che mantiene un riferimento all'oggetto di ambiente per i tag custom."""
    env_ref = None

# --- Costruttori dei Tag ---
def yaml_include_constructor(loader, node):
    # Usa il riferimento all'ambiente per ricaricare un file
    return loader.env_ref.yaml_engine.load(node.value)

def yaml_constructor_include_merge(loader, node):
    items = loader.construct_sequence(node)
    final_dict = {}
    for filename in items:
        res = loader.env_ref.yaml_engine.load(filename)
        if isinstance(res, dict): final_dict.update(res)
    return final_dict

def yaml_constructor_list_merge(loader, node):
    items = loader.construct_sequence(node)
    final_list = []
    for filename in items:
        res = loader.env_ref.yaml_engine.load(filename)
        if isinstance(res, list): final_list.extend(res)
        elif res is not None: final_list.append(res)
    return final_list

def join_path(loader, node):
    return os.path.join(*loader.construct_sequence(node))

def join_str(loader, node):
    return ''.join([str(i) for i in loader.construct_sequence(node)])

# Registrazione Tag
lnYamlLoader.add_constructor('!include', yaml_include_constructor)
lnYamlLoader.add_constructor('!include_merge', yaml_constructor_include_merge)
lnYamlLoader.add_constructor('!list_merge', yaml_constructor_list_merge)
lnYamlLoader.add_constructor('!join_path', join_path)
lnYamlLoader.add_constructor('!join_str', join_str)

# --- Engine Principale ---
import os
import yaml
from typing import Any, Optional, List

# --- [Il codice precedente dei costruttori e DummyLogger rimane invariato] ---

class YamlEngine:
    def __init__(self, environment, search_paths: List[str] = None, recursive: bool = False):
        """
        :param environment: L'oggetto di contesto (lnYamlEnvironment)
        :param search_paths: Lista di directory dove cercare i file (es. ['conf', 'settings/user'])
        :param recursive: Se True, cerca anche nelle sottocartelle dei search_paths
        """
        self.env = environment
        lnYamlLoader.env_ref = environment
        self.logger = environment.logger

        # Default alla cartella corrente se non specificato
        self.search_paths = search_paths or ["."]
        self.recursive = recursive

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

    def find_file(self, filename: str) -> Optional[str]:
        """Cerca il file nei path configurati, eventualmente in modo ricorsivo."""
        for base_path in self.search_paths:
            if not os.path.exists(base_path):
                self.logger.warning("Il percorso di ricerca '%s' non esiste.", base_path)
                continue

            if self.recursive:
                # Scansione ricorsiva delle sottodirectory
                for root, dirs, files in os.walk(base_path):
                    if filename in files:
                        return os.path.join(root, filename)
            else:
                # Ricerca solo nella root del path specificato
                full_path = os.path.join(base_path, filename)
                if os.path.exists(full_path):
                    return full_path

        return None

    def load(self, filename_with_pointer: str) -> Any:
        # 1. Split puntatore #
        if '#' in filename_with_pointer:
            target_file, keypath = filename_with_pointer.split('#', 1)
        else:
            target_file, keypath = filename_with_pointer, None

        # 2. Ricerca file
        filepath = self.find_file(target_file)
        if not filepath:
            self.logger.error("File '%s' non trovato nei percorsi: %s (Ricorsivo: %s)",
                              target_file, self.search_paths, self.recursive)
            return {}

        # 3. Lettura e Parsing
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            content = os.path.expandvars(content)
            data = yaml.load(content, Loader=lnYamlLoader)

            # 4. Navigazione Keypath
            result = self._get_keypath(data, keypath) if keypath else data
            self.logger.trace("Caricato: %s", filepath)
            return result

        except Exception as e:
            self.logger.error("Errore critico durante il parsing di %s: %s", target_file, str(e))
            return {}

# --- Esempio di utilizzo aggiornato ---

class lnYamlEnvironment:
    def __init__(self, logger, paths: list=["conf"], recursive=True):
        # self.logger = DummyLogger()
        self.logger = logger

        # Definiamo dove cercare e se andare in profondità
        # paths = ["./config", "./internal/settings", "conf"]
        # paths = ["conf"]

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