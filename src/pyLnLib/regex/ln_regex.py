#!/usr/bin/env python3
#
# Progamma per testare regex
#
# ruff: noqa: C401 - Unnecessary generator (rewrite as a set comprehension) help: Rewrite as a set comprehension (Ruff C401)
#


import sys


sys.dont_write_bytecode = True

import re
import time
from _collections_abc import Callable
# from itertools import permutations
from functools import wraps
from dataclasses import dataclass

from pyLnLib import get_logger
from pyLnLib import clean_doc
# logger = None
# breakpoint()
logger = get_logger()
# print(logger.getConsoleLoggerLevel())


# this=sys.modules[__name__]
# this.logger = logger

@dataclass(slots=True, frozen=True)
class RegexItems:
    index: int
    matched_string: str

    start: int
    end: int

    context_length: int
    context: str
    match_start: int
    match_end: int

    ignore_case: bool


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


#################################
#
#################################
def _processOccurrencies(p, source_data: str, normalize_text: bool, context_length: int=0, ignore_case: bool=False) -> list[RegexItems]:

    # logger = get_logger()
    print(logger.name)
    logger.function(clean_doc(f"""processItems called with:
        compiled_pattern={p}
        normalize_text={normalize_text}
        context_length={context_length}
        ignore_case={ignore_case}"""))

    occurrencies = []

    # Normalizza il testo
    if normalize_text:
        source_data = source_data.replace('\n', ' ')
        source_data = ' '.join(source_data.split())

    for match in p.finditer(source_data):
        start, end = match.span()
        matched_string = match.group()


        # Estrai il contesto
        if context_length > 0:
            start_context = max(0, start - context_length)
            end_context = min(len(source_data), end + context_length)
            context = source_data[start_context:end_context]
        else:
            start_context = 0
            end_context = len(matched_string)
            context = matched_string

        occurrence = RegexItems(
            index=len(occurrencies),
            matched_string=matched_string,
            start=start,
            end=end,
            context=context,
            ignore_case=ignore_case,
            context_length=context_length,
            match_start=start - start_context,
            match_end=end - start_context,
        )
        # if context_length>0:
        #     occurrence.begin_string = start_context
        #     occurrence.len_string = end_context - start_context

        # breakpoint()
        occurrencies.append(occurrence)

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
            ) -> list[RegexItems]:
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
    print(logger.name)
        # source_data={source_data}
    logger.function(clean_doc(f"""processItems called with:
        terms={terms}
        normalize_text={normalize_text}
        context_length={context_length}
        ignore_case={ignore_case}"""))

    if len(terms) != 1:
        raise ValueError("search_term() requires exactly one search term")

    pattern = _escape_terms(terms, boundary)[0]

    flags = re.UNICODE
    if ignore_case:
        flags |= re.IGNORECASE

    p = re.compile(pattern, flags)

    return _processOccurrencies(
        p,
        source_data=source_data,
        normalize_text=normalize_text,
        context_length=context_length,
        ignore_case=ignore_case,
    )





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

    logger = get_logger()
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

    logger = get_logger()
    logger.function(clean_doc(f"""build_sequence_pattern called with:
        terms={terms}
        boundary={boundary}"""))

    escaped = _escape_terms(terms, boundary)
    return ".*".join(escaped)


######################################################
# Builds a regex pattern for near terms search
######################################################
def _build_near_pattern(
                        terms: list[str],
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

    logger = get_logger()
    logger.function(clean_doc(f"""build_near_pattern called with:
        terms={terms}
        max_words_between={max_words_between}
        any_order={any_order}
        boundary={boundary}"""))

    if len(terms) != 2:
        raise ValueError("NEAR search requires exactly two terms")

    # wrapper = r"\b{}\b" if boundary else "{}"
    escaped = _escape_terms(terms, boundary)
    term1, term2 = escaped

    # term1 = wrapper.format(re.escape(terms[0]))
    # term2 = wrapper.format(re.escape(terms[1]))

    separator = rf"(?:\W+\w+){{0,{max_words_between}}}\W+"

    forward = term1 + separator + term2

    if any_order:
        backward = term2 + separator + term1
        return rf"(?:{forward}|{backward})"

    return forward














@this_function_executing_time
def and_search(source_data: str,
                words_list: list,
                normalize_text: bool = False,
                max_words_between: int | None = None,
                ignore_case: bool = False,
                any_order: bool = False,
                context_length: int = 0,
                boundary: bool=False) -> list[RegexItems]:
    """
    Cerca tutte le parole/string nel testo devono seistere.
    """
    logger=get_logger()
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
        pattern = _build_near_pattern(terms=words_list[:2],
                                    max_words_between=max_words_between,
                                    any_order=any_order,
                                    boundary=boundary)
    elif any_order:
        pattern = _build_lookahead_pattern(terms=words_list, boundary=boundary)
    else:
        pattern = _build_sequence_pattern(terms=words_list, boundary=boundary)


    flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE
    p = re.compile(pattern, flags=flags)
    return _processOccurrencies(p,
        source_data=source_data,
        normalize_text=normalize_text,
        context_length=context_length,
        ignore_case=ignore_case)







# @this_function_executing_time
def or_search(source_data: str,
                words_list: list,
                normalize_text: bool = False,
                ignore_case: bool = False,
                context_length: int = 0,
                boundary: bool=False) -> list[RegexItems]:
    """
    Cerca tutte le parole/string nel testo devono seistere.
    """
    logger = get_logger()
    logger.function(clean_doc(f"""and_search called with:
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
        # source_data = ' '.join(source_data.split())

    flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE

    occurrences = []
    for term in words_list:
        logger.info("searching for term: %s", term)
        pattern = _build_sequence_pattern(terms=[term], boundary=boundary)
        p = re.compile(pattern, flags=flags)
        result = _processOccurrencies(p,
                source_data=source_data,
                normalize_text=normalize_text,
                context_length=context_length,
                ignore_case=ignore_case)
        occurrences.extend(result)

    return occurrences
