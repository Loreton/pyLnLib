#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 12-06-2026 20.24.21
#

import sys
import os

from .context import gVars as gv, Colors as C
from .beep import playBeep




# -------------------------------
def caller_info(message, stacknum=2):
    from inspect import getframeinfo, stack
    caller = getframeinfo(stack()[stacknum][0])
    module_name=os.sep.join(caller.filename.split(os.sep)[-1:])
    msg=f"\n\t{C.blueH}[{module_name}:{caller.lineno}] - {C.yellow}{message}{C.reset}"
    return msg


#######################################################
# permette multiple choices
# return list[] of choice(s)
#######################################################
def keyboardPrompt(text_msg: str, validKeys: list=["y", "n"], exitKeys: list=["x", "q"], multi_choices: bool=False) -> list:
    logger = gv.logger
    # # -------------------------------
    def check_MC():
        if not choice:
            # print("ERROR: no choice entered")
            return False
        for ch in choice.split():
            if ch not in validKeys:
                print(f"ERROR: choice %{ch} is not valid")
                return False
        return True
    # # -------------------------------


    if text_msg[0] == '\n':
        newLine = True
        text_msg = text_msg[1:]
    else:
        newLine = False

    text_msg+= " - [" + '|'.join(exitKeys) + "]quit ->: "
    text_msg=caller_info(message=text_msg)
    if "ENTER" in exitKeys: exitKeys.append("")
    if "ENTER" in validKeys: validKeys.append("")

    while True:
        if newLine: print()
        choice=input(text_msg).lower()

        if choice in exitKeys: # diamo priorità all'uscita
            print("Exiting on user request.")
            playBeep()
            sys.exit(0)

        elif multi_choices and check_MC():
            break

        elif choice in validKeys:
            break

        else:
            print('\n... please enter some valid key:', validKeys, "or exit key:", exitKeys)

    return choice.split() if multi_choices else choice


