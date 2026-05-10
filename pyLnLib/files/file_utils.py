#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 10-05-2026 15.25.44
#

import sys; sys.dont_write_bytecode=True; this=sys.modules[__name__]
import os
import zipfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any, List, Optional, Tuple
import shutil


from ..context import gVars as ctx

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
            result = searchingZipFile(filename=filename, archive_file=sys.argv[0], search_paths=["conf"], recursive=True, extraction_dir=self.temp_dir)
            if not result.filepath:
                ctx.logger.error("filename: %s not found on filesysten neither in zipfile", filename, exit=True)
        else:
            ctx.logger.warning("filename: %s not found on fileSystem", filename, exit=True)
'''


def searchingFile(filename: str, search_paths: list=["conf"], recursive: bool=False, copy_to: str=None) -> Tuple[Optional[str], bool]:
    #------------------------------------
    def read_content(filename):
        result.filepath = filename
        if copy_to:
            shutil.copyfile(filename, copy_to)
        with open(filename, 'r') as f:
            result.content = f.read().encode('utf-8')
        return result
    #------------------------------------

    result = SimpleNamespace(content=None, filepath=None, is_recursive=False)

    ctx.logger.info("FileSystem searching for file: %s", filename)
    if os.path.exists(filename): ### esiste già come file completo
        return read_content(filename)

    if filename.startswith('/'): ### absolute path inutile cercarlo altrove se non già trovato nel filesuistem
        return result


    ff = Path(filename)
    fname=ff.name.__str__()
    fpath=ff.parent.__str__()


    # --- 1. Ricerca Esterna (Filesystem) tramite search_paths ---
    for base_path in search_paths:
        ctx.logger.info("on base_path: %s", base_path)
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


    return result





# #################################
# # -
# #################################
# def _searchFile(filename: str, search_paths: list=["conf"], recursive: bool=True, archive_file: str=sys.argv[0]) -> Tuple[Optional[str], bool, bool]:
#     """
#     Cerca il file prima nel filesystem esterno, poi dentro il .pyz o zip.
#     Ritorna: (path_o_nome, is_inside_zip)
#     """
#     IS_IN_ZIP=False
#     IS_RECURSIVE=False

#     ctx.logger.debug("FileSystem searching.....")
#     # --- 1. Ricerca Esterna (Filesystem) direttamente il filename ---
#     ctx.logger.debug("filename: %s", filename)
#     if os.path.exists(filename): ### esiste già come file completo
#         ctx.logger.debug("...found")
#         return filename, IS_RECURSIVE, IS_IN_ZIP

#     ff = Path(filename)
#     fname=ff.name.__str__()
#     fpath=ff.parent.__str__()


#     # --- 1. Ricerca Esterna (Filesystem) tramite search_paths ---
#     for base_path in search_paths:
#         if os.path.exists(base_path):
#             ctx.logger.debug("on base_path: %s", base_path)
#             if recursive:
#                 IS_RECURSIVE=True

#                 for root, _, files in os.walk(base_path):

#                     if filename in files:
#                         ctx.logger.debug("...found")
#                         return os.path.join(root, filename), IS_RECURSIVE, IS_IN_ZIP

#                     for file in files:
#                         if root == base_path and filename.endswith(file):
#                             ctx.logger.debug("...found")
#                             return file, IS_RECURSIVE, IS_IN_ZIP

#                         elif root.startswith(base_path) and filename.endswith(file):
#                             ctx.logger.debug("...found")
#                             return file, IS_RECURSIVE, IS_IN_ZIP

#             else:
#                 IS_RECURSIVE=False
#                 full_path = os.path.join(base_path, filename)
#                 if os.path.exists(full_path):
#                     ctx.logger.debug("...found")
#                     return full_path, IS_RECURSIVE, IS_IN_ZIP

#             ctx.logger.error("...not found")



#     # --- 2. Ricerca Interna (ZIP/PYZ) ---
#     if zipfile.is_zipfile(archive_file):
#         ctx.logger.debug("ZIP  searching.....")
#         ctx.logger.debug("filename: %s", filename)
#         IS_RECURSIVE=False
#         IS_IN_ZIP=True
#         z=zipfile.ZipFile(archive_file, "r")
#         zip_content=z.namelist()

#         ### - cerca direttamente il filename... se esiste
#         if filename in zip_content:
#             return filename, IS_RECURSIVE, IS_IN_ZIP

#         # Cerchiamo nei search_paths interni allo zip
#         for base_path in search_paths:
#             ctx.logger.debug("on base_path: [%s]", base_path)
#             IS_RECURSIVE=False
#             # ctx.logger.debug("ZIP  searching: [%s]: filename: %s", base_path, filename)
#             # Normalizziamo il path interno (niente drive letter, slash avanti)
#             target_in_zip = os.path.join(base_path, filename).replace('\\', '/') ### nel caso stessimo in Windows
#             if target_in_zip in zip_content:
#                 ctx.logger.info("...found")
#                 return target_in_zip, IS_RECURSIVE, IS_IN_ZIP

#             # Se ricorsivo, cerchiamo corrispondenze parziali
#             if recursive:
#                 IS_RECURSIVE=True
#                 for member in zip_content:
#                     if member.startswith(base_path) and member.endswith(filename):
#                         ctx.logger.info("...found")
#                         return member, IS_RECURSIVE, IS_IN_ZIP

#             ctx.logger.error("...not found")
#     return None, False, False

















def findFileInPaths(filename: str, search_paths: list, exit_on_not_found: bool=True):
    filepath = None

    # if os.path.isabs(filename) and os.path.isfile(filename):
    if os.path.isfile(filename):
        return filename

    for path in search_paths:
        if file_path := this.findFile(root=path, filename=filename):
            filepath = file_path
            break
    if not filepath:
        ctx.logger.error("filename: %s not found in searching paths: %s", filename, search_paths, exc_info=exit_on_not_found)

    return filepath


def getFileContent(filename: str, search_paths: list, resolve_vars: bool=True, exit_on_not_found: bool=True):
    content = None
    if file_path := this.findFileInPaths(filename, search_paths=search_paths):
        with open(file_path, mode="r") as f:
            content=f.read() # single strin
        if resolve_vars:
            content = os.path.expandvars(content)

    if not content and exit_on_not_found:
        ctx.logger.error("content not found on file: %s", filename, exc_info=exit_on_not_found)
    return content




















#################################
# -
#################################
def searchingZipFile(filename: str, archive_file: str, search_paths: list=["conf"], recursive: bool=True, extraction_dir: str=None) -> Tuple[Optional[str], bool]:
    # --- 2. Ricerca Interna (ZIP/PYZ) ---
    result = SimpleNamespace(content=None, filepath=None, is_in_zip=False, is_recursive=False)

    if zipfile.is_zipfile(archive_file):
        ctx.logger.info("ZipFile searching for file: %s", filename)

        is_recursive=False
        z=zipfile.ZipFile(archive_file, "r")
        zip_content=z.namelist()

        ### - cerca direttamente il filename... se esiste
        if filename in zip_content:
            result.filepath=filename
            result.is_in_zip=True
            return result

        # Cerchiamo nei search_paths interni allo zip
        for base_path in search_paths:
            ctx.logger.info("on base_path: [%s]", base_path)

            # Normalizziamo il path interno (niente drive letter, slash avanti)
            fpath = os.path.join(base_path, filename).replace('\\', '/') ### nel caso stessimo in Windows
            if fpath in zip_content:
                result.filepath = fpath
                result.is_in_zip=True
                if extraction_dir:
                    z.extract(member=fpath, path=extraction_dir, pwd=None)
                with z.open(filename) as f:
                    result.content = f.read().decode('utf-8')
                return result


            # Se ricorsivo, cerchiamo corrispondenze parziali
            if recursive:
                for member in zip_content:
                    if member.startswith(base_path) and member.endswith(filename):
                        result.is_recursive=True
                        result.filepath = member
                        return result


    return result



#################################
# -
#################################
def searchingFilesystem(filename: str, search_paths: list=["conf"], recursive: bool=True) -> Tuple[Optional[str], bool]:
    """
    Cerca il file prima nel filesystem esterno, poi dentro il .pyz o zip.
    Ritorna: (path_o_nome, is_inside_zip)
    """
    result = SimpleNamespace(content=None, filepath=None, is_zipfile=False, is_recursive=False)
    ctx.logger.info("FileSystem searching for file: %s", filename)
    if os.path.exists(filename): ### esiste già come file completo
        result.filepath=filename
        return result

    if filename.startswith('/'): ### absolute path inutile cercarlo altrove se non già trovato nel filesuistem
        return result


    ff = Path(filename)
    fname=ff.name.__str__()
    fpath=ff.parent.__str__()


    # --- 1. Ricerca Esterna (Filesystem) tramite search_paths ---
    for base_path in search_paths:
        ctx.logger.info("on base_path: %s", base_path)
        if os.path.exists(base_path):
            if recursive:
                result.recursive=True

                for root, _, files in os.walk(base_path):

                    if filename in files:
                        result.filepath=os.path.join(root, filename)
                        return result

                    for file in files:
                        if root == base_path and filename.endswith(file):
                            result.filepath=file
                            return result


                        elif root.startswith(base_path) and filename.endswith(file):
                            result.filepath=file
                            return result

            else:
                full_path = os.path.join(base_path, filename)
                if os.path.exists(full_path):
                    result.recursive=False
                    result.filepath=full_path
                    return result


    return result



def searchFile(filename: str, search_paths: list=["conf"], recursive: bool=True, archive_file: str=None, extraction_dir: str='/tmp') -> Tuple[Optional[str], bool, bool]:
    res = searchingFilesystem(filename=filename, search_paths=search_paths, recursive=recursive)
    if res.filepath:
        ctx.logger.info("found - is_recursive: %s", res.is_recursive)
        return res
    else:
        ctx.logger.error("not found in filesystem")


    if zipfile.is_zipfile(archive_file):
        res = searchingZipFile(filename=filename, archive_file=archive_file, search_paths=search_paths, recursive=recursive, extraction_dir=extraction_dir)
        if res.filepath:
            ctx.logger.info("found - is_recursive: %s", res.is_recursive)
            return res
        else:
            ctx.logger.error("not found in zip_file")

    return res







##################################################################################################################################
#   M A I N
##################################################################################################################################
if __name__ == '__main__':
    # global ctx
    # from types import SimpleNamespace
    # ctx=SimpleNamespace()
    # from coloredLogger_simple import setupLogger, testLogger
    # ctx.logger=setupLogger(colored=True, logger_name='Loreto', logger_level="debug")
    ctx.logger.info(msg='------- Starting -----------')
    FINDFILE = True

    if FINDFILE:
        myPaths = [".", "conf/", "test/prova/"]
        myPaths = ["conf/", "test/prova/"]
        files_to_check=[
                        'test/prova/test.txt', ## solo locale
                        'test.txt', ## solo locale
                        'conf/profiles/HD2510_500GB.yaml', # in zip
                        'conf/@lnSync_config.yaml', # in zip
                        'WD264F_500GB.yaml', # in zip
                        '/home/loreto/filu/Programming/gitREPO/lnSync/conf/rclone_options.yaml', # in zip
                        ]
        # filename = findFileInPaths(filename="@lnSync_config.yaml", paths=myPaths)
        for filename in files_to_check:
            res = searchFile(filename=filename,
                                  search_paths=myPaths,
                                  recursive=True,
                                  archive_file='/home/loreto/filu/Programming/gitREPO/lnSync/dist/lnSync.pyz')
            if res.filepath:
                ctx.logger.notify(f"FOUND {res.filepath = }")
            else:
                ctx.logger.error(f"NOT FOUND {filename = }")

            print('\n'*2)