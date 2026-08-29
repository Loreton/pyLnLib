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
import zipfile
import tempfile
import shutil
import re
from _collections_abc import Generator
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

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
        self._modified = False  # Traccia se ci sono modifiche

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

    @property
    def is_modified(self) -> bool:
        """Indica se il libro è stato modificato."""
        return self._modified

    # ======================================================================
    # Metadata - Lettura
    # ======================================================================

    def _get_dc(self, key: str) -> str | None:
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
    # Metadata - Scrittura (SOLUZIONE DEFINITIVA - MODIFICA DIRETTA OPF)
    # ======================================================================

    def _find_opf_file(self, epub_path: Path) -> Path]:
        """Trova il file OPF (package document) all'interno dell'EPUB."""
        with zipfile.ZipFile(epub_path, 'r') as zip_ref:
            # Cerca il file container.xml
            try:
                with zip_ref.open('META-INF/container.xml') as f:
                    content = f.read().decode('utf-8')
                    # Cerca il full-path del OPF
                    match = re.search(r'full-path="([^"]+)"', content)
                    if match:
                        return Path(match.group(1))
            except KeyError:
                pass

            # Se non trovato, cerca il primo file .opf
            for name in zip_ref.namelist():
                if name.endswith('.opf'):
                    return Path(name)

        return None

    def _modify_opf_metadata(self, source_epub: Path, target_epub: Path, updates: dict[str, str]) -> bool:
        """
        Modifica i metadati direttamente nel file OPF e salva in un nuovo EPUB.
        """
        try:
            # Trova il file OPF
            opf_path = self._find_opf_file(source_epub)
            if not opf_path:
                logger.error("File OPF non trovato")
                return False

            # Estrai tutto in una directory temporanea
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_dir_path = Path(tmp_dir)

                # Estrai l'EPUB sorgente
                with zipfile.ZipFile(source_epub, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir_path)

                # Leggi il file OPF
                opf_full_path = tmp_dir_path / opf_path
                with open(opf_full_path, 'r', encoding='utf-8') as f:
                    opf_content = f.read()

                # Modifica il contenuto OPF per ogni metadata
                for key, value in updates.items():
                    # Cerca il tag metadata esistente
                    # Esempio: <dc:title>vecchio titolo</dc:title>
                    # Nota: può esserci anche con namespace diverso: <dc:title xmlns:dc="...">...
                    pattern = rf'<dc:{key}[^>]*>.*?</dc:{key}>'
                    replacement = f'<dc:{key}>{value}</dc:{key}>'

                    # Sostituisci il vecchio valore
                    opf_content, count = re.subn(pattern, replacement, opf_content, flags=re.DOTALL)

                    # Se non trovato, aggiungi il tag
                    if count == 0:
                        # Trova il tag <metadata> e aggiungi il nuovo tag
                        metadata_pattern = r'(<metadata[^>]*>)'
                        opf_content = re.sub(
                            metadata_pattern,
                            rf'\1\n    <dc:{key}>{value}</dc:{key}>',
                            opf_content,
                            count=1
                        )

                # Salva il file OPF modificato
                with open(opf_full_path, 'w', encoding='utf-8') as f:
                    f.write(opf_content)

                # Ricrea l'EPUB nella destinazione
                with zipfile.ZipFile(target_epub, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                    for file_path in tmp_dir_path.rglob('*'):
                        if file_path.is_file():
                            arcname = str(file_path.relative_to(tmp_dir_path))
                            zip_ref.write(file_path, arcname)

            return True

        except Exception as e:
            logger.error(f"Errore nella modifica dell'OPF: {e}")
            return False

    def set_dc_metadata(self, key: str, value: str) -> bool:
        """
        Modifica un metadata DC (Dublin Core).
        Usa la modifica diretta del file OPF su una copia.
        """
        if not self._is_valid:
            logger.error("EPUB non valido")
            return False

        try:
            # Crea un file temporaneo per la modifica
            with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp_file:
                temp_epub = Path(tmp_file.name)

            # Modifica la copia
            if not self._modify_opf_metadata(self._file_path, temp_epub, {key: value}):
                return False

            # Ricarica il libro dalla copia modificata
            self._book = epub.read_epub(str(temp_epub))

            # Salva il percorso del file temporaneo come nuovo file
            self._file_path = temp_epub
            self._modified = True

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

        try:
            # Crea un file temporaneo per la modifica
            with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp_file:
                temp_epub = Path(tmp_file.name)

            # Modifica la copia
            if not self._modify_opf_metadata(self._file_path, temp_epub, updates):
                return False

            # Ricarica il libro dalla copia modificata
            self._book = epub.read_epub(str(temp_epub))

            # Salva il percorso del file temporaneo come nuovo file
            self._file_path = temp_epub
            self._modified = True

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

    def save(self, output_path: str | Path = None) -> bool:
        """Salva le modifiche all'EPUB."""
        if not self._is_valid:
            logger.error("EPUB non valido, impossibile salvare")
            return False

        try:
            output = Path(output_path) if output_path else self._file_path

            # Se il libro è stato modificato e abbiamo un file temporaneo
            if self._modified and self._file_path.name.startswith('tmp'):
                # Copia il file temporaneo nella destinazione
                shutil.copy2(self._file_path, output)
                logger.info(f"EPUB salvato in: {output}")
                return True
            else:
                # Se non ci sono modifiche, copia l'originale
                if output != self._file_path:
                    shutil.copy2(self._file_path, output)
                    logger.info(f"EPUB salvato in: {output}")
                    return True
                else:
                    logger.info("Nessuna modifica da salvare")
                    return True

        except Exception as e:
            logger.error(f"Errore durante il salvataggio: {e}")
            return False

    def __del__(self):
        """Pulizia: rimuovi i file temporanei."""
        if hasattr(self, '_file_path') and self._file_path:
            if self._file_path.name.startswith('tmp') and self._file_path.exists():
                try:
                    self._file_path.unlink()
                except:
                    pass

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
    original_file = '/home/loreto/Downloads/test_epubs/Billionaire 02 - Miele - Meghan March.epub'

    print("=" * 60)
    print("TEST MODIFICA METADATA EPUB")
    print("=" * 60)

    # Crea una copia di lavoro per non modificare l'originale
    work_file = Path('libro_test_lavoro.epub')
    shutil.copy2(original_file, work_file)

    book = EpubProcessor(work_file)

    print(f"\nPrima:")
    print(f"  Titolo: {book.title}")
    print(f"  Autore: {book.author}")

    # Modifica
    print("\nModifico titolo e autore...")
    book.set_title('Nuovo Titolo Modificato')
    book.set_author('Nuovo Autore Modificato')

    print(f"\nDopo la modifica (in memoria):")
    print(f"  Titolo: {book.title}")
    print(f"  Autore: {book.author}")

    print("get_metadata('DC', 'title'):", book._book.get_metadata('DC', 'title'))
    print("get_metadata('DC', 'creator'):", book._book.get_metadata('DC', 'creator'))

    # Salva in un nuovo file
    output_file = 'libro_test_modificato.epub'
    book.save(output_file)

    # Riapri per verificare
    print("\n--- Verifica dopo salvataggio ---")
    book2 = EpubProcessor(output_file)
    print(f"  Titolo: {book2.title}")
    print(f"  Autore: {book2.author}")

    # Verifica che l'originale non sia stato modificato
    print("\n--- Verifica file originale ---")
    book_orig = EpubProcessor(original_file)
    print(f"  Titolo originale: {book_orig.title}")
    print(f"  Autore originale: {book_orig.author}")

    print("\n✅ Test completato!")
