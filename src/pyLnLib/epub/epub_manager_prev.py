#!/usr/bin/env python3
# ln_ebook_manager.py
#
# ruff: noqa: BLE001  Do not catch blind exception: `Exception` (Ruff BLE001)
# ruff: noqa: I001  Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
#
#
#
from __future__ import annotations

import json
from _collections_abc import Generator
from pathlib import Path
from dataclasses import dataclass

from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT

from pyLnLib.logger import get_logger
from pyLnLib.files import get_unique_filename

logger = get_logger()


# per memorizzare le section dell'ebook
@dataclass(slots=True)
class BookSection:
    file: str
    title: str | None
    text: str


class EpubProcessor:
    """ Simple EPUB reader.
    da usare con il context manager:
        for file in book_files:
            with EpubProcessor(file) as processor:
                if processor:  # Usa __bool__
                    valid_books.append(processor)
                    print(f"✅ {processor.get_title()} - {processor.get_author()}")
                else:
                    print(f"❌ {file.name}: EPUB non valido")
    ...oppure

    book = get_epub_processor(file)
    if book is None:
        continue
    """

    def __init__(self, filename: str | Path):
        self._file_path = Path(filename)
        self._sections: list[BookSection] | None = None
        self._book = None
        self._is_valid = True
        self._index = 0

        if not self._file_path.is_file():
            raise FileNotFoundError(f"File non trovato: {self._file_path}")

        try:
            self._book = epub.read_epub(str(self._file_path))
            self._is_valid = True

        except Exception as e:
            logger.error(f"{self._file_path.stem}\nFailed to read EPUB: {e}")
            self._book = None
            self._is_valid = False

    def __bool__(self):
        return self._is_valid and self._book is not None

    # - utilizzato da manage_epub_processor() per permettere di conoscere il numero di libri processati
    def set_index(self, index: int):
        self._index = index

    @property
    def index(self) -> int:
        return self._index

    # ======================================================================
    # Properties
    # ======================================================================

    @property
    def file_path(self) -> Path:
        return self._file_path

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    # ======================================================================
    # Metadata - Lettura
    # ======================================================================

    def _get_dc_XXX(self, key: str) -> str | None:
        """Legge un metadata DC (Dublin Core)."""
        values = self._book.get_metadata("DC", key)
        if not values:
            return None
        return values[0][0]

    @property
    def metadata(self) -> dict:
        return self._book.metadata

    @property
    def title(self) -> str | None:
        return self._get_dc("title")

    @property
    def author(self) -> str | None:
        return self._get_dc("creator")

    @property
    def language(self) -> str | None:
        return self._get_dc("language")

    @property
    def publisher(self) -> str | None:
        return self._get_dc("publisher")

    @property
    def date(self) -> str | None:
        return self._get_dc("date")

    @property
    def identifier(self) -> str | None:
        return self._get_dc("identifier")

    # ======================================================================
    # Metadata - Scrittura (SOLUZIONE CHE FUNZIONA)
    # ======================================================================

    def _clear_all_dc_metadata(self) -> None:
        """
        Rimuove TUTTI i metadati DC dal libro.
        Questo è drastico ma necessario per evitare duplicati.
        """
        # Rimuovi dal dizionario metadata
        if 'DC' in self._book.metadata:
            del self._book.metadata['DC']

        # Rimuovi anche dalla struttura interna di ebooklib
        # ebooklib tiene traccia dei metadati in self._book.metadata
        # ma anche in self._book._metadata (struttura interna)
        if hasattr(self._book, '_metadata'):
            if 'DC' in self._book._metadata:
                del self._book._metadata['DC']









    def _rebuild_dc_metadata(self, updates: dict[str, str]) -> None:
        """
        Aggiorna i metadati DC rimuovendo le chiavi esistenti (comprese le tuple/namespace)
        e reinserendo i nuovi valori tramite l'API nativa di ebooklib.
        """
        if 'DC' not in self._book.metadata:
            self._book.metadata['DC'] = {}

        dc_dict = self._book.metadata['DC']

        for key, new_val in updates.items():
            if new_val is None:
                continue

            # 1. Trova e rimuovi TUTTE le varianti della chiave (sia stringhe che tuple)
            keys_to_remove = [
                k for k in list(dc_dict.keys())
                if (isinstance(k, str) and k.lower() == key.lower())
                or (isinstance(k, tuple) and len(k) > 1 and k[1].lower() == key.lower())
            ]
            for k in keys_to_remove:
                del dc_dict[k]

            # 2. Re-inserisci il nuovo valore tramite l'API ufficiale
            self._book.add_metadata('DC', key, str(new_val))




    def _get_dc(self, key: str) -> str | None:
         """Legge il primo valore di un metadata DC."""
         if not self._book:
             return None
         values = self._book.get_metadata("DC", key)
         if not values:
             return None
         return values[0][0]

    def set_dc_metadata(self, key: str, value: str) -> bool:
         """
         Modifica un metadata DC (Dublin Core) sovrascrivendolo completamente.
         """
         if not self._is_valid or self._book is None:
             logger.error("EPUB non valido")
             return False

         try:
             # Assicurati che il dizionario DC esista
             if 'DC' not in self._book.metadata:
                 self._book.metadata['DC'] = {}

             dc_dict = self._book.metadata['DC']

             # 1. Trova TUTTE le chiavi nel dizionario 'DC' che corrispondono a key (ignorando il case)
             keys_to_remove = [k for k in dc_dict.keys() if str(k).lower() == key.lower()]

             # 2. Elimina fisicamente le chiavi esistenti dal dizionario interno
             for k in keys_to_remove:
                 del dc_dict[k]

             # 3. Aggiungi il nuovo metadato usando l'API nativa
             if value is not None:
                 self._book.add_metadata('DC', key, str(value))

             logger.debug(f"Metadata '{key}' impostato a: {value}")
             return True

         except Exception as e:
             logger.error(f"Errore nell'impostare '{key}': {e}")
             return False

















    def set_multiple_metadata(self, updates: dict[str, str]) -> bool:
        """Modifica multipli metadata DC in una sola operazione."""
        if not self._is_valid:
            logger.error("EPUB non valido")
            return False

        success = True
        for key, value in updates.items():
            if not self.set_dc_metadata(key, value):
                success = False

        return success




    def set_dc_metadata_XXX(self, key: str, value: str) -> bool:
        """
        Modifica un metadata DC (Dublin Core).
        Sostituisce completamente il valore esistente.

        Args:
            key: Chiave del metadata (es. 'title', 'creator', 'publisher', etc.)
            value: Nuovo valore

        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if not self._is_valid:
            logger.error("EPUB non valido")
            return False

        try:
            # Leggi TUTTI i metadati DC esistenti
            all_metadata = {}

            # Leggi tutti i metadati che ci interessano
            dc_keys = ['title', 'creator', 'publisher', 'language', 'date', 'identifier',
                      'description', 'subject', 'coverage', 'rights', 'format', 'type',
                      'source', 'relation', 'contributor']

            for k in dc_keys:
                if k == key:
                    # Questo è il valore che vogliamo sostituire
                    continue
                values = self._book.get_metadata('DC', k)
                if values:
                    # Prendi il primo valore e i suoi attributi
                    all_metadata[k] = values[0]

            # Rimuovi TUTTI i metadati DC
            self._clear_all_dc_metadata()

            # Ricostruisci i metadati con i valori salvati + il nuovo
            all_metadata[key] = (value, {})

            # Aggiungi tutti i metadati
            for k, (v, attrs) in all_metadata.items():
                self._book.add_metadata('DC', k, v, attrs if attrs else {})

            logger.debug(f"Metadata '{key}' impostato a: {value}")
            return True

        except Exception as e:
            logger.error(f"Errore nell'impostare '{key}': {e}")
            return False

    def set_multiple_metadata_XXX(self, updates: dict[str, str]) -> bool:
        """
        Modifica multipli metadata DC in una sola operazione.

        Args:
            updates: Dizionario con le chiavi e valori da aggiornare

        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if not self._is_valid:
            logger.error("EPUB non valido")
            return False

        try:
            # Leggi TUTTI i metadati DC esistenti
            all_metadata = {}

            dc_keys = ['title', 'creator', 'publisher', 'language', 'date', 'identifier',
                      'description', 'subject', 'coverage', 'rights', 'format', 'type',
                      'source', 'relation', 'contributor']

            for k in dc_keys:
                if k in updates:
                    # Questo valore verrà sostituito
                    continue
                values = self._book.get_metadata('DC', k)
                if values:
                    all_metadata[k] = values[0]

            # Rimuovi TUTTI i metadati DC
            self._clear_all_dc_metadata()

            # Aggiungi i valori aggiornati
            for k, v in updates.items():
                all_metadata[k] = (v, {})

            # Aggiungi tutti i metadati
            for k, (v, attrs) in all_metadata.items():
                self._book.add_metadata('DC', k, v, attrs if attrs else {})

            logger.debug(f"Multipli metadata aggiornati: {updates}")
            return True

        except Exception as e:
            logger.error(f"Errore nell'impostare multipli metadata: {e}")
            return False

    def set_title(self, new_title: str) -> bool:
        """Modifica il titolo."""
        return self.set_dc_metadata('title', new_title)

    def set_author(self, new_author: str) -> bool:
        """Modifica l'autore."""
        return self.set_dc_metadata('creator', new_author)

    def set_publisher(self, new_publisher: str) -> bool:
        """Modifica l'editore."""
        return self.set_dc_metadata('publisher', new_publisher)

    def set_language(self, new_language: str) -> bool:
        """Modifica la lingua."""
        return self.set_dc_metadata('language', new_language)

    def set_date(self, new_date: str) -> bool:
        """Modifica la data."""
        return self.set_dc_metadata('date', new_date)

    def set_identifier(self, new_identifier: str) -> bool:
        """Modifica l'identificatore."""
        return self.set_dc_metadata('identifier', new_identifier)

    # ======================================================================
    # Save
    # ======================================================================

    def save(self, output_path: str | Path) -> bool:
        """Salva le modifiche all'EPUB."""
        if not self._is_valid:
            logger.error("EPUB non valido, impossibile salvare")
            return False

        try:
            # output = Path(output_path) if output_path else self._file_path
            # breakpoint()
            output = Path(output_path)
            epub.write_epub(name=str(output), book=self._book)
            logger.info(f"EPUB salvato in: {output}")
            return True
        except Exception as e:
            logger.error(f"Errore durante il salvataggio: {e}")
            return False

    # ======================================================================
    # Content
    # ======================================================================

    def get_sections(self) -> list[BookSection]:
        """
        Return the ebook sections.

        The EPUB is parsed only the first time this method is called.
        """

        if self._sections is not None:
            return self._sections

        sections: list[BookSection] = []

        for item in self._book.get_items():

            if item.get_type() != ITEM_DOCUMENT:
                continue

            soup = BeautifulSoup(
                item.get_body_content(),
                "html.parser"
            )

            text = soup.get_text(separator=" ", strip=True)

            title = None

            if soup.title:
                title = soup.title.get_text(strip=True)

            if not title:
                h1 = soup.find("h1")
                if h1:
                    title = h1.get_text(strip=True)

            sections.append(
                BookSection(
                    file=item.file_name,
                    title=title,
                    text=text,
                )
            )

        self._sections = sections
        return self._sections

    def get_text(self) -> str:
        return "\n\n".join(
            section.text
            for section in self.get_sections()
            if section.text
        )

    # ======================================================================
    # Export
    #   replace: sovrascrive se il file esiste
    #   unique:  crea uno con nome diverso e il file esiste
    # ======================================================================

    def to_text(self, txt_filename: Path|str, replace: bool = False, force_log: bool=False) -> bool:
        logger.debug("Exporting epub book:\n%s\nto txt file:\n%s", self._file_path, txt_filename, force_log=force_log)

        if isinstance(txt_filename, str):
            txt_filename = Path(txt_filename)

        if not txt_filename.parent.exists():
            logger.debug("Creating target parent directory", force_log=force_log)
            txt_filename.parent.mkdir(parents=True, exist_ok=True)

        if txt_filename.exists():
            if replace: # sovrascrive il file esistente
                logger.debug("\tremoving existing file due to replace option!", force_log=force_log)
                txt_filename.unlink()
            else:
                logger.debug("\tfile already exists!", force_log=force_log)
                return False # non modifica il file esistente

        try:
            with txt_filename.open("w", encoding="utf-8") as fp:
                fp.write("=" * 60 + "\n")
                fp.write("METADATI\n")
                fp.write("=" * 60 + "\n")

                fp.write(f"Titolo          : {self.title}\n")
                fp.write(f"Autore          : {self.author}\n")
                fp.write(f"Lingua          : {self.language}\n")
                fp.write(f"Editore         : {self.publisher}\n")
                fp.write(f"Data            : {self.date}\n")
                fp.write(f"Identificativo  : {self.identifier}\n")
                fp.write(f"File originale  : {self.file_path.name}\n")

                fp.write("\n")
                fp.write("=" * 60 + "\n")
                fp.write("CONTENUTO\n")
                fp.write("=" * 60 + "\n\n")

                for n, section in enumerate(self.get_sections(), start=1):
                    fp.write("=" * 40 + "\n")
                    fp.write(f"SEZIONE {n}\n")
                    fp.write("=" * 40 + "\n")

                    fp.write(f"File   : {section.file}\n")

                    if section.title:
                        fp.write(f"Titolo : {section.title}\n")

                    fp.write("\n")
                    fp.write(section.text)
                    fp.write("\n\n")

        except Exception as e:
            logger.error("Errore durante l'esportazione del libro in formato testo: %s", txt_filename)
            logger.error("Dettagli dell'errore: %s", e)
            txt_filename.unlink(missing_ok=True)
            return False

        logger.debug("\tsaved filename: %s", txt_filename, force_log=force_log)
        return True

    # ======================================================================
    # Custom Metadata
    # ======================================================================

    def set_custom_metadata(self, key: str, value: str, namespace: str = "CUSTOM") -> bool:
        """Imposta un metadata custom."""
        if not self._is_valid:
            logger.error("EPUB non valido")
            return False

        try:
            # Rimuovi vecchio valore
            if namespace not in self._book.metadata:
                self._book.metadata[namespace] = {}

            # ebooklib usa liste di tuple per i valori
            # rimuoviamo eventuali valori esistenti per questa chiave
            self._book.metadata[namespace] = {
                k: v for k, v in self._book.metadata[namespace].items()
                if k != key
            }

            self._book.add_metadata(namespace, key, value)
            logger.debug(f"Metadata custom impostato: {namespace}:{key} = {value}")
            return True

        except Exception as e:
            logger.error(f"Errore nell'impostare metadata custom: {e}")
            return False

    def get_custom_metadata(self, key: str, namespace: str = "CUSTOM") -> str | None:
        """Recupera un metadata custom."""
        if not self._is_valid:
            return None

        try:
            values = self._book.get_metadata(namespace, key)
            return values[0][0] if values else None
        except Exception as e:
            logger.error(f"Errore nel recuperare metadata custom: {e}")
            return None

    def set_custom_json(self, data: dict, key: str = 'custom_data') -> bool:
        """Salva dati JSON come metadata custom."""
        try:
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            return self.set_custom_metadata(key, json_str)
        except Exception as e:
            logger.error(f"Errore nella serializzazione JSON: {e}")
            return False

    def get_custom_json(self, key: str = 'custom_data') -> dict | None:
        """Recupera e deserializza dati JSON."""
        data = self.get_custom_metadata(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                logger.error("Errore nella deserializzazione JSON")
                return None
        return None

    def list_custom_metadata(self, namespace: str = "CUSTOM") -> dict:
        """Lista tutti i metadata custom in un namespace."""
        if not self._is_valid:
            return {}

        try:
            return self._book.metadata.get(namespace, {})
        except Exception as e:
            logger.error(f"Errore nel listare metadata custom: {e}")
            return {}


# ============================================
# Funzioni di utilità
# ============================================

def get_epub_processor(filename: str | Path) -> EpubProcessor | None:
    """
    Factory function che crea un processore EPUB.
    Restituisce None se il libro non è valido.
    """
    try:
        processor = EpubProcessor(filename)
        return processor if processor.is_valid else None
    except Exception as e:
        logger.error(f"Errore nella creazione del processore: {e}")
        return None


def manage_epub_processor(book_files: list[str | Path]) -> Generator[EpubProcessor, object, object]:
    """
    Generatore che processa file EPUB e yield solo quelli validi.

    Args:
        book_files: Lista di percorsi di file EPUB

    Yields:
        EpubProcessor: Processori validi
    """

    for index, file in enumerate(book_files, 1):
        file_path = Path(file)
        processor = EpubProcessor(file_path)
        processor.set_index(index)

        if processor.is_valid:
            yield processor
        else:
            logger.error(f"{file_path.name}: EPUB non valido o corrotto")



# ============================================
# Test
# ============================================
if __name__ == "__main__":
    # Test diagnostico
    filename='/home/loreto/Downloads/test_epubs/Billionaire 02 - Miele - Meghan March.epub'
    book1 = EpubProcessor(filename)

    print(f"Prima: {book1.title} - {book1.author}")

    # Modifica
    book1.set_title('Nuovo Titolo')
    book1.set_author('Nuovo Autore')

    print(f"Dopo: {book1.title} - {book1.author}")

    # Verifica
    print("get_metadata('DC', 'title'):", book1._book.get_metadata('DC', 'title'))
    print("get_metadata('DC', 'creator'):", book1._book.get_metadata('DC', 'creator'))

    # Salva
    filename='libro_test_modificato.epub'
    book1.save(filename)

    print("\n--- Verifica dopo salvataggio ---")
    book2 = EpubProcessor(filename)

    print(f"Prima: {book2.title} - {book2.author}")

    # Modifica
    book2.set_title('Nuovo Titolo')
    book2.set_author('Nuovo Autore')

    print(f"Dopo: {book2.title} - {book2.author}")

    # Verifica
    # print("get_metadata('DC', 'title'):", book._book.get_metadata('DC', 'title'))
    # print("get_metadata('DC', 'creator'):", book._book.get_metadata('DC', 'creator'))
