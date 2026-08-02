#|/usr/bin/env python3
# ln_ebook_manager.py
#
# from curses import meta
from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass

from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT


from pyLnLib.files import unique_filename


# per memorizzare le section dell'ebook
@dataclass(slots=True)
class BookSection:
    file: str
    title: str | None
    text: str


class EpubProcessor:
    """Simple EPUB reader."""

    def __init__(self, filename: str | Path):

        self._filename = Path(filename)
        """  memorizzare le sezioni.
        Altrimenti, ogni chiamata a get_sections() riparsa tutto l'EPUB.
        Se poi chiami get_text() e export_text(), il parsing viene eseguito tre volte.
        """
        # self._sections = None
        self._sections: list[BookSection] | None = None

        if not self._filename.is_file():
            raise FileNotFoundError(self._filename)

        self._book = epub.read_epub(str(self._filename))

    # ======================================================================
    # Properties
    # ======================================================================

    @property
    def filename(self) -> Path:
        return self._filename

    # ======================================================================
    # Metadata
    # ======================================================================

    def get_metadata(self) -> dict:
        return self._book.metadata

    def get_title(self) -> str | None:
        return self._get_dc("title")

    def get_author(self) -> str | None:
        return self._get_dc("creator")

    def get_language(self) -> str | None:
        return self._get_dc("language")

    def get_publisher(self) -> str | None:
        return self._get_dc("publisher")

    def get_date(self) -> str | None:
        return self._get_dc("date")

    def get_identifier(self) -> str | None:
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


    # def get_sections_(self) -> list[dict]:
    #     """
    #     Return the ebook sections.

    #     Each element contains:

    #         {
    #             "file": "...",
    #             "title": "...",
    #             "text": "..."
    #         }
    #     """
    #     if self._sections is not None:
    #         return self._sections


    #     sections = []

    #     for item in self._book.get_items():

    #         if item.get_type() != ITEM_DOCUMENT:
    #             continue

    #         soup = BeautifulSoup(
    #             item.get_body_content(),
    #             "html.parser"
    #         )

    #         text = soup.get_text(separator=" ", strip=True)

    #         title = None

    #         if soup.title:
    #             title = soup.title.get_text(strip=True)

    #         if not title:
    #             h1 = soup.find("h1")
    #             if h1:
    #                 title = h1.get_text(strip=True)

    #         sections.append(
    #             {
    #                 "file": item.file_name,
    #                 "title": title,
    #                 "text": text,
    #             }
    #         )


    #     self._sections = sections
    #     return self._sections


    def get_text(self) -> str:
        return "\n\n".join(
            section.text
            for section in self.get_sections()
            if section.text
        )
        # return "\n\n".join(
        #     section["text"]
        #     for section in self.get_sections()
        #     if section["text"]
        # )

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

        return filename

    # ======================================================================
    # Private
    # ======================================================================

    def _get_dc(self, key: str) -> str | None:

        values = self._book.get_metadata("DC", key)

        if not values:
            return None

        return values[0][0]
