#!/usr/bin/env python3
#
# Progamma per testare regex
#
# ruff: noqa: C401 - Unnecessary generator (rewrite as a set comprehension) help: Rewrite as a set comprehension (Ruff C401)
#


from audioop import mul
import sys; sys.dont_write_bytecode = True

import re
import time
from itertools import permutations

from pyLnLib import get_logger
logger = get_logger()


# import time
from functools import wraps
# from typing import Callable

def this_function_executing_time(func: Callable) -> Callable:
    """
    Decorator per misurare il tempo di esecuzione di una funzione.
    Usa logger.notify() per il logging.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
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
                stacklevel=3  # Mostra il chiamante corretto
            )

    return wrapper




from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class RegexItems:
    index: int
    matched_string: str
    start: int
    end: int
    context: str


# def build_pattern(terms: list[str], boundary: bool) -> str:
#     wrapper = r"\b{}\b" if boundary else "{}"

#     return "".join(
#         rf"(?=.*{wrapper.format(re.escape(term))})"
#         for term in terms
#     )

############################################################
# Builds a regex pattern from a list of terms with optional boundary matching
# Search words in any order
# :param terms: List of terms to match
# :param boundary: Whether to match whole word boundaries
# :return: A regex pattern string
############################################################
def build_lookahead_pattern(terms: list[str], boundary: bool) -> str:
    wrapper = r"\b{}\b" if boundary else "{}"

    return (
        "".join(
            rf"(?=.*{wrapper.format(re.escape(term))})"
            for term in terms
        )
        + r".*"
    )

############################################################
# Builds a regex pattern from a list of terms with optional boundary matching
# Search words in sequential order
# :param terms: List of terms to match
# :param boundary: Whether to match whole word boundaries
# :return: A regex pattern string
############################################################
def build_sequence_pattern(terms: list[str], boundary: bool) -> str:
    wrapper = r"\b{}\b" if boundary else "{}"

    return ".*".join(
        wrapper.format(re.escape(term))
        for term in terms
    )




#################################
# return: {
#           {
#                "matched_string": xx,
#                "start": xx,
#                "end": yy,
#                "context": "text"
#            }
#          }
#################################
# @this_function_executing_time
def _processItems(p, source_data: str, context_length: int=0) -> list:
    occurrencies = []

    for match in p.finditer(source_data):
        start, end = match.span()
        matched_string = match.group()

        # Estrai il contesto
        if context_length > 0:
            start_context = max(0, start - context_length)
            end_context = min(len(source_data), end + context_length)
            context = source_data[start_context:end_context]
        else:
            context = matched_string

        occurrence = RegexItems(
            index=len(occurrencies),
            matched_string=matched_string,
            start=start,
            end=end,
            context=context
        )

        occurrencies.append(occurrence)

    return occurrencies

@this_function_executing_time
def search_anywhere(source_data: str, words_list: list, normalize_text: bool, ignore_case: bool, context_length: int):
    """
    Cerca le parole ovunque nel testo (senza vincoli di distanza).
    Usa lookahead per trovare tutte le parole.
    """
    flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE

    # Normalizza il testo
    if normalize_text:
        source_data = ' '.join(source_data.split())

    # Crea un pattern che cerca tutte le parole in qualsiasi punto
    # Usa lookahead positivo per ogni parola
    lookaheads = ''.join([rf'(?=.*\b{re.escape(word)}\b)' for word in words_list])
    pattern = lookaheads + r'.*'

    p = re.compile(pattern, flags=flags)
    return _processItems(p=p, source_data=source_data, context_length=context_length)


@this_function_executing_time
def multi_near_words(source_data: str,
                            words_list: list,
                            words_distance: list | None = None,
                            normalize_text: bool=False,
                            ignore_case: bool=True,
                            context_length: int=0):

    # Validazione input
    if not isinstance(source_data, str):
        logger.warning("Input non valido. No source data.")
        return {}

    if words_distance is None:
        return search_anywhere(source_data=source_data, normalize_text=normalize_text, words_list=words_list, ignore_case=ignore_case, context_length=context_length)

    if not isinstance(words_distance, list) or len(words_distance) != 2:
        logger.warning("Input non valido. Fornire una lista di due interi [min, max] per la distanza delle words.")
        return []

    if not isinstance(words_list, list) or len(words_list) < 2:
        logger.warning("Input non valido. Fornire una lista di almeno due parole.")
        return []


    # Normalizza il testo
    if normalize_text:
        source_data = ' '.join(source_data.split())

    py_flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE

    min_words, max_words = words_distance
    # if min_words == 0: min_words = 1
    # if max_words == 0: max_words = 999999999
    # Costruisci il pattern come nel tuo codice ma per N parole
    pattern_parts = [rf'\b{words_list[0]}\b']

    for i in range(1, len(words_list)):
        # Usa \W+ invece di \s+ per essere più flessibile con la punteggiatura
        pattern_parts.append(rf'\W+(?:\w+\W+){{{min_words},{max_words}}}{words_list[i]}\b')

    pattern = ''.join(pattern_parts)

    logger.info("Pattern: %s", pattern)
    # Compila l'espressione regolare
    p = re.compile(pattern, flags=py_flags)

    return _processItems(p=p, source_data=source_data, context_length=context_length)



@this_function_executing_time
def multi_near_words_any_order(source_data: str,
                              words_list: list,
                              words_distance: list,
                              normalize_text: bool=False,
                              ignore_case: bool=True,
                              context_length: int=0):

    if normalize_text:
        source_data = ' '.join(source_data.split())

    min_words, max_words = words_distance
    if min_words == 0: min_words = 1
    if max_words == 0: max_words = 999999999
    # Se abbiamo poche parole, usa le permutazioni (più veloce)
    if len(words_list) <= 4:
        py_flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE
        middle_pattern = rf'\W+(?:\w+\W+){{{min_words},{max_words}}}'

        all_patterns = []
        for perm in permutations(words_list):
            pattern_parts = [rf'\b{perm[0]}\b']
            for i in range(1, len(perm)):
                pattern_parts.append(rf'{middle_pattern}{perm[i]}\b')
            all_patterns.append(''.join(pattern_parts))

        combined_pattern = '|'.join(all_patterns)
        p = re.compile(combined_pattern, flags=py_flags)
        logger.info("Pattern: %s", combined_pattern)

        return _processItems(p=p, source_data=source_data, context_length=context_length)

    else:
        # Per molte parole, usa l'approccio token-based
        return _multi_near_words_token_based(source_data, words_list, words_distance,
                                            normalize_text, ignore_case, context_length)

# @this_function_executing_time
def _multi_near_words_token_based(source_data: str,
                                 words_list: list,
                                 words_distance: list,
                                 normalize_text: bool=False,
                                 ignore_case: bool=True,
                                 context_length: int=0):

    if normalize_text:
        source_data = ' '.join(source_data.split())

    min_words, max_words = words_distance
    if min_words == 0: min_words = 1
    if max_words == 0: max_words = 999999999

    results = []

    # Tokenizza il testo
    word_pattern = re.compile(r'\b\w+\b', re.UNICODE)
    matches = list(word_pattern.finditer(source_data))
    tokens = [m.group() for m in matches]

    words_set = set(word.lower() for word in words_list) # ruff C401

    for i in range(len(tokens)):
        if tokens[i].lower() not in words_set:
            continue

        for j in range(i + min_words + 1, min(i + max_words + 2, len(tokens))):
            if tokens[j].lower() not in words_set:
                continue

            found = set()
            for k in range(i, j + 1):
                if tokens[k].lower() in words_set:
                    found.add(tokens[k].lower())

            if found == words_set:
                start_pos = matches[i].start()
                end_pos = matches[j].end()

                matched = ' '.join(tokens[i:j+1])

                if context_length > 0:
                    start_ctx = max(0, start_pos - context_length)
                    end_ctx = min(len(source_data), end_pos + context_length)
                    context = source_data[start_ctx:end_ctx]
                else:
                    context = matched

                results.append(RegexItems(
                    index=len(results),
                    matched_string=matched,
                    start=start_pos,
                    end=end_pos,
                    context=context
                ))

    return results


def and_search(source_data: str,
                        words_list: list[str],
                        words_distance: list,
                        any_order: bool = False,
                        ignore_case: bool = True,
                        normalize_text: bool = False,
                        context_length: int = 0) -> list[RegexItems]:
    """
    Versione ottimizzata che riutilizza le tue funzioni esistenti.
    """
    if not source_data or not words_list or len(words_list) < 2:
        return []

    # if normalize_text:
        # source_data = ' '.join(source_data.split())
    # Usa le tue funzioni esistenti
    if any_order:
        # Se vuoi qualsiasi ordine
        return multi_near_words_any_order(
            source_data=source_data,
            words_list=words_list,
            words_distance=words_distance,
            ignore_case=ignore_case,
            normalize_text=normalize_text,
            context_length=context_length)
    else:
        # Usa la tua multi_near_words per l'ordine specificato
        return multi_near_words(
            source_data=source_data,
            words_list=words_list,
            words_distance=words_distance,
            normalize_text=normalize_text,
            ignore_case=ignore_case,
            context_length=context_length
        )

def _and_search_with_permutations(text: str,
                                 words: list[str],
                                 max_distance: int | None = None,
                                 ignore_case: bool = True,
                                 context_length: int = 0) -> list[RegexItems]:
    """
    Cerca le parole in qualsiasi ordine usando permutazioni.
    """
    if len(words) > 4:
        # Per molte parole, usa l'approccio token-based
        return _and_search_token_based(text, words, max_distance, ignore_case, context_length)

    flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE
    escaped_words = [re.escape(word) for word in words]

    if max_distance is not None:
        middle = rf'(?:\W+\w+){{0,{max_distance}}}'
    else:
        middle = r'(?:\W+\w+)*'

    # Genera tutte le permutazioni
    all_patterns = []
    for perm in permutations(escaped_words):
        pattern_parts = [rf'\b{perm[0]}\b']
        for i in range(1, len(perm)):
            pattern_parts.append(rf'{middle}\b{perm[i]}\b')
        all_patterns.append(''.join(pattern_parts))

    pattern = '|'.join(all_patterns)
    p = re.compile(pattern, flags=flags)

    # Usa la tua processItems
    return _processItems(p=p, source_data=text, context_length=context_length)
