#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 21-06-2026 17.42.30
#

from typing import List, Any, Union, Optional, Iterable, TypeVar
import sys
import subprocess
import platform

sys.dont_write_bytecode = True

# Type variable per generici
T = TypeVar('T')


############################################################
# [[a,b,c], [c,d,e], [1,2], f] --> [a,b,c,d,e,f,1,2]
############################################################
def flatten_nested_list(lst: Optional[List[Any]] = None) -> List[Any]:
    """
    Appiattisce una lista che può contenere elementi nidificati.

    Args:
        lst: Lista da appiattire, può contenere liste o tuple nidificate

    Returns:
        Lista appiattita con tutti gli elementi
    """
    if lst is None:
        lst = []

    output: List[Any] = []

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


def flatten_and_filter(
    seq: Iterable[Any],
    remove_whitespace_strings: bool = False
) -> List[Any]:
    """
    Appiattisce una sequenza e filtra i valori vuoti.

    Args:
        seq: Sequenza da appiattire (lista, tupla, o iterabile)
        remove_whitespace_strings: Se True, rimuove anche le stringhe che contengono solo spazi

    Returns:
        Lista appiattita e filtrata

    Examples:
        >>> flatten_and_filter([1, [8, 9, 6], [4, 5], 0, ''])
        [1, 8, 9, 6, 4, 5, 0]

        >>> flatten_and_filter([1, ['  ', 2], None, 3])
        [1, 2, 3]

        >>> flatten_and_filter([1, ['  ', 2], None, 3], remove_whitespace_strings=True)
        [1, 2, 3]
    """
    result: List[Any] = []

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


def flatten_and_filter_unique(
    seq: Iterable[Any],
    remove_whitespace_strings: bool = False
) -> List[Any]:
    """
    Appiattisce, filtra e rimuove i duplicati mantenendo l'ordine.

    Args:
        seq: Sequenza da appiattire
        remove_whitespace_strings: Se True, rimuove anche le stringhe con solo spazi

    Returns:
        Lista appiattita, filtrata e senza duplicati
    """
    flattened: List[Any] = flatten_and_filter(seq, remove_whitespace_strings)
    # Rimuove duplicati mantenendo l'ordine
    return list(dict.fromkeys(flattened))


def flatten_nested_list_safe(
    lst: Any,
    max_depth: int = 10
) -> List[Any]:
    """
    Appiattisce una lista con controllo della profondità massima.

    Args:
        lst: Lista da appiattire
        max_depth: Profondità massima di ricorsione

    Returns:
        Lista appiattita

    Raises:
        RecursionError: Se la profondità supera max_depth
    """
    output: List[Any] = []

    def _flatten(item: Any, depth: int) -> None:
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
def flatten_strings(seq: Iterable[Any]) -> List[str]:
    """
    Appiattisce e filtra restituendo solo stringhe.

    Args:
        seq: Sequenza da appiattire

    Returns:
        Lista di sole stringhe
    """
    flattened: List[Any] = flatten_and_filter(seq)
    return [str(item) for item in flattened if item is not None]


# Funzione per processare file paths
def flatten_paths(
    paths: Union[str, List[str], List[List[str]]]
) -> List[str]:
    """
    Appiattisce percorsi di file/directory.

    Args:
        paths: Stringa singola, lista di stringhe, o lista nidificata

    Returns:
        Lista di percorsi appiattiti
    """
    if isinstance(paths, str):
        return [paths]

    flattened: List[str] = []
    for item in paths:
        if isinstance(item, str):
            flattened.append(item)
        elif isinstance(item, (list, tuple)):
            flattened.extend(flatten_paths(item))

    return flattened


# Versione deprecata con tipo di default migliore
def flatten_nested_list_deprecated(lst: List[Any] = []) -> List[Any]:
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
    example1: List[Any] = [1, [8, 9, 6], [4, 5], 0, '']
    print(f"flatten_nested_list: {flatten_nested_list(example1)}")

    example2: List[Any] = [1, ['  ', 2], None, 3]
    print(f"flatten_and_filter: {flatten_and_filter(example2)}")
    print(f"flatten_and_filter (remove whitespace): {flatten_and_filter(example2, True)}")

    example3: List[Any] = [1, [2, 3], [3, 4], 5]
    print(f"flatten_and_filter_unique: {flatten_and_filter_unique(example3)}")
