#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 30-04-2026 17.47.37
#


import sys; sys.dont_write_bytecode=True
# import os
import subprocess
import platform


### --------------------
### --- project modules
### --------------------
# from Source  import getGlobalVars



############################################################
# [[a,b,c], [c,d,e], [1,2], f] --> [a,b,c,d,e,f,1,2]
############################################################
def flatten_nested_list(lst: list=[]):
    output = []

    for item in lst:
        if isinstance(item, (list, tuple)):
            output.extend(item)
        elif item != '':  # Rimuove solo le stringhe vuote, mantiene lo 0
            output.append(item)

    return output

    '''
    _list=[]
    if isinstance(array, (list, tuple)):
        for item in array:
            if not item: continue
            if isinstance(item, list):
                _list.extend(item)
            else:
                _list.append(item)

    else:
        _list.append(array)

    # remove duplicates
    _list=list(dict.fromkeys(_list))

    return _list
    '''


def flatten_and_filter(seq, remove_whitespace_strings=False):
    result = []
    for item in seq:
        # Non iterare sulle stringhe: trattiamo solo liste/tuple come contenitori
        if isinstance(item, (list, tuple)):
            result.extend(flatten_and_filter(item, remove_whitespace_strings))
            continue

        # Filtri per "empty"
        if item is None:
            continue
        if isinstance(item, str):
            if remove_whitespace_strings:
                if item.strip() == '':
                    continue
            else:
                if item == '':
                    continue

        result.append(item)
    return result

# Esempio:
# lst = [1, [8, 9, 6], [4, 5], 0, '']
# print(flatten_and_filter(lst))  # [1, 8, 9, 6, 4, 5, 0]