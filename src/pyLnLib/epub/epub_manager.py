"""
EPUB Manager - Modulo per la manipolazione, estrazione e modifica di metadati e contenuti EPUB.
Requisiti: Python 3.10+ (Ottimizzato per Python 3.14+)
"""

import json
# import logging
import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, field, asdict
from pathlib import Path
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
# import json
# import re
# import xml.etree.ElementTree as ET


from pyLnLib import lnDict
from pyLnLib.logger import get_logger
logger = get_logger()

@dataclass
class BookSection:
    id: str
    href: str
    title: str
    content: str  # HTML / XHTML sorgente
    order: int

    def section_to_text(self) -> str:
        """Estrae solo il testo visibile rimuovendo i tag HTML/XHTML."""
        if not self.content:
            return ""
        try:
            # Tenta di parsare l'HTML/XHTML come XML pulito
            root = ET.fromstring(self.content)
            return "".join(root.itertext()).strip()
        except ET.ParseError:
            # Fallback tramite Regex se l'XHTML non è ben formato
            text = re.sub(r"<style.*?>.*?</style>", "", self.content, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<script.*?>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", "", text)
            return re.sub(r"\s+", " ", text).strip()


    def to_dict(self) -> lnDict[str, object]:
        """Converte l'oggetto in un dizionario."""
        return lnDict(asdict(self))




@dataclass
class EpubMetadata:
    """Rappresenta i metadati completi del libro (Dublin Core + Calibre + Custom)."""

    # Dublin Core standard
    title: str = ""
    authors: list[str] = field(default_factory=list)
    language: str = ""
    publisher: str = ""
    pub_date: str = ""
    identifier: str = ""
    isbn: str = ""
    description: str = ""
    subject: list[str] = field(default_factory=list)
    rights: str = ""

    # Serie (scorciatoie di livello base)
    series: str = ""
    series_index: float = 0.0

    # Metadati specifici Calibre (campi noti + colonne custom #)
    calibre: dict[str, object] = field(default_factory=dict)

    # Campi custom generici (non-Calibre)
    custom: dict[str, object] = field(default_factory=dict)

    CALIBRE_KNOWN_FIELDS = {
        "title_sort",
        "author_link_map",
        "user_categories",
        "user_metadata",
        "rating",
        "timestamp",
        "pubdate",
        "last_modified",
        "modified_by",
    }

    def set_calibre_entry(self, key: str, value: object) -> None:
        """Smista il metadato nella chiave corretta."""
        # if not key or value is None:
        #     return
        if not key:
            return

        # Pulizia prefisso calibre: se presente
        clean_key = key.replace("calibre:", "")

        # Gestione Serie
        if clean_key == "series":
            self.series = str(value)
            return
        if clean_key == "series_index":
            try:
                self.series_index = float(value)
            except (ValueError, TypeError):
                self.series_index = 0.0
            return

        # Smistamento in calibre dict o custom dict
        if clean_key in self.CALIBRE_KNOWN_FIELDS or clean_key.startswith("#"):
            if clean_key.startswith("#"):
                clean_key = clean_key.removeprefix("#") # per poter gestire il campo con lnDict
            self.calibre[clean_key] = value
        else:
            self.custom[clean_key] = value

    def to_dict(self) -> lnDict[str, object]:
        """Converte l'oggetto in un lnDict."""
        return lnDict(asdict(self))




class EpubManager:
    """Gestore completo per la lettura, modifica e salvataggio di file EPUB."""

    NS = {
        "container": "urn:oasis:names:tc:opendocument:xmlns:container",
        "opf": "http://www.idpf.org/2007/opf",
        "dc": "http://purl.org/dc/elements/1.1/",
        "calibre": "http://calibre.kovidgoyal.net/2009/metadata",
    }




    def __init__(self, epub_path: str | Path, auto_load: bool = True):
        self.epub_path = Path(epub_path)
        self.logger = logger
        self._temp_dir: str | None = None
        self.metadata: EpubMetadata = EpubMetadata()
        self.sections: list[BookSection] = []
        self._opf_relative_path: Path | None = None


        if auto_load:
            self.load()

    def __enter__(self):
        if not self._temp_dir:
            self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def cleanup(self) -> None:
        """Pulisce la directory temporanea allocata."""
        self.close()
        self.logger.info("Cleanup completato")

    def close(self) -> None:
        """Pulisce la directory temporanea allocata."""
        if self._temp_dir and Path(self._temp_dir).exists():
            try:
                shutil.rmtree(self._temp_dir)
                self.logger.debug(f"Directory temporanea rimossa: {self._temp_dir}")
            except Exception as e:
                self.logger.warning(f"Errore durante la pulizia della directory temporanea: {e}")
            finally:
                self._temp_dir = None

    def load(self) -> bool:
        """Carica ed estrae l'EPUB nella cartella temporanea."""
        if not self.epub_path.exists():
            raise FileNotFoundError(f"File EPUB non trovato: {self.epub_path}")

        self.close()
        self._temp_dir = tempfile.mkdtemp(prefix="epub_")
        self.logger.debug(f"Estratto EPUB in: {self._temp_dir}")

        try:
            with zipfile.ZipFile(self.epub_path, "r") as zip_ref:
                zip_ref.extractall(self._temp_dir)

            opf_path = self._find_opf_file()
            if not opf_path:
                raise ValueError("File OPF non trovato all'interno dell'EPUB.")

            self._parse_metadata(opf_path)
            self._parse_sections(opf_path)
            return True

        except Exception as e:
            self.logger.error(f"Errore durante il caricamento dell'EPUB: {e}")
            self.close()
            raise

    # -------------------------------------------------------------------------
    # Getters & Setters Metadati Standard
    # -------------------------------------------------------------------------
    @property
    def title(self) -> str:
        return self.metadata.title

    def set_title(self, title: str) -> None:
        self.metadata.title = title

    @property
    def authors(self) -> list[str]:
        return self.metadata.authors

    def set_authors(self, authors: list[str] | str) -> None:
        if isinstance(authors, str):
            self.metadata.authors = [a.strip() for a in authors.split(",")]
        else:
            self.metadata.authors = authors

    @property
    def language(self) -> str:
        return self.metadata.language

    def set_language(self, language: str) -> None:
        self.metadata.language = language

    @property
    def publisher(self) -> str:
        return self.metadata.publisher

    def set_publisher(self, publisher: str) -> None:
        self.metadata.publisher = publisher

    @property
    def description(self) -> str:
        return self.metadata.description

    def set_description(self, description: str) -> None:
        self.metadata.description = description

    @property
    def isbn(self) -> str:
        return self.metadata.isbn

    def set_isbn(self, isbn: str) -> None:
        self.metadata.isbn = re.sub(r"[^\dX]", "", isbn.upper())

    # -------------------------------------------------------------------------
    # Getters & Setters Custom / Calibre Metadata
    # -------------------------------------------------------------------------

    def get_series(self) -> str:
        return self.metadata.series

    def set_series(self, series: str, index: float = 1.0) -> None:
        self.metadata.series = series
        self.metadata.series_index = index

    def get_metadata(self) -> lnDict:
        return self.metadata.to_dict()


    def get_custom_metadata(self, key: str | None = None) -> dict | str | int | float | list | None:
        _dict=lnDict(self.metadata.custom)
        if key:
            return _dict.get(key)
        return _dict
        # return lnDict(self.metadata.custom)

    def set_custom_metadata(self, key: str, value: str | int | float | list) -> None:
        """Aggiunge o aggiorna un campo personalizzato nei metadati."""
        self.metadata.custom[key] = value

    # -------------------------------------------------------------------------
    # Estrazione Testo
    # -------------------------------------------------------------------------


    def _clean_html(self, html_content: str) -> str:
        """Rimuove il markup HTML e restituisce solo il testo pulito."""
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, "html.parser")

        # Rimuove elementi non visibili come script e style se presenti
        for element in soup(["script", "style"]):
            element.decompose()

        # Estrae il testo inserendo una nuova riga tra i blocchi (p, div, h1, etc.)
        text = soup.get_text(separator="\n\n")

        # Pulisce eventuali righe vuote in eccesso
        lines = [line.strip() for line in text.splitlines()]
        clean_text = "\n".join(line for line in lines if line)

        return clean_text


    def get_text(self, separator: str = "\n\n") -> str:
        """Restituisce il testo completo del libro convertito da HTML a testo piano."""
        sections_text = [section.section_to_text() for section in self.sections]
        return separator.join(filter(None, sections_text))



    def save_text_prev(self, output_file: str | Path, replace: bool = False) -> bool:
        """Esporta il libro come file di testo formattato e pulito (senza HTML).

        Args:
            output_file: Percorso del file TXT di output.
            replace: Se True, sovrascrive il file se esiste già.

        Returns:
            bool: True se l'esportazione è andata a buon fine.
        """
        output_file = Path(output_file)

        if output_file.exists() and not replace:
            logger.warning(f"File di output già esistente: {output_file}")
            return False

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                # Intestazione Metadati
                f.write("=" * 60 + "\n")
                f.write("METADATI DEL LIBRO\n")
                f.write("=" * 60 + "\n\n")

                if self.metadata:
                    authors_str = (
                        ", ".join(self.metadata.authors)
                        if self.metadata.authors
                        else "N/A"
                    )
                    subjects_str = (
                        ", ".join(self.metadata.subject)
                        if self.metadata.subject
                        else "N/A"
                    )

                    f.write(f"Titolo:         {self.metadata.title or 'N/A'}\n")
                    f.write(f"Autore/i:       {authors_str}\n")
                    f.write(f"Lingua:         {self.metadata.language or 'N/A'}\n")
                    f.write(f"Editore:        {self.metadata.publisher or 'N/A'}\n")
                    f.write(f"Data Pubbl.:    {self.metadata.pub_date or 'N/A'}\n")
                    f.write(
                        f"Identificatore: {self.metadata.identifier or 'N/A'}\n"
                    )
                    if self.metadata.isbn:
                        f.write(f"ISBN:           {self.metadata.isbn}\n")

                    if self.metadata.series:
                        f.write(
                            f"Serie:          {self.metadata.series} (Vol."
                            f" {self.metadata.series_index})\n"
                        )
                    f.write(f"Soggetti:       {subjects_str}\n")

                    if self.metadata.custom:
                        f.write("\n--- Metadati Custom ---\n")
                        for key, value in self.metadata.custom.items():
                            # f.write(f"{k}: {v}\n")
                            f.writelines(f"{key}: {value}\n")


                # Contenuto del libro
                f.write("\n" + "=" * 60 + "\n")
                f.write("CONTENUTO\n")
                f.write("=" * 60 + "\n\n")

                for section in self.sections:
                    if section.title:
                        f.write(f"\n--- {section.title} ---\n\n")

                    # Recupera l'HTML e lo converte in testo pulito
                    raw_html = getattr(section, "content", None) or getattr( section, "text", "" )
                    clean_text = self._clean_html(raw_html)

                    f.write(clean_text)
                    f.write("\n\n")

            logger.info(f"Testo esportato correttamente: {output_file.name}")
            return True

        except OSError as e:
            logger.error(f"Errore durante l'esportazione del testo: {e}")
            return False

    def to_text(self, output_file: str | Path | None = None, replace: bool = False) -> str:
        """Esporta il libro come file di testo formattato e pulito (senza HTML).

        Args:
            output_file: Percorso del file TXT di output.
            replace: Se True, sovrascrive il file se esiste già.

        Returns:
            bool: True se l'esportazione è andata a buon fine.
        """
        data: str = ""

        # Intestazione Metadati
        data += "=" * 60 + "\n"
        data += "METADATI DEL LIBRO\n"
        data += "=" * 60 + "\n\n"

        if self.metadata:
            authors_str = (
                ", ".join(self.metadata.authors)
                if self.metadata.authors
                else "N/A"
            )
            subjects_str = (
                ", ".join(self.metadata.subject)
                if self.metadata.subject
                else "N/A"
            )

            data += f"Titolo:         {self.metadata.title or 'N/A'}\n"
            data += f"Autore/i:       {authors_str}\n"
            data += f"Lingua:         {self.metadata.language or 'N/A'}\n"
            data += f"Editore:        {self.metadata.publisher or 'N/A'}\n"
            data += f"Data Pubbl.:    {self.metadata.pub_date or 'N/A'}\n"
            data += (
                f"Identificatore: {self.metadata.identifier or 'N/A'}\n"
            )
            if self.metadata.isbn:
                data += f"ISBN:           {self.metadata.isbn}\n"

            if self.metadata.series:
                data += (
                    f"Serie:          {self.metadata.series} (Vol."
                    f" {self.metadata.series_index})\n"
                )
            data += f"Soggetti:       {subjects_str}\n"

            if self.metadata.custom:
                data += "\n--- Metadati Custom ---\n"
                for key, value in self.metadata.custom.items():
                    data += f"{key}: {value}\n"

            if self.metadata.calibre:
                data += "\n--- Metadati Calibre ---\n"
                for key, value in self.metadata.calibre.items():
                    data += f"{key}: {value}\n"


        # Contenuto del libro
        data += "\n" + "=" * 60 + "\n"
        data += "CONTENUTO\n"
        data += "=" * 60 + "\n\n"

        for section in self.sections:
            if section.title:
                data += f"\n--- {section.title} ---\n\n"

            # Recupera l'HTML e lo converte in testo pulito
            raw_html = getattr(section, "content", None) or getattr(section, "text", "")
            clean_text = self._clean_html(raw_html)

            data += clean_text
            data += "\n\n"


        if output_file:
            output_file = Path(output_file)
            if output_file.exists() and not replace:
                logger.warning(f"File di output già esistente: {output_file}")

            else:
                try:
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(data)
                    logger.info(f"Testo esportato correttamente: {output_file.name}")

                except OSError as e:
                    logger.error(f"Errore durante l'esportazione del testo: {e}")
                    return ""

        return data



    # -------------------------------------------------------------------------
    # Parsing ed Elaborazione Interna
    # -------------------------------------------------------------------------

    def _find_opf_file(self) -> Path:
        temp_path = Path(self._temp_dir)
        container_path = temp_path / "META-INF" / "container.xml"

        if not container_path.exists():
            raise ValueError("META-INF/container.xml mancante.")

        tree = ET.parse(container_path)
        root = tree.getroot()
        rootfile = root.find(".//container:rootfile", self.NS)

        if rootfile is not None and "full-path" in rootfile.attrib:
            rel_path = Path(rootfile.attrib["full-path"])
            self._opf_relative_path = rel_path
            return temp_path / rel_path

        raise ValueError("Impossibile determinare il percorso del file OPF da container.xml")




    def _parse_metadata(self, opf_path: Path) -> None:
        tree = ET.parse(opf_path)
        root = tree.getroot()
        metadata_elem = root.find("opf:metadata", self.NS)

        if metadata_elem is None:
            self.metadata = EpubMetadata()
            return

        meta = EpubMetadata()

        # --- 1. Dublin Core Standard ---
        title_elem = metadata_elem.find("dc:title", self.NS)
        meta.title = (
            title_elem.text if title_elem is not None and title_elem.text else ""
        )

        authors = metadata_elem.findall("dc:creator", self.NS)
        meta.authors = [a.text for a in authors if a.text]

        lang_elem = metadata_elem.find("dc:language", self.NS)
        meta.language = (
            lang_elem.text if lang_elem is not None and lang_elem.text else ""
        )

        pub_elem = metadata_elem.find("dc:publisher", self.NS)
        meta.publisher = (
            pub_elem.text if pub_elem is not None and pub_elem.text else ""
        )

        date_elem = metadata_elem.find("dc:date", self.NS)
        meta.pub_date = (
            date_elem.text if date_elem is not None and date_elem.text else ""
        )

        desc_elem = metadata_elem.find("dc:description", self.NS)
        meta.description = (
            desc_elem.text if desc_elem is not None and desc_elem.text else ""
        )

        rights_elem = metadata_elem.find("dc:rights", self.NS)
        meta.rights = (
            rights_elem.text if rights_elem is not None and rights_elem.text else ""
        )

        subjects = metadata_elem.findall("dc:subject", self.NS)
        meta.subject = [s.text for s in subjects if s.text]

        # Identifiers & ISBN
        for identifier in metadata_elem.findall("dc:identifier", self.NS):
            text = identifier.text or ""
            scheme = identifier.attrib.get(f"{{{self.NS['opf']}}}scheme", "").lower()

            if not meta.identifier:
                meta.identifier = text

            if "isbn" in scheme or "isbn" in text.lower():
                meta.isbn = re.sub(r"[^\dX]", "", text.upper())

        # --- 2. Meta Tags (Calibre EPUB 2 e EPUB 3) ---
        for meta_tag in metadata_elem.findall("opf:meta", self.NS):
            # Supporta sia EPUB 2 ('name') che EPUB 3 ('property')
            key = meta_tag.attrib.get("name") or meta_tag.attrib.get("property") or ""

            # Recupera il valore da 'content' oppure dal testo interno del nodo
            value = meta_tag.attrib.get("content") or meta_tag.text or ""

            if not key:
                continue

            # Gestione Colonne Custom Calibre (calibre:user_metadata:#colonna)
            if "user_metadata:" in key:
                self._parse_calibre_custom_metadata(meta_tag, meta, key, value)

            # Metadati Calibre Standard (es. calibre:series, calibre:title_sort)
            elif key.startswith("calibre:"):
                meta.set_calibre_entry(key, value)

            # Altri metadati generici
            else:
                meta.custom[key] = value

        self.metadata = meta
        self.logger.debug(
            f"Metadati letti | Calibre: {len(meta.calibre)} voci | Custom:"
            f" {len(meta.custom)} voci"
        )


    def _parse_calibre_custom_metadata(
        self, meta_tag: ET.Element, meta: EpubMetadata, key: str, value: str
    ) -> None:
        """Decodifica i metadati custom in formato JSON da Calibre."""
        # Se 'content' o 'text' non contengono il JSON, cerca se il testo è nel nodo figlio
        raw_json = value.strip() if value else ""

        if not raw_json and len(meta_tag) > 0:
            raw_json = meta_tag.text or ""

        if not raw_json:
            return

        try:
            data = json.loads(raw_json)

            # Ricava il nome della colonna (es. #status, #tipologia)
            col_name = key.split("user_metadata:")[-1]

            # Estrae il valore effettivo memorizzato nel dizionario JSON da Calibre
            if isinstance(data, dict) and "#value#" in data:
                val = data["#value#"]
                meta.set_calibre_entry(col_name, val)

        except (json.JSONDecodeError, TypeError, KeyError):
            pass

    # def set_calibre_entry(self, key: str, value: object) -> None:
    #     """Aggiunge una chiave nel dizionario calibre se valida.

    #     Supporta campi noti Calibre o colonne custom (#).
    #     """
    #     if not key:
    #         return

    #     # Gestisce direttamente serie e serie_index se passate qui
    #     if key == "series":
    #         self.series = str(value or "")
    #         return
    #     if key == "series_index":
    #         try:
    #             self.series_index = float(value)
    #         except (ValueError, TypeError):
    #             self.series_index = 0.0
    #         return

    #     # Popola il dizionario calibre se è un campo noto o una colonna custom (#)
    #     if key in self.CALIBRE_KNOWN_FIELDS or key.startswith("#"):
    #         self.metadata.calibre[key] = value
    #     else:
    #         # Se non fa parte del mondo Calibre, va in custom generico
    #         self.metadata.custom[key] = value

    def _parse_sections(self, opf_path: Path) -> None:
        tree = ET.parse(opf_path)
        root = tree.getroot()

        manifest_elem = root.find("opf:manifest", self.NS)
        spine_elem = root.find("opf:spine", self.NS)

        if manifest_elem is None or spine_elem is None:
            return

        manifest: dict[str, dict[str, str]] = {}
        for item in manifest_elem.findall("opf:item", self.NS):
            item_id = item.attrib.get("id")
            href = item.attrib.get("href")
            media_type = item.attrib.get("media-type")
            if item_id and href:
                manifest[item_id] = {"href": href, "media-type": media_type}

        spine_order = []
        for itemref in spine_elem.findall("opf:itemref", self.NS):
            idref = itemref.attrib.get("idref")
            if idref in manifest:
                spine_order.append(idref)

        self.sections = []
        opf_dir = opf_path.parent

        for idx, item_id in enumerate(spine_order):
            item_data = manifest[item_id]
            file_path = (opf_dir / item_data["href"]).resolve()

            content = ""
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    content = file_path.read_text(encoding="latin-1", errors="replace")

            self.sections.append(
                BookSection(
                    id=item_id,
                    href=item_data["href"],
                    title=f"Sezione {idx + 1}",
                    content=content,
                    order=idx,
                )
            )

    # -------------------------------------------------------------------------
    # Sincronizzazione XML e Salvataggio
    # -------------------------------------------------------------------------

    def _update_opf_metadata(self) -> bool:
        """Aggiorna l'albero XML dell'OPF applicando i nuovi metadati prima del salvataggio."""
        if not self._temp_dir or not self._opf_relative_path:
            return False

        opf_path = Path(self._temp_dir) / self._opf_relative_path
        if not opf_path.exists():
            return False

        for prefix, uri in self.NS.items():
            ET.register_namespace(prefix, uri)

        tree = ET.parse(opf_path)
        root = tree.getroot()
        metadata_elem = root.find("opf:metadata", self.NS)

        if metadata_elem is None:
            metadata_elem = ET.SubElement(root, f"{{{self.NS['opf']}}}metadata")

        def _set_or_create_dc(tag: str, value: str):
            if not value:
                return
            elem = metadata_elem.find(f"dc:{tag}", self.NS)
            if elem is None:
                elem = ET.SubElement(metadata_elem, f"{{{self.NS['dc']}}}{tag}")
            elem.text = value

        # Aggiornamento metadati base
        _set_or_create_dc("title", self.metadata.title)
        _set_or_create_dc("language", self.metadata.language)
        _set_or_create_dc("publisher", self.metadata.publisher)
        _set_or_create_dc("description", self.metadata.description)

        # Autori
        for old_creator in metadata_elem.findall("dc:creator", self.NS):
            metadata_elem.remove(old_creator)

        for author in self.metadata.authors:
            creator_elem = ET.SubElement(metadata_elem, f"{{{self.NS['dc']}}}creator")
            creator_elem.text = author

        # Metadati Custom e Serie Calibre
        if self.metadata.series:
            series_meta = metadata_elem.find("opf:meta[@name='calibre:series']", self.NS)
            if series_meta is None:
                series_meta = ET.SubElement(metadata_elem, f"{{{self.NS['opf']}}}meta")
                series_meta.set("name", "calibre:series")
            series_meta.set("content", self.metadata.series)

            idx_meta = metadata_elem.find("opf:meta[@name='calibre:series_index']", self.NS)
            if idx_meta is None:
                idx_meta = ET.SubElement(metadata_elem, f"{{{self.NS['opf']}}}meta")
                idx_meta.set("name", "calibre:series_index")
            idx_meta.set("content", str(self.metadata.series_index))

        # custom metadata dict -> meta tag calibre
        for key, val in self.metadata.custom.items():
            meta_name = f"calibre:user_metadata:{key}"
            custom_elem = metadata_elem.find(f"opf:meta[@name='{meta_name}']", self.NS)
            if custom_elem is None:
                custom_elem = ET.SubElement(metadata_elem, f"{{{self.NS['opf']}}}meta")
                custom_elem.set("name", meta_name)

            custom_payload = {"#value#": val, "#extra#": None}
            custom_elem.set("content", json.dumps(custom_payload))

        tree.write(opf_path, encoding="utf-8", xml_declaration=True)
        return True

    def save(self, output_path: str | Path) -> bool:
        """Salva il file EPUB garantendo le specifiche d'archivio ZIP per EPUB."""
        if not self._temp_dir:
            self.logger.error("Nessun EPUB caricato da salvare.")
            return False

        if not self._update_opf_metadata():
            self.logger.error("Errore durante l'aggiornamento dell'OPF, salvataggio annullato.")
            return False

        output_path = Path(output_path)
        temp_path = Path(self._temp_dir)
        mimetype_file = temp_path / "mimetype"

        try:
            with zipfile.ZipFile(output_path, "w") as zip_ref:
                # 1. Scrittura mimetype non compresso per specifica EPUB
                if mimetype_file.exists():
                    zip_ref.write(mimetype_file, "mimetype", compress_type=zipfile.ZIP_STORED)

                # 2. Compressione degli altri file
                for file_path in temp_path.rglob("*"):
                    if file_path.is_file() and file_path != mimetype_file:
                        arcname = str(file_path.relative_to(temp_path))
                        zip_ref.write(file_path, arcname, compress_type=zipfile.ZIP_DEFLATED)

            self.logger.info(f"EPUB salvato correttamente in: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Errore durante la creazione del file ZIP EPUB: {e}")
            return False

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


"""
test_epub_manager.py - Script di test per EpubManager
"""

from pathlib import Path
# Assicurati di importare logger ed EpubManager dal tuo modulo
# from epub_manager import EpubManager, logger


def test_read_main_metadata(book: EpubManager):
    """Verifica e stampa i metadati iniziali e la struttura delle sezioni."""
    logger.info("--- METADATI ORIGINALI ---")
    if book.metadata:
        logger.info(f"  Titolo:  {book.title}")
        logger.info(f"  Autori:  {book.authors}")
        logger.info(f"  Dizionario completo: {book.metadata.to_dict()}")

    logger.info(f"--- CAPITOLI TROVATI: {len(book.sections)} ---")
    for i, section in enumerate(book.sections[:3], 1):
        title = section.title or f"Capitolo {i}"
        text_len = len(getattr(section, "content", "") or getattr(section, "text", ""))
        logger.info(f"  {i}. {title} ({text_len} caratteri)")

    if len(book.sections) > 3:
        logger.info(f"  ... e altri {len(book.sections) - 3} capitoli.")


def test_modify_metadata(book: EpubManager):
    """Applica modifiche ai metadati standard e custom."""
    logger.info("--- MODIFICA METADATI ---")
    logger.info(f"  Custom metadata (prima): {book.get_custom_metadata()}")

    book.set_title("Test Titolo Modificato")
    book.set_authors(["Test Autore Modificato"])  # Passare lista o stringa in base all'implementazione di set_authors

    logger.info(f"  Nuovo titolo: {book.title}")
    logger.info(f"  Nuovo autore: {book.authors}")

    book.set_custom_metadata("test_key", "test_value")
    book.set_custom_metadata("processed_by", "EpubManager v2.0")
    logger.info(f"  processed_by: {book.get_custom_metadata(key='processed_by')}")

    logger.info(f"  Custom metadata (dopo): {book.get_custom_metadata()}")


def scan_directory(root_dir: Path | str, pattern: str = "*.epub", recursive: bool = True) -> list[Path]:
    """Scansiona una directory per individuare i file EPUB."""
    root_path = Path(root_dir)
    if not root_path.exists():
        logger.error(f"Directory non trovata: {root_path}")
        return []

    file_list = list(root_path.glob(f"**/{pattern}")) if recursive else list(root_path.glob(pattern))
    logger.info(f"Trovati {len(file_list)} file '{pattern}' in {root_path}")
    return file_list


if __name__ == "__main__":
    epub_inp_path = Path("/home/loreto/Downloads/epubs_test/Owens, Ivy")
    epub_out_path = Path("/home/loreto/Downloads/epubs_out")

    file_list = scan_directory(epub_inp_path, "*.epub")
    epub_out_path.mkdir(parents=True, exist_ok=True)

    for epub_path in file_list:
        logger.info(f"\n================ Processing: {epub_path.name} ================")

        # Uso del context manager per gestire 'load' e 'cleanup' in automatico
        with EpubManager(epub_path) as book:
            test_read_main_metadata(book)
            test_modify_metadata(book)

            # Salvataggio del nuovo EPUB
            output_file = epub_out_path / book.epub_path.name
            book.save(output_file)
            logger.notify(f"EPUB salvato: {output_file}")

            # Esportazione in TXT
            txt_file = epub_out_path / f"{book.epub_path.stem}_estratto.txt"
            if book.to_text(txt_file, replace=True):
                logger.notify(f"Testo esportato: {txt_file}")
