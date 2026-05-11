#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 11-05-2026 10.08.33
#

import sys; sys.dont_write_bytecode=True; this=sys.modules[__name__]
import os, stat
import zipfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any, List, Optional, Tuple
import shutil


from ..context import gVars as ctx; C=ctx.colors

def findFile(root: str, filename: str):
    for dirpath, _, files in os.walk(root):
        file_path = os.path.join(dirpath, filename)
        ctx.logger.debug("checking for: %s", file_path)
        if filename in files:
            ctx.logger.notify("found: %s", file_path)
            return file_path
    return None



#################################
# - return SimpleNamespace:
# -     content:      contetnof file
# -     filepath:     filepath of found file or None
# -     is_recursive: 
#################################
''' calling example:
    result = searchingFile(filename=filename, search_paths=["conf"], recursive=False, copy_to=self.rclone_config_file)
    if not result.filepath:
        if zipfile.is_zipfile(sys.argv[0]):
            result = searchFileInZip(filename=filename, archive_file=sys.argv[0], search_paths=["conf"], recursive=True, extraction_dir=self.temp_dir)
            if not result.filepath:
                ctx.logger.error("filename: %s not found on filesysten neither in zipfile", filename, exit=True)
        else:
            ctx.logger.warning("filename: %s not found on fileSystem", filename, exit=True)
'''


def searchFileOnFS(filename: str,
                    search_paths: list,
                    recursive: bool=False,
                    extract_to: str=None,
                    stacklevel=-1) -> Tuple[Optional[str], bool]:
    #------------------------------------
    def read_content(filename):
        result.filepath = filename
        if extract_to:
            # shutil.copyfile(filename, extract_to)
            # copy2() - come copy() ma mantiene anche i metadati (date, ecc.)
            shutil.copy(filename, extract_to)  # Funziona anche con directory
            dest_file = os.path.join(extract_to, os.path.basename(filename))
            # Ottieni i permessi attuali
            current_permissions = os.stat(dest_file).st_mode
            # Aggiungi solo il permesso di scrittura (senza rimuovere altri)
            os.chmod(dest_file, current_permissions | stat.S_IWUSR)  # solo per utente

        with open(filename, 'r') as f:
            result.content = f.read()
        return result_and_exit()
    #------------------------------------

    #------------------------------------
    def result_and_exit():
        if result.filepath:
            ctx.logger.info("FOUND: %s on fileSystem", result.filepath, color=C.magenta)
        else:
            ctx.logger.warning("NOT FOUND: %s on fileSystem", filename)
        return result
    #------------------------------------



    STACKLEVEL = stacklevel+1
    result = SimpleNamespace(content=None, filepath=None, is_recursive=False)
    ctx.logger.info("searching for file: %s (on paths: %s)", filename, search_paths, stacklevel=STACKLEVEL)
    # import pdb; pdb.set_trace(); # by Loreto
    if os.path.exists(filename): ### esiste già come file completo
        return read_content(filename)

    if filename.startswith('/'): ### absolute path inutile cercarlo altrove se non già trovato nel filesuistem
        return result_and_exit()


    # ff = Path(filename)
    # fname=ff.name.__str__()
    # fpath=ff.parent.__str__()

    # --- 1. Ricerca Esterna (Filesystem) tramite search_paths ---
    for base_path in search_paths:
        # ctx.logger.info("on base_path: %s", base_path)
        ctx.logger.debug("searching: %s/.../%s", base_path, filename, stacklevel=STACKLEVEL)
        if os.path.exists(base_path):
            if recursive:
                is_recursive=True
                for root, _, files in os.walk(base_path):

                    if filename in files:
                        return read_content(os.path.join(root, filename))

                    for file in files:
                        if (root == base_path or root.startswith(base_path)) and filename.endswith(file):
                            return read_content(os.path.join(root, filename))

            else:
                is_recursive=False
                full_path = os.path.join(base_path, filename)
                if os.path.exists(full_path):
                    return read_content(full_path)

    # if result.filepath:
    #     ctx.logger.info("%s has been found on fileSystem", result.filepath)
    # else:
    #     ctx.logger.warning("%s not found on fileSystem", filename)
    return result_and_exit()





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
        ctx.logger.error("filename: %s not found in searching paths: %s", filename, search_paths, stacklevel=2)
        sys.exit(1)

    return filepath




# def getFileContent(filename: str, search_paths: list, resolve_vars: bool=True, exit_on_not_found: bool=True, stacklevel=0):
#     content = None
#     if file_path := this.findFileInPaths(filename, search_paths=search_paths):
#         with open(file_path, mode="r") as f:
#             content=f.read() # single strin
#         if resolve_vars:
#             content = os.path.expandvars(content)

#     if not content and exit_on_not_found:
#         ctx.logger.error("content not found on file: %s", filename, exc_info=exit_on_not_found, stacklevel=stacklevel+1)
#     return content




def searchFile(filename:           str,
                    search_paths:       list,
                    recursive:          bool=False,
                    extract_to:         str=None, ### se si viuole copiare il file in altra destinazione
                    exit_on_not_found:  bool=False,
                    stacklevel:         int=-1):
    ### --- copy_to importante perché il file rclone.conf dovro' passarlo come parametro a rclone,
    result = searchFileOnFS(filename=filename, search_paths=search_paths, recursive=recursive, extract_to=extract_to, stacklevel=stacklevel+1)

    if not result.filepath:
        if zipfile.is_zipfile(sys.argv[0]):
            result = searchFileInZip(filename=filename, archive_file=sys.argv[0], search_paths=search_paths, recursive=recursive, extraction_dir=extract_to)
            if not result.filepath:
                ctx.logger.error("filename: %s not found on filesysten neither in zipfile", filename, exit=exit_on_not_found)
        else:
            ctx.logger.warning("filename: %s not found on fileSystem", filename, exit=exit_on_not_found)

    return result

##################################################################################################################################
#   M A I N
##################################################################################################################################
if __name__ == '__main__':
    ...
