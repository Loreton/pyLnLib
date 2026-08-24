#!/usr/bin/env python3
#
# Progamma per testare regex
#
# updated by ...: Loreto Notarantonio


import sys; sys.dont_write_bytecode = True

import re
import time

from pyLnLib import get_logger
logger = get_logger()




def this_function_executing_time(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.notify(f"[Function: {func.__name__}] eseguita in {end - start:.6f} secondi", stacklevel=3)
        return result
    return wrapper



from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class RegexItems:
    index: int
    matched_string: str
    start: int
    end: int
    context: str


#################################
#################################
# @this_function_executing_time
def processItems(p, source_data: str, context_length: int=0) -> list:
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
def findIter_prev(p, source_data: str, context_length: int=0) -> list:
    logger.info("processing:     %s %s", type(p), p)

    occurrencies = []

    for match in p.finditer(source_data):
        start, end   = match.span()
        matched_string = match.group() ### nome della word


        ### --- Estrai il contesto
        if context_length > 0:
            start_context = max(0, start - context_length)
            end_context   = min(len(source_data), end + context_length)
            context       = source_data[start_context:end_context]
        else:
            context = matched_string

        # crea il dictionary dell'item trovato
        occurrence = {}
        occurrence["matched_string"] = matched_string
        occurrence["start"]          = start
        occurrence["end"]            = end
        occurrence["context"]        = context

        # aggiungi alla list di ritorno
        occurrencies.append(occurrence)

    if not occurrencies:
        logger.warning("orrurrency: %s", occurrencies)
    return occurrencies


#################################
#
#################################
def FindAll(p, data: (str, list, tuple), ignore_case: bool=True):
    logger.debug("processing: %s", p)
    if isinstance(data, (list, tuple)): data=' '.join(data)

    py_flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE
    occurrencies = p.findall(data, flags=py_flags)

    result=[]
    if  occurrencies:
        # if fPRINT:print(occurrencies)
        result.extend(occurrencies)

    return result










#################################
# - search string / word
#################################
# @this_function_executing_time
def STRING(source_data: str, stringa: str, word_boundary: bool=False, normalize_text: bool=False, context_length: int=0, ignore_case: bool=True):
    logger.notify("sarching the following string: %s", stringa)

    # Normalizza il testo per la ricerca
    if normalize_text: source_data = ' '.join(source_data.split())
    py_flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE

    # prepara il pattern
    base_pattern = r'\b({stringa})\b' if word_boundary else r'({stringa})'
    p=re.compile(base_pattern.format(**locals()), flags=py_flags)
    result: list = findIter(p=p, source_data=source_data, context_length=context_length)

    return result










#################################
# - search all words (AND) any order
# - ritorna il contesto
#################################
@this_function_executing_time
# def AND(source_data: str, string_list: list, word_boundary=False, context_length: int=0, normalize_text: bool=False, ignore_case: bool=True, exit_on_first_notfound: bool=True):
def AND(source_data: str, string_list: list,
            word_boundary:  bool=False,
            context_length: int=0,
            normalize_text: bool=False,
            ignore_case:    bool=True,
            exit_on_first_notfound: bool=True):
    '''
        Esegue una ricerca AND per verificare se tutte le parole di string_list sono presenti nel testo.

        Args:
            source_data (str): Il testo in cui cercare.
            string_list (list): La lista di parole da cercare.
            word_boundary (bool): Se True, cerca le parole come entità separate.

        Returns:
            dict: entries se tutte le parole sono presenti, altrimenti {}.
    '''

    # Normalizza il testo per la ricerca
    if normalize_text: source_data = ' '.join(source_data.split())
    py_flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE

    logger.notify("sarching the following words: %s", string_list)

    base_pattern = r'\b({item})\b' if word_boundary else r'({item})'

    matches={}

    for item in string_list:
        p=re.compile(base_pattern.format(**locals()), flags=py_flags)
        result: list = findIter(p=p, source_data=source_data, context_length=context_length)
        import pdb; pdb.set_trace() # by Loreto

        ### --- esci alla prima stringa non trovata
        if not result:
            if exit_on_first_notfound:
                matches={}
                break
            else:
                matches.update({item: "NOT_FOUND"})
        else:
            matches.update(_dict)

    return matches





#################################
# - search all words (AND)
##################################
@this_function_executing_time
def AND_justCheck(source_data: str, string_list: list, word_boundary=False, normalize_text: bool=False, ignore_case: bool=True):
    '''
        Esegue una ricerca AND per verificare se tutte le parole di string_list sono presenti nel testo.

        Args:
            source_data (str): Il testo in cui cercare.
            string_list (list): La lista di parole da cercare.
            word_boundary (bool): Se True, cerca le parole come entità separate.

        Returns:
            bool: True se tutte le parole sono presenti, altrimenti False.
    '''
    # Normalizza il testo per la ricerca
    if normalize_text: source_data = ' '.join(source_data.split())
    py_flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE


    # Itera su ogni parola e verifica la sua presenza
    for word in string_list:
        if word_boundary:
            # Crea un pattern con il confine di parola
            pattern = fr'\b{re.escape(word)}\b'
        else:
            # Crea un pattern senza il confine di parola
            pattern = re.escape(word)

        if re.search(pattern, source_data, flags=py_flags) is None:
            # Se una parola non viene trovata, restituisce False immediatamente
            return False

    # Se il ciclo termina, tutte le parole sono state trovate
    return True




#################################
# - search any word (OR)
#################################
# @this_function_executing_time
# def OR(source_data: str, string_list: list, word_boundary=False, context_length: int=0, normalize_text: bool=False, ignore_case: bool=True):
def OR(source_data: str, string_list: list,
                    word_boundary:  bool=False,
                    context_length: int=0,
                    normalize_text: bool=False,
                    ignore_case:    bool=True,
                    return_dict:    bool=False):

    logger.notify("sarching far all the following strings: %s", string_list)

    base_pattern = r'\b({item})\b' if word_boundary else r'({item})'

    # Normalizza il testo per la ricerca
    if normalize_text: source_data = ' '.join(source_data.split())
    py_flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE

    matches={}

    for item in string_list:
        p=re.compile(base_pattern.format(**locals()), flags=py_flags)
        _result = FindIter(p=p, source_data=source_data, context_length=context_length, return_dict=return_dict)
        if _result:
            matches.update(_result) if return_dict else matches.extend(_result)


    return matches



#################################
# - search near words
#################################
def multi_near_words_new(source_data: str,
                    words_list: list,
                    words_distance: list,
                    normalize_text: bool=False,
                    ignore_case: bool=True,
                    context_length: int=0):


    # Validazione input
    if not isinstance(source_data, str) or not isinstance(words_list, list) or len(words_list) < 2:
        return []

    if not isinstance(words_distance, list) or len(words_distance) != 2:
        return []

    # Normalizza il testo
    if normalize_text:
        source_data = ' '.join(source_data.split())

    min_words, max_words = words_distance
    py_flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE

    # COSTRUZIONE DEL PATTERN CORRETTO
    # Cattura il testo tra le due parole, comprese le parole stesse

    # Pattern per le parole intermedie:
    # (?:\s+\w+){{min,max}}? - matcha esattamente il numero di parole specificato
    middle_words = rf'(?:\s+\w+){{{min_words},{max_words}}}?'

    # Pattern completo: prima parola + parole intermedie + seconda parola
    pattern = rf'\b{words_list[0]}\b{middle_words}\s+{words_list[1]}\b'

    # Se ci sono più di 2 parole, estendiamo il pattern
    for i in range(2, len(words_list)):
        pattern += rf'{middle_words}\s+{words_list[i]}\b'

    # Compila l'espressione regolare
    p = re.compile(pattern, flags=py_flags)

    return processItems(p=p, source_data=source_data, context_length=context_length)


#################################
# - search near words
#################################
@this_function_executing_time
def multi_near_words(source_data: str,
                    words_list: list,
                    words_distance: list,
                    normalize_text: bool=False,
                    ignore_case: bool=True,
                    context_length: int=0):

    # Controllo che gli input siano validi e che ci siano almeno due parole
    if not isinstance(source_data, str) or not isinstance(words_list, list) or len(words_list) < 2 or not isinstance(words_distance, list) or len(words_distance) != 2:
        print("Input non valido. Fornire una lista di almeno due parole.")
        return {}


    # Normalizza il testo per la ricerca  in modo che gli spazi multipli e i caratteri di a capo non alterino il conteggio delle parole.
    if normalize_text: source_data = ' '.join(source_data.split())
    py_flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE

    min_words, max_words = words_distance


    # Costruisci l'espressione regolare per la prima parola
    pattern_parts = [rf'\b{words_list[0]}\b']

    # Aggiungi le altre parole e lo spazio tra di esse
    # Il loop parte dalla seconda parola
    for i in range(1, len(words_list)):
        pattern_parts.append(rf'\W+(?:\w+\W+){{{min_words},{max_words}}}{words_list[i]}\b')

    # Unisci le parti del pattern
    pattern = ''.join(pattern_parts)

    # Compila l'espressione regolare
    p = re.compile(pattern, flags=py_flags)

    return processItems(p=p, source_data=source_data, context_length=context_length)

def multi_near_words_unordered_type1(source_data: str,
                              words_list: list,
                              words_distance: list,
                              normalize_text: bool=False,
                              ignore_case: bool=True,
                              context_length: int=0):

    if normalize_text:
        source_data = ' '.join(source_data.split())

    min_words, max_words = words_distance
    py_flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE

    # Pattern per le parole intermedie
    middle_words = rf'(?:\s+\w+){{{min_words},{max_words}}}?'

    # Crea un lookahead per verificare che TUTTE le parole siano presenti
    # Questo è più efficiente delle permutazioni
    words_pattern = '|'.join(rf'\b{word}\b' for word in words_list)

    # Pattern che cerca qualsiasi parola della lista, poi verifica la distanza
    # Usa un lookahead per controllare che tutte le parole siano nel range
    lookahead_parts = []
    for i, word in enumerate(words_list):
        # Per ogni parola, crea un lookahead che la cerca entro il limite
        lookahead_parts.append(
            rf'(?=.*\b{word}\b)'
        )

    # Pattern principale: trova la prima parola e poi le altre entro il limite
    # Questo è un approccio più complesso ma più efficiente
    first_word = words_list[0]
    other_words = words_list[1:]

    # Costruisci pattern che cerca la prima parola e poi le altre in qualsiasi ordine
    pattern = rf'\b{first_word}\b'

    for other in other_words:
        pattern += rf'(?:\s+\w+){{{min_words},{max_words}}}\s+\b{other}\b'

    p = re.compile(pattern, flags=py_flags)
    return processItems(p=p, source_data=source_data, context_length=context_length)


# usa il token
def multi_near_words_unordered_type2(source_data: str,
                           words_list: list,
                           words_distance: list,
                           normalize_text: bool=False,
                           ignore_case: bool=True,
                           context_length: int=0):

    if normalize_text:
        source_data = ' '.join(source_data.split())

    min_words, max_words = words_distance
    results = []

    # Tokenizza il testo
    tokens = source_data.split()
    words_set = set(words_list)

    # Cerca tutte le combinazioni
    for i, token in enumerate(tokens):
        if token.lower() in words_set:  # Prima parola trovata
            # Cerca le altre parole entro il limite
            for j in range(i + min_words + 1, min(i + max_words + 2, len(tokens))):
                if tokens[j].lower() in words_set:
                    # Verifica che tutte le parole siano presenti
                    found_words = set()
                    for k in range(i, j + 1):
                        if tokens[k].lower() in words_set:
                            found_words.add(tokens[k].lower())

                    # Se abbiamo trovato TUTTE le parole
                    if found_words == words_set:
                        start = source_data.find(tokens[i], 0)
                        end = source_data.find(tokens[j], start) + len(tokens[j])

                        matched_string = ' '.join(tokens[i:j+1])

                        # Estrai contesto
                        if context_length > 0:
                            start_context = max(0, start - context_length)
                            end_context = min(len(source_data), end + context_length)
                            context = source_data[start_context:end_context]
                        else:
                            context = matched_string

                        results.append(RegexItems(
                            index=len(results),
                            matched_string=matched_string,
                            start=start,
                            end=end,
                            context=context
                        ))

    return results
def multi_near_words_flexible_(source_data: str,
                             words_list: list,
                             words_distance: list,
                             normalize_text: bool=False,
                             ignore_case: bool=True,
                             context_length: int=0):

    if normalize_text:
        source_data = ' '.join(source_data.split())

    min_words, max_words = words_distance
    py_flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE

    # Costruisci pattern per parole in qualsiasi ordine
    # Cerca la prima parola e poi la seconda entro il limite di parole
    word1, word2 = words_list[0], words_list[1]

    # Pattern che cerca word1, poi da min a max parole, poi word2
    pattern = rf'\b{word1}\b(?:\s+\w+){{{min_words},{max_words}}}\s+{word2}\b'

    # E viceversa (per cercare anche word2 prima di word1)
    pattern_reverse = rf'\b{word2}\b(?:\s+\w+){{{min_words},{max_words}}}\s+{word1}\b'

    # Unisci i pattern con OR
    full_pattern = rf'({pattern})|({pattern_reverse})'

    p = re.compile(full_pattern, flags=py_flags)
    return processItems(p=p, source_data=source_data, context_length=context_length)


#################################
# - search near words
#################################
@this_function_executing_time
def multi_near_words_unordered(source_data: str, words_list: list, near: list, normalize_text: bool=False, ignore_case: bool=True, return_dict: bool=False):
    import itertools
    # Controllo che gli input siano validi e che ci siano almeno due parole
    if not isinstance(source_data, str) or not isinstance(words_list, list) or len(words_list) < 2 or not isinstance(near, list) or len(near) != 2:
        print("Input non valido. Fornire una lista di almeno due parole.")
        return {}


    # Normalizza il testo per la ricerca  in modo che gli spazi multipli e i caratteri di a capo non alterino il conteggio delle parole.
    if normalize_text: source_data = ' '.join(source_data.split())
    py_flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE

    min_words, max_words = near

    n_words=len(words_list)
    matches = {} if return_dict else []

    # 2) Tutte le permutazioni (ordine conta)
    for r in range(1, n_words+1):
        for perm_list in itertools.permutations(words_list, r):
            if len(perm_list) != n_words:
                continue

            # matched_key = {normalize_word(w) for w in perm_list}
            oreder_words = [normalize_word(w) for w in perm_list]
            matched_key = ' '.join(oreder_words)
            logger.notify("Working on sequence: %s", matched_key)

            # Costruisci l'espressione regolare per la prima parola
            pattern_parts = [rf'\b{perm_list[0]}\b']

            # Aggiungi le altre parole e lo spazio tra di esse
            # Il loop parte dalla seconda parola
            for i in range(1, len(perm_list)):
                pattern_parts.append(rf'\W+(?:\w+\W+){{{min_words},{max_words}}}{perm_list[i]}\b')

            # Unisci le parti del pattern
            pattern = ''.join(pattern_parts)

            # Compila l'espressione regolare
            p = re.compile(pattern, flags=py_flags)

            result = FindIter(p=p, source_data=source_data)

            if return_dict:
                matches[matched_key] = result
            else:
                matches.append(result)

    import pdb; pdb.set_trace() # by Loreto
    return matches





def normalize_word(word):
    """Rimuove la punteggiatura e converte in minuscolo."""
    # Usiamo un regex per rimuovere la punteggiatura e caratteri non-parola dai confini
    return re.sub(r'^\W+|\W+$', '', word, flags=re.UNICODE).lower()

# def multi_near_words_unordered(source_data: str, words_list: list, near: list, normalize_text: bool=False, ignore_case: bool=True):

#     # Normalizza il testo per la ricerca  in modo che gli spazi multipli e i caratteri di a capo non alterino il conteggio delle parole.
#     if normalize_text: source_data = ' '.join(source_data.split())

#     # 1. Trova gli indici di TUTTE le parole nel testo normalizzato
#     text_words = source_data.split()

#     # Raccogli gli indici di tutte le occorrenze di ogni parola target
#     word_indices = {}

#     # Prepara le parole target per la ricerca case-insensitive
#     target_words_set = {w.lower() for w in words_list}

#     for i, word in enumerate(text_words):
#         if word.lower() in target_words_set:
#             # Memorizza l'indice di posizione delle singole parole {'word1': [10673, 14699, 34441], 'word2': [15379]}
#             word_indices.setdefault(word.lower(), []).append(i)

#     # Verifica: se non hai trovato tutte le parole, non c'è corrispondenza
#     if len(word_indices) < len(words_list):
#         return {}


def sanitize_path(s, resolve_realpath=False):
    WHITELIST = re.compile(r'[^A-Za-z0-9_\-./\\:~ ]+')
    # trim virgolette, virgole residue
    s = s.strip().strip('"\',')
    # rimuovi caratteri non permessi
    s = WHITELIST.sub('', s)
    # collapse multipli slash/backslash
    s = re.sub(r'/+', '/', s)
    s = re.sub(r'\\+', '\\\\', s)
    # trim spazi esterni
    s = s.strip()
    if resolve_realpath:
        try:
            s = os.path.realpath(s)
        except Exception:
            pass
    return s
    # esempio di call
    #  raw = '"/home/loreto/lnFreex/SublimeText4/Data/Packages/User",'
    #  print(sanitize_path(raw, resolve_realpath=True))



@this_function_executing_time
def multi_near_words_unordered_(source_data: str, words_list: list, near: list, normalize_text: bool=False, ignore_case: bool=True):
    # Normalizza il testo per la ricerca  in modo che gli spazi multipli e i caratteri di a capo non alterino il conteggio delle parole.
    if normalize_text: source_data = ' '.join(source_data.split())

    # 1. Normalizza e splitta il testo, ripulendo OGNI parola
    text_words = [normalize_word(w) for w in source_data.split()]

    # 2. Prepara le parole target normalizzate
    target_words_set = {normalize_word(w) for w in words_list}

    # Rimuovi eventuali stringhe vuote se la parola originale era solo punteggiatura
    target_words_set.discard('')

    # Raccogli gli indici di tutte le occorrenze di ogni parola target
    word_indices = {}

    for i, word in enumerate(text_words):
        if word in target_words_set:
            # Memorizza l'indice di posizione della parola
            word_indices.setdefault(word, []).append(i)


    # Verifica: se non hai trovato tutte le parole, non c'è corrispondenza
    if len(word_indices) < len(words_list):
        return {}


    min_dist, max_dist = near

    # 2. Confronta le posizioni per trovare combinazioni valide
    valid_matches = []

    # Ottieni tutte le occorrenze di ciascuna parola target
    # Esempio: [[idx_w1a, idx_w1b], [idx_w2a, idx_w2b]]
    all_occurrencies = list(word_indices.values())

    # Genera tutte le possibili combinazioni di indici (una per ogni parola target)
    from itertools import product

    # product genera tuple come: (idx_w1a, idx_w2a, idx_w3a, ...)
    for combination in product(*all_occurrencies):

        # Ordina gli indici per trovare la distanza tra il minimo e il massimo
        min_index = min(combination)
        max_index = max(combination)

        # La distanza in termini di *parole* è (max_index - min_index)
        # La distanza in termini di *parole intermedie* è (max_index - min_index - 1)

        intermediate_words_count = max_index - min_index - 1

        # Controlla se la distanza rientra nel range specificato
        if min_dist <= intermediate_words_count <= max_dist:
            # Trovato un match valido, ora dobbiamo ricostruire la stringa e l'indice
            start_word = text_words[min_index]
            end_word = text_words[max_index]
            matched_substring_list = text_words[min_index : max_index + 1]

            # Ricostruisci il testo del match
            matched_string = ' '.join(matched_substring_list)

            valid_matches.append(matched_string)

    # L'output qui è una lista di stringhe che soddisfano il criterio di distanza
    # La funzione FindIter originale è complessa per questo scopo,
    # quindi si restituiscono i match trovati.
    return {match: {} for match in set(valid_matches)}







#################################
# Individua la prima occorrenza di una stringa racchiusa da prefisso/suffisso.
# Supporta la sostituzione opzionale.
#################################
# @this_function_executing_time
def FindFirstEnclosed(source_data: str, prefix: str, suffix: str, replace_with: str = None, ignore_case: bool = True):
    fALL=0
    fPREFIX=1
    fTEXT=2
    fSUFFIX=3
    '''
        Trova la prima stringa racchiusa tra prefisso e suffisso e opzionalmente la sostituisce.

        Args:
            source_data (str): Il testo in cui cercare.
            prefix (str): La stringa prefisso che precede la stringa da trovare.
            suffix (str): La stringa suffisso che segue la stringa da trovare.
            replace_with (str, optional): Se fornito, la stringa racchiusa viene sostituita
                                          con questo valore e viene restituito l'intero testo modificato.
            ignore_case (bool): Se True, la ricerca è case-insensitive.

        Returns:
            dict or str:
                - Se replace_with è None: Ritorna un dict con la prima stringa trovata,
                  il suo start, e l'end, relativi alla source_data.
                - Se replace_with è valorizzato: Ritorna l'intera stringa source_data
                  con la prima occorrenza sostituita.
                - Ritorna None se la stringa non viene trovata.
    '''
    # 1. Escaping e costruzione del pattern
    escaped_prefix = re.escape(prefix)
    escaped_suffix = re.escape(suffix)

    # Il pattern cattura l'intera occorrenza (inclusi prefix e suffix)
    pattern = rf'({escaped_prefix})(.*?)({escaped_suffix})'

    logger.debug("Generated pattern: %s", pattern)

    py_flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE

    # 2. Ricerca della prima occorrenza
    match = re.search(pattern, source_data, flags=py_flags)

    if not match:
        logger.warning(f"No match found for pattern: {prefix}...{suffix}")
        return None  # Ritorna None se non trova nulla

    # 3. Estrazione dei dati
    #    Pattern e Gruppi di Cattura: Il pattern è (prefix)(.*?)(suffix).
    #    match.group(0) è l'intera stringa: prefix + contenuto + suffix
    #    match.group(1) è il prefisso.
    #    match.group(2) è solo il contenuto racchiuso
    #    match.group(3) è il suffisso.
    #    stessa logica per match.span(x)
    #    match.span(2) fornisce le posizioni esatte (start_content, end_content) del contenuto nel testo sorgente.


    # 4. Gestione della Sostituzione (Replace)
    if replace_with is not None:
        logger.debug(f"Replacing first occurrence with: {replace_with}")
        start, end = match.span(fALL)
        new_source_data = (source_data[:start] + replace_with + source_data[end:])
        return new_source_data

    # 5. Ritorno delle posizioni (caso senza replace)
    else:
        start, end = match.span(fALL)
        full_text = match.group(fALL)
        found_text = match.group(fTEXT)
        start_content, end_content = match.span(fTEXT)

        return {
            "text": found_text,
            "start": start_content,
            "end": end_content,

            "full_text": full_text,
            "full_start": start, # Aggiunto per riferimento
            "full_end": end,     # Aggiunto per riferimento
        }





#################################
# Individua stringhe racchiuse da un prefisso e un suffisso
#################################
# @this_function_executing_time
def FindEnclosedStrings(source_data: str, prefix: str, suffix: str, ignore_case: bool=True):
    '''
        Individua tutte le stringhe racchiuse tra il prefisso e il suffisso specificati.

        Args:
            source_data (str): Il testo in cui cercare.
            prefix (str): La stringa prefisso che precede la stringa da trovare.
            suffix (str): La stringa suffisso che segue la stringa da trovare.
            ignore_case (bool): Se True, la ricerca è case-insensitive.

        Returns:
            list: Una lista delle stringhe trovate tra prefisso e suffisso.
    '''
    # 1. Utilizza re.escape per trattare prefisso e suffisso come caratteri letterali,
    #    anche se contengono caratteri speciali di regex (es: $, {, (, ).
    escaped_prefix = re.escape(prefix)
    escaped_suffix = re.escape(suffix)

    # 2. Costruisci il pattern regex:
    #    - {escaped_prefix}: Il prefisso (escaped).
    #    - (.*?): Gruppo di cattura. Il punto (.) matcha qualsiasi carattere (eccetto newline
    #      se re.DOTALL non è usato, ma qui non è necessario).
    #      Il punto interrogativo (?) rende la cattura *non avida* (non-greedy),
    #      catturando il minor numero possibile di caratteri fino al suffisso.
    #    - {escaped_suffix}: Il suffisso (escaped).
    #    Il pattern cerca esattamente il prefisso, seguito da qualsiasi cosa (catturata),
    #    seguita esattamente dal suffisso.
    pattern = rf'{escaped_prefix}(.*?){escaped_suffix}'

    logger.debug("Generated pattern: %s", pattern)

    py_flags = re.UNICODE | re.IGNORECASE if ignore_case else re.UNICODE

    # 3. Compila il pattern
    p = re.compile(pattern, flags=py_flags)

    # 4. Usa findall. Poiché il pattern contiene un gruppo di cattura (),
    #    findall restituirà solo il contenuto del gruppo di cattura,
    #    ovvero la stringa racchiusa.
    result = p.findall(source_data)

    return result

















#################################################################
# --- remove extra blanks on string
#################################################################
def remove_extra_blanks(data: str) -> str:
    return re.sub(r'\s+', ' ', data.strip())



#################################################################
# --- remove multiple consecutive blank lines
#################################################################
def remove_multiple_consecutive_blank_lines(content: list) -> str:
    _str='\n'.join(content)
    new_data=re.sub(r'[\r\n][\r\n]{2,}', '\n\n', _str)
    return new_data









###############################################################
# Usato in DictUtils.py
# Search string between delimiters
# if fLAST==True search for the last occurrency
# return:
#        pattern if data==None
#        result  if data
###############################################################
def regex_search(data: str, prefix: str, suffix: str, fLAST=False):
    # import re
    from types import SimpleNamespace
    _prefix=prefix.replace('$', '\\$')
    _suffix=suffix.replace('$', '\\$')
    pattern=f'{_prefix}(.*?){_suffix}'
    regex=re.compile(pattern, re.IGNORECASE)

    ret=None
    if isinstance(data, (str, bytes)):
        start_pos=data.rfind(prefix) if fLAST else 0
        if start_pos>=0:
            matched=regex.search(data, start_pos)
            if matched:
                # gv.logger.debug('MATCH FOUND: %s', matched)
                llen=len(prefix)
                rlen=len(suffix)

                ret=SimpleNamespace()
                matched_str, ret.start_pos, ret.end_pos=matched.group(), matched.start(), matched.end()
                ret.name=matched_str[llen:-rlen] #- strip prefix and suffix

    return ret


'''



###############################################################
# Search string between delimiters
# if fLAST==True search for the last occurrency
# return:
#        pattern if data==None
#        result  if data
###############################################################
def regex_getDelimitedString(data: str, prefix: str, suffix: str, fLAST=False):
    import re
    # pattern=r"" + prefix + "(.*?)" + suffix
    pattern=prefix + "(.*?)" + suffix

    # - remove escape char
    prefix=prefix.replace('\\', "")
    suffix=suffix.replace('\\', "")

    # - compile pattern
    regex=re.compile(pattern, re.IGNORECASE)
    ret=None
    if isinstance(data, (str, bytes)):
        llen=len(prefix)
        rlen=len(suffix)
        start_pos=data.rfind(prefix) if fLAST else 0
        if start_pos>=0:
            matched=regex.search(data, start_pos)
            if matched:
                gv.logger.debug('MATCH FOUND: %s', matched)

                ret=SimpleNamespace()
                matched_str, ret.start_pos, ret.end_pos=matched.group(), matched.start(), matched.end()
                ret.name=matched_str[llen:-rlen] #- strip prefix and suffix

    return ret.name



###############################################################
# Search string between delimiters
# if fLAST==True search for the last occurrency
# return:
#        pattern if data==None
#        result  if data
###############################################################
def regex_findAll(data: str, prefix: str, suffix: str):
    import re
    pattern=prefix + "(.*?)" + suffix

    # - remove escape char
    prefix=prefix.replace('\\', "")
    suffix=suffix.replace('\\', "")

    # - compile pattern
    regex=re.compile(pattern, re.IGNORECASE)

    return regex.findall(data)





'''











if __name__ == '__main__':
    # sys.path.insert(0, "test")
    print("ESEGUIRE:" "test/LnRegex_TEST.py")
