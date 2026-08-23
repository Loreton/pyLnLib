from __future__ import annotations

import re
import sys
from itertools import combinations
from pathlib import Path

import yaml


from pyLnLib.logger import get_logger
# logger = get_logger()


class AuthorRegistry:
    """
    Registro persistente degli autori.

    Formato YAML:

        authors:
          Smith:
            - John
            - Mark
            - David

          Eco:
            - Umberto

          García Márquez:
            - Gabriel

          van Gogh:
            - Vincent

        ignore:
          - I Denti Della Tigre Ita Libro

    Uso normale:

        author = registry.format(book.author)

    La classe si occupa autonomamente di:

        - pulizia del nome
        - ricerca del cognome
        - cognomi composti
        - cognomi non necessariamente consecutivi
        - ricerca fino a 4 parole
        - richiesta all'utente quando necessario
        - memorizzazione delle esclusioni
        - aggiornamento del registro
        - salvataggio YAML
    """

    MAX_SURNAME_WORDS = 4

    def __init__(self, filename: str | Path):
        self.filename = Path(filename)

        # {
        #     "Smith": {"John", "Mark"},
        #     "García Márquez": {"Gabriel"},
        # }

        self.logger = get_logger()
        self.logger.info(f"AuthorRegistry: {self.filename}")

        self.authors: dict[str, set[str]] = {}

        # Valori di author da ignorare.
        self.ignore: set[str] = set()

        self.load()

    # ==================================================================
    # Normalizzazione
    # ==================================================================

    @staticmethod
    def _key(value: str) -> str:
        """
        Chiave usata per i confronti case-insensitive.
        """

        return value.strip().casefold()

    @staticmethod
    def _clean__(value_str: list[str]) -> str:
        """
        Pulisce il valore dell'autore.

        Esempio:

            'mark, Smith, .-'

        diventa:

            'mark Smith'
        """
        value = " ".join(value_str)
        value = value.replace(",", " ")

        value = re.sub( r"[^\w\s]", " ", value, flags=re.UNICODE, )

        return " ".join(value.split())

    @staticmethod
    def _clean(value: str) -> str:
        """
        Pulisce il valore dell'autore.

        Esempio:

            'mark, Smith, .-'

        diventa:

            'mark Smith'
        """
        value = value.replace(",", " ")

        value = re.sub( r"[^\w\s]", " ", value, flags=re.UNICODE, )

        return " ".join(value.split())

    # ==================================================================
    # YAML
    # ==================================================================

    def load(self) -> None:
        """Carica il registro dal file YAML."""

        self.authors.clear()
        self.ignore.clear()

        if not self.filename.exists():
            self.logger.warning(f"File YAML non trovato: {self.filename}")
            return

        with self.filename.open( "r", encoding="utf-8", ) as fp:
            data = yaml.safe_load(fp) or {}

        # --------------------------------------------------------------
        # Autori
        # --------------------------------------------------------------
        for surname, names in data.get( "authors", {}, ).items():
            if names is None:
                names = []

            self.authors[str(surname)] = { str(name) for name in names }

        # --------------------------------------------------------------
        # Valori da ignorare
        # --------------------------------------------------------------
        for value in data.get( "ignore", [], ) or []:
            self.ignore.add(str(value))


    # --------------------------------------------------------------
    # - Save registry yaml
    # --------------------------------------------------------------
    def save(self) -> None:
        """Salva il registro nel file YAML."""

        self.filename.parent.mkdir( parents=True, exist_ok=True, )

        authors = {}

        for surname in sorted( self.authors, key=str.casefold, ):
            authors[surname] = sorted( self.authors[surname], key=str.casefold, )

        ignore = sorted( self.ignore, key=str.casefold, )

        data = {
            "authors": authors,
            "ignore": ignore,
        }

        with self.filename.open( "w", encoding="utf-8", ) as fp:
            yaml.safe_dump( data, fp, allow_unicode=True, indent=4, sort_keys=False, default_flow_style=False )


    # ==================================================================
    # Ricerca cognome
    # ==================================================================
    def _find_surname( self, req_name: str, ) -> str | None:
        """
        Cerca un cognome nel registro.

        Il confronto è case-insensitive.

        Restituisce il valore originale presente nel YAML.
        """

        # controllo solo il valore normale oppure lower_case,
        # se serviranno altre cose le faremo più avanti, per ora basta così.
        if req_name not in self.authors and req_name.lower() not in self.authors:
            return None

        return req_name


    # ==================================================================
    # Ricerca combinazioni
    # ==================================================================

    def _find_surname_candidates( self, words: list[str], ) -> tuple[str, list[str]] | tuple[None, list[str]]:
        """
        Se siamo qui è perché non abbiamo trovato un cognome nel registro.

        Vengono considerate combinazioni di parole fino a
        MAX_SURNAME_WORDS.

        se la combinazione esiste nel registro.

        Ritorna:
            (surname, rest) dove rest è il resto delle words che non fanno parte del cognome.
        """

        # --------------------------------------------------------------
        # - numero max di words da provare per il la permutazione
        # --------------------------------------------------------------
        max_words = min( self.MAX_SURNAME_WORDS, len(words))

        # --------------------------------------------------------------
        # - Tentativo automatico
        # --------------------------------------------------------------
        words = words[:max_words]
        for permutazione in self._list_permutations(words, reverse=True):
            candidate = " ".join(permutazione)
            self.logger.debug("Dati permutazione:\npermutazione: %s\ncandidate: %s", permutazione, candidate)
            surname = self._find_surname(candidate)
            if surname:

                # ----------------------------------------
                # - se surname trovato, ritorna il cognome
                # - ed il resto delle parole come name
                # ----------------------------------------
                name = words.copy()
                for word in permutazione:
                    name.remove(word)
                return (surname, name)

        else:
            return (None, words)


    # ==================================================================
    # - Inserimento
    # ==================================================================
    def _add( self, surname: str, name: str, ) -> None:
        """Aggiunge un'associazione cognome/nome."""


        surname = " ".join(surname.split())
        name = " ".join(name.split())

        real_surname = self._find_surname( surname )

        f_save: bool = False
        if real_surname is None:
            self.authors[surname] = {name}
            f_save=True
        else:
            if name not in self.authors[real_surname]:
                self.authors[real_surname].add(name)
                f_save=True

        if f_save:
            self.save()



    # ==================================================================
    def _add_ignore( self, value: str) -> None:
        """Aggiunge un valore alla lista degli elementi da ignorare."""
        print(f"Ignorato: {value}")
        self.ignore.add(value)
        self.save()


    # ==================================================================
    # Identificazione
    #    author = "Cognome| Nome"  --> proviene da calibre
    #    author = "Cognome, Nome"  --> comunque chiaro
    #    author = "Cognome Nome"  --> da identificare
    #    author = "Nome Cognnome"  --> da identificare
    # ==================================================================
    def _identify( self, author: str, registry_update: bool) -> tuple[str, str] | None:
        """
        Identifica un autore.

        Restituisce: (surname, name)
        oppure:      None   - se il valore viene ignorato.

        """


        # --------------------------------------------------------------
        # - Verifichiamo se l'autore ha un formato riconoscibile
        # - Se così allora lo aggiungiamo al registro e lo restituiamo
        # --------------------------------------------------------------
        valid_separators=["|", ","]
        for sep in valid_separators:
            if sep in author:
                cognome, nome = author.split(sep, 1)
                cognome=cognome.strip()
                nome=nome.strip()
                cleaned = self._clean(cognome) + (" " + self._clean(nome) if nome else "")
                if not cleaned:
                    return None
                if registry_update:
                    self._add(surname=cognome, name=nome)
                return (cognome, nome)
                # break # solo per non far dare lsegnalazione all'else:

        else:
            # -----------------------------------------
            # - author non trovato nel registro,
            # - proviamo a fare un tentativo automatico
            # -----------------------------------------
            cleaned = self._clean(author)
            if not cleaned:
                return None



        # --------------------------------------------------------------
        # - Controlliamo se questo valore era già stato ignorato.
        # --------------------------------------------------------------
        cleaned_key = self._key(cleaned)
        if any( self._key(item) == cleaned_key for item in self.ignore ):
            self.logger.warning(f"Autore ignorato: {cleaned}")
            return None


        # --------------------------------------------------------------
        # - Tentativo automatico
        # --------------------------------------------------------------
        words = cleaned.split()
        surname, name = self._find_surname_candidates(words)

        # --------------------------------------------------------------
        # - Nessun candidato.
        # --------------------------------------------------------------
        if surname is None and registry_update:
            self._add_ignore(cleaned)
            return None

        name =" ".join(name)
        self._add( surname, name )

        return surname, name

    # ==================================================================
    # Risoluzione candidati
    # ==================================================================

    def _resolve_candidates( self, author: str,
                                   words: list[str],
                                   candidates: list[ tuple[str, tuple[int, ...]] ],
                                   registry_update: bool) -> tuple[str, str] | None:
        """
        Chiede all'utente di scegliere tra più cognomi
        possibili già presenti nel registro.
        """

        print()
        print(
            f"Più possibili cognomi trovati per: "
            f"{author}"
        )
        print()

        for index, (surname, indexes) in enumerate( candidates, start=1, ):
            print( f"  {index}) {surname}" )


        print()
        print("  0) Ignora / non è un autore")
        print()

        while True:

            value = input( "Seleziona il cognome: " ).strip()

            if value in ["xq"]:
                sys.exit("Uscita richiesta dall'utente.")

            if value == "0" and registry_update:
                self._add_ignore(author)
                return None

            try:
                choice = int(value)

            except ValueError:
                print( "Inserire il numero " "del cognome." )
                continue


            if not 1 <= choice <= len(candidates):
                print( "Scelta non valida." )
                continue

            surname, indexes = candidates[ choice - 1 ]

            name = " ".join(
                word
                for index, word in enumerate(words)
                if index not in indexes
            )

            if name:
                self._add( surname, name, )

            return surname, name




    # ==================================================================
    # API pubblica
    # ==================================================================
    def format( self, authors: list[str]|str, canonical: bool = True, registry_update: bool = False) -> list[str]:
        """
        Normalizza e formatta un autore.

        canonical=True:

            'Surname, Name'

        canonical=False:

            'Surname Name'

        Se l'autore non viene riconosciuto e l'utente
        seleziona 0, restituisce una stringa vuota.
        """
        if not authors:
            return []

        if isinstance(authors, str):
            authors = [authors.strip()]

        result_author=[]
        separators = ["&", " and ", ";", ","]
        for sep in separators:
            if sep in authors[0]:
                authors = [author.strip() for author in authors[0].split(sep)]
                break

        for author in authors: # oppure strip("&")????
            if not author:
                continue

            author = author.strip()
            if any( self._key(item) == self._key(author) for item in self.ignore ):
                self.logger.warning(f"Autore ignorato: {author}")
                continue

            author = self._identify(author, registry_update=registry_update)

            if author is None:
                continue

            surname, name = author

            result_author.append(f"{surname}, {name}" if canonical else f"{surname} {name}")

        return result_author

    # ==================================================================
    # Utility
    # ==================================================================



    # SOLO PERMUTAZIONI (tutti gli ordini, SENZA ripetizioni)
    # Numero totale: per 4 parole: 4!/(4-1)! + 4!/(4-2)! + 4!/(4-3)! + 4! = 4 + 12 + 24 + 24 = 64 permutazioni
    def _list_permutations(self, lista_parole, reverse=False):
        from itertools import permutations
        """Genera tutte le permutazioni di tutte le lunghezze senza ripetizioni."""
        if reverse:
            """Genera tutte le permutazioni di tutte le lunghezze, partendo da quelle più lunghe."""
            for r in range(len(lista_parole), 0, -1):  # Da n a 1
                for perm in permutations(lista_parole, r):
                    yield perm
        else:
            for r in range(1, len(lista_parole) + 1):
                for perm in permutations(lista_parole, r):
                    yield perm




    def __iter__(self):
        """Itera sugli autori registrati."""

        for surname in sorted(
            self.authors,
            key=str.casefold,
        ):

            for name in sorted(
                self.authors[surname],
                key=str.casefold,
            ):

                yield surname, name

    def __len__(self) -> int:
        """Numero di combinazioni cognome/nome registrate."""

        return sum(
            len(names)
            for names in self.authors.values()
        )


if __name__ == "__main__":
    registry = AuthorRegistry("authors.yaml")

    tests = [
        "mark, Smith, .-",
        "Smith, David",
        "Umberto Eco",
        "Gabriel García Márquez",
        "Vincent van Gogh",
    ]

    for value in tests:
        author = registry.identify( value)

        print(
            f"{value!r:30} -> "
            f"{registry.format(author) if author else None}"
        )
