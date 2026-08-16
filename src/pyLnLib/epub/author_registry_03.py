from __future__ import annotations

import re
from pathlib import Path

import yaml


class AuthorRegistry:
    """
    Registro persistente degli autori.

    Il formato YAML è:

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

    L'uso normale della classe è semplicemente:

        author = registry.format(book.author)

    La classe si occupa autonomamente di:
        - pulizia del nome
        - ricerca
        - riconoscimento dei cognomi composti
        - richiesta all'utente quando necessario
        - aggiornamento del registro
        - salvataggio YAML
    """

    def __init__(self, filename: str | Path):
        self.filename = Path(filename)
        self.authors: dict[str, set[str]] = {}

        self.load()

    # ==================================================================
    # Normalizzazione
    # ==================================================================

    @staticmethod
    def _key(value: str) -> str:
        """Chiave per confronti case-insensitive."""

        return value.strip().casefold()

    @staticmethod
    def _clean(value: str) -> str:
        """
        Pulisce una stringa autore.

        Esempio:

            'mark, Smith, .-'

        diventa:

            'mark Smith'
        """

        value = value.replace(",", " ")

        value = re.sub(
            r"[^\w\s]",
            " ",
            value,
            flags=re.UNICODE,
        )

        return " ".join(value.split())

    # ==================================================================
    # YAML
    # ==================================================================

    def load(self) -> None:
        """Carica il registro dal file YAML."""

        self.authors.clear()

        if not self.filename.exists():
            return

        with self.filename.open(
            "r",
            encoding="utf-8",
        ) as fp:
            data = yaml.safe_load(fp) or {}

        for surname, names in data.get("authors", {}).items():

            if names is None:
                names = []

            self.authors[str(surname)] = {
                str(name)
                for name in names
            }

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

        data = {
            "authors": authors,
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
    # Ricerca
    # ==================================================================

    def _find_surname(
        self,
        value: str,
    ) -> str | None:
        """Cerca un cognome nel registro."""

        key = self._key(value)

        for surname in self.authors:

            if self._key(surname) == key:
                return surname

        return None

    def _find_surname_in_words(
        self,
        words: list[str],
    ) -> tuple[str, int, int] | None:
        """
        Cerca un cognome composto all'interno delle parole.

        Restituisce:

            surname, start, length

        Esempio:

            ['Vincent', 'van', 'Gogh']

        restituisce:

            ('van Gogh', 1, 2)
        """

        if not words:
            return None

        # Prima le sequenze più lunghe.
        for length in range(
            len(words),
            0,
            -1,
        ):
            for start in range(
                len(words) - length + 1
            ):
                candidate = " ".join(
                    words[start:start + length]
                )

                surname = self._find_surname(candidate)

                if surname is not None:
                    return surname, start, length

        return None

    # ==================================================================
    # Inserimento
    # ==================================================================

    def _add(
        self,
        surname: str,
        name: str,
    ) -> None:
        """Aggiunge un'associazione cognome/nome."""

        surname = " ".join(surname.split())
        name = " ".join(name.split())

        real_surname = self._find_surname(surname)

        if real_surname is None:
            self.authors[surname] = {name}
        else:
            self.authors[real_surname].add(name)

        self.save()

    # ==================================================================
    # Prompt
    # ==================================================================

    def _author_prompt(
        self,
        author: str,
        words: list[str],
    ) -> list[int]:
        """
        Chiede all'utente quali parole compongono il cognome.

        Esempio:

            Autore sconosciuto: Jean De La Fontaine

              1) Jean
              2) De
              3) La
              4) Fontaine

            Inserisci gli indici del cognome [es. 2 3 4]:
        """

        print()
        print(f"Autore sconosciuto: {author}")
        print()
        print("Quali parole compongono il cognome?")

        for index, word in enumerate(
            words,
            start=1,
        ):
            print(f"  {index}) {word}")

        while True:

            value = input(
                "Inserisci gli indici "
                "del cognome [es. 2 3 4]: "
            ).strip()

            if not value:
                print("Specificare almeno una parola.")
                continue

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

            if any(
                index < 0 or index >= len(words)
                for index in indexes
            ):
                print("Indice non valido.")
                continue

            if len(indexes) != len(set(indexes)):
                print("Indice duplicato.")
                continue

            # Le parole del cognome devono essere consecutive.
            expected = list(
                range(
                    indexes[0],
                    indexes[0] + len(indexes),
                )
            )

            if indexes != expected:
                print(
                    "Le parole del cognome devono "
                    "essere consecutive."
                )
                continue

            return indexes

    # ==================================================================
    # Identificazione interna
    # ==================================================================

    def _identify(
        self,
        value: str,
    ) -> tuple[str, str] | None:
        """
        Identifica internamente un autore.

        Questo metodo NON dovrebbe essere normalmente chiamato
        dall'esterno. Il punto di ingresso pubblico è format().
        """

        cleaned = self._clean(value)

        if not cleaned:
            return None

        words = cleaned.split()

        if len(words) < 2:
            return None

        # --------------------------------------------------------------
        # Tentativo automatico
        # --------------------------------------------------------------

        found = self._find_surname_in_words(words)

        if found is not None:

            surname, start, length = found

            name_words = (
                words[:start]
                + words[start + length:]
            )

            name = " ".join(name_words)

            # Il cognome è noto.
            # Se il nome è nuovo viene semplicemente aggiunto.
            if name:
                self._add(
                    surname,
                    name,
                )

            return surname, name

        # --------------------------------------------------------------
        # Non riconosciuto.
        # Chiediamo all'utente.
        # --------------------------------------------------------------

        indexes = self._author_prompt(
            cleaned,
            words,
        )

        surname = " ".join(
            words[index]
            for index in indexes
        )

        name = " ".join(
            word
            for index, word in enumerate(words)
            if index not in indexes
        )

        self._add(
            surname,
            name,
        )

        return surname, name

    # ==================================================================
    # API pubblica
    # ==================================================================
    def format( self, value: str | None, canonical: bool = True ) -> str:
        """
        Normalizza e formatta un autore.

        canonical=True:
            'Surname, Name'

        canonical=False:
            'Surname Name'
        """
        if not value:
            return ""
        print(value)

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
