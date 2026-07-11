#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 11-07-2026 12.10.24
#

import sys; sys.dont_write_bytecode=True; this=sys.modules[__name__]
import os
# import stat
import zipfile
from pathlib import Path
from types import SimpleNamespace


from ..context import gVars as ctx
from ..colors import get_colors
from ..logger import get_logger
from .zip_file_utils import searchFileInZip

C=get_colors()
logger=get_logger()


# from pathlib import Path
# from typing import Optional

# def find_project_root_XXX(start_path: Optional[Path] = None, max_depth: int = 10) -> Optional[Path]:
#     """
#     Trova la root del progetto risalendo la gerarchia delle directory.

#     Cerca:
#     1. Una directory 'conf'
#     2. Un file 'pyproject.toml'

#     Args:
#         start_path: Percorso di partenza (default: directory del file chiamante)
#         max_depth: Numero massimo di livelli da risalire

#     Returns:
#         Path della directory root se trovata, altrimenti None
#     """
#     if start_path is None:
#         start_path = Path(__file__).resolve().parent

#     # Assicurati che sia una directory
#     if start_path.is_file():
#         start_path = start_path.parent

#     current = start_path.resolve()

#     for _ in range(max_depth):
#         # Cerca directory 'conf'
#         conf_dir = current / 'conf'
#         if conf_dir.exists() and conf_dir.is_dir():
#             return current

#         # Cerca file 'pyproject.toml'
#         pyproject = current / 'pyproject.toml'
#         if pyproject.exists() and pyproject.is_file():
#             return current

#         # Se siamo alla root, fermati
#         if current.parent == current:
#             break

#         # Risali di un livello
#         current = current.parent

#     return None



# def get_conf_dir(start_path: Path | None = None, max_depth: int = 10) -> Path:
#     """
#     Trova la directory 'conf' nella root del progetto.

#     Returns:
#         Path della directory conf se trovata, altrimenti None
#     """
#     root = find_project_root(start_path, max_depth)
#     if root:
#         conf_dir = root / 'conf'
#         if conf_dir.exists() and conf_dir.is_dir():
#             return conf_dir
#     return None

# def get_project_root(start_path: Path | None = None, max_depth: int = 10) -> Path:
#     """
#     Trova la root del progetto (dove si trova pyproject.toml o conf/).

#     Returns:
#         Path della root se trovata, altrimenti None
#     """
#     return find_project_root(start_path, max_depth)


# def find_project_root(max_depth: int = 10) -> Path:
#     """Trova la root del progetto."""
#     current = Path(sys.argv[0]).resolve().parent
#     for _ in range(max_depth):
#         if (current / 'conf').exists() or (current / 'pyproject.toml').exists() or (current / 'src').exists():
#             return current
#         if current.parent == current:
#             break
#         current = current.parent

#     if not current or str(current) in ['/']:
#         sys.exit(f"\t[context.py] Project root: {current} not found")
#     return current


# def get_conf_dir() -> Path:
#     """Restituisce la directory conf oppure exit"""
#     if self.project_root:
#         conf = self.project_root / 'conf'
#         if conf.exists():
#             return conf
#         else:
#             sys.exit(f"Conf directory: {conf} not found")
#     else:
#         sys.exit(f"Project root: {self.project_root} not found")

# Esempio di utilizzo
# if __name__ == "__main__":
#     # Test con percorso specifico
#     test_path = Path("/home/loreto/filu/Programming/gitREPO/lnSync/src/lnsync/main.py")

#     root = find_project_root(test_path)
#     if root:
#         print(f"Root trovata: {root}")
#         conf = root / 'conf'
#         if conf.exists():
#             print(f"Directory conf: {conf}")
#         else:
#             print("Nessuna directory conf trovata")

#         pyproject = root / 'pyproject.toml'
#         if pyproject.exists():
#             print(f"pyproject.toml: {pyproject}")
#     else:
#         print("Root non trovata")

def findFile(root: str, filename: str):
    for dirpath, _, files in os.walk(root):
        file_path = os.path.join(dirpath, filename)
        logger.debug("checking for: %s", file_path)
        if filename in files:
            logger.notify("found: %s", file_path)
            return file_path
    return None

#################################
# - read file content as str
# - return str | None
#################################
def read_file_content(filename: str|Path) -> str | None:
    if not os.path.exists(filename):
        logger.warning("%s NOT FOUND on fileSystem", filename, stacklevel=2) # type: ignore
        return None

    logger.info("reading %s on fileSystem", filename, stacklevel=2) # type: ignore
    fTYPE=1
    if fTYPE==1:
        with open(filename, 'r') as f: # modalita testo
            content_str   = f.read()  # Già una stringa (str)
            # se si ha bisogno dei bytes prima...
            # content_bytes = f.read().encode('utf-8')  # bytes
            # content_str   = content_bytes.decode('utf-8')  # str
    else:
        with open(filename, 'rb') as f: # modalità binaria
            content_bytes = f.read()  # bytes
            content_str   = content_bytes.decode('utf-8')  # str

    if len(content_str) == 0:
        logger.warning("%s does NOT contain any content", filename, stacklevel=2) # type: ignore

    return content_str

#################################
# - return SimpleNamespace:
# -     content:      contetnof file
# -     filepath:     filepath of found file or None
# -     is_recursive:
#################################
def searchFileOnFS(filename: str|Path,
                    search_paths: list,
                    recursive: bool=False,
                    extract_to: str | None = None,
                    stacklevel=-1) -> SimpleNamespace:
    # import pdb; pdb.set_trace(); # by Loreto
    # getLogger()
    # import pdb; pdb.set_trace(); # by Loreto
    result = SimpleNamespace(content=None, filepath=None, is_recursive=recursive)
    content: str | None = None  # definizione di content
    #------------------------------------
    # def result_and_exit() -> SimpleNamespace:
    #     if result.filepath:
    #         logger.info("%s FOUND on fileSystem", result.filepath, color=C.magenta, stacklevel=2)
    #     else:
    #         logger.warning("%s NOT FOUND on fileSystem", filename, stacklevel=2) # type: ignorex
    #     return result
    #------------------------------------



    STACKLEVEL = stacklevel+1
    result.filepath = filename
    logger.debug("searching for file: %s (on paths: %s)", filename, search_paths, stacklevel=STACKLEVEL)
    if os.path.exists(filename): ### esiste già come file completo
        if (content := read_file_content(filename)) is not None:
            result.content = content
            return result

    if str(filename).startswith('/'): ### absolute path inutile cercarlo altrove se non già trovato nel filesystem
        return result


    # ff = Path(filename)
    # fname=ff.name.__str__()
    # fpath=ff.parent.__str__()

    # --- 1. Ricerca Esterna (Filesystem) tramite search_paths ---
    search_paths.append(str(ctx.get_config_dir()))
    for base_path in search_paths:
        logger.debug("searching: %s/.../%s", base_path, filename, stacklevel=STACKLEVEL)
        if os.path.exists(base_path):
            if recursive:
                for root, _, files in os.walk(base_path):

                    if filename in files:
                        if (content := read_file_content(os.path.join(root, filename))) is not None:
                            result.content = content
                            result.filepath = os.path.join(root, filename)
                            return result

                    for file in files:
                        if (root == base_path or root.startswith(base_path)) and str(filename).endswith(file):
                            if (content := read_file_content(os.path.join(root, file))) is not None:
                                result.content = content
                                result.filepath = os.path.join(root, file)
                                return result

            else:
                full_path: str = os.path.join(base_path, filename)
                if (content := read_file_content(full_path)) is not None:
                    result.content = content
                    result.filepath = full_path
                    return result

    return result





def findFileInPaths_prev(filename: str, search_paths: list, exit_on_not_found: bool=True):
    filepath = None

    # if os.path.isabs(filename) and os.path.isfile(filename):
    if os.path.isfile(filename):
        return filename

    for path in search_paths:
        if file_path := this.findFile(root=path, filename=filename):
            filepath = file_path
            break
    if not filepath:
        logger.error("filename: %s not found in searching paths: %s", filename, search_paths, stacklevel=2)
        sys.exit(1)

    return filepath




def searchFile(filename:           str|Path,
                    search_paths:       list,
                    recursive:          bool=False,
                    extract_to:         str | None = None, ### se si viuole copiare il file in altra destinazione
                    exit_on_not_found:  bool=False,
                    stacklevel:         int=-1):
    ### --- copy_to importante perché il file rclone.conf dovro' passarlo come parametro a rclone,

    result = searchFileOnFS(filename=filename, search_paths=search_paths, recursive=recursive, extract_to=extract_to, stacklevel=stacklevel+1)

    if not result.filepath:
        if zipfile.is_zipfile(sys.argv[0]):
            result = searchFileInZip(filename=filename,
                                        archive_file=sys.argv[0],
                                        search_paths=search_paths,
                                        recursive=recursive,
                                        extract_to=extract_to)
            if not result.filepath:
                logger.error("filename: %s not found on filesysten neither in zipfile", filename, exit=exit_on_not_found)
        else:
            logger.warning("filename: %s not found on fileSystem", filename, exit=exit_on_not_found)

    return result



######################################################################
''' example:
   for file in dirlist(top_dir='/usr/share/sounds/freedesktop/stereo', file_pattern="*.oga", recursive=False):
        print(file)
    sys.exit()
'''
######################################################################
def dirList(top_dir: str, file_pattern: str, recursive: bool=False):
    files=Path(top_dir).glob(file_pattern)
    for file in files:
        yield file


##################################################################################################################################
#   M A I N
##################################################################################################################################
if __name__ == '__main__':
    ...
