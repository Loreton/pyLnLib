#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 05-05-2026 15.36.18
#

import sys; sys.dont_write_bytecode=True; this=sys.modules[__name__]
import os
import zipfile
from pathlib import Path
from typing import Any, List, Optional, Tuple
from types import SimpleNamespace

if __name__ == '__main__':
    sys.path.append("/home/loreto/filu/Programming/gitREPO/lnSync/pyLnLib")
    from dummy_logger import DummyLogger
    ctx = SimpleNamespace(logger=DummyLogger(level="TRACE", show_caller=True, module=False, function=True))

else:
    from .context import gVars as ctx





#################################
# -
#################################
def searchingZipFile(filename: str, archive_file: str, search_paths: list=["conf"], recursive: bool=True, extraction_dir: str=None) -> Tuple[Optional[str], bool]:
    #------------------------------------
    def extract_file(zz, filename):
        result.filepath = filename
        result.is_in_zip=True
        if extraction_dir:
            zz.extract(member=filename, path=extraction_dir, pwd=None)
        with zz.open(filename, 'r') as f:
            result.content = f.read().decode('utf-8')
        return result
    #------------------------------------

    result = SimpleNamespace(content=None, filepath=None, is_in_zip=False, is_recursive=False)


    # --- Ricerca Interna (ZIP/PYZ) ---
    if zipfile.is_zipfile(archive_file):
        ctx.logger.info("ZipFile searching for file: %s", filename)

        is_recursive=False
        z=zipfile.ZipFile(archive_file, "r")
        zip_content=z.namelist()

        ### - cerca direttamente il filename... se esiste
        if filename in zip_content:
            return extract_file(zz=z, filename=filename)
            # return result

        # Cerchiamo nei search_paths interni allo zip
        for base_path in search_paths:

            ctx.logger.info("on base_path: [%s]", base_path)

            # Normalizziamo il path interno (niente drive letter, slash avanti)
            fpath = os.path.join(base_path, filename).replace('\\', '/') ### nel caso stessimo in Windows
            if fpath in zip_content:
                return extract_file(zz=z, filename=fpath)
                # return result


            # Se ricorsivo, cerchiamo corrispondenze parziali
            if recursive:
                for member in zip_content:
                    if member.startswith(base_path) and member.endswith(filename):
                        result.is_recursive=True
                        return extract_file(zz=z, filename=member)
                        # return result
    return result



#################################
# -
#################################
def searchingFilesystem(filename: str, search_paths: list=["conf"], recursive: bool=False) -> Tuple[Optional[str], bool]:
    #------------------------------------
    def read_content(filename):
        result.filepath = filename
        with open(filename, 'r') as f:
            result.content = f.read().encode('utf-8')
        return result
    #------------------------------------

    result = SimpleNamespace(content=None, filepath=None, is_zipfile=False, is_recursive=False)
    ctx.logger.info("FileSystem searching for file: %s", filename)
    if os.path.exists(filename): ### esiste già come file completo
        read_content(filename)
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
                        return read_content(os.path.join(root, filename))
                        # return result

                    for file in files:
                        if root == base_path and filename.endswith(file):
                            return read_content(file)
                            # result.filepath=file
                            # return result


                        elif root.startswith(base_path) and filename.endswith(file):
                            return read_content(file)
                            # result.filepath=file
                            # return result

            else:
                full_path = os.path.join(base_path, filename)
                if os.path.exists(full_path):
                    result.recursive=False
                    return read_content(full_path)
                    # result.filepath=full_path
                    # return result


    return result



def searchFile(filename: str, search_paths: list=["conf"], recursive: bool=False, archive_file: str=None, extraction_dir: str=None) -> Tuple[Optional[str], bool, bool]:
    """
    Cerca il file prima nel filesystem esterno, poi dentro il .pyz o zip.
    Ritorna: (path_o_nome, is_inside_zip)
    """
    ctx=SimpleNamespace(logger=DummyLogger(show_caller=True))

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
                              archive_file='/home/loreto/filu/Programming/gitREPO/lnSync/dist/lnSync.pyz',
                              extraction_dir='/tmp')
            if res.filepath:
                ctx.logger.notify(f"FOUND {res.filepath = }")
            else:
                ctx.logger.error(f"NOT FOUND {filename = }")

            print('\n'*2)