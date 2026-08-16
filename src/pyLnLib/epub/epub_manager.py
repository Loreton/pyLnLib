#|/usr/bin/env python3
# ln_ebook_manager.py
#
# ruff: noqa: BLE001  Do not catch blind exception: `Exception` (Ruff BLE001)
# ruff: noqa: I001  Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
#
#
#
from __future__ import annotations
from _collections_abc import Generator

from pathlib import Path
from dataclasses import dataclass

from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT


# from pyLnLib.files import get_unique_filename
from pyLnLib.logger import get_logger

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

    #
    def __init___WITH_CONTEXT(self, filename: str | Path):
        self._filename = Path(filename)
        self._sections: list[BookSection] | None = None
        self._book = None
        self.is_valid = True

        # Verifica che il file esista
        if not self._filename.is_file():
            raise FileNotFoundError(f"File non trovato: {self._filename}")

        # Tenta di caricare il libro
        try:
            self._book = epub.read_epub(str(self._filename))
            self.is_valid = True
            logger.debug(f"EPUB caricato con successo: {self._filename.stem}")

        except Exception as e:
            logger.error(f"{self._filename.stem}\nFailed to read EPUB: {e}")
            self._book = None
            self.is_valid = False

    def __bool___WITH_CONTEXT(self):
        """Permette di usare 'if processor:' per verificare la validità."""
        return self.is_valid and self._book is not None

    def __enter___WITH_CONTEXT(self):
        """Context manager per gestire automaticamente le risorse."""
        return self

    def __exit___WITH_CONTEXT(self, exc_type, exc_val, exc_tb):
        """Pulisce le risorse quando si esce dal context manager."""
        self.close()

    def close_WITH_CONTEXT(self):
        """Rilascia le risorse."""
        self._book = None
        self._sections = None



    def __init__(self, filename: str | Path):
        self._filename = Path(filename)
        self._sections: list[BookSection] | None = None
        self._book = None
        self.is_valid = True
        self._index = 0

        if not self._filename.is_file():
            raise FileNotFoundError(f"File non trovato: {self._filename}")

        try:
            self._book = epub.read_epub(str(self._filename))
            self.is_valid = True

        except Exception as e:
            logger.error(f"{self._filename.stem}\nFailed to read EPUB: {e}")
            self._book = None
            self.is_valid = False

    def __bool__(self):
        return self.is_valid and self._book is not None

    # - utilizzato da manage_epub_processor() per permettere di conoscere il numero di libri processati
    def set_index(self, index: int):
        self._index = index

    @property
    def index(self) -> int:
        return self._index

    def __init__XXX(self, filename: str | Path):

        self._filename = Path(filename)
        """  memorizzare le sezioni.
        Altrimenti, ogni chiamata a get_sections() riparsa tutto l'EPUB.
        Se poi chiami get_text() e export_text(), il parsing viene eseguito tre volte.
        """
        # self._sections = None
        self._sections: list[BookSection] | None = None

        if not self._filename.is_file():
            raise FileNotFoundError(self._filename)

        self.is_valid= True
        try:
            self._book = epub.read_epub(str(self._filename))
        except Exception as e:
            logger.error(f"{self._filename.stem}\nFailed to read EPUB: {e}", exit=True)
            self._book = None
            self.is_valid= False
            # raise

    # ======================================================================
    # Properties
    # ======================================================================

    @property
    def filename(self) -> Path:
        return self._filename

    # ======================================================================
    # Metadata
    # ======================================================================

    # def get_metadata(self) -> dict:
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
    #   replace: se il file esiste, sovrascrive
    #   unique: se il file esiste, crea uno con nome diverso
    # ======================================================================

    def export_text(self, filename: Path|str, unique: bool = False, replace: bool = False) -> Path:
        filename = Path(filename)
        if not filename.parent.exists():
            filename.parent.mkdir(parents=True, exist_ok=True)

        if filename.exists():
            if replace: # sovrascrive il file esistente
                filename.unlink()
            elif unique:
                filename = unique_filename(filename) # crea uno con nome diverso
            else:
                logger.debug("file already exists: %s", filename)
                return filename # non modifica il file esistente

        with filename.open("w", encoding="utf-8") as fp:

            fp.write("=" * 60 + "\n")
            fp.write("METADATI\n")
            fp.write("=" * 60 + "\n")

            fp.write(f"Titolo          : {self.get_title()}\n")
            fp.write(f"Autore          : {self.get_author()}\n")
            fp.write(f"Lingua          : {self.get_language()}\n")
            fp.write(f"Editore         : {self.get_publisher()}\n")
            fp.write(f"Data            : {self.get_date()}\n")
            fp.write(f"Identificativo  : {self.get_identifier()}\n")
            fp.write(f"File originale  : {self.filename.name}\n")

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

        logger.debug("saved filename: %s", filename)
        return filename

    # ======================================================================
    # Private
    # ======================================================================

    def _get_dc(self, key: str) -> str | None:

        values = self._book.get_metadata("DC", key)

        if not values:
            return None

        return values[0][0]



#============================================
# Mi permette di gestire book che hanno errori
#============================================
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
            # logger.info(f"{processor.title} - {processor.author}")
            yield processor
        else:
            logger.error(f"{file_path.name}: EPUB non valido o corrotto")
