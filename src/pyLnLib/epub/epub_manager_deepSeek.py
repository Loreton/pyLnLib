# /home/loreto/filu/Programming/gitREPO/pyLnLib/src/pyLnLib/epub/epub_manager.py
"""
epub_manager.py - Gestione EPUB con zipfile + lxml

Caratteristiche:
- Supporto context manager e uso diretto
- Parsing robusto di metadati (DC, OPF, Calibre)
- Estrazione e modifica di metadati
- Salvataggio con preservazione della struttura
- Gestione memoria efficiente

Esempi:
    # Con context manager
    with EpubManager('libro.epub') as book:
        book.set_title('Nuovo Titolo')
        book.set_author('Nuovo Autore')
        book.save('output.epub')

    # Senza context manager
    book = EpubManager('libro.epub', auto_load=True)
    try:
        print(f"Titolo: {book.title}")
        book.set_title('Nuovo Titolo')
        book.save('output.epub')
    finally:
        book.cleanup()
"""

from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from bs4 import BeautifulSoup
from lxml import etree

from pyLnLib import lnDict
from pyLnLib.logger import get_logger

logger = get_logger()

# ============================================================================
# Costanti
# ============================================================================

NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "opf": "http://www.idpf.org/2007/opf",
    "xhtml": "http://www.w3.org/1999/xhtml",
    "xml": "http://www.w3.org/XML/1998/namespace",
    "dcterms": "http://purl.org/dc/terms/",
    "calibre": "http://calibre.kovidgoyal.net/2009/metadata",
}

# Campi Calibre comuni
CALIBRE_FIELDS: Set[str] = {
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

CALIBRE_CUSTOM_FIELDS: Set[str] = {
    "#comments",
    "#read_date_text",
    "#status",
    "#tipologia",
}

CALIBRE_ALL_FIELDS = CALIBRE_FIELDS | CALIBRE_CUSTOM_FIELDS

# Tipi di documento
DOCUMENT_MEDIA_TYPES = {"application/xhtml+xml", "text/html", "application/xhtml"}

# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class BookSection:
    """Rappresenta una sezione/capitolo del libro."""

    file: str
    title: str | None
    text: str
    order: int

    def to_dict(self) -> dict[str, Any]:
        """Converte l'oggetto in un dizionario."""
        return lnDict({
            "file": self.file,
            "title": self.title,
            "text": self.text,
            "order": self.order,
        })


@dataclass
class EpubMetadata:
    """Rappresenta i metadati del libro."""

    title: str | None = None
    creator: str | None = None  # autore
    language: str | None = None
    publisher: str | None = None
    date: str | None = None
    identifier: str | None = None
    description: str | None = None
    subject: List[str] = field(default_factory=list)
    rights: str | None = None
    # Campi custom
    custom: Dict[str, str] = field(default_factory=dict)
    calibre: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converte l'oggetto in un dizionario."""
        return lnDict({
            "title": self.title,
            "creator": self.creator,
            "language": self.language,
            "publisher": self.publisher,
            "date": self.date,
            "identifier": self.identifier,
            "description": self.description,
            "subject": self.subject,
            "rights": self.rights,
            "custom": self.custom,
            "calibre": self.calibre,
        })

    def has_metadata(self) -> bool:
        """Verifica se ci sono metadati significativi."""
        return bool(
            self.title
            or self.creator
            or self.publisher
            or self.custom
            or self.calibre
        )


# ============================================================================
# Eccezioni Personalizzate
# ============================================================================

class EpubError(Exception):
    """Eccezione base per errori EPUB."""

    pass


class EpubLoadError(EpubError):
    """Errore durante il caricamento dell'EPUB."""

    pass


class EpubMetadataError(EpubError):
    """Errore durante il parsing dei metadati."""

    pass


class EpubNotLoadedError(EpubError):
    """Errore quando si tenta di operare su un EPUB non caricato."""

    pass


# ============================================================================
# Classe Principale
# ============================================================================

class EpubManager:
    """
    Gestore EPUB che usa zipfile + lxml per operazioni sui metadati.
    """

    # Limite dimensione file (100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024

    def __init__(self, filename: str | Path, auto_load: bool = False):
        """
        Inizializza il gestore EPUB.

        Args:
            filename: Percorso del file EPUB
            auto_load: Se True, carica automaticamente il libro

        Raises:
            FileNotFoundError: Se il file non esiste
            ValueError: Se il file non è valido
        """
        self._source_path = Path(filename)
        self._temp_dir: Optional[Path] = None
        self._opf_path: Optional[Path] = None
        self._metadata: Optional[EpubMetadata] = None
        self._sections: List[BookSection] = []
        self._is_loaded = False
        self._is_cleaned = False
        self._metadata_elem: Optional[etree._Element] = None
        self._opf_tree: Optional[etree._ElementTree] = None

        # Valida il file
        self._validate_file()

        # Caricamento automatico se richiesto
        if auto_load:
            self.load()

    # ========================================================================
    # Proprietà Pubbliche
    # ========================================================================

    @property
    def source_path(self) -> Path:
        """Percorso del file sorgente."""
        return self._source_path

    @property
    def title(self) -> str | None:
        """Titolo del libro."""
        return self._metadata.title if self._metadata else None

    @property
    def author(self) -> str | None:
        """Autore del libro."""
        return self._metadata.creator if self._metadata else None

    @property
    def metadata(self) -> Optional[EpubMetadata]:
        """Tutti i metadati."""
        return self._metadata

    @property
    def sections(self) -> List[BookSection]:
        """Sezioni del libro."""
        return self._sections

    @property
    def is_loaded(self) -> bool:
        """Verifica se il libro è caricato."""
        return self._is_loaded and not self._is_cleaned

    # ========================================================================
    # Context Manager
    # ========================================================================

    def __enter__(self) -> EpubManager:
        """Entra nel context manager."""
        self.load()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Esce dal context manager."""
        self.cleanup()

    def __del__(self) -> None:
        """Distruttore."""
        self.cleanup()

    # ========================================================================
    # Caricamento
    # ========================================================================

    def load(self) -> bool:
        """
        Carica l'EPUB in una directory temporanea.

        Returns:
            bool: True se caricato con successo, False altrimenti
        """
        if self._is_loaded:
            return True

        try:
            self._temp_dir = Path(tempfile.mkdtemp(prefix="epub_"))
            self._extract_epub()
            self._find_opf()
            self._load_metadata()
            self._load_sections()

            self._is_loaded = True
            logger.info(f"EPUB caricato: {self._source_path.name}")
            return True

        except (zipfile.BadZipFile, etree.ParseError, OSError) as e:
            logger.error(f"Errore caricamento {self._source_path.name}: {e}")
            self.cleanup()
            return False

        except Exception as e:
            logger.error(f"Errore inaspettato caricamento {self._source_path.name}: {e}")
            self.cleanup()
            return False

    def _validate_file(self) -> None:
        """Valida il file prima del caricamento."""
        if not self._source_path.exists():
            raise FileNotFoundError(f"File non trovato: {self._source_path}")

        if not self._source_path.is_file():
            raise ValueError(f"Non è un file: {self._source_path}")

        # Controllo dimensione
        if self._source_path.stat().st_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"File troppo grande ({self._source_path.stat().st_size} bytes): {self._source_path}"
            )

        # Controllo estensione
        if self._source_path.suffix.lower() != ".epub":
            raise ValueError(f"File non EPUB: {self._source_path}")

    def _extract_epub(self) -> None:
        """Estrae il file EPUB nella directory temporanea."""
        try:
            with zipfile.ZipFile(self._source_path, "r") as zip_ref:
                zip_ref.extractall(self._temp_dir)
        except zipfile.BadZipFile as e:
            raise EpubLoadError(f"File ZIP corrotto: {e}") from e

    def _find_opf(self) -> None:
        """Trova il file OPF nel container.xml o per estensione."""
        container = self._temp_dir / "META-INF" / "container.xml"

        if container.exists():
            try:
                tree = etree.parse(str(container))
                root = tree.getroot()
                # Cerca full-path
                for elem in root.iter():
                    if "full-path" in elem.attrib:
                        self._opf_path = self._temp_dir / elem.attrib["full-path"]
                        return
            except etree.ParseError as e:
                logger.warning(f"Errore parsing container.xml: {e}")

        # Cerca file .opf
        opf_files = list(self._temp_dir.rglob("*.opf"))
        if opf_files:
            self._opf_path = opf_files[0]
            logger.debug(f"OPF trovato per estensione: {self._opf_path}")
            return

        raise EpubLoadError("File OPF non trovato")

    def _load_metadata(self) -> None:
        """Carica i metadati dal file OPF."""
        if not self._opf_path:
            raise EpubLoadError("Nessun file OPF caricato")

        self._metadata = self._parse_metadata()
        self._metadata.calibre = self._parse_calibre_metadata()

        logger.debug(f"Metadati caricati: titolo={self._metadata.title}")

    def _load_sections(self) -> None:
        """Carica le sezioni del libro."""
        if not self._temp_dir or not self._opf_path:
            raise EpubLoadError("Directory temporanea o OPF non disponibili")

        self._sections = self._parse_sections()

    # ========================================================================
    # Parsing Metadati
    # ========================================================================

    def _parse_metadata(self) -> EpubMetadata:
        """Parsa i metadati dal file OPF."""
        if not self._opf_path:
            raise EpubMetadataError("Nessun file OPF disponibile")

        try:
            self._opf_tree = etree.parse(str(self._opf_path))
            root = self._opf_tree.getroot()

            metadata_elem = root.find(".//opf:metadata", namespaces=NAMESPACES)
            if metadata_elem is None:
                logger.warning("Nessun elemento metadata trovato")
                return EpubMetadata()

            self._metadata_elem = metadata_elem

            # Parsa i metadati
            metadata = EpubMetadata()

            # 1. Metadati Dublin Core
            self._parse_dc_metadata(metadata, metadata_elem)

            # 2. Metadati Custom
            self._parse_custom_metadata(metadata, metadata_elem)

            # 3. Metadati OPF
            self._parse_opf_metadata(metadata, metadata_elem)

            return metadata

        except etree.ParseError as e:
            raise EpubMetadataError(f"Errore parsing OPF: {e}") from e

    def _parse_dc_metadata(self, metadata: EpubMetadata, metadata_elem: etree._Element) -> None:
        """Estrae metadati Dublin Core."""
        dc_ns = NAMESPACES["dc"]

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

        for tag, attr in dc_mapping.items():
            elem = metadata_elem.find(f".//{{{dc_ns}}}{tag}")
            if elem is not None and elem.text:
                setattr(metadata, attr, elem.text.strip())

        # Subject (multi)
        subjects = metadata_elem.findall(f".//{{{dc_ns}}}subject")
        if subjects:
            metadata.subject = [s.text.strip() for s in subjects if s.text]

    def _parse_custom_metadata(self, metadata: EpubMetadata, metadata_elem: etree._Element) -> None:
        """Estrae metadati custom."""
        # Cerca tag con namespace custom
        for elem in metadata_elem:
            if "}" in elem.tag:
                namespace = elem.tag.split("}")[0].strip("{")
                if "custom" in namespace.lower() or "example" in namespace.lower():
                    tag_name = elem.tag.split("}")[-1]
                    if elem.text:
                        metadata.custom[tag_name] = elem.text.strip()

        # Cerca tag <meta> con property o name custom
        for elem in metadata_elem.findall(".//opf:meta", namespaces=NAMESPACES):
            prop = elem.get("property", "")
            name = elem.get("name", "")

            for attr_value in [prop, name]:
                if attr_value and attr_value.startswith("custom:"):
                    key = attr_value.split(":", 1)[1] if ":" in attr_value else attr_value
                    if elem.text:
                        metadata.custom[key] = elem.text.strip()
                    break

        if metadata.custom:
            logger.debug(f"Custom metadata trovati: {len(metadata.custom)}")

    def _parse_opf_metadata(self, metadata: EpubMetadata, metadata_elem: etree._Element) -> None:
        """Estrae metadati OPF aggiuntivi."""
        # Cerca altri metadati OPF
        for elem in metadata_elem.findall(".//opf:meta", namespaces=NAMESPACES):
            name = elem.get("name", "")
            content = elem.get("content", "")
            prop = elem.get("property", "")

            # Salta campi Calibre (gestiti separatamente)
            if name and not name.startswith("calibre:"):
                if content:
                    metadata.custom[f"opf_{name}"] = content
                elif elem.text:
                    metadata.custom[f"opf_{name}"] = elem.text.strip()

            # Cerca property
            if prop and not prop.startswith("calibre:"):
                if content:
                    metadata.custom[f"opf_{prop}"] = content
                elif elem.text:
                    metadata.custom[f"opf_{prop}"] = elem.text.strip()

    # ========================================================================
    # Parsing Calibre Metadata
    # ========================================================================

    def _parse_calibre_metadata(self) -> Dict[str, Any]:
        """Estrae i metadati Calibre specifici."""
        if self._metadata_elem is None:
            return {}

        calibre_data: Dict[str, Any] = {}

        for meta in self._metadata_elem.findall(".//opf:meta", namespaces=NAMESPACES):
            name = meta.get("name", "")
            prop = meta.get("property", "")

            # Caso 1: calibre:user_metadata:field
            if name and name.startswith("calibre:user_metadata:"):
                field = name.split(":", 2)[2] if ":" in name else name
                if field in CALIBRE_ALL_FIELDS:
                    value = self._extract_meta_value(meta)
                    if value is not None:
                        calibre_data[field] = value

            # Caso 2: calibre:field
            elif name and name.startswith("calibre:"):
                field = name.split(":", 1)[1] if ":" in name else name
                if field in CALIBRE_ALL_FIELDS:
                    if meta.text:
                        calibre_data[field] = meta.text.strip()
                    elif meta.attrib.get("content"):
                        calibre_data[field] = meta.attrib.get("content").strip()

            # Caso 3: calibre:user_metadata (JSON completo)
            elif prop == "calibre:user_metadata" and meta.text:
                try:
                    data = json.loads(meta.text)
                    for key, value in data.items():
                        if isinstance(value, dict):
                            actual_value = value.get("#value#")
                            name_value = value.get("name", key.lstrip("#"))
                            if actual_value is not None:
                                clean_key = key.lstrip("#")
                                calibre_data[f"user_{clean_key}"] = actual_value
                                calibre_data[f"user_{clean_key}_name"] = name_value
                except json.JSONDecodeError as e:
                    logger.debug(f"Errore parsing JSON Calibre: {e}")

        if calibre_data:
            logger.debug(f"Calibre metadata trovati: {len(calibre_data)}")

        return calibre_data

    @staticmethod
    def _extract_meta_value(meta: etree._Element) -> Any:
        """Estrae il valore da un elemento <meta>."""
        if meta.text:
            try:
                value = json.loads(meta.text)
                if isinstance(value, dict) and "#value#" in value:
                    return value["#value#"]
                return meta.text
            except json.JSONDecodeError:
                return meta.text

        content = meta.attrib.get("content")
        if content:
            try:
                value = json.loads(content)
                if isinstance(value, dict) and "#value#" in value:
                    return value["#value#"]
                return content
            except json.JSONDecodeError:
                return content

        return None

    # ========================================================================
    # Parsing Sezioni
    # ========================================================================

    def _parse_sections(self) -> List[BookSection]:
        """Parsa le sezioni del libro."""
        if not self._opf_path:
            return []

        sections: List[BookSection] = []

        try:
            tree = etree.parse(str(self._opf_path))
            root = tree.getroot()

            manifest = root.find(".//opf:manifest", namespaces=NAMESPACES)
            if manifest is None:
                return sections

            # Raccogli i documenti HTML
            html_items = self._collect_html_items(manifest)

            # Ordina per posizione nello spine
            html_items = self._order_by_spine(html_items, root)

            # Leggi il contenuto
            for html_item in html_items:
                section = self._read_section(html_item)
                if section:
                    sections.append(section)

        except (etree.ParseError, OSError) as e:
            logger.error(f"Errore parsing sezioni: {e}")

        return sections

    def _collect_html_items(self, manifest: etree._Element) -> List[Dict[str, Any]]:
        """Raccoglie gli item HTML dal manifest."""
        html_items = []

        for item in manifest.findall("opf:item", namespaces=NAMESPACES):
            media_type = item.get("media-type", "")
            if media_type in DOCUMENT_MEDIA_TYPES:
                href = item.get("href")
                if href and not href.endswith(".ncx"):
                    html_items.append({
                        "id": item.get("id"),
                        "href": href,
                        "media_type": media_type,
                        "order": 999,  # Default
                    })

        return html_items

    def _order_by_spine(self, html_items: List[Dict], root: etree._Element) -> List[Dict]:
        """Ordina gli item secondo lo spine."""
        spine = root.find(".//opf:spine", namespaces=NAMESPACES)
        if spine is not None:
            order = 0
            for itemref in spine.findall("opf:itemref", namespaces=NAMESPACES):
                idref = itemref.get("idref")
                for item in html_items:
                    if item["id"] == idref:
                        item["order"] = order
                        order += 1
                        break

        return sorted(html_items, key=lambda x: x.get("order", 999))

    def _read_section(self, html_item: Dict[str, Any]) -> Optional[BookSection]:
        """Legge una sezione dal file HTML."""
        if not self._temp_dir:
            return None

        file_path = self._temp_dir / html_item["href"]
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            soup = BeautifulSoup(content, "html.parser")

            # Estrai testo
            text = soup.get_text(separator=" ", strip=True)

            # Cerca titolo
            title = self._find_section_title(soup)

            return BookSection(
                file=html_item["href"],
                title=title,
                text=text,
                order=html_item.get("order", 999),
            )

        except (OSError, UnicodeDecodeError) as e:
            logger.error(f"Errore lettura file {html_item['href']}: {e}")
            return None

    @staticmethod
    def _find_section_title(soup: BeautifulSoup) -> Optional[str]:
        """Trova il titolo di una sezione."""
        # Cerca nel titolo della pagina
        if soup.title:
            title = soup.title.get_text(strip=True)
            if title:
                return title

        # Cerca heading
        for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            heading = soup.find(tag)
            if heading:
                return heading.get_text(strip=True)

        return None

    # ========================================================================
    # Modifica Metadati
    # ========================================================================

    def _ensure_loaded(self) -> None:
        """Assicura che il libro sia caricato."""
        if not self.is_loaded:
            raise EpubNotLoadedError(f"Libro non caricato: {self._source_path}")

    def set_title(self, new_title: str) -> bool:
        """
        Modifica il titolo.

        Args:
            new_title: Nuovo titolo

        Returns:
            bool: True se modificato con successo
        """
        self._ensure_loaded()
        if self._metadata:
            self._metadata.title = new_title
            self._metadata.custom["modified_by"] = "EpubManager"
            return True
        return False

    def set_author(self, new_author: str) -> bool:
        """
        Modifica l'autore.

        Args:
            new_author: Nuovo autore

        Returns:
            bool: True se modificato con successo
        """
        self._ensure_loaded()
        if self._metadata:
            self._metadata.creator = new_author
            self._metadata.custom["modified_by"] = "EpubManager"
            return True
        return False

    def set_metadata(self, key: str, value: Any) -> bool:
        """
        Imposta un metadata (campo DC o custom).

        Args:
            key: Chiave del metadata (title, creator, custom:key, etc.)
            value: Valore

        Returns:
            bool: True se impostato con successo
        """
        self._ensure_loaded()

        if not self._metadata:
            return False

        # Mappatura chiavi DC
        dc_mapping = {
            "title": "title",
            "author": "creator",
            "creator": "creator",
            "language": "language",
            "publisher": "publisher",
            "date": "date",
            "description": "description",
            "rights": "rights",
            "identifier": "identifier",
        }

        # Verifica se è un campo DC
        if key in dc_mapping:
            attr = dc_mapping[key]
            setattr(self._metadata, attr, str(value) if value else None)
            self._metadata.custom["modified_by"] = "EpubManager"
            return True

        # Verifica se è un campo custom
        if key.startswith("custom:"):
            custom_key = key.split(":", 1)[1]
            self._metadata.custom[custom_key] = str(value)
            return True

        # Tentativo come custom
        self._metadata.custom[key] = str(value)
        return True

    def get_metadata(self, key: str) -> Optional[Any]:
        """
        Recupera un metadata.

        Args:
            key: Chiave del metadata

        Returns:
            Valore o None se non trovato
        """
        self._ensure_loaded()

        if not self._metadata:
            return None

        # Mappatura chiavi DC
        dc_mapping = {
            "title": "title",
            "author": "creator",
            "creator": "creator",
            "language": "language",
            "publisher": "publisher",
            "date": "date",
            "description": "description",
            "rights": "rights",
            "identifier": "identifier",
        }

        if key in dc_mapping:
            attr = dc_mapping[key]
            return getattr(self._metadata, attr, None)

        if key.startswith("custom:"):
            custom_key = key.split(":", 1)[1]
            return self._metadata.custom.get(custom_key)

        return self._metadata.custom.get(key)

    def get_custom_metadata(self) -> Dict[str, str]:
        """
        Recupera tutti i metadati custom.

        Returns:
            Dict: Dizionario dei metadati custom
        """
        self._ensure_loaded()
        return self._metadata.custom if self._metadata else {}

    # ========================================================================
    # Aggiornamento OPF
    # ========================================================================

    def _update_opf_metadata(self) -> bool:
        """Aggiorna il file OPF con i metadati modificati."""
        if not self._opf_path or not self._metadata or self._opf_tree is None:
            return False

        try:
            root = self._opf_tree.getroot()

            # Trova o crea metadata
            metadata_elem = root.find(".//opf:metadata", namespaces=NAMESPACES)
            if metadata_elem is None:
                metadata_elem = etree.Element(
                    "{http://www.idpf.org/2007/opf}metadata",
                    nsmap={
                        "dc": "http://purl.org/dc/elements/1.1/",
                        "opf": "http://www.idpf.org/2007/opf",
                    },
                )
                root.insert(0, metadata_elem)

            # Aggiorna DC metadata
            self._update_dc_metadata(metadata_elem)

            # Aggiorna custom metadata
            self._update_custom_metadata(metadata_elem)

            # Salva
            self._opf_tree.write(
                str(self._opf_path),
                encoding="utf-8",
                xml_declaration=True,
                pretty_print=True,
            )

            return True

        except (OSError, etree.ParseError) as e:
            logger.error(f"Errore nell'aggiornamento del OPF: {e}")
            return False

    def _update_dc_metadata(self, metadata_elem: etree._Element) -> None:
        """Aggiorna i metadati Dublin Core."""
        dc_ns = NAMESPACES["dc"]

        dc_fields = {
            "title": self._metadata.title,
            "creator": self._metadata.creator,
            "language": self._metadata.language,
            "publisher": self._metadata.publisher,
            "date": self._metadata.date,
            "identifier": self._metadata.identifier,
            "description": self._metadata.description,
            "rights": self._metadata.rights,
        }

        for field_name, value in dc_fields.items():
            old_elem = metadata_elem.find(f".//{{{dc_ns}}}{field_name}")

            if value:
                if old_elem is None:
                    new_elem = etree.Element(f"{{{dc_ns}}}{field_name}")
                    new_elem.text = str(value)
                    metadata_elem.append(new_elem)
                else:
                    old_elem.text = str(value)
            elif old_elem is not None:
                metadata_elem.remove(old_elem)

        # Aggiorna subject
        old_subjects = metadata_elem.findall(f".//{{{dc_ns}}}subject")
        for elem in old_subjects:
            metadata_elem.remove(elem)

        if self._metadata.subject:
            for subject in self._metadata.subject:
                new_elem = etree.Element(f"{{{dc_ns}}}subject")
                new_elem.text = subject
                metadata_elem.append(new_elem)

    def _update_custom_metadata(self, metadata_elem: etree._Element) -> None:
        """Aggiorna i metadati custom."""
        # Rimuovi vecchi custom metadata
        for meta in metadata_elem.findall(".//opf:meta", namespaces=NAMESPACES):
            prop = meta.get("property", "")
            if prop and prop.startswith("custom:"):
                metadata_elem.remove(meta)

        # Aggiungi nuovi custom metadata
        for key, value in self._metadata.custom.items():
            if value and not key.startswith("opf_"):
                meta = etree.Element(
                    "{http://www.idpf.org/2007/opf}meta",
                    nsmap={"opf": "http://www.idpf.org/2007/opf"},
                )
                meta.set("property", f"custom:{key}")
                meta.text = str(value)
                metadata_elem.append(meta)

        # Aggiorna metadati Calibre se presenti
        for key, value in self._metadata.calibre.items():
            if value and not key.startswith("user_"):
                meta = etree.Element(
                    "{http://www.idpf.org/2007/opf}meta",
                    nsmap={"opf": "http://www.idpf.org/2007/opf"},
                )
                meta.set("name", f"calibre:{key}")
                if isinstance(value, (dict, list)):
                    meta.text = json.dumps(value)
                else:
                    meta.text = str(value)
                metadata_elem.append(meta)

    # ========================================================================
    # Salvataggio
    # ========================================================================

    def save(self, output_path: str | Path) -> bool:
        """
        Salva il libro modificato in un nuovo file.

        Args:
            output_path: Percorso di output

        Returns:
            bool: True se salvato con successo
        """
        self._ensure_loaded()
        output_path = Path(output_path)

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Aggiorna il file OPF con i metadati
            if not self._update_opf_metadata():
                return False

            # Crea il nuovo EPUB
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zip_ref:
                for file_path in self._temp_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to(self._temp_dir))
                        zip_ref.write(file_path, arcname)

            logger.info(f"EPUB salvato: {output_path.name}")
            return True

        except (OSError, zipfile.ZipFile) as e:
            logger.error(f"Errore nel salvataggio: {e}")
            return False

    # ========================================================================
    # Cleanup
    # ========================================================================

    def cleanup(self) -> None:
        """Rimuove i file temporanei."""
        if self._is_cleaned:
            return

        if self._temp_dir and self._temp_dir.exists():
            try:
                shutil.rmtree(self._temp_dir)
                logger.debug(f"Directory temporanea rimossa: {self._temp_dir}")
            except OSError as e:
                logger.error(f"Errore rimozione directory temporanea: {e}")

        self._is_cleaned = True
        self._is_loaded = False

    # ========================================================================
    # Utility
    # ========================================================================

    def get_text(self) -> str:
        """
        Restituisce tutto il testo del libro.

        Returns:
            str: Testo completo
        """
        return "\n\n".join(section.text for section in self.sections if section.text)

    def to_text(self, output_file: str | Path, replace: bool = False) -> bool:
        """
        Esporta il libro come file di testo.

        Args:
            output_file: Percorso del file di output
            replace: Se True, sovrascrive il file esistente

        Returns:
            bool: True se esportato con successo
        """
        output_file = Path(output_file)

        if output_file.exists() and not replace:
            logger.warning(f"File esiste già: {output_file}")
            return False

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                # Intestazione
                f.write("=" * 60 + "\n")
                f.write("METADATI\n")
                f.write("=" * 60 + "\n\n")

                if self.metadata:
                    f.write(f"Titolo: {self.metadata.title or 'N/A'}\n")
                    f.write(f"Autore: {self.metadata.creator or 'N/A'}\n")
                    f.write(f"Lingua: {self.metadata.language or 'N/A'}\n")
                    f.write(f"Editore: {self.metadata.publisher or 'N/A'}\n")
                    f.write(f"Data: {self.metadata.date or 'N/A'}\n")
                    f.write(f"Identificatore: {self.metadata.identifier or 'N/A'}\n")

                    if self.metadata.custom:
                        f.write("\n--- Metadati Custom ---\n")
                        for key, value in self.metadata.custom.items():
                            f.write(f"{key}: {value}\n")

                # Contenuto
                f.write("\n" + "=" * 60 + "\n")
                f.write("CONTENUTO\n")
                f.write("=" * 60 + "\n\n")

                for section in self.sections:
                    if section.title:
                        f.write(f"\n--- {section.title} ---\n\n")
                    f.write(section.text)
                    f.write("\n\n")

            logger.info(f"Testo esportato: {output_file.name}")
            return True

        except OSError as e:
            logger.error(f"Errore esportazione testo: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Ottiene statistiche sul libro.

        Returns:
            Dict: Statistiche (parole, caratteri, sezioni, ecc.)
        """
        text = self.get_text()
        words = [w for w in




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
            calibre_data = book.parse_calibre_metadata()


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
