#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# updated by ...: Loreto Notarantonio
# Version ......: 08-01-2021 18.10.41
#
import  sys; sys.dont_write_bytecode = True
import os
import zipfile, io
from typing import Any, List, Optional, Tuple
from types import SimpleNamespace



from ..context import gVars as ctx



def zipNameList___(zip_filename):
    """ check it its a zip file """
    zFileNamelist=[]
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




def zipReadFile___(filename: str, archive_file: str, extraction_dir: str='/tmp'):
    content=None
    try:
        if zipfile.is_zipfile(zip_filename):
            with zipfile.ZipFile(zip_filename, 'r') as z:
                with z.open(filename) as f:
                    content = f.read().decode('utf-8')

    except Exception as e:
        ctx.logger.error("Errore nel caricamento di %s: %s", target_file, str(e))

    return content


############################################################
#
############################################################
# def zipExtractFile(archive_file: str, filename: str, content: bool=False, search_paths: list=[], out_dir: str='/tmp'):
def zipExtractFile___(archive_file: str, filename: str, out_dir: str='/tmp'):
    """ check it its a zip file """
    if zipfile.is_zipfile(archive_file):
        zFile=zipfile.ZipFile(archive_file, "r")
        zFileNamelist=zFile.namelist()
        search_paths.insert(0, '')
        for path in search_paths:
            filepath=os.path.join(path, filename)
            if filepath in zFileNamelist:
                if content:
                    buffer=io.BytesIO(zFile.read(filepath))
                    content=buffer.read()
                    return content
                else:
                    zFile.extract(member=filepath, path=out_dir, pwd=None)
                    ftemp=f'{out_dir}/{filepath}'
                    return ftemp

    return None


#################################
# -
#################################
def searchingZipFile(archive_file: str, filename: str, *, search_paths: list=["conf"], recursive: bool=True, extraction_dir: str=None) ->  Tuple[Optional[str], bool]:
    #------------------------------------
    def extract_file(zz, filename):
        result.filepath=filename
        result.recursice=is_recursive

        if extraction_dir:
            zz.extract(member=filename, path=extraction_dir, pwd=None)
        with zz.open(filename, 'r') as f:
            result.content = f.read().decode('utf-8')
        return result
    #------------------------------------

    result = SimpleNamespace(content=None, filepath=None, is_recursive=False)

    # --- Ricerca Interna (ZIP/PYZ) ---
    if zipfile.is_zipfile(archive_file):
        ctx.logger.info("ZipFile searching for file: %s", filename)

        is_recursive=False
        z=zipfile.ZipFile(archive_file, "r")
        zip_content=z.namelist()

        ### - cerca direttamente il filename... se esiste
        if filename in zip_content:
            return extract_file(zz=z, filename=filename)

        # Cerchiamo nei search_paths interni allo zip
        for base_path in search_paths:

            ctx.logger.info("on base_path: [%s]", base_path)

            # Normalizziamo il path interno (niente drive letter, slash avanti)
            fpath = os.path.join(base_path, filename).replace('\\', '/') ### nel caso stessimo in Windows
            if fpath in zip_content:
                return extract_file(zz=z, filename=fpath)

            # Se ricorsivo, cerchiamo corrispondenze parziali
            if recursive:
                for member in zip_content:
                    if member.startswith(base_path) and member.endswith(filename):
                        result.is_recursive=True
                        return extract_file(zz=z, filename=member)
    return result




if __name__ == '__main__':
    zip_filename='/home/loreto/filu/Programming/gitREPO/lnSync/dist/lnSync.pyz'
    config_file='conf/@lnSync_config.yaml'
    # data=read_file_in_zip_prev(zip_filename, config_file)
    # print(data)
    data=zipReadFile(zip_filename, config_file)
    print(data)


