#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
#

import sys; sys.dont_write_bytecode = True
from collections.abc import Iterable
from typing import TypeVar



# Type variable per generici
T = TypeVar('T')


############################################################
# [[a,b,c], [c,d,e], [1,2], f] --> [a,b,c,d,e,f,1,2]
############################################################
def flatten_nested_list(lst: list[any]|None = None) -> list[any]:
    """
    Appiattisce una lista che può contenere elementi nidificati.

    Args:
        lst: lista da appiattire, può contenere liste o tuple nidificate

    Returns:
        lista appiattita con tutti gli elementi
    """
    if lst is None:
        lst = []

    output: list[any] = []

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


def flatten_and_filter( seq: Iterable[any], remove_whitespace_strings: bool = False ) -> list[any]:
    """
    Appiattisce una sequenza e filtra i valori vuoti.

    Args:
        seq: Sequenza da appiattire (lista, tupla, o iterabile)
        remove_whitespace_strings: Se True, rimuove anche le stringhe che contengono solo spazi

    Returns:
        lista appiattita e filtrata

    Examples:
        >>> flatten_and_filter([1, [8, 9, 6], [4, 5], 0, ''])
        [1, 8, 9, 6, 4, 5, 0]

        >>> flatten_and_filter([1, ['  ', 2], None, 3])
        [1, 2, 3]

        >>> flatten_and_filter([1, ['  ', 2], None, 3], remove_whitespace_strings=True)
        [1, 2, 3]
    """
    result: list[any] = []

    for item in seq:
        # Non iterare sulle stringhe: trattiamo solo liste/tuple come contenitori
        if isinstance(item, (list, tuple)):
            result.extend(flatten_and_filter(item, remove_whitespace_strings))
            continue

        # Filtri per valori vuoti
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


def flatten_and_filter_unique( seq: Iterable[any], remove_whitespace_strings: bool = False ) -> list[any]:
    """
    Appiattisce, filtra e rimuove i duplicati mantenendo l'ordine.

    Args:
        seq: Sequenza da appiattire
        remove_whitespace_strings: Se True, rimuove anche le stringhe con solo spazi

    Returns:
        lista appiattita, filtrata e senza duplicati
    """
    flattened: list[any] = flatten_and_filter(seq, remove_whitespace_strings)
    # Rimuove duplicati mantenendo l'ordine
    return list(dict.fromkeys(flattened))


def flatten_nested_list_safe( lst: any, max_depth: int = 10 ) -> list[any]:
    """
    Appiattisce una lista con controllo della profondità massima.

    Args:
        lst: lista da appiattire
        max_depth: Profondità massima di ricorsione

    Returns:
        lista appiattita

    Raises:
        RecursionError: Se la profondità supera max_depth
    """
    output: list[any] = []

    def _flatten(item: any, depth: int) -> None:
        if depth > max_depth:
            raise RecursionError(f"Profondità massima ({max_depth}) superata")

        if isinstance(item, (list, tuple)):
            for sub_item in item:
                _flatten(sub_item, depth + 1)
        elif item is not None and item != '':
            output.append(item)

    _flatten(lst, 0)
    return output


# Utility per tipi di ritorno specifici
def flatten_strings(seq: Iterable[any]) -> list[str]:
    """
    Appiattisce e filtra restituendo solo stringhe.

    Args:
        seq: Sequenza da appiattire

    Returns:
        lista di sole stringhe
    """
    flattened: list[any] = flatten_and_filter(seq)
    return [str(item) for item in flattened if item is not None]


# Funzione per processare file paths
def flatten_paths( paths: str|list[str]|list[list[str]]) -> list[str]:
    """
    Appiattisce percorsi di file/directory.

    Args:
        paths: Stringa singola, lista di stringhe, o lista nidificata

    Returns:
        lista di percorsi appiattiti
    """
    if isinstance(paths, str):
        return [paths]

    flattened: list[str] = []
    for item in paths:
        if isinstance(item, str):
            flattened.append(item)
        elif isinstance(item, (list, tuple)):
            flattened.extend(flatten_paths(item))

    return flattened


# Versione deprecata con tipo di default migliore
def flatten_nested_list_deprecated(lst: list[any]) -> list[any]:
    """
    Versione deprecata: usa flatten_nested_list invece.
    """
    import warnings
    warnings.warn(
        "flatten_nested_list_deprecated è deprecata, usa flatten_nested_list",
        DeprecationWarning,
        stacklevel=2
    )
    return flatten_nested_list(lst)


# Se la funzione è usata come modulo
if __name__ == "__main__":
    # Test esempi
    example1: list[any] = [1, [8, 9, 6], [4, 5], 0, '']
    print(f"flatten_nested_list: {flatten_nested_list(example1)}")

    example2: list[any] = [1, ['  ', 2], None, 3]
    print(f"flatten_and_filter: {flatten_and_filter(example2)}")
    print(f"flatten_and_filter (remove whitespace): {flatten_and_filter(example2, True)}")

    example3: list[any] = [1, [2, 3], [3, 4], 5]
    print(f"flatten_and_filter_unique: {flatten_and_filter_unique(example3)}")
