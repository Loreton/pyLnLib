#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 02-05-2026 17.40.03
#
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import zipfile
from typing import Any, Optional, List

# ============================================================
# Loader YAML personalizzato
# ============================================================

class lnYamlLoader(yaml.FullLoader):
    """Loader che mantiene un riferimento all'ambiente."""
    env_ref = None
    current_dir = ""   # 👈 AGGIUNTO

# -------------------- TAG CUSTOM ----------------------------

def yaml_include_constructor(loader, node):
    filename = node.value

    # 👇 PRIORITÀ: path relativo al file corrente
    if not os.path.isabs(filename) and loader.current_dir:
        rel_path = os.path.normpath(os.path.join(loader.current_dir, filename))
    else:
        rel_path = filename

    return loader.env_ref.yaml_engine.load(rel_path, base_dir=os.path.dirname(rel_path)
    )


def yaml_constructor_include_merge(loader, node):
    items = loader.construct_sequence(node)
    final_dict = {}

    for filename in items:
        if not os.path.isabs(filename) and loader.current_dir:
            filename = os.path.normpath(os.path.join(loader.current_dir, filename))

        res = loader.env_ref.yaml_engine.load(filename, base_dir=os.path.dirname(filename) )

        if isinstance(res, dict):
            final_dict.update(res)

    return final_dict

def yaml_constructor_list_merge(loader, node):
    items = loader.construct_sequence(node)
    final_list = []

    for filename in items:
        if not os.path.isabs(filename) and loader.current_dir:
            filename = os.path.normpath(os.path.join(loader.current_dir, filename))

        res = loader.env_ref.yaml_engine.load(filename, base_dir=os.path.dirname(filename) )

        if isinstance(res, list):
            final_list.extend(res)
        elif res is not None:
            final_list.append(res)

    return final_list


def join_path(loader, node):
    return os.path.join(*loader.construct_sequence(node))


def join_str(loader, node):
    return ''.join([str(i) for i in loader.construct_sequence(node)])


# Registrazione tag
lnYamlLoader.add_constructor('!include', yaml_include_constructor)
lnYamlLoader.add_constructor('!include_merge', yaml_constructor_include_merge)
lnYamlLoader.add_constructor('!list_merge', yaml_constructor_list_merge)
lnYamlLoader.add_constructor('!join_path', join_path)
lnYamlLoader.add_constructor('!join_str', join_str)


# ============================================================
# Engine YAML
# ============================================================

class YamlEngine:

    def __init__(self, environment,
                 search_paths: List[str] = None,
                 recursive: bool = False,
                 package: str = None):
        """
        :param environment: oggetto ambiente
        :param search_paths: directory FS
        :param recursive: ricerca ricorsiva
        :param package: package python (per .pyz)
        """
        self.env = environment
        lnYamlLoader.env_ref = environment
        self.logger = environment.logger

        self.search_paths = search_paths or ["."]
        self.recursive = recursive

        # es: "myapp.conf"
        self.package = package

    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # FILESYSTEM SEARCH
    # --------------------------------------------------------

    def find_file(self, filename: str) -> Optional[str]:
        for base_path in self.search_paths:
            if not os.path.exists(base_path):
                self.logger.debug("Path '%s' non esiste", base_path)
                continue

            if self.recursive:
                for root, _, files in os.walk(base_path):
                    if filename in files:
                        return os.path.join(root, filename)
            else:
                full_path = os.path.join(base_path, filename)
                if os.path.exists(full_path):
                    return full_path

        return None

    # --------------------------------------------------------
    # LETTURA FILE (FS + PYZ)
    # --------------------------------------------------------

    def read_file(self, filename: str) -> Optional[str]:
        """
        Ordine:
        1. filesystem
        2. package (pyz)
        3. zip diretto (fallback)
        """

        # ---- 1. FILESYSTEM ----
        filepath = self.find_file(filename)
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.logger.trace("FS load: %s", filepath)
                    return f.read()
            except Exception as e:
                self.logger.error("Errore lettura FS %s: %s", filepath, e)

        # ---- 2. PACKAGE (IMPORTLIB) ----
        if self.package:
            try:
                import importlib.resources as pkg_resources
                content = pkg_resources.files(self.package).joinpath(filename).read_text(encoding='utf-8')
                self.logger.trace("PKG load: %s:%s", self.package, filename)
                return content
            except Exception:
                pass

        # ---- 3. PYZ DIRETTO (fallback) ----
        try:
            archive = sys.argv[0]
            if zipfile.is_zipfile(archive):
                with zipfile.ZipFile(archive) as z:
                    with z.open(filename) as f:
                        self.logger.trace("PYZ load: %s", filename)
                        return f.read().decode('utf-8')
        except Exception:
            pass

        return None

    # --------------------------------------------------------
    # LOAD YAML
    # --------------------------------------------------------

    # def load(self, filename_with_pointer: str) -> Any:
    def load(self, filename_with_pointer: str, base_dir: str = "") -> Any:

        # split #keypath
        if '#' in filename_with_pointer:
            target_file, keypath = filename_with_pointer.split('#', 1)
        else:
            target_file, keypath = filename_with_pointer, None


        # if not base_dir:
        #     base_dir = os.path.dirname(target_file) or "conf"
        # se non ho base_dir, prova a dedurlo dai search_paths
        if not base_dir and not os.path.isabs(target_file):
            for p in self.search_paths:
                candidate = os.path.join(p, target_file)
                if self.read_file(candidate):
                    target_file = candidate
                    base_dir = os.path.dirname(candidate)
                    break

        # risoluzione path relativo
        if not os.path.isabs(target_file) and base_dir:
            target_file = os.path.normpath(os.path.join(base_dir, target_file))

        # lettura contenuto
        content = self.read_file(target_file)

        if content is None:
            self.logger.error("File '%s' non trovato (FS + package + pyz)", target_file )
            sys.exit(1)
            return {}

        try:
            content = os.path.expandvars(content)
            current_dir = os.path.dirname(target_file)

            loader = lnYamlLoader(content)
            loader.env_ref = self.env
            loader.current_dir = current_dir   # 👈 QUI IL FIX

            data = loader.get_single_data()
            result = self._get_keypath(data, keypath) if keypath else data
            return result

        except Exception as e:
            self.logger.error("Errore parsing YAML %s: %s", target_file, e)
            return {}


# ============================================================
# ENVIRONMENT
#   myapp/
#     ├── __main__.py
#     ├── core/
#     │   └── yaml_engine.py
#     └── conf/
#         ├── __init__.py
#         ├── config.yaml
#         └── db.yaml
#   potrebbero esserci più packages in un .pyz
#      quindi devo dire a pyhton qual'è il pachage da usare
#      e cioe: package="myapp.conf"
# ============================================================


class lnYamlEnvironment:
    def __init__(self, logger,
                 paths: List[str] = None,
                 recursive: bool = True,
                 package: str = None):

        self.logger = logger

        self.yaml_engine = YamlEngine(
            self,
            search_paths=paths or ["conf"],
            recursive=recursive,
            package=package  # <-- fondamentale per .pyz
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    class DummyLogger:
        def critical(self, msg, *a): print("CRITICAL:", msg % a if a else msg)
        def error(self, msg, *a):    print("ERROR:", msg % a if a else msg)
        def warning(self, msg, *a):  print("WARNING:", msg % a if a else msg)
        def info(self, msg, *a):     print("INFO:", msg % a if a else msg)
        def debug(self, msg, *a):    print("DEBUG:", msg % a if a else msg)
        def trace(self, msg, *a):    print("TRACE:", msg % a if a else msg)

    env = lnYamlEnvironment(
        logger=DummyLogger(),
        paths=["conf", "conf/profiles"],
        recursive=False,
        package="myapp.conf"   # <-- importante
    )

    config = env.yaml_engine.load("config.yaml#myDirs")
    print(config)
