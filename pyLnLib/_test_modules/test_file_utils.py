#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 11-05-2026 09.40.40
#

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys; sys.dont_write_bytecode = True
import os
import zipfile
from pathlib import Path

from pyLnLib import lnLogger, gVars as ctx
from pyLnLib import searchFile, searchFileOnFS, searchFileInZip


# -------------------------------
# Test
# -------------------------------
if __name__ == "__main__":

    logger=lnLogger(name=Path(__file__).stem,
                            console_logger_level="info", ### --- default
                            file_logger_level="warning",
                            logging_dir=None, # no filehandler
                            threads=False)

    logger.test(logger=logger)
    ctx.logger=logger
    FINDFILE = True

    if FINDFILE:
        search_paths = ["conf/", "test/prova/"]
        search_paths = ["conf"]
        archive_file = '/home/loreto/filu/Programming/gitREPO/lnSync/dist/lnSync.pyz'
        recursive = True
        files_to_check=[
                        'rclone.conf', ## solo locale
                        'test/prova/test.txt', ## solo locale
                        'test.txt', ## solo locale
                        'conf/profiles/HD2510_500GB.yaml', # in zip
                        'conf/@lnSync_config.yaml', # in zip
                        'WD264F_500GB.yaml', # in zip
                        '/home/loreto/filu/Programming/gitREPO/lnSync/conf/rclone_options.yaml', # in zip
                        ]


        # cerca separatament in filesystem che in zipfile
        for filename in files_to_check:
            result = searchFileOnFS(filename=filename, search_paths=search_paths, recursive=recursive, extract_to='/tmp', stacklevel=-1)

            if not result.filepath:
                if zipfile.is_zipfile(archive_file):
                    result = searchFileInZip(filename=filename, archive_file=archive_file, search_paths=search_paths, recursive=recursive, extract_to="/tmp", stacklevel=-1)
                    if not result.filepath:
                        ctx.logger.error("filename: %s not found on filesysten neither in zipfile", filename, exit=True)
                else:
                    ctx.logger.warning("filename: %s not found on fileSystem", filename, exit=True)



        # cerca sia in filesystem che in zipfile
        for filename in files_to_check:
            res = searchFile(filename=filename,
                                  search_paths=search_paths,
                                  recursive=True,
                                  extract_to='/tmp',
                                  exit_on_not_found=True)
            if res.filepath:
                ctx.logger.notify(f"FOUND {res.filepath = }")
            else:
                ctx.logger.error(f"NOT FOUND {filename = }")

            print('\n'*2)



