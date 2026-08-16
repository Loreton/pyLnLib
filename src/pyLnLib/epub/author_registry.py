from __future__ import annotations

import re
from pathlib import Path
import yaml


class AuthorRegistry:
    """
    Registro persistente degli autori.

    Esempio di YAML:

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

          De La Fontaine:
            - Jean

    Il registro permette di riconoscere automaticamente gli autori
    già conosciuti e di chiedere all'utente come interpretare quelli
    nuovi.
    """

    def __init__(self, filename: str | Path):
        self.filename = Path(filename)

        # Forma interna:
        #
        # {
        #     "Smith": {"John", "Mark", "David"},
        #     "Eco": {"Umberto"},
        #     "García Márquez": {"Gabriel"},
        # }
        self.authors: dict[str, set[str]] = {}

        self.load()

    # ==================================================================
    # Normalizzazione
    # ==================================================================

    @staticmethod
    def _key(value: str) -> str:
        """
        Restituisce la chiave usata per i confronti.

        Il confronto è case-insensitive.
        """
        return value.strip().casefold()

    @staticmethod
    def clean_author(value: str) -> str:
        """
        Pulisce il nome dell'autore.

        Vengono mantenuti:
            - lettere Unicode
            - numeri
            - spazi

        La virgola viene considerata come separatore.

        Esempi:

            'mark, Smith, .-'
                -> 'mark Smith'

            'García Márquez, Gabriel'
                -> 'García Márquez Gabriel'
        """

        # La virgola viene trasformata in spazio.
        value = value.replace(",", " ")

        # Manteniamo caratteri alfanumerici Unicode e spazi.
        value = re.sub(
            r"[^\w\s]",
            " ",
            value,
            flags=re.UNICODE,
        )

        # Normalizziamo gli spazi.
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

        authors = data.get("authors", {})

        for surname, names in authors.items():

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

        # Ordiniamo i cognomi per mantenere il file leggibile.
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
    # Ricerca cognome
    # ==================================================================

    def find_surname(
        self,
        value: str,
    ) -> str | None:
        """
        Cerca un cognome nel registro.

        Il confronto non distingue maiuscole/minuscole.

        Restituisce il valore originale presente nel YAML.
        """

        key = self._key(value)

        for surname in self.authors:

            if self._key(surname) == key:
                return surname

        return None

    def find_surname_in_words( self, words: list[str], ) -> tuple[str, int, int] | None:
        """
        Cerca un cognome all'interno di una lista di parole.

        Vengono provate tutte le sequenze consecutive, partendo
        dalle più lunghe.

        Esempio:

            words = [
                "Gabriel",
                "García",
                "Márquez",
            ]

        Se nel registro esiste:

            García Márquez

        restituisce:

            ("García Márquez", 1, 2)

        dove:

            surname = "García Márquez"
            start   = 1
            length  = 2
        """

        if not words:
            return None

        # Prima proviamo le sequenze più lunghe.
        #
        # Esempio con 4 parole:
        #
        # lunghezza 4
        # lunghezza 3
        # lunghezza 2
        # lunghezza 1
        #
        # In questo modo "De La Fontaine" viene preferito
        # a "Fontaine" se entrambi fossero presenti.
        for length in range( len(words), 0, -1, ):
            for start in range( len(words) - length + 1 ):
                candidate = " ".join( words[start:start + length] )
                surname = self.find_surname(candidate)

                if surname is not None:
                    return surname, start, length

        return None

    # ==================================================================
    # Ricerca nome
    # ==================================================================

    def find_name( self, surname: str, name: str, ) -> bool:
        """
        Verifica se la coppia cognome/nome è già conosciuta.
        """

        real_surname = self.find_surname(surname)

        if real_surname is None:
            return False

        name_key = self._key(name)

        return any(
            self._key(item) == name_key
            for item in self.authors[real_surname]
        )

    # ==================================================================
    # Inserimento
    # ==================================================================

    def add( self, surname: str, name: str, save: bool = True, ) -> None:
        """
        Aggiunge un autore al registro.

        Se il cognome esiste già, viene aggiunto solamente
        il nuovo nome.
        """

        surname = " ".join(surname.split())
        name = " ".join(name.split())

        real_surname = self.find_surname(surname)

        if real_surname is None:

            self.authors[surname] = {name}

        else:

            self.authors[real_surname].add(name)

        if save:
            self.save()

    # ==================================================================
    # Prompt
    # ==================================================================

    def _author_prompt( self, author: str, words: list[str], ) -> list[int]:
        """
        Chiede all'utente quali parole compongono il cognome.

        Esempio:

            Autore sconosciuto: Jean De La Fontaine

              1) Jean
              2) De
              3) La
              4) Fontaine

            Inserisci gli indici del cognome [es. 2 3 4]:

        Restituisce gli indici zero-based.
        """

        print()
        print(f"Autore sconosciuto: {author}")
        print()
        print("Quali parole compongono il cognome?")

        for index, word in enumerate( words, start=1, ):
            print(f"  {index}) {word}")

        while True:
            value = input( "Inserisci gli indici " "del cognome [es. 2 3 4]: " ).strip()

            if not value:
                print( "Specificare almeno una parola." )
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

            # ----------------------------------------------------------
            # Verifica che gli indici siano validi.
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
            # Eliminiamo eventuali duplicati.
            # ----------------------------------------------------------
            if len(indexes) != len(set(indexes)):
                print(
                    "Non è possibile specificare "
                    "lo stesso indice più volte."
                )
                continue

            # ----------------------------------------------------------
            # Il cognome deve essere composto da parole consecutive.
            # ----------------------------------------------------------
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
    # Identificazione
    # ==================================================================

    def identify( self, value: str, ) -> tuple[str, str] | None:
        """
        Identifica un autore.

        Restituisce:

            (cognome, nome)

        oppure None se non è possibile identificarlo.

        La procedura è:

        1. pulisce il valore;
        2. cerca un cognome già conosciuto;
        3. supporta cognomi composti;
        4. se trova il cognome, il resto è il nome;
        5. se il cognome non è conosciuto, chiede all'utente;
        6. salva la nuova associazione.
        """

        cleaned = self.clean_author(value)

        if not cleaned:
            return None

        words = cleaned.split()

        if len(words) < 2:
            return None

        # --------------------------------------------------------------
        # Cerchiamo un cognome conosciuto.
        # --------------------------------------------------------------
        found = self.find_surname_in_words(words)

        if found is not None:
            surname, start, length = found

            # ----------------------------------------------------------
            # Il cognome occupa una sequenza di parole.
            #
            # Esempio:
            #
            #   ["Jean", "De", "La", "Fontaine"]
            #             ^^^^^^^^^^^^^^^^^^^
            #
            # start  = 1
            # length = 3
            # ----------------------------------------------------------

            name_words = (
                words[:start]
                + words[start + length:]
            )

            name = " ".join(name_words)

            # ----------------------------------------------------------
            # Il cognome è già noto.
            #
            # Se il nome non è ancora presente, lo aggiungiamo.
            # ----------------------------------------------------------

            self.add( surname, name, )

            return surname, name

        # --------------------------------------------------------------
        # Nessun cognome conosciuto.
        # --------------------------------------------------------------

        indexes = self._author_prompt( cleaned, words )

        # --------------------------------------------------------------
        # Costruiamo il cognome.
        # --------------------------------------------------------------

        surname = " ".join( words[index] for index in indexes )

        # --------------------------------------------------------------
        # Tutte le altre parole costituiscono il nome.
        # --------------------------------------------------------------

        name = " ".join(
            word
            for index, word in enumerate(words)
            if index not in indexes
        )

        # --------------------------------------------------------------
        # Registriamo la nuova associazione.
        # --------------------------------------------------------------

        self.add( surname, name )

        return surname, name

    # ==================================================================
    # Formattazione
    # ==================================================================

    @staticmethod
    def format( author: tuple[str, str] | None, ) -> str:
        """
        Restituisce l'autore nella forma:

            Cognome, Nome
        """

        if author is None:
            return ""

        surname, name = author

        if not name:
            return surname

        return f"{surname}, {name}"

    # ==================================================================
    # Utility
    # ==================================================================

    def __iter__(self):
        """
        Itera sugli autori in ordine alfabetico.
        """

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
        """
        Restituisce il numero totale di combinazioni
        cognome/nome registrate.
        """

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
