#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 09-06-2026 15.10.16
#

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys; sys.dont_write_bytecode = True
import os
from pathlib import Path

from pyLnLib import gVars as ctx
import pyLnLib as lnLib ### usiamo questo....
# from pyLnLib import loadIni, writeIni, updateIniKey


###############################################
# Example usage
###############################################
if __name__ == "__main__":
    logger=lnLib.lnLogger(name=Path(__file__).stem, console_logger_level="trace")
    ctx.logger=logger
    logger.test(logger=logger)


    # Example dictionary
    example_ini_dict = {
        'Database': {
            'host': 'localhost',
            'port': '3306',
            'user': 'admin',
            'password': 'secret123'
        },
        'Logging': {
            'level': 'INFO',
            'file': '/var/log/app.log',
            'max_size': '10MB'
        },
        'Settings': {
            'debug': 'true',
            'timeout': '30'
        }
    }

    # Write to file
    success = lnLib.writeIni(example_ini_dict, 'example.ini')

    if success:
        print("INI file created successfully")

        # Read it back to verify
        loaded_dict = lnLib.loadIni(filepath='example.ini')
        print("\nLoaded dictionary:")
        print(loaded_dict)

        # Update a single key
        lnLib.updateIniKey('example.ini', 'Database', 'port', '5432')
        print("\nUpdated port to 5432")