#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# updated by ...: Loreto Notarantonio
# Version ......: 08-01-2021 18.10.41
#
import  sys; sys.dont_write_bytecode = True
import zipfile, io

try:
    from .context import gVars as ctx
except:
    ctx = None


def zipNameList(zip_filename):
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




def zipReadFile(filename: str, archive_file: str, extraction_dir: str='/tmp'):
    content=None
    try:
        if zipfile.is_zipfile(zip_filename):
            with zipfile.ZipFile(zip_filename, 'r') as z:
                with z.open(filename) as f:
                    content = f.read().decode('utf-8')

    except Exception as e:
        if ctx:
            ctx.logger.error("Errore nel caricamento di %s: %s", target_file, str(e))
        else:
            # - per debug... se questo script lanciato standalone
            print("\t\tErrore nel caricamento di %s: %s", target_file, str(e))

    return content


############################################################
#
############################################################
# def zipExtractFile(archive_file: str, filename: str, content: bool=False, search_paths: list=[], out_dir: str='/tmp'):
def zipExtractFile(archive_file: str, filename: str, out_dir: str='/tmp'):
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

    # """ check it its a zip file """
    # if zipfile.is_zipfile(archive_file):
    #     zFile=zipfile.ZipFile(archive_file, "r")
    #     zFileNamelist=zFile.namelist()
    #     search_paths.insert(0, '')
    #     for path in search_paths:
    #         filepath=os.path.join(path, filename)
    #         if filepath in zFileNamelist:
    #             if content:
    #                 buffer=io.BytesIO(zFile.read(filepath))
    #                 content=buffer.read()
    #                 return content
    #             else:
    #                 zFile.extract(member=filepath, path=out_dir, pwd=None)
    #                 ftemp=f'{out_dir}/{filepath}'
    #                 return ftemp

    # return None





if __name__ == '__main__':
    zip_filename='/home/loreto/filu/Programming/gitREPO/lnSync/dist/lnSync.pyz'
    config_file='conf/@lnSync_config.yaml'
    # data=read_file_in_zip_prev(zip_filename, config_file)
    # print(data)
    data=zipReadFile(zip_filename, config_file)
    print(data)


