#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 04-07-2026 18.55.56
#


import sys; sys.dont_write_bytecode = True
import os
import time
from pathlib import Path

os.environ["LN_PROJECT_NAME"] = "lndict_test"
from pyLnLib.context import gVars as ctx, get_logger
from pyLnLib import lnDict, LnDictResolver


logger = get_logger()



my_dict='''
    main:
      rclone_config_file: rclone.conf
      temp_dir: /tmp/lnsync

      profiles:
        filesystem_HD2510_500GB:
          dirs_to_sync:
            _dir0:
              from: /home/loreto/filu
              to: /media/loreto/HD2510_500GB/filu
              exclude_patterns:
              - dummyxxxx
              folders:
              - Programming      10         unlimited        60
              - myData           10         unlimited        60
          node_in_rclone_clonf: filesystem
          sync_program: rsync
'''

if __name__ == "__main__":
    import yaml
    logger.test(logger=logger)

    config_str: dict = yaml.load(my_dict, Loader=yaml.FullLoader)
    config = lnDict(data=config_str)

    # TUTTI FUNZIONANO!
    print(config.main.rclone_config_file)           # rclone.conf ✅
    print(config.main.get("rclone_config_file"))    # rclone.conf ✅
    print(config.get("main.rclone_config_file"))    # rclone.conf ✅ (ORA FUNZIONA!)
    print(config["main.rclone_config_file"])        # rclone.conf ✅
# -------------------------------
# Test
# -------------------------------
# if __name__ == "__main__":
#     import yaml
#     logger.test(logger=logger)

#     config_str: dict = yaml.load(my_dict, Loader=yaml.FullLoader)
#     config: dict = lnDict(data=config_str)
#     print(config)
#     print(config.main.rclone_config_file)
#     print(config.main.get("rclone_config_file"))
#     print(config.get("main.rclone_config_file"))
#     # import pdb; pdb.set_trace();  # by Loreto
