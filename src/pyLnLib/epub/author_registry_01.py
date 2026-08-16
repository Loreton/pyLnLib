from __future__ import annotations

import re
from pathlib import Path
# from collections.abc import Callable

import yaml

from ..varie.keyboard_prompt import keyboardPrompt


class AuthorRegistry:
    """
    Registro persistente degli autori.

    Esempio YAML:

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
    """

    def __init__(self, filename: str | Path):
        self.filename = Path(filename)
        self.authors: dict[str, set[str]] = {}

        self.load()

    # ------------------------------------------------------------------
    # Normalizzazione
    # ------------------------------------------------------------------

    @staticmethod
    def _key(value: str) -> str:
        """Chiave utilizzata per i confronti case-insensitive."""
        return value.strip().casefold()

    @staticmethod
    def clean_author(value: str) -> str:
        """
        Pulisce il nome dell'autore.

        Esempio:

            'mark, Smith, .-'
                ->
            'mark Smith'
        """

        # La virgola viene considerata separatore.
        value = value.replace(",", " ")

        # Manteniamo lettere Unicode, numeri e spazi.
        value = re.sub( r"[^\w\s]", " ", value, flags=re.UNICODE, )

        return " ".join(value.split())

    # ------------------------------------------------------------------
    # YAML
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Carica il registro dal file YAML."""

        self.authors.clear()

        if not self.filename.exists():
            return

        with self.filename.open( "r", encoding="utf-8", ) as fp:
            data = yaml.safe_load(fp) or {}

        for surname, names in data.get("authors", {}).items():
            if names is None:
                names = []

            self.authors[str(surname)] = { str(name) for name in names }


    #=======================================
    def save(self) -> None:
        """Salva il registro nel file YAML."""

        self.filename.parent.mkdir( parents=True, exist_ok=True, )

        authors = {}

        for surname in sorted( self.authors, key=str.casefold, ):
            authors[surname] = sorted( self.authors[surname], key=str.casefold, )

        data = {
            "authors": authors,
        }

        with self.filename.open( "w", encoding="utf-8", ) as fp:
            yaml.safe_dump( data, fp, allow_unicode=True, sort_keys=False, indent=4, default_flow_style=False, )


    #=======================================
    # Ricerca cognomi
    #=======================================
    def find_surname(self, value: str) -> str | None:
        """
        Cerca un cognome nel registro.

        Il confronto non distingue maiuscole/minuscole.
        """

        key = self._key(value)

        for surname in self.authors:
            if self._key(surname) == key:
                return surname

        return None

    #=======================================
    # Ricerca cognomi
    #=======================================
    def find_surname_in_words( self, words: list[str], ) -> tuple[str, int] | None:
        """
        Cerca un cognome all'interno di una lista di parole.

        Vengono provate prima le combinazioni più lunghe.

        Esempio:

            words = ["Gabriel", "García", "Márquez"]

        con:

            García Márquez

        nel registro restituisce:

            ("García Márquez", 2)

        Il secondo valore indica quante parole compongono il cognome.
        """

        if not words:
            return None

        # Proviamo prima i cognomi più lunghi.
        for length in range( len(words) - 1, 0, -1, ):
            for start in range( len(words) - length + 1 ):
                candidate = " ".join( words[start:start + length] )

                surname = self.find_surname(candidate)

                if surname is not None:
                    return surname, length

        return None

    # ------------------------------------------------------------------
    # Ricerca nomi
    # ------------------------------------------------------------------

    def find_name( self, surname: str, name: str, ) -> bool:
        """Verifica se la coppia cognome/nome è conosciuta."""

        real_surname = self.find_surname(surname)

        if real_surname is None:
            return False

        name_key = self._key(name)

        return any( self._key(item) == name_key for item in self.authors[real_surname] )

    # ------------------------------------------------------------------
    # Inserimento
    # ------------------------------------------------------------------

    def add( self, surname: str, name: str, save: bool = True, ) -> None:
        """Aggiunge un autore al registro."""

        surname = " ".join(surname.split())
        name = " ".join(name.split())

        real_surname = self.find_surname(surname)

        if real_surname is None:
            self.authors[surname] = {name}
        else:
            self.authors[real_surname].add(name)

        if save:
            self.save()

    # ------------------------------------------------------------------
    # Identificazione
    # ------------------------------------------------------------------

    def identify( self, value: str, prompt: bool=True) -> tuple[str, str] | None:
        """
        Identifica un autore.

        Restituisce:

            (cognome, nome)

        oppure None se non è possibile identificarlo.
        """

        cleaned = self.clean_author(value)

        if not cleaned:
            return None

        words = cleaned.split()

        if len(words) < 2:
            return None

        # --------------------------------------------------------------
        # 1. Cerchiamo un cognome già presente nel registro.
        # --------------------------------------------------------------
        found = self.find_surname_in_words(words)

        if found is not None:
            surname, surname_length = found

            # Troviamo esattamente le parole che compongono
            # il cognome.
            surname_words = self._key(surname).split()

            remaining = words.copy()

            # Rimuoviamo dal testo le parole del cognome.
            for surname_word in surname_words:
                for index, word in enumerate(remaining):
                    if self._key(word) == self._key(surname_word):
                        remaining.pop(index)
                        break

            name = " ".join(remaining)

            # ----------------------------------------------------------
            # Il cognome è noto.
            #
            # Se il nome è nuovo, lo aggiungiamo automaticamente.
            # Non serve chiedere all'utente quale sia il cognome.
            # ----------------------------------------------------------

            if name:
                self.add(surname, name)

            return surname, name

        # --------------------------------------------------------------
        # 2. Nessun cognome conosciuto.
        # --------------------------------------------------------------

        if prompt is None:
            return None

        # index = prompt(cleaned, words)
        index = self._author_prompt(cleaned, words)

        if not 0 <= index < len(words):
            return None

        surname = words[index]

        name = " ".join( word for i, word in enumerate(words) if i != index )

        self.add(surname, name)

        return surname, name

    # ------------------------------------------------------------------
    # Formattazione
    # ------------------------------------------------------------------

    @staticmethod
    def format( author: tuple[str, str], ) -> str:
        """Restituisce l'autore nella forma canonica."""

        surname, name = author

        if not name:
            return surname

        return f"{surname}, {name}"

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def __iter__(self):
        for surname in sorted( self.authors, key=str.casefold, ):
            for name in sorted( self.authors[surname], key=str.casefold, ):
                yield surname, name

    def __len__(self) -> int:
        return sum(
            len(names)
            for names in self.authors.values()
        )

    def _author_prompt(self, author: str, words: list[str], ) -> int:

        print()
        print(f"Autore sconosciuto: {author}")
        print()
        print("Quale parola è il cognome?")

        for index, word in enumerate(words, start=1):
            print(f"  {index}) {word}")

        while True:
            try:
                breakpoint()
                choice = int(input("> ")) - 1

                if 0 <= choice < len(words):
                    return choice

            except ValueError:
                pass

            print("Scelta non valida.")

def author_prompt( author: str, words: list[str], ) -> int:

    print()
    print(f"Autore sconosciuto: {author}")
    print()
    print("Quale parola è il cognome?")

    for index, word in enumerate(words, start=1):
        print(f"  {index}) {word}")

    while True:
        try:
            choice = int(input("> ")) - 1

            if 0 <= choice < len(words):
                return choice

        except ValueError:
            pass

        print("Scelta non valida.")

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
        # author = registry.identify( value, prompt=author_prompt, )
        author = registry.identify( value, prompt=True )

        print(
            f"{value!r:30} -> "
            f"{registry.format(author) if author else None}"
        )
