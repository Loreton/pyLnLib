import os
import sys
# from typing import List, Union

from .keyboard_prompt import keyboardPrompt
from ..colors import get_colors
C = get_colors()



######################################################################
# - select item from list[str]
# - default set index for default choice if "ENTER" is pressed
# - return tuple(index, and list_item)
######################################################################
def menu_select_from_list(data: list[str], default: int = 0) -> tuple[int, str]:
    items = len(data)
    choice: int = 0

    if items > 1:
        valid_keys: list[str]=[]
        # - print list of items
        for index, item in enumerate(data, 1):
            if index == default:
                print(f"\t{C.white}*{index:1}. - {C.cyanH}{item}")
            else:
                print(f"\t{C.white} {index:1}. - {C.cyanH}{item}")
            valid_keys.append(str(index))

        valid_keys.append("ENTER")
        valid_keys.append("s")
        l_choice = keyboardPrompt(text_msg="please select library number", validKeys=valid_keys )

        item = ""
        if l_choice[0] == "ENTER":
            choice = default-1
            item = data[choice]
        elif l_choice[0] == "s":
            choice = -1
        else:
            choice = int(l_choice[0]) - 1
            item = data[choice]

    return choice, item


######################################################################
# - select item from list[str]
# - default set index for default choice if "ENTER" is pressed
# - return tuple(index, and list_item)
######################################################################
def select_from_list(data: list[str], text_msg: str = "please select item number", extra_validKeys: list=[], default: int = 0) -> str:
    items = len(data)
    choice: int = 0

    if items > 1:
        valid_keys: list[str]=[]
        # - print list of items
        for index, item in enumerate(data, 1):
            if index == default:
                print(f"\t{C.white}*{index:1}. - {C.cyanH}{item}")
            else:
                print(f"\t{C.white} {index:1}. - {C.cyanH}{item}")
            valid_keys.append(str(index))



        valid_keys.extend(extra_validKeys)
        choosed_item = keyboardPrompt(text_msg=text_msg, validKeys=valid_keys )

        # choosed_item = ""
        if choosed_item[0] == "ENTER":
            choice = default-1
            choosed_item = data[choice]
        # elif l_choice[0] == "s":
        #     choice = -1
        #     choosed_item = ""
        elif any(chr.isdigit() for chr in choosed_item[0]):
            choice = int(choosed_item[0]) - 1
            choosed_item = data[choice]
        else:
            choosed_item = choosed_item[0]

    return choosed_item
