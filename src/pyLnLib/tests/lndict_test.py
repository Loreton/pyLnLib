#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 05-07-2026 14.05.20
#


import sys; sys.dont_write_bytecode = True
import os
import time
# from pathlib import Path

os.environ["LN_PROJECT_NAME"] = "lndict_test"
from pyLnLib.context import gVars as ctx, get_logger
from pyLnLib import lnDict, LnDictResolver, get_project_vars


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

def test_attributes():
    import yaml

    config_str: dict = yaml.load(my_dict, Loader=yaml.FullLoader)
    config = lnDict(data=config_str)

    print("=== TEST 1: attributes ===")
    print("config.main.rclone_config_file        :", config.main.rclone_config_file)           # rclone.conf ✅
    print("config.main.get('rclone_config_file') :", config.main.get("rclone_config_file"))    # rclone.conf ✅
    print("config.get('main.rclone_config_file') :", config.get("main.rclone_config_file"))    # rclone.conf ✅ (ORA FUNZIONA!)
    print("config['main.rclone_config_file'])    :", config["main.rclone_config_file"])        # rclone.conf ✅
    print()



def test_recursive_update():
    # Test per vedere recursive
    data = {
        "level1": {
            "level2": {
                "level3": "valore"
            }
        }
    }


    print("=== TEST 1: update() ===")
    config1 = lnDict()
    config1.update(data)
    print("config1.level1:               ",type(config1.level1))           # lnDict
    print("config1.level1.level2:        ",type(config1.level1.level2))  # ???
    print("config1.level1.level2.level3: ",type(config1.level1.level2.level3))  # str


    print("\n=== TEST 2: costruttore ===")
    config3 = lnDict(data)
    print("config3.level1:               ",type(config3.level1))           # lnDict
    print("config3.level1.level2:        ",type(config3.level1.level2))  # lnDict


    # Test con aggiornamenti successivi
    config = lnDict({"existing": "value"})

    # CASO 1: update() - CONVERSAZIONE SOLO PRIMO LIVELLO
    new_data = {
        "new": {
            "deep": {
                "nested": "data"
            }
        }
    }
    config.update(new_data)
    print("config.new:                   ", type(config["new"]))              # lnDict ✅
    print("config.new.deep:              ", type(config["new"]["deep"]))      # dict ❌ (NON convertito!)


def test_project_vars():
    # Test per vedere recursive
    data = {
        "level1": {
            "level2": {
                "level3": "valore"
            }
        }
    }


    print("=== TEST 1: project_vars() ===")
    prjVars = get_project_vars()


    prjVars.update(data)
    print("prjVars.level1:               ",type(prjVars.level1))           # lnDict
    print("prjVars.level1.level2:        ",type(prjVars.level1.level2))  # ???
    print("prjVars.level1.level2.level3: ",type(prjVars.level1.level2.level3))  # str




if __name__ == "__main__":
    test_attributes()
    test_recursive_update()
    test_project_vars()
