#!/usr/bin/env python3
#
# Progamma per testare regex
#
# ruff: noqa: C401 - Unnecessary generator (rewrite as a set comprehension) help: Rewrite as a set comprehension (Ruff C401)
# ruff: noqa: 113 - Use `enumerate()` for index variable `index` in `for` loop (Ruff SIM113)
#


import sys


sys.dont_write_bytecode = True

import re
import time
from _collections_abc import Callable
# from itertools import permutations
# from dataclasses import dataclass, asdict
from typing import TypedDict

from pyLnLib.logger import get_logger
from pyLnLib.system import clean_doc
from pyLnLib.lndict import lnDict

logger = get_logger()



class RegexItemsDict(TypedDict, total=False):
    # - source_data sarà riempito solo per il primo item dell'occurrencies
    # - perché l'originale potrebbessere stato normalizzato
    source_data: str
    index: list[int] # contiene gli indici delle occurrencies. Se più di uno vuol dire che include altri context poi disabilitati
    ignore_case: bool

    matched_string: str
    matched_string_length: int

    start: int
    end: int

    context_string: str
    context_start: int
    context_end: int
    context_length: int # intesa come parte prima/dopo di start/end

    valid: bool


    # def to_dict(self) -> dict[str, object]:
    #     """Converte l'oggetto in un dizionario."""
    #     return asdict(self)

# def _escape_term(term: str, boundary: bool) -> str:
#     term = re.escape(term)
#     return rf"\b{term}\b" if boundary else term

def _escape_terms(terms: list[str], boundary: bool) -> list[str]:
    """
    Escape a list of terms and optionally wrap them with word boundaries.
    """
    wrapper = r"\b{}\b" if boundary else "{}"

    return [ wrapper.format(re.escape(term)) for term in terms ]


def this_function_executing_time(func: Callable) -> Callable:
    """
    Decorator per misurare il tempo di esecuzione di una funzione.
    Usa logger.notify() per il logging.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # logger = get_logger()
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end = time.perf_counter()
            elapsed = end - start

            # Messaggio con nome funzione e tempo
            logger.notify(
                f"[Function: {func.__name__}] eseguita in {elapsed:.6f} secondi",
                stacklevel=1  # Mostra il chiamante corretto
            )

    return wrapper


def processContext(occurrencies_list: list[RegexItemsDict]) -> list[RegexItemsDict]:
    n_occurrencies = len(occurrencies_list)
    if n_occurrencies <= 1:
        return occurrencies_list

    # context_len = occurrencies[0].context_length
    # source_data = occurrencies[0].source_data
    '''
        _range=list(range(n_occurrencies))
        _range=list(range(1, -1, -1))  # start=1, stop=-1 (escluso), step=-1
        _range=list(reversed(range(2)))  # [1, 0] range(2) è iterabile, reversed lo gestisce direttamente
        # devo fare un reversed range che si fermi al secondo (1) item
        _range=list(range(n_occurrencies, 0, -1))  # start=1, stop=0 (escluso), step=-1
        # devo fare un ascendente range che parti dal secondo (1) item
        _range=list(range(1, n_occurrencies, 1))  # start=1, stop=max (escluso), step=1
    '''

    _range=list(range(1, n_occurrencies, 1))  # start=1, stop=max (escluso), step=1  [1,2,3,...,n]
    for index in _range:
        # print(f"{index  = }")
        curr = occurrencies_list[index]
        prev = occurrencies_list[index-1]

        # ----------------------------------------------------
        # Se ci troviamo nelle condizioni che seguono allora
        # sil allargheranno i context_start context_end di curr per ospitare
        # gli spazi di prev e flagghiamo prev come invalido
        # prev !-----------------!
        # curr      !---------!            # (non credo che possa capitare...))
        # curr      !-----------------!
        # ----------------------------------------------------
        if prev.context_start <= curr.context_start <= prev.context_end: # se current rientra nel precedente context
            prev.valid = False
            curr.index.extend(prev.index)  # estendiamo l'indice di curr con quello di prev
            curr.context_start = prev.context_start  # allarghiamo il contesto attuale
            curr.context_end = max(curr.context_end, prev.context_end)

    return occurrencies_list

# def processContext_01(occurrencies: list[RegexItems], source_data: str) -> list[RegexItems]:
#     n_occurrencies = len(occurrencies)
#     # print(f"{n_occurrencies = }")
#     if n_occurrencies <= 1:
#         return occurrencies

#     context_len= occurrencies[0].context_length
#     data = source_data

#     for index in range(n_occurrencies):
#         # print(f"{index  = }")
#         curr = occurrencies[index]
#         if not curr.valid:
#             continue
#         if index+1 < n_occurrencies:
#             next=occurrencies[index+1]
#             if curr.start-context_len <= next.start <= curr.end+context_len: # se start_nextè  all'interno del primo range
#                 context = data[curr.start-context_len:next.end+context_len]
#                 next.valid = False
#             else:
#                 context = data[curr.start-context_len:curr.end+context_len]

#             curr.context = context

#     return occurrencies

#################################
#
#################################
def _processOccurrencies(p, source_data: str,
                            normalize_text: bool,
                            context_length: int=0,
                            ignore_case: bool=False) -> list[RegexItemsDict]:

    # logger = get_logger()
    # print(logger.name)
    logger.debug(clean_doc(f"""processItems called with:
        compiled_pattern={p}
        normalize_text={normalize_text}
        context_length={context_length}
        ignore_case={ignore_case}"""))

    occurrencies: list[lnDict] = []

    # Normalizza il testo
    if normalize_text:
        source_data = source_data.replace('\n', ' ')
        source_data = ' '.join(source_data.split())



    matches = [ (m.start(), m.end(), m.group()) for m in p.finditer(source_data) ]
    index: int=0
    for start, end, matched_string in matches:

        matched_string_length = len(matched_string)

        # context = matched_string # come default
        occurrence: RegexItemsDict = {
            "index": [index],
            "matched_string": matched_string,
            "start": start,
            "end": end,
            "valid": True,
            "ignore_case": ignore_case,
            # "context_string": source_data[start-context_length:end+context_length],
            "context_length": context_length,
            "context_start": start - context_length,
            "context_end": end + context_length,
            "matched_string_length": matched_string_length,
        }
        # if index==0:
        #     occurrence["source_data"] = source_data

        occurrencies.append(lnDict(occurrence))
        index += 1 # for index variable `index` in `for` loop (Ruff SIM113)

    return occurrencies

#################################
#
#################################
# @this_function_executing_time
def search_term( source_data: str, terms: list[str],
                *,
                boundary: bool = True,
                normalize_text: bool = False,
                ignore_case: bool = True,
                context_length: int = 0,
            ) -> list[RegexItemsDict]:
    """
    Search a single word/string in the source text.

    :param source_data: Source text.
    :param term: Word or string to search.
    :param boundary: If True, match whole words only.
    :param normalize_text: Normalize whitespace before searching.
    :param ignore_case: Case-insensitive search.
    :param context_length: Number of surrounding characters to include.
    :return: List of RegexItems.
    """
    # logger = get_logger()
    # print(logger.name)
        # source_data={source_data}
    logger.function(clean_doc(f"""search_term called with:
        terms={terms}
        normalize_text={normalize_text}
        context_length={context_length}
        ignore_case={ignore_case}"""))

    if len(terms) != 1:
        logger.error("search_term() requires exactly one search term\nwords received: %s", terms, exit=True)

    pattern = _escape_terms(terms, boundary)[0]

    flags = re.UNICODE
    if ignore_case:
        flags |= re.IGNORECASE

    p = re.compile(pattern, flags)
    # occurrencies = re.findall(pattern, source_data, flags=flags)
    # logger.debug("found occurrencies: %s", len(occurrencies))


    return _processOccurrencies(
        p,
        source_data=source_data,
        normalize_text=normalize_text,
        ignore_case=ignore_case,
    )
        # context_length=context_length,





# @this_function_executing_time
def replace(input_string: str, substring: str, replace_string: str, ignore_case: bool=False) -> str:
    f_inline =False
    flags = re.UNICODE
    if ignore_case:
        flags |= re.IGNORECASE
        inline_flag = '(?i)'
    else:
        inline_flag = ''

    if f_inline:
        result = re.sub(inline_flag + re.escape(substring), replace_string, input_string)
    else:
        compiled_pattern = re.compile(re.escape(substring), flags)
        result = compiled_pattern.sub(replace_string, input_string)

    return result





############################################################
# Builds a regex pattern from a list of terms with optional boundary matching
# Search words in any order
# :param terms: List of terms to match
# :param boundary: Whether to match whole word boundaries
# :return: A regex pattern string
############################################################
def _build_lookahead_pattern(terms: list[str], boundary: bool) -> str:

    # logger = get_logger()
    logger.function(clean_doc(f"""build_lookahead_pattern called with:
        terms={terms}
        boundary={boundary}"""))


    escaped = _escape_terms(terms, boundary)
    return "".join( rf"(?=.*{term})" for term in escaped ) + ".*"


############################################################
# Builds a regex pattern from a list of terms with optional boundary matching
# Search words in sequential order
# :param terms: List of terms to match
# :param boundary: Whether to match whole word boundaries
# :return: A regex pattern string
############################################################
def _build_sequence_pattern(terms: list[str], boundary: bool) -> str:

    # logger = get_logger()
    logger.function(clean_doc(f"""build_sequence_pattern called with:
        terms={terms}
        boundary={boundary}"""))

    escaped = _escape_terms(terms, boundary)
    return ".*".join(escaped)


######################################################
# Builds a regex pattern for near terms search
######################################################
def _build_near_words(terms: list[str],
                        max_words_between: int,
                        boundary: bool = True,
                        any_order: bool = False,
                    ) -> str:
    """
    Builds a regex pattern to search two terms within a maximum number
    of words.

    :param terms: List containing exactly two words/strings.
    :param max_words_between: Maximum number of words between the terms.
    :param boundary: Match whole words if True, otherwise substrings.
    :param any_order: Search terms in both directions.
    :return: Regex pattern string.
    """

    # logger = get_logger()
    logger.function(clean_doc(f"""build_near_pattern called with:
        terms={terms}
        max_words_between={max_words_between}
        any_order={any_order}
        boundary={boundary}"""))

    if len(terms) != 2:
        logger.error(f"NEAR search requires exactly two terms: got {terms}",exit=True, stacklevel=1)
        # raise ValueError("NEAR search requires exactly two terms")

    # wrapper = r"\b{}\b" if boundary else "{}"
    escaped = _escape_terms(terms, boundary)
    term1, term2 = escaped

    separator = rf"(?:\W+\w+){{0,{max_words_between}}}\W+"

    forward = term1 + separator + term2

    if any_order:
        backward = term2 + separator + term1
        return rf"(?:{forward}|{backward})"

    return forward



def _build_multi_near_words( terms: list,
                            max_words_between: int,
                            ):
    logger.function(clean_doc(f"""_build_multi_near_words:
            terms={terms}
            max_words_between={max_words_between}"""))


    # Validazione input
    if max_words_between < 0:
        logger.error("Input non valido. Fornire un intero non negativo per la distanza delle words. %s", max_words_between, exit=True)

    min_words_between =  0


    # Costruisci il pattern come nel tuo codice ma per N parole
    pattern_parts = [rf'\b{terms[0]}\b']
    for i in range(1, len(terms)):
        # Usa \W+ invece di \s+ per essere più flessibile con la punteggiatura
        pattern_parts.append(rf'\W+(?:\w+\W+){{{min_words_between},{max_words_between}}}{terms[i]}\b')

    pattern = ''.join(pattern_parts)

    return pattern











# @this_function_executing_time
def and_search(source_data: str,
                words_list: list,
                normalize_text: bool = False,
                max_words_between: int | None = None,
                ignore_case: bool = False,
                any_order: bool = False,
                context_length: int = 0,
                boundary: bool=False) -> list[RegexItemsDict]:
    """
    Cerca tutte le parole/string nel testo devono seistere.
    """
    # logger=get_logger()
    logger.function(clean_doc(f"""and_search called with:
        words_list={words_list}
        normalize_text={normalize_text}
        max_words_between={max_words_between}
        ignore_case={ignore_case}
        any_order={any_order}
        context_length={context_length}
        boundary={boundary}"""))


    # logger.info("processItems called with:\nnormalize_text=%s\ncontext_length=%s", normalize_text, context_length)
    if max_words_between is not None:
        if len(words_list) > 2:
            pattern = _build_multi_near_words(terms=words_list,
                                        max_words_between=max_words_between)
        else:
            pattern = _build_near_words(terms=words_list,
                                        max_words_between=max_words_between,
                                        any_order=any_order,
                                        boundary=boundary)
    elif any_order:
        pattern = _build_lookahead_pattern(terms=words_list, boundary=boundary)
    else:
        pattern = _build_sequence_pattern(terms=words_list, boundary=boundary)


    flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE
    p = re.compile(pattern, flags=flags)
    occurrencies_list = _processOccurrencies(p,
        source_data=source_data,
        normalize_text=normalize_text,
        context_length=context_length,
        ignore_case=ignore_case)


    if len(occurrencies_list) > 0:
        # -facciamo il sort per context_start
        # occurrencies = sorted(occurrencies_list, key=lambda x: x["context_start"], reverse=False)
        from operator import itemgetter
        occurrencies = sorted(occurrencies_list, key=itemgetter("context_start"), reverse=False) # più veloce

        # - ins eriamo nella prima occurrency il source_data
        occurrencies[0]["source_data"] = source_data  # - il text sorgente lo trovo nella prima occurrency.
    else:
        occurrencies = []

    return occurrencies





# @this_function_executing_time
def or_search(source_data: str,
                words_list: list,
                normalize_text: bool = False,
                ignore_case: bool = False,
                context_length: int = 0,
                boundary: bool=False) -> list[RegexItemsDict]:
    """
    Cerca tutte le parole/string nel testo devono seistere.
    """
    # logger = get_logger()
    logger.function(clean_doc(f"""or_search called with:
        words_list={words_list}
        normalize_text={normalize_text}
        ignore_case={ignore_case}
        context_length={context_length}
        boundary={boundary}
        """))

    # facciamolo solo una volta
    if normalize_text:
        source_data = source_data.replace('\n', ' ')
        normalize_text=False

    flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE

    occurrencies_list = []
    for term in words_list:
        logger.info("searching for term: %s", term)
        pattern = _build_sequence_pattern(terms=[term], boundary=boundary)
        # matches = re.findall(pattern, source_data, flags=flags)
        p = re.compile(pattern, flags=flags)
        positions = [ (m.start(), m.end()) for m in p.finditer(source_data) ]
        logger.info("   found: %s matches", len(positions))
        result = _processOccurrencies(p,
                source_data=source_data,
                normalize_text=normalize_text,
                context_length=context_length,
                ignore_case=ignore_case)
        occurrencies_list.extend(result)


    if len(occurrencies_list) > 0:
        # -facciamo il sort per context_start
        # occurrencies = sorted(occurrencies_list, key=lambda x: x["context_start"], reverse=False)
        from operator import itemgetter
        occurrencies = sorted(occurrencies_list, key=itemgetter("context_start"), reverse=False) # più veloce

        # - ins eriamo nella prima occurrency il source_data
        occurrencies[0]["source_data"] = source_data  # - il text sorgente lo trovo nella prima occurrency.
    else:
        occurrencies = []

    return occurrencies
