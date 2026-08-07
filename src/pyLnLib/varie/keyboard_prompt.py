#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
#

import os
import sys
# from typing import List, Union

from .beep import playBeep
from ..colors import get_colors
C = get_colors()


# -------------------------------
def caller_info(message: str, stacknum: int = 2) -> str:
    from inspect import getframeinfo, stack

    caller = getframeinfo(stack()[stacknum][0])
    module_name: str = os.sep.join(caller.filename.split(os.sep)[-1:])
    msg: str = (
        f"\n\t{C.blueH}[{module_name}:{caller.lineno}] - {C.yellow}{message}{C.reset}"
    )
    return msg


#######################################################
# permette multiple choices
# return list[] of choice(s)
#######################################################
def keyboardPrompt( text_msg: str,
                    validKeys: list[str] = ["y", "n"],
                    exitKeys: list[str] = ["x", "q"],
                    multi_choices: bool = False, ) -> list[str]:
    """
    Funzione per input da tastiera con validazione.

    Args:
        text_msg: Messaggio da mostrare
        validKeys: Lista di chiavi valide
        exitKeys: Lista di chiavi per uscire
        multi_choices: Se True, permette scelte multiple (spazio separate)

    Returns:
        Se multi_choices è True: Lista di stringhe con le scelte
        Se multi_choices è False: Stringa con la scelta singola
    """

    # # -------------------------------
    def check_MC(choice: str, validKeys: List[str]) -> bool:
        if not choice:
            return False
        for ch in choice.split():
            if ch not in validKeys:
                print(f"ERROR: choice {ch} is not valid")
                return False
        return True

    # # -------------------------------

    # Gestione newline iniziale
    if text_msg.startswith("\n"):
        newLine: bool = True
        text_msg = text_msg[1:]
    else:
        newLine = False

    # Costruzione del messaggio
    text_msg += " - [" + "|".join(exitKeys) + "]quit ->: "
    text_msg = caller_info(message=text_msg)
    # import pdb; pdb.set_trace();  # by Loreto
    # Gestione ENTER key
    # if "ENTER" in exitKeys:
    #     exitKeys.append("")
    # if "ENTER" in validKeys:
    #     validKeys.append("")

    choice: str = ""

    while True:
        if newLine:
            print()

        choice = input(text_msg).lower()
        if choice == "":
            choice = "ENTER"
        # Controllo uscita
        if choice in exitKeys:
            print("Exiting on user request.")
            playBeep("INFO")
            sys.exit(0)

        # Controllo scelte multiple
        elif multi_choices and check_MC(choice, validKeys):
            break

        # Controllo scelta singola
        elif choice in validKeys:
            break

        else:
            print(
                "\n... please enter some valid key:",
                validKeys,
                "or exit key:",
                exitKeys,
            )

    # Ritorno appropriato
    if multi_choices:
        return choice.split()
    else:
        return [choice]


# Versione con default None per backward compatibility
def keyboardPrompt_with_default( text_msg: str,
                                    validKeys: list[str] | None = None,
                                    exitKeys: list[str] | None = None,
                                    multi_choices: bool = False, ) -> list[str]:
    """
    Versione con default None per evitare problemi di mutability.
    """
    if validKeys is None:
        validKeys = ["y", "n"]
    if exitKeys is None:
        exitKeys = ["x", "q"]

    return keyboardPrompt(text_msg, validKeys, exitKeys, multi_choices)
