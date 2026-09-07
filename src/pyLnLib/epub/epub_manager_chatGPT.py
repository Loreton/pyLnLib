
from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from lxml import etree

from pyLnLib import lnDict
from pyLnLib.logger import get_logger
logger = get_logger()

NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "opf": "http://www.idpf.org/2007/opf",
    "xhtml": "http://www.w3.org/1999/xhtml",
    "xml": "http://www.w3.org/XML/1998/namespace",
}

EPUB_MIMETYPE = "application/epub+zip"


@dataclass(slots=True)
class BookSection:
    """Rappresenta una sezione/capitolo del libro."""

    file: str
    title: str | None
    text: str
    order: int

    def to_dict(self) -> dict[str, object]:
        """Converte la sezione in un dizionario."""
        return lnDict(asdict(self))


@dataclass(slots=True)
class EpubMetadata:
    """Metadati principali di un libro EPUB."""

    title: str | None = None
    creator: str | None = None
    language: str | None = None
    publisher: str | None = None
    date: str | None = None
    identifier: str | None = None
    description: str | None = None
    subject: list[str] = field(default_factory=list)
    rights: str | None = None

    # Metadati custom dell'EPUB.
    custom: dict[str, str] = field(default_factory=dict)

    # Metadati specifici di Calibre.
    # I valori possono essere stringhe, numeri, liste o dizionari.
    calibre: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> lnDict[str, object]:
        """Converte i metadati in un dizionario."""
        return lnDict(asdict(self))


class EpubManager:
    """
    Gestisce un file EPUB.

    Il file originale non viene mai modificato direttamente.

    Il contenuto dell'EPUB viene estratto in una directory temporanea,
    modificato in memoria/file system e infine ricompattato durante save().

    Sono supportati entrambi gli utilizzi:

        with EpubManager(path) as book:
            print(book.title)

    oppure:

        book = EpubManager(path, auto_load=True)
        try:
            print(book.title)
        finally:
            book.cleanup()
    """

    def __init__( self, filename: str | Path, auto_load: bool = False, ) -> None:
        self.logger = get_logger()

        self._source_path = Path(filename)
        self._temp_dir: Path | None = None
        self._opf_path: Path | None = None

        self._metadata = EpubMetadata()
        self._sections: list[BookSection] = []

        self._is_loaded = False
        self._is_cleaned = False

        if not self._source_path.is_file():
            raise FileNotFoundError(
                f"File non trovato: {self._source_path}"
            )

        if auto_load:
            self.load()

    # ==================================================================
    # Context manager / lifecycle
    # ==================================================================

    def __enter__(self) -> EpubManager:
        self.load()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        self.cleanup()

    def __del__(self) -> None:
        # __del__ viene considerato solo come ultima rete di sicurezza.
        try:
            self.cleanup()
        except Exception:
            pass

    @property
    def path(self) -> Path:
        """Percorso del file EPUB originale."""
        return self._source_path

    def cleanup(self) -> None:
        """Rimuove la directory temporanea utilizzata dall'EPUB."""
        if self._is_cleaned:
            return

        if self._temp_dir is not None and self._temp_dir.exists():
            shutil.rmtree(self._temp_dir, ignore_errors=True)

        self._temp_dir = None
        self._opf_path = None
        self._is_cleaned = True

        self.logger.debug("Cleanup completato")

    def is_loaded(self) -> bool:
        """Restituisce True se il libro è attualmente caricato."""
        return self._is_loaded and not self._is_cleaned

    def _ensure_loaded(self) -> None:
        """Verifica che il libro sia stato caricato."""
        if not self.is_loaded():
            raise RuntimeError(
                f"Libro non caricato: {self._source_path}"
            )

    # ==================================================================
    # Caricamento
    # ==================================================================

    def load(self) -> bool:
        """
        Carica e analizza l'EPUB.

        Returns:
            True se il caricamento ha avuto successo, False altrimenti.
        """
        if self.is_loaded():
            return True

        # Permette di ricaricare l'oggetto dopo cleanup().
        self._is_cleaned = False

        try:
            self._temp_dir = Path(
                tempfile.mkdtemp(prefix="epub_")
            )

            self._extract_epub(self._temp_dir)

            self._opf_path = self._find_opf(self._temp_dir)

            if self._opf_path is None:
                raise ValueError(
                    f"File OPF non trovato: {self._source_path}"
                )

            self._metadata = self._parse_metadata(self._opf_path)
            self._sections = self._parse_sections(
                self._temp_dir,
                self._opf_path,
            )

            self._is_loaded = True

            self.logger.info(
                "EPUB caricato: %s",
                self._source_path,
            )

            return True

        except Exception as exc:
            self.logger.error(
                "Errore nel caricamento dell'EPUB: %s",
                exc,
                show_stack=True,
            )

            self._is_loaded = False
            self.cleanup()

            return False

    def _extract_epub(self, destination: Path) -> None:
        """Estrae e verifica il contenuto dell'EPUB."""

        with zipfile.ZipFile(self._source_path, "r") as archive:
            if archive.testzip() is not None:
                raise ValueError(
                    f"Archivio EPUB corrotto: {self._source_path}"
                )

            mimetype = archive.read("mimetype").decode("ascii").strip()

            if mimetype != EPUB_MIMETYPE:
                raise ValueError(
                    f"mimetype EPUB non valido: {mimetype!r}"
                )

            archive.extractall(destination)

    # ==================================================================
    # OPF
    # ==================================================================

    def _find_opf(self, base_path: Path) -> Path | None:
        """
        Trova il file OPF dell'EPUB.

        Prima viene consultato META-INF/container.xml.
        Come fallback viene cercato un qualsiasi file *.opf.
        """

        container_path = base_path / "META-INF" / "container.xml"

        if container_path.is_file():
            try:
                tree = etree.parse(str(container_path))

                for element in tree.getroot().iter():
                    full_path = element.get("full-path")

                    if not full_path:
                        continue

                    opf_path = base_path / full_path

                    if opf_path.is_file():
                        return opf_path

            except etree.XMLSyntaxError as exc:
                self.logger.warning(
                    "Errore nel parsing di container.xml: %s",
                    exc,
                )

        opf_files = list(base_path.rglob("*.opf"))

        if opf_files:
            return opf_files[0]

        return None

    # ==================================================================
    # Metadata
    # ==================================================================

    def _parse_metadata(self, opf_path: Path) -> EpubMetadata:
        """Parsa tutti i metadati presenti nel file OPF."""

        tree = etree.parse(str(opf_path))
        root = tree.getroot()

        metadata_elem = root.find(
            ".//opf:metadata",
            namespaces=NAMESPACES,
        )

        metadata = EpubMetadata()

        if metadata_elem is None:
            self.logger.warning(
                "Elemento <metadata> non trovato in %s",
                opf_path,
            )
            return metadata

        self._parse_dc_metadata(metadata_elem, metadata)
        self._parse_custom_metadata(metadata_elem, metadata)

        metadata.calibre = self._parse_calibre_metadata(
            metadata_elem
        )

        return metadata

    def _parse_dc_metadata(
        self,
        metadata_elem: etree._Element,
        metadata: EpubMetadata,
    ) -> None:
        """Estrae i metadati Dublin Core."""

        dc_mapping = {
            "title": "title",
            "creator": "creator",
            "language": "language",
            "publisher": "publisher",
            "date": "date",
            "identifier": "identifier",
            "description": "description",
            "rights": "rights",
        }

        dc_ns = NAMESPACES["dc"]

        for tag, attribute in dc_mapping.items():
            element = metadata_elem.find(
                f".//{{{dc_ns}}}{tag}"
            )

            if element is not None and element.text:
                setattr(
                    metadata,
                    attribute,
                    element.text.strip(),
                )

        metadata.subject = [
            subject.text.strip()
            for subject in metadata_elem.findall(
                f".//{{{dc_ns}}}subject"
            )
            if subject.text
        ]

    def _parse_custom_metadata(
        self,
        metadata_elem: etree._Element,
        metadata: EpubMetadata,
    ) -> None:
        """Estrae i metadati custom dell'EPUB."""

        # Elementi con namespace custom/example.
        for element in metadata_elem:
            if "}" not in element.tag:
                continue

            namespace = element.tag.split("}", 1)[0].strip("{")

            if (
                "custom" not in namespace.lower()
                and "example" not in namespace.lower()
            ):
                continue

            if not element.text:
                continue

            tag_name = element.tag.rsplit("}", 1)[-1]

            metadata.custom[tag_name] = element.text.strip()

        # <meta property="custom:key">
        # <meta name="custom:key">
        for element in metadata_elem.findall(
            ".//opf:meta",
            namespaces=NAMESPACES,
        ):
            for attribute_name in ("property", "name"):
                value = element.get(attribute_name)

                if not value or not value.startswith("custom:"):
                    continue

                key = value.split(":", 1)[1]

                text = element.text
                if text:
                    metadata.custom[key] = text.strip()

                break

        if metadata.custom:
            self.logger.debug(
                "Custom metadata trovati: %s",
                metadata.custom,
            )

    def _parse_calibre_metadata(
        self,
        metadata_elem: etree._Element,
    ) -> dict[str, Any]:
        """Estrae i metadati specifici di Calibre."""

        calibre_fields = {
            "title_sort",
            "author_link_map",
            "user_categories",
            "user_metadata",
            "series",
            "series_index",
            "rating",
            "timestamp",
            "pubdate",
            "last_modified",
            "modified_by",
        }

        calibre_custom_columns = {
            "#comments",
            "#read_date_text",
            "#status",
            "#tipologia",
        }

        allowed_user_fields = (
            calibre_fields | calibre_custom_columns
        )

        result: dict[str, Any] = {}

        for meta in metadata_elem.findall(
            ".//opf:meta",
            namespaces=NAMESPACES,
        ):
            name = meta.get("name", "")
            prop = meta.get("property", "")

            # ----------------------------------------------------------
            # calibre:user_metadata:<field>
            # ----------------------------------------------------------
            if name.startswith("calibre:user_metadata:"):
                field_name = name.split(":", 2)[2]

                if field_name not in allowed_user_fields:
                    continue

                value = self._extract_meta_value(meta)

                if value is not None:
                    result[field_name] = value

                continue

            # ----------------------------------------------------------
            # calibre:<field>
            # ----------------------------------------------------------
            if name.startswith("calibre:"):
                field_name = name.split(":", 1)[1]

                if field_name not in calibre_fields:
                    continue

                value = self._extract_meta_value(meta)

                if value is not None:
                    result[field_name] = value

                continue

            # ----------------------------------------------------------
            # calibre:user_metadata JSON completo
            # ----------------------------------------------------------
            if (
                prop == "calibre:user_metadata"
                and meta.text
            ):
                self._parse_calibre_user_metadata(
                    meta.text,
                    result,
                )

        self.logger.debug(
            "Calibre metadata: %s",
            result,
        )

        return result

    @staticmethod
    def _extract_meta_value(
        meta_elem: etree._Element,
    ) -> Any | None:
        """
        Estrae il valore da un elemento <meta>.

        Calibre utilizza in alcuni casi JSON con la struttura:

            {"#value#": ...}
        """

        raw_value = meta_elem.text

        if raw_value is None:
            raw_value = meta_elem.get("content")

        if raw_value is None:
            return None

        raw_value = raw_value.strip()

        if not raw_value:
            return None

        try:
            value = json.loads(raw_value)

        except json.JSONDecodeError:
            return raw_value

        if isinstance(value, dict) and "#value#" in value:
            return value["#value#"]

        return value

    def _parse_calibre_user_metadata(
        self,
        raw_data: str,
        result: dict[str, Any],
    ) -> None:
        """Parsa il blocco JSON calibre:user_metadata."""

        try:
            data = json.loads(raw_data)

        except json.JSONDecodeError as exc:
            self.logger.warning(
                "JSON calibre:user_metadata non valido: %s",
                exc,
            )
            return

        if not isinstance(data, dict):
            self.logger.warning(
                "calibre:user_metadata non contiene un dizionario"
            )
            return

        for key, value in data.items():
            if not isinstance(value, dict):
                continue

            actual_value = value.get("#value#")

            if actual_value is None:
                continue

            name_value = value.get(
                "name",
                key.lstrip("#"),
            )

            clean_key = key.lstrip("#")

            result[f"user_{clean_key}"] = actual_value
            result[f"user_{clean_key}_name"] = name_value

    # ==================================================================
    # Sections
    # ==================================================================

    def _parse_sections(
        self,
        base_path: Path,
        opf_path: Path,
    ) -> list[BookSection]:
        """
        Estrae le sezioni XHTML seguendo l'ordine dello spine.
        """

        tree = etree.parse(str(opf_path))
        root = tree.getroot()

        manifest = root.find(
            ".//opf:manifest",
            namespaces=NAMESPACES,
        )

        spine = root.find(
            ".//opf:spine",
            namespaces=NAMESPACES,
        )

        if manifest is None or spine is None:
            return []

        manifest_items = {
            item.get("id"): item
            for item in manifest.findall(
                "opf:item",
                namespaces=NAMESPACES,
            )
            if item.get("id")
        }

        sections: list[BookSection] = []

        for order, itemref in enumerate(
            spine.findall(
                "opf:itemref",
                namespaces=NAMESPACES,
            )
        ):
            idref = itemref.get("idref")

            if not idref:
                continue

            item = manifest_items.get(idref)

            if item is None:
                self.logger.warning(
                    "idref dello spine non trovato nel manifest: %s",
                    idref,
                )
                continue

            media_type = item.get("media-type", "")

            if media_type not in {
                "application/xhtml+xml",
                "text/html",
            }:
                continue

            href = item.get("href")

            if not href:
                continue

            file_path = self._resolve_opf_href(
                opf_path,
                href,
            )

            if not file_path.is_file():
                self.logger.warning(
                    "File XHTML non trovato: %s",
                    file_path,
                )
                continue

            try:
                section = self._read_section(
                    file_path,
                    href,
                    order,
                )

            except (OSError, UnicodeError) as exc:
                self.logger.error(
                    "Errore nella lettura di %s: %s",
                    href,
                    exc,
                )
                continue

            sections.append(section)

        return sections

    @staticmethod
    def _resolve_opf_href(
        opf_path: Path,
        href: str,
    ) -> Path:
        """
        Risolve un href del manifest rispetto alla directory OPF.

        L'href presente nel manifest è relativo alla posizione
        del file OPF, non alla root dell'archivio EPUB.
        """

        # Gli EPUB normalmente utilizzano slash '/' anche su Linux.
        href_path = Path(href)

        return opf_path.parent / href_path

    def _read_section(
        self,
        file_path: Path,
        href: str,
        order: int,
    ) -> BookSection:
        """Legge ed estrae una singola sezione XHTML."""

        content = file_path.read_text(encoding="utf-8")

        soup = BeautifulSoup(
            content,
            "html.parser",
        )

        text = soup.get_text(
            separator=" ",
            strip=True,
        )

        title = self._extract_section_title(soup)

        return BookSection(
            file=href,
            title=title,
            text=text,
            order=order,
        )

    @staticmethod
    def _extract_section_title(
        soup: BeautifulSoup,
    ) -> str | None:
        """Estrae il titolo più probabile di una sezione."""

        if soup.title:
            title = soup.title.get_text(strip=True)

            if title:
                return title

        for tag in ("h1", "h2"):
            heading = soup.find(tag)

            if heading:
                title = heading.get_text(strip=True)

                if title:
                    return title

        return None

    # ==================================================================
    # Properties
    # ==================================================================

    @property
    def source_path(self) -> str:
        """Percorso del file EPUB originale."""

        return str(self._source_path)

    @property
    def title(self) -> str | None:
        """Titolo del libro."""

        return self._metadata.title

    @property
    def author(self) -> str | None:
        """Autore del libro."""

        return self._metadata.creator

    @property
    def metadata(self) -> EpubMetadata:
        """Restituisce tutti i metadati."""

        return self._metadata

    @property
    def sections(self) -> tuple[BookSection, ...]:
        """
        Restituisce le sezioni del libro.

        Viene restituita una tupla per evitare che il chiamante
        possa modificare direttamente lo stato interno.
        """

        return tuple(self._sections)

    # ==================================================================
    # Metadata modification
    # ==================================================================

    def set_title(self, new_title: str) -> None:
        """Modifica il titolo del libro."""

        self._ensure_loaded()

        self._metadata.title = new_title
        self._metadata.custom["modified_by"] = "EpubManager"

    def set_author(self, new_author: str) -> None:
        """Modifica l'autore del libro."""

        self._ensure_loaded()

        self._metadata.creator = new_author
        self._metadata.custom["modified_by"] = "EpubManager"

    def set_custom_metadata(
        self,
        key: str,
        value: str,
    ) -> None:
        """Imposta un metadata custom."""

        self._ensure_loaded()

        self._metadata.custom[key] = value

    def get_custom_key(
        self,
        key: str,
    ) -> str | None:
        """Restituisce un metadata custom."""

        self._ensure_loaded()

        return self._metadata.custom.get(key)

    def get_custom_metadata(self) -> lnDict[str, str]:
        """Restituisce tutti i metadata custom."""

        self._ensure_loaded()

        return lnDict(self._metadata.custom)

    # ==================================================================
    # OPF modification
    # ==================================================================

    def _update_opf_metadata(self) -> bool:
        """Aggiorna i metadati nel file OPF."""

        self._ensure_loaded()

        if self._opf_path is None:
            return False

        try:
            tree = etree.parse(str(self._opf_path))
            root = tree.getroot()

            metadata_elem = root.find(
                ".//opf:metadata",
                namespaces=NAMESPACES,
            )

            if metadata_elem is None:
                metadata_elem = etree.Element(
                    f"{{{NAMESPACES['opf']}}}metadata",
                )

                root.insert(0, metadata_elem)

            self._update_dc_metadata(metadata_elem)
            self._update_custom_metadata(metadata_elem)

            tree.write(
                str(self._opf_path),
                encoding="utf-8",
                xml_declaration=True,
                pretty_print=True,
            )

            return True

        except Exception as exc:
            self.logger.error(
                "Errore nell'aggiornamento dell'OPF: %s",
                exc,
                show_stack=True,
            )
            return False

    def _update_dc_metadata(
        self,
        metadata_elem: etree._Element,
    ) -> None:
        """Aggiorna i metadati Dublin Core."""

        dc_ns = NAMESPACES["dc"]

        fields = (
            "title",
            "creator",
            "language",
            "publisher",
            "date",
            "identifier",
            "description",
            "rights",
        )

        for field_name in fields:
            value = getattr(
                self._metadata,
                field_name,
            )

            element = metadata_elem.find(
                f".//{{{dc_ns}}}{field_name}"
            )

            if value is None or value == "":
                if element is not None:
                    metadata_elem.remove(element)

                continue

            if element is None:
                element = etree.Element(
                    f"{{{dc_ns}}}{field_name}"
                )
                metadata_elem.append(element)

            element.text = value

    def _update_custom_metadata(
        self,
        metadata_elem: etree._Element,
    ) -> None:
        """
        Aggiorna i metadata custom gestiti da EpubManager.

        Per evitare di distruggere metadata appartenenti ad altri
        strumenti, vengono modificati/rimossi solo i custom:* già
        presenti che corrispondono alle nostre chiavi.
        """

        existing_custom: dict[str, etree._Element] = {}

        for meta in metadata_elem.findall(
            ".//opf:meta",
            namespaces=NAMESPACES,
        ):
            prop = meta.get("property", "")

            if not prop.startswith("custom:"):
                continue

            key = prop.split(":", 1)[1]
            existing_custom[key] = meta

        for key, value in self._metadata.custom.items():
            old_element = existing_custom.get(key)

            if not value:
                if old_element is not None:
                    metadata_elem.remove(old_element)

                continue

            if old_element is None:
                old_element = etree.Element(
                    f"{{{NAMESPACES['opf']}}}meta"
                )
                old_element.set(
                    "property",
                    f"custom:{key}",
                )
                metadata_elem.append(old_element)

            old_element.text = value

    # ==================================================================
    # Save
    # ==================================================================

    def save(
        self,
        output_path: str | Path,
    ) -> bool:
        """
        Salva l'EPUB modificato in un nuovo file.

        Il file originale non viene modificato.
        """

        self._ensure_loaded()

        output_path = Path(output_path)

        try:
            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            if not self._update_opf_metadata():
                self.logger.error(
                    "Impossibile aggiornare l'OPF"
                )
                return False

            if self._temp_dir is None:
                raise RuntimeError(
                    "Directory temporanea non disponibile"
                )

            self._write_epub(
                output_path,
                self._temp_dir,
            )

            self.logger.info(
                "EPUB salvato: %s",
                output_path,
            )

            return True

        except Exception as exc:
            self.logger.error(
                "Errore nel salvataggio dell'EPUB: %s",
                exc,
                show_stack=True,
            )
            return False

    @staticmethod
    def _write_epub(
        output_path: Path,
        source_dir: Path,
    ) -> None:
        """
        Ricrea l'archivio EPUB.

        Il file mimetype deve essere:
        - presente;
        - il primo file dell'archivio;
        - non compresso.
        """

        mimetype_path = source_dir / "mimetype"

        if not mimetype_path.is_file():
            raise ValueError(
                "Il file EPUB non contiene mimetype"
            )

        with zipfile.ZipFile(
            output_path,
            "w",
        ) as archive:

            # ----------------------------------------------------------
            # mimetype DEVE essere il primo elemento e non compresso.
            # ----------------------------------------------------------
            archive.write(
                mimetype_path,
                "mimetype",
                compress_type=zipfile.ZIP_STORED,
            )

            for file_path in sorted(source_dir.rglob("*")):
                if not file_path.is_file():
                    continue

                relative_path = file_path.relative_to(source_dir)

                if relative_path.as_posix() == "mimetype":
                    continue

                archive.write(
                    file_path,
                    relative_path.as_posix(),
                    compress_type=zipfile.ZIP_DEFLATED,
                )

    # ==================================================================
    # Utility
    # ==================================================================

    def get_text(self) -> str:
        """Restituisce tutto il testo del libro."""

        self._ensure_loaded()

        return "\n\n".join(
            section.text
            for section in self._sections
            if section.text
        )

    def to_text(
        self,
        output_file: str | Path,
        replace: bool = False,
    ) -> bool:
        """Esporta il libro in formato testo."""

        self._ensure_loaded()

        output_file = Path(output_file)

        if output_file.exists() and not replace:
            return False

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            file.write("=" * 60 + "\n")
            file.write("METADATI\n")
            file.write("=" * 60 + "\n\n")

            file.write(
                f"Titolo: {self.metadata.title or 'N/A'}\n"
            )
            file.write(
                f"Autore: {self.metadata.creator or 'N/A'}\n"
            )
            file.write(
                f"Lingua: {self.metadata.language or 'N/A'}\n"
            )
            file.write(
                f"Editore: {self.metadata.publisher or 'N/A'}\n"
            )
            file.write(
                f"Data: {self.metadata.date or 'N/A'}\n"
            )
            file.write(
                f"Identificatore: "
                f"{self.metadata.identifier or 'N/A'}\n"
            )

            if self.metadata.custom:
                file.write("\n--- Metadati Custom ---\n")

                for key, value in self.metadata.custom.items():
                    file.write(f"{key}: {value}\n")

            file.write("\n" + "=" * 60 + "\n")
            file.write("CONTENUTO\n")
            file.write("=" * 60 + "\n\n")

            for section in self._sections:
                if section.title:
                    file.write(
                        f"\n--- {section.title} ---\n\n"
                    )

                file.write(section.text)
                file.write("\n\n")

        return True









# ============================================
# Esempio di utilizzo
# 1. Pulizia dei file temporanei
# Con with:
#   la pulizia è automatica (__exit__). Senza, devi chiamare cleanup() manualmente.
#
# 2. Caricamento automatico
#   Con with, load() viene chiamato automaticamente (__enter__). Senza, devi chiamarlo esplicitamente.
#
# 3. Stato inconsistente
#   Se dimentichi di chiamare load(), il libro non è caricato e le operazioni falliscono.
# ============================================
"""
test_epub_manager.py - Script di test per EpubManager
"""


def test_read_main_metadata(book: EpubManager):
        # 2. Leggi metadati originali
        logger.debug("METADATI ORIGINALI:")
        # logger.debug(f"\tTitolo:  {book.title}")
        # logger.debug(f"\tAutore:  {book.author}")
        # logger.debug(f"\tLingua:  {book.metadata.language if book.metadata else 'N/A'}")
        # logger.debug(f"\tEditore: {book.metadata.publisher if book.metadata else 'N/A'}")
        # logger.debug(f"\tData:    {book.metadata.date if book.metadata else 'N/A'}")
        logger.info(f"\tall metadata:    {book.metadata.to_dict() if book.metadata else 'N/A'}")

        # 3. Verifica sezioni
        logger.info(f"CAPITOLI: {len(book.sections)}")
        for i, section in enumerate(book.sections[:3], 1):  # Mostra solo primi 3
            title = section.title or f"Capitolo {i}"
            logger.info(f"\t{i}. {title} ({len(section.text)} caratteri)")
        if len(book.sections) > 3:
            logger.info(f"\t  ... e altri {len(book.sections) - 3} capitoli")



def test_modify_metadata(book: EpubManager):
    logger.info(f"  Custom metadata (before adding): {book.metadata.custom}")

    # 4. Modifica metadati
    logger.info("MODIFICA METADATI:")
    book.set_title("Test Titolo Modificato")
    book.set_author("Test Autore Modificato")

    logger.info(f"  Nuovo titolo: {book.title}")
    logger.info(f"  Nuovo autore: {book.author}")

    book.set_custom_metadata("test_key", "test_value")
    book.set_custom_metadata("processed_by", "EpubManager v2.0")
    # logger.info(f"  Custom metadata: {book.metadata.custom}")
    # logger.info(f"  processed_by: {book.metadata.custom.get('processed_by')}")
    # logger.info(f"  processed_by: {book.get_custom_key('processed_by')}")
    # logger.info(f"  custom metadata: {book.get_custom_metadata()}")
    logger.info(f"\tall metadata:    {book.metadata.to_dict() if book.metadata else 'N/A'}")
    # breakpoint()



def scan_directory(root_dir: Path|str, pattern: str, recursive: bool = True) -> list[Path]:
    """
    Scansiona una directory per trovare file EPUB

    Args:
        root_dir: Directory root da scansionare
        pattern: Pattern dei file da cercare
        recursive: Se cercare ricorsivamente

    Returns:
        list[Path]: Lista di percorsi dei file trovati
    """

    root_path = Path(root_dir)
    if not root_path.exists():
        logger.error(f"Directory non trovata: {root_path}")
        return []

    if recursive:
        file_list = list(root_path.glob(f'**/{pattern}'))
    else:
        file_list = list(root_path.glob(pattern))

    logger.info(f"Trovati {len(file_list)} file {pattern} in {root_path}")
    return file_list


if __name__ == "__main__":
    import sys
    # Path del tuo EPUB di test
    epub_path = "/home/loreto/filu/ln-eBooks/lnExtracted/epubs/Yap, Felicia/giorno solo, Un.epub"
    epub_path = "/home/loreto/filu/ln-eBooks/lnLibraries/new_Entries/Hoover, Colleen/It Ends With Us_ Siamo noi a dire basta (379)/It Ends With Us_ Siamo noi a dire basta - Hoover, Colleen.epub"
    epub_path = "/home/loreto/Downloads/aaa/Bosco, Annamaria & Guarino, Mariarosaria/Knockout.epub.zip" # con calibre metadata
    epub_path = "/home/loreto/Downloads/a2/Hoover, Colleen/Ugly Love.epub"
    epub_path = "/home/loreto/Downloads/aaa/Ardone, Viola/Tanta ancora vita.epub" # con calibre metadata
    epub_path = "/home/loreto/Downloads/aaa/Hoover, Colleen/Verity.epub" # con calibre metadata
    epub_path = "/home/loreto/Downloads/aaa/Hoover, Colleen/Verity.epub" # con calibre metadata

    epub_inp_path = Path("/home/loreto/Downloads/epubs_test")
    epub_out_path = Path("/home/loreto/Downloads/epubs_out")
    file_list = scan_directory(epub_inp_path, "*.epub")
    epub_out_path.mkdir(parents=True, exist_ok=True)



    for epub_path in file_list:
        book = EpubManager(epub_path)
        try:
            book.load()
            test_read_main_metadata(book=book)
            # calibre_data = book.parse_calibre_metadata()


            test_modify_metadata(book=book)

            # 5. Salva in nuovo file
            output_file = epub_out_path / book.path.name
            book.save(output_file)
            logger.notify(f"Salvataggio completato:\n{output_file}")

            # 6. Esporta come testo
            txt_file = epub_out_path / f"{book.path.stem}_estratto.txt"
            if book.to_text(txt_file, replace=True):
                logger.notify(f"Esportato come testo:\n{txt_file}")




        finally:
            book.cleanup()
