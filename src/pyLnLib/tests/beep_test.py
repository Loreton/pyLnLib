#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 04-07-2026 09.05.00
#


import os
import sys
import time
from pathlib import Path

os.environ["LN_PROJECT_NAME"] = "beep_test"

from pyLnLib.colors import get_colors
from pyLnLib.keyboard_prompt import keyboardPrompt
from pyLnLib.context import get_context
from pyLnLib.beep import playBeep, get_beep_types

ctx = get_context()
C = get_colors()
sys.dont_write_bytecode = True



def beepTypes():
    sounds: dict = get_beep_types()

    # ============================================
    # --- start display sound names and create array of valid keys
    validKeys: list[str] = []
    soundKeys: list[str] = []
    TAB: str = " " * 8
    sound_names: list[str] = sorted(sounds.keys())

    for (index, name ) in enumerate(sound_names, 1):
        print(f"{TAB}{C.yellow}{index:2} - {C.cyanH}{name:20}: {sounds[name]}{C.reset}")
        validKeys.append(str(index))
        soundKeys.append(name)
    # --- end display sound names and create array of valid keys
    # ============================================

    keyb_msg: str= f"\n{C.yellow}select desired sound type{C.reset}"
    while True:
        choice = keyboardPrompt(text_msg=keyb_msg, validKeys=validKeys)
        beep_name = soundKeys[int(choice) - 1]  # type: ignore
        print(beep_name)
        playBeep(sounds[beep_name])


# -------------------------------
# Test
# -------------------------------
if __name__ == "__main__":
    # logger = ctx.get_logger()
    logger = ctx.my_logger
    logger.test(logger=logger)

    beepTypes()
