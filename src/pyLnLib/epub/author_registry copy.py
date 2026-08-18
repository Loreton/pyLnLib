from __future__ import annotations

import re
import sys
from itertools import combinations
from pathlib import Path

import yaml


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
            return

        with self.filename.open(
            "r",
            encoding="utf-8",
        ) as fp:
            data = yaml.safe_load(fp) or {}

        # --------------------------------------------------------------
        # Autori
        # --------------------------------------------------------------

        for surname, names in data.get(
            "authors",
            {},
        ).items():

            if names is None:
                names = []

            self.authors[str(surname)] = {
                str(name)
                for name in names
            }

        # --------------------------------------------------------------
        # Valori da ignorare
        # --------------------------------------------------------------

        for value in data.get(
            "ignore",
            [],
        ) or []:

            self.ignore.add(str(value))

    def save(self) -> None:
        """Salva il registro nel file YAML."""

        self.filename.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        authors = {}

        for surname in sorted(
            self.authors,
            key=str.casefold,
        ):
            authors[surname] = sorted(
                self.authors[surname],
                key=str.casefold,
            )

        ignore = sorted(
            self.ignore,
            key=str.casefold,
        )

        data = {
            "authors": authors,
            "ignore": ignore,
        }

        with self.filename.open(
            "w",
            encoding="utf-8",
        ) as fp:

            yaml.safe_dump(
                data,
                fp,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
            )

    # ==================================================================
    # Ricerca cognome
    # ==================================================================

    def _find_surname(
        self,
        value: str,
    ) -> str | None:
        """
        Cerca un cognome nel registro.

        Il confronto è case-insensitive.

        Restituisce il valore originale presente nel YAML.
        """

        key = self._key(value)

        for surname in self.authors:

            if self._key(surname) == key:
                return surname

        return None

    # ==================================================================
    # Ricerca combinazioni
    # ==================================================================

    def _find_surname_candidates( self, words: list[str], ) -> list[tuple[str, tuple[int, ...]]]:
        """
        Cerca tutti i cognomi conosciuti possibili.

        Vengono considerate combinazioni di parole fino a
        MAX_SURNAME_WORDS.

        Le parole non devono necessariamente essere consecutive.

        Esempio:

            words =
                ["Gogh", "van", "Vincent"]

        potrebbe trovare:

            ("van Gogh", (0, 1))

        se il cognome esiste nel registro.

        Restituisce una lista di:

            (surname, indexes)

        dove indexes contiene le posizioni originali
        delle parole.
        """

        candidates: list[ tuple[str, tuple[int, ...]] ] = []
        max_words = min( self.MAX_SURNAME_WORDS, len(words), )

        # --------------------------------------------------------------
        # Proviamo prima i cognomi più lunghi.
        # --------------------------------------------------------------
        for length in range( max_words, 0, -1, ):
            for indexes in combinations( range(len(words)), length, ):
                candidate = " ".join( words[index] for index in indexes )
                surname = self._find_surname( candidate )
                if surname is not None:
                    candidates.append( ( surname, indexes, ) )

        return candidates

    # ==================================================================
    # Inserimento
    # ==================================================================
    def _add( self, surname: str, name: str, ) -> None:
        """Aggiunge un'associazione cognome/nome."""

        surname = " ".join(surname.split())
        name = " ".join(name.split())

        real_surname = self._find_surname( surname )

        if real_surname is None:
            self.authors[surname] = {name}
        else:
            self.authors[real_surname].add(name)

        self.save()



    # ==================================================================
    def _add_ignore( self, value: str, ) -> None:
        """Aggiunge un valore alla lista degli elementi da ignorare."""

        self.ignore.add(value)
        self.save()

    # ==================================================================
    # Prompt
    # ==================================================================

    def _author_prompt( self, author: str, words: list[str], ) -> list[int] | None:
        """
        Chiede all'utente quali parole compongono il cognome.

        Le parole possono essere selezionate in qualsiasi ordine.

        Esempi validi:

            3
            3 4
            4 3
            4 2 1

        Gli indici vengono poi ordinati secondo la posizione
        originale delle parole.

        Restituisce:

            list[int]
                indici zero-based del cognome

            None
                se l'utente sceglie 0
        """

        print()
        print(f"Autore sconosciuto: {author}")
        print()
        print("Quali parole compongono il cognome?")
        print()

        for index, word in enumerate( words, start=1, ):
            print( f"  {index}) {word}" )

        print()
        print("  0) Ignora / non è un autore")
        print()

        while True:

            value = input( "Inserisci gli indici " "del cognome [es. 2 3 4]: " ).strip()

            if not value:
                print( "Specificare almeno una parola." )
                continue

            # ----------------------------------------------------------
            # 0 = ignora
            # ----------------------------------------------------------

            if value == "0":
                return None

            if value in ["qx"]:
                sys.exit("Uscita richiesta dall'utente.")

            # ----------------------------------------------------------
            # Conversione
            # ----------------------------------------------------------

            try:

                indexes = [
                    int(item) - 1
                    for item in value.split()
                ]

            except ValueError:

                print(
                    "Inserire gli indici separati "
                    "da spazio."
                )
                continue

            if not indexes:
                continue

            # ----------------------------------------------------------
            # Verifica massimo 4 parole.
            # ----------------------------------------------------------

            if len(indexes) > self.MAX_SURNAME_WORDS:

                print(
                    f"Il cognome può contenere al massimo "
                    f"{self.MAX_SURNAME_WORDS} parole."
                )
                continue

            # ----------------------------------------------------------
            # Verifica indici validi.
            # ----------------------------------------------------------

            if any(
                index < 0 or index >= len(words)
                for index in indexes
            ):

                print(
                    "Uno o più indici non sono validi."
                )
                continue

            # ----------------------------------------------------------
            # Nessun duplicato.
            # ----------------------------------------------------------

            if len(indexes) != len(set(indexes)):

                print(
                    "Non è possibile specificare "
                    "lo stesso indice più volte."
                )
                continue

            # ----------------------------------------------------------
            # IMPORTANTE:
            #
            # l'utente può scrivere:
            #
            #     4 2 1
            #
            # ma noi ricostruiamo il cognome secondo
            # l'ordine originale delle parole.
            #
            #     1 2 4
            # ----------------------------------------------------------

            indexes.sort()

            return indexes

    # ==================================================================
    # Identificazione
    # ==================================================================

    def _identify( self, value: str, ) -> tuple[str, str] | None:
        """
        Identifica un autore.

        Restituisce: (surname, name)
        oppure:      None

        se il valore viene ignorato.
        """

        cleaned = self._clean(value)

        if not cleaned:
            return None

        # --------------------------------------------------------------
        # Controlliamo se questo valore era già stato ignorato.
        # --------------------------------------------------------------

        if any( self._key(item) == self._key(cleaned) for item in self.ignore ):
            return None

        words = cleaned.split()

        if len(words) < 2:
            return None
        elif len(words) > 2:
            # Ricerca automatica.
            candidates = self._find_surname_candidates( words )
        else:
            # Ricerca manuale.
            candidates = None


        # --------------------------------------------------------------
        # Nessun candidato.
        # --------------------------------------------------------------
        if not candidates:
            indexes = self._author_prompt( cleaned, words, )

            # 0 = ignora
            if indexes is None:
                self._add_ignore(cleaned)
                return None

            surname = " ".join( words[index] for index in indexes )

            name = " ".join( word for index, word in enumerate(words) if index not in indexes )

            self._add( surname, name, )

            return surname, name

        # --------------------------------------------------------------
        # I candidati sono già ordinati per numero di parole,
        # quindi il primo è quello più specifico.
        # --------------------------------------------------------------

        best_length = len( candidates[0][1] )

        best = [ candidate for candidate in candidates if len(candidate[1]) == best_length ]

        # --------------------------------------------------------------
        # Una sola soluzione.
        # --------------------------------------------------------------
        if len(best) == 1:
            surname, indexes = best[0]
            name = " ".join( word for index, word in enumerate(words) if index not in indexes )

            if name:
                self._add( surname, name, )

            return surname, name

        # --------------------------------------------------------------
        # Più soluzioni equivalenti.
        #
        # Per il momento chiediamo all'utente.
        # --------------------------------------------------------------

        return self._resolve_candidates( cleaned, words, best, )

    # ==================================================================
    # Risoluzione candidati
    # ==================================================================

    def _resolve_candidates( self, author: str, words: list[str], candidates: list[ tuple[str, tuple[int, ...]] ], ) -> tuple[str, str] | None:
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

            if value == "0":
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

    def format( self, value: str | None, canonical: bool = True, ) -> str:
        """
        Normalizza e formatta un autore.

        canonical=True:

            'Surname, Name'

        canonical=False:

            'Surname Name'

        Se l'autore non viene riconosciuto e l'utente
        seleziona 0, restituisce una stringa vuota.
        """

        if not value:
            return ""

        author = self._identify(value)

        if author is None:
            return ""

        surname, name = author

        if not name:
            return surname

        if canonical:
            return f"{surname}, {name}"

        return f"{surname} {name}"

    # ==================================================================
    # Utility
    # ==================================================================

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
