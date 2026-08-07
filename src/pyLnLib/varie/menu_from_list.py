import os
import sys
# from typing import List, Union

from .keyboard_prompt import keyboardPrompt
from ..colors import get_colors
C = get_colors()

def menu_select_from_list(data: list[str]) -> int:
    items = len(data)
    choice: int = 0

    if items > 1:
        valid_keys: list[str]=[]
        for index, item in enumerate(data, 1):
            print(f"\t{C.white}{index:1}. - {C.cyanH}{item}")
            valid_keys.append(str(index))

        l_choice = keyboardPrompt(text_msg="please select library number", validKeys=valid_keys )
        choice = int(l_choice[0]) -1

    return choice
