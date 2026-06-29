#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 13-06-2026 14.01.43
#

import sys; sys.dont_write_bytecode=True; this=sys.modules[__name__]
import os
import stat
import zipfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any   # Any, List, Optional, Tuple


from ..context import gVars as ctx
from .zip_file_utils import searchFileInZip

C=ctx.colors
logger: Any=ctx.get_logger()




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
def searchFileOnFS(filename: str,
                    search_paths: list,
                    recursive: bool=False,
                    extract_to: str | None = None,
                    stacklevel=-1) -> SimpleNamespace:
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

    if filename.startswith('/'): ### absolute path inutile cercarlo altrove se non già trovato nel filesystem
        return result


    # ff = Path(filename)
    # fname=ff.name.__str__()
    # fpath=ff.parent.__str__()

    # --- 1. Ricerca Esterna (Filesystem) tramite search_paths ---
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
                        if (root == base_path or root.startswith(base_path)) and filename.endswith(file):
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




def searchFile(filename:           str,
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
