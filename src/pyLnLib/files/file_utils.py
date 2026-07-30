#!/usr/bin/env python3
# ruff: noqa: SIM102 Use a single `if` statement instead of nested `if` statements help: Combine `if` statements using `and` (Ruff SIM102)
# ruff: noqa: I001 Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
#
# updated by ...: Loreto Notarantonio
# Date .........: 11-07-2026 15.37.33
#
from __future__ import annotations

import sys

import os
# import stat
import zipfile
from pathlib import Path
from types import SimpleNamespace

from ..context import ctx
from ..colors import get_colors
from ..logger import get_logger
from .zip_file_utils import searchFileInZip

C=get_colors()
# logger=get_logger()


def findFile(root: str, filename: str):
    for dirpath, _, files in os.walk(root):
        file_path = os.path.join(dirpath, filename)
        logger.debug("checking for: %s", file_path)
        if filename in files:
            logger.notify("found: %s", file_path)
            return file_path
    return None





def unique_filename(filename: Path, suffix_pattern: str = "-{:03d}") -> Path:
    """Return a non-existing filename.

    Example:
        report.txt
        report_001.txt
        report_002.txt
        ...
    """

    if not filename.exists():
        return filename

    stem = filename.stem
    suffix = filename.suffix
    parent = filename.parent

    index = 1

    while True:
        # candidate = parent / f"{stem}_{index:03d}{suffix}"
        candidate = parent / (
            stem +
            suffix_pattern.format(index) +
            suffix
        )

        if not candidate.exists():
            return candidate

        index += 1




def scan_directory(root_dir: Path|str, pattern: str, recursive: bool = True) -> list[Path]:
    """
    Scansiona una directory per trovare file EPUB

    Args:
        root_dir: Directory root da scansionare
        pattern: Pattern dei file da cercare
        recursive: Se cercare ricorsivamente

    Returns:
        list[Path]: Lista di percorsi dei file trovati
    """
    root_path = Path(root_dir)
    if not root_path.exists():
        self.logger.error(f"Directory non trovata: {root_path}")
        return []

    if recursive:
        file_list = list(root_path.glob(f'**/{pattern}'))
    else:
        file_list = list(root_path.glob(pattern))

    logger.info(f"Trovati {len(file_list)} file {pattern} in {root_path}")
    return file_list



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
        base_path = str(base_path)
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



# ######################################################################
# ''' example:
#    for file in dirlist(top_dir='/usr/share/sounds/freedesktop/stereo', file_pattern="*.oga", recursive=False):
#         print(file)
#     sys.exit()
# '''
# ######################################################################
# def dirList(top_dir: str|Path, file_pattern: str, recursive: bool=False):
#     files=Path(top_dir).glob(file_pattern)
#     yield from files
#     for _element in files:
#         y = _element
#         yield y
#     # for file in files:
#     #     yield file



def get_file_list(top_dir, file_pattern="*", verbose=False):
    """Genera lista file che soddisfano i filtri"""
    for filepath in Path(top_dir).glob(f"**/{file_pattern}"):
        if not filepath.is_file():
            continue

        if verbose:
            print(f"{C.yellow}Included: {filepath}{C.reset}")
        yield filepath



##################################################################################################################################
#   M A I N
##################################################################################################################################
if __name__ == '__main__':
    ...
