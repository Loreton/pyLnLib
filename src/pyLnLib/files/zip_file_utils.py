#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# updated by ...: Loreto Notarantonio
# Version ......: 08-01-2021 18.10.41
#
import  sys; sys.dont_write_bytecode = True
import os, stat
import zipfile, io
from typing import Optional # Any, List, Optional, Tuple
from types import SimpleNamespace



from ..context import gVars as ctx
C=ctx.colors
logger=ctx.get_logger()

def ____zipNameList(zip_filename):
    """ check it its a zip file """
    # _zFileNamelist=[]
    fileNamelist = None
    if zipfile.is_zipfile(zip_filename):
        z=zipfile.ZipFile(zip_filename, "r")
        fileNamelist=z.namelist()

    return fileNamelist


def read_file_in_zip_prev(zip_filename, filename):
    content=[]
    if zipfile.is_zipfile(zip_filename):
        z=zipfile.ZipFile(zip_filename, "r")
        with z.open(filename) as f:
            _data=f.read()
        _buffer=io.TextIOWrapper(io.BytesIO(_data))
        # contents =io.TextIOWrapper(io.BytesIO(_data), encoding='iso-8859-1', newline='\n')#
        for line in _buffer:
            content.append(line)
        # content='\n'.join(content)
        content=''.join(content)

    else:
        content=[]
    return content







############################################################
#
############################################################
# def zipExtractFile(archive_file: str, filename: str, content: bool=False, search_paths: list=[], out_dir: str='/tmp'):



#################################
# -
#################################
def searchFileInZip(archive_file: str,
                        filename: str, *,
                        search_paths: list,
                        recursive: bool=False,
                        extract_to: Optional[str]=None,
                        stacklevel=-1) ->  SimpleNamespace:
                        # stacklevel=-1) ->  Tuple[Optional[str], bool]:
    #------------------------------------
    def extract_file(zz, filename):
        result.filepath=filename
        result.recursice=is_recursive
        result.extracted_file=None
        if extract_to:
            zz.extract(member=filename, path=extract_to, pwd=None)
            dest_file = os.path.join(extract_to, os.path.basename(filename))
            # Ottieni i permessi attuali
            current_permissions = os.stat(dest_file).st_mode
            # Aggiungi solo il permesso di scrittura (senza rimuovere altri)
            os.chmod(dest_file, current_permissions | stat.S_IWUSR)  # solo per utente
            result.extracted_file = dest_file

        with zz.open(filename, 'r') as f:
            content = f.read() # bytes

        if isinstance(content, bytes):
            content = content.decode('utf-8')  # str

        result.content = content
        return result_and_exit()


    def result_and_exit():
        if result.filepath:
            logger.info("%s FOUND in zipFile: %s [extracted: %s]", result.filepath, archive_file, result.extracted_file, color=C.magenta)
        else:
            logger.warning("%s NOT FOUND in zipFile: %s", filename, archive_file)
        return result

    #------------------------------------
    # logger = ctx.logger

    result = SimpleNamespace(content=None, filepath=None, is_recursive=False)
    STACKLEVEL = stacklevel+1
    # --- Ricerca Interna (ZIP/PYZ) ---
    if zipfile.is_zipfile(archive_file):
        logger.info("ZipFile searching for file: %s - (on paths: %s)", filename, search_paths, stacklevel=STACKLEVEL)

        is_recursive=False
        z=zipfile.ZipFile(archive_file, "r")
        zip_content=z.namelist()

        ### - cerca direttamente il filename... se esiste
        if filename in zip_content:
            return extract_file(zz=z, filename=filename)


        # Cerchiamo nei search_paths interni allo zip
        for base_path in search_paths:

            logger.debug("searching: %s/%s", base_path, filename)

            # Normalizziamo il path interno (niente drive letter, slash avanti)
            fpath = os.path.join(base_path, filename).replace('\\', '/') ### nel caso stessimo in Windows
            if fpath in zip_content:
                return extract_file(zz=z, filename=fpath)

            # Se ricorsivo, cerchiamo corrispondenze parziali
            if recursive:
                logger.debug("searching: %s/.../%s", base_path, filename)
                for member in zip_content:
                    if member.startswith(base_path) and member.endswith(filename):
                        result.is_recursive=True
                        return extract_file(zz=z, filename=member)


    return result_and_exit()




if __name__ == '__main__':
    zip_filename='/home/loreto/filu/Programming/gitREPO/lnSync/dist/lnSync.pyz'
    config_file='conf/@lnSync_config.yaml'
    # data=read_file_in_zip_prev(zip_filename, config_file)
    # print(data)
    # data=zipReadFile(zip_filename, config_file)
    # print(data)
