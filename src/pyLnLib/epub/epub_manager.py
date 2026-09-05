# /home/loreto/filu/Programming/gitREPO/pyLnLib/src/pyLnLib/epub/epub_manager.py
#
# ruff: noqa: BLE001x  Do not catch blind exception: `Exception` (Ruff BLE001)
# ruff: noqa: I001x  Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
# ruff: noqa: SIM102 Use a single `if` statement instead of nested `if` statements help: Combine `if` statements using `and` (Ruff SIM102)
#

from __future__ import annotations


"""
epub_manager.py - Gestione EPUB con zipfile + lxml
E' configurato per essere usato sia con with che senza context manager.

1. Con context manager (come prima)
    with EpubManager(epub_path) as book:
        book.set_title('Nuovo Titolo')
        book.set_author('Nuovo Autore')
        book.save('output.epub')
    # cleanup automatico

2. Senza context manager (passaggio ad altre funzioni)
    # Caricamento automatico all'init

    book = EpubManager(epub_path, auto_load=True)
    try:
        # Usa subito, è già caricato
        print(f"Titolo: {book.title}")
        book.set_title('Nuovo Titolo')
        book.save('output.epub')
    finally:
        book.cleanup()

3. Try/finally (se devi passare il book):
    book = EpubManager(epub_path)
    try:
        book.load()
        # lavoro... (anche in altre funzioni)
    finally:
        book.cleanup()

# NOTA: I metadati Calibre che non sono stringhe (es. datetime, dict)
# vengono saltati durante il salvataggio per evitare errori con lxml.
# Questo significa che campi come "readdate" potrebbero andare persi.
# Se necessario, convertire in stringa durante la lettura.

"""

import shutil
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup
from lxml import etree



from pyLnLib import lnDict
from pyLnLib.logger import get_logger
logger = get_logger()

# Namespace EPUB
NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "opf": "http://www.idpf.org/2007/opf",
    "xhtml": "http://www.w3.org/1999/xhtml",
    "xml": "http://www.w3.org/XML/1998/namespace",
}


@dataclass
class BookSection:
    """Rappresenta una sezione/capitolo del libro."""

    file: str
    title: str | None
    text: str
    order: int


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
    subject: list[str] = field(default_factory=list)
    rights: str | None = None
    # Campi custom
    custom: dict[str, str] = field(default_factory=dict)


class EpubManager:
    """
    Gestore EPUB che usa zipfile + lxml per operazioni sui metadati.
    """

    # def __init__(self, filename: str | Path):
    def __init__(self, filename: str | Path, auto_load: bool = False):
        self.logger = get_logger()
        self._source_path = Path(filename)
        self.path = Path(filename)
        self._temp_dir: str | None = None
        self._opf_path: Path | None = None
        self._metadata: EpubMetadata = EpubMetadata()  # Inizializzato!
        self._sections: list[BookSection] = []
        self._is_loaded = False  # indica che il fileè  caricato quindi valido
        self._is_cleaned = False  # Traccia se è stato fatto cleanup

        if not self._source_path.exists():
            raise FileNotFoundError(f"File non trovato: {self._source_path}")

        # Caricamento automatico se richiesto
        if auto_load:
            self.load()

        # -----------------------------------------------
        # con with verrà eseguito automaticamente self.__enter__()
        # -----------------------------------------------



        # ======================================================================
        # Pulizia
        # ======================================================================


    def cleanup(self):
        """Rimuove i file temporanei."""
        if self._is_cleaned:
            return
        if self._temp_dir and Path(self._temp_dir).exists():
            shutil.rmtree(self._temp_dir)
        self._is_cleaned = True
        self.logger.info("Cleanup completato")

    def __del__(self):
        self.cleanup()

    # -  vieneseguito all'apertura/init della classe
    def __enter__(self):
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def _ensure_loaded(self):
        """Assicura che il libro sia caricato."""
        if not self.is_loaded():
            raise RuntimeError(f"Libro non caricato: {self._source_path}")

    def is_loaded(self) -> bool:
        """Verifica se il libro è caricato correttamente."""
        return self._is_loaded and not self._is_cleaned

    # ======================================================================
    # Caricamento e parsing
    # ======================================================================
    def load(self) -> bool:
        """Carica l'EPUB in una directory temporanea."""
        if self._is_loaded:
            return True  # Già caricato

        try:
            self._temp_dir = tempfile.mkdtemp(prefix='epub_')
            temp_path = Path(self._temp_dir)

            with zipfile.ZipFile(self._source_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)

            self._opf_path = self._find_opf(temp_path)
            if not self._opf_path:
                self.logger.error("File OPF non trovato:\n%s", self._source_path)
                return False

            self._metadata = self._parse_metadata(self._opf_path)
            self._sections = self._parse_sections(temp_path, self._opf_path)
            self._is_loaded = True
            self.logger.info("Load completato")
            return True

        except Exception as e:
            self.logger.error("Errore nel caricamento dell'EPUB: %s", e)
            self.cleanup()  # Pulisci in caso di errore
            return False




    # =======================================================
    # =
    # =======================================================
    def _find_opf(self, base_path: Path) -> Path | None:
        """Trova il file OPF nel container.xml o per estensione."""
        container = base_path / "META-INF" / "container.xml"
        if container.exists():
            try:
                tree = etree.parse(str(container))
                root = tree.getroot()
                # Cerca full-path
                for elem in root.iter():
                    if "full-path" in elem.attrib:
                        return base_path / elem.attrib["full-path"]
            except Exception as e:
                self.logger.error("Errore nel parsing di container.xml: %s", e)

        # Cerca file .opf
        for file in base_path.rglob("*.opf"):
            return file

        return None









    # =======================================================
    # =
    # =======================================================
    def parse_calibre_metadata(self) -> dict:
        """Estrae i metadati Calibre specifici."""
        import json

        # calibre_data = {}
        calibre_data = lnDict()
        metadata_elem = self.metadata_elem
        if metadata_elem is None:
            return calibre_data

        # Campi Calibre comuni
        calibre_fields = [
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
        ]
        calibre_custom_column = [
              "#comments",
              "#read_date_text",
              "#status",
              "#tipologia",
            ]

        my_calibre_fields = calibre_fields + calibre_custom_column


        # =======================================================
        def extract_value(meta_elem: etree.Element) -> str | None:
            """Estrae il valore da un elemento <meta>."""
            if meta_elem.text:
                try:
                    value = json.loads(meta_elem.text)
                    if isinstance(value, dict) and "#value#" in value:
                        return value["#value#"]
                    return meta_elem.text
                except json.JSONDecodeError:
                    return meta_elem.text
            elif meta_elem.attrib.get("content"):
                try:
                    value = json.loads(meta_elem.attrib.get("content"))
                    if isinstance(value, dict) and "#value#" in value:
                        return value["#value#"]
                    return meta_elem.attrib.get("content")
                except json.JSONDecodeError:
                    return meta_elem.attrib.get("content")
            return None
        # =======================================================


        for meta in metadata_elem.findall(".//opf:meta", namespaces=NAMESPACES):
            name = meta.get("name", "")
            prop = meta.get("property", "")

            # Cerca calibre:user_metadata:field
            if name and name.startswith("calibre:user_metadata:"):
                # self.logger.info(f"calibre metadata: {name}")
                field = name.split(":", 2)[2] if ":" in name else name
                self.logger.debug(f"\tfield: {field}")
                if not field in my_calibre_fields:
                    self.logger.debug(f"\t...skipping field")
                    continue
                self.logger.debug(f"\tfield: {field}")
                extracted_value = extract_value(meta)
                calibre_data[f"custom_{field}"] = extracted_value


            # Cerca calibre:field
            elif name and name.startswith("calibre:"):
                # self.logger.info(f"calibre: {name}")
                field = name.split(":", 1)[1] if ":" in name else name
                # if not field in calibre_fields and not field in calibre_custom_column:
                    # continue
                if meta.text:
                    if field in calibre_fields:
                        calibre_data[field] = meta.text.strip()
                elif meta.attrib.get("content"):
                    if field in calibre_fields:
                        calibre_data[field] = meta.attrib.get("content").strip()
                    elif field in calibre_custom_column:
                        calibre_data[field] = meta.attrib.get("content").strip()

            # Cerca calibre:user_metadata (JSON completo)
            elif prop == "calibre:user_metadata" and meta.text:
                self.logger.info(f"calibre metadata: {prop}")
                self.logger.info(f"metadata text:      {type(meta.text)} {meta.text}")
                try:
                    import json

                    data = json.loads(meta.text)
                    for key, value in data.items():
                        if isinstance(value, dict):
                            # Estrai il valore e il nome
                            actual_value = value.get("#value#")
                            name_value = value.get("name", key.lstrip("#"))
                            if actual_value is not None:
                                clean_key = key.lstrip("#")
                                calibre_data[f"user_{clean_key}"] = actual_value
                                if isinstance(actual_value, dict) and actual_value != name_value:
                                    self.logger.warning(f"trovato dict all'interno di calibre metadata: {key}")
                                calibre_data[f"user_{clean_key}_name"] = name_value
                except:
                    pass

            elif prop == "custom":
                self.logger.info(f"custom: {prop}")



        self.logger.info(f"calibre data: {calibre_data}")
        return calibre_data





    def _parse_metadata(self, opf_path: Path) -> EpubMetadata:
        """Parsa i metadati dal file OPF."""
        tree = etree.parse(str(opf_path))
        root = tree.getroot()

        metadata = EpubMetadata()

        # Trova il tag metadata
        metadata_elem = root.find(".//opf:metadata", namespaces=NAMESPACES)
        self.metadata_elem = metadata_elem # mi serve per passarlo a calibre_metadata
        if metadata_elem is None:
            return metadata

        # ============================================================
        # 1. Leggi metadati DC (Dublin Core)
        # ============================================================
        dc_ns = NAMESPACES["dc"]

        # Mappatura tag DC -> attributo
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

        # ============================================================
        # 2. Leggi metadati custom (IN TUTTI I FORMATI POSSIBILI)
        # ============================================================

        # 2a. Cerca tag con namespace che contiene 'custom'
        for elem in metadata_elem:
            if "}" in elem.tag:
                namespace = elem.tag.split("}")[0].strip("{")
                if "custom" in namespace.lower() or "example" in namespace.lower():
                    tag_name = elem.tag.split("}")[-1]
                    if elem.text:
                        metadata.custom[tag_name] = elem.text.strip()

        # 2b. Cerca tag <meta property="custom:key">
        # 2c. Cerca tag <meta name="custom:key">
        # 2d. Cerca qualsiasi tag con attributo che inizia con 'custom:'
        for elem in metadata_elem.iter():
            # Controlla tutti gli attributi
            for attr_value in elem.attrib.values():
                if attr_value and isinstance(attr_value, str):
                    if attr_value.startswith("custom:"):
                        key = (
                            attr_value.split(":", 1)[1]
                            if ":" in attr_value
                            else attr_value
                        )
                        if elem.text:
                            metadata.custom[key] = elem.text.strip()
                        break  # Esci dopo aver trovato un attributo custom

        # 2e. Cerca specificamente tag <meta> con property o name
        for elem in metadata_elem.findall(".//opf:meta", namespaces=NAMESPACES):
            prop = elem.get("property", "")
            name = elem.get("name", "")

            for attr_value in [prop, name]:
                if attr_value and attr_value.startswith("custom:"):
                    key = (
                        attr_value.split(":", 1)[1] if ":" in attr_value else attr_value
                    )
                    if elem.text:
                        metadata.custom[key] = elem.text.strip()
                    break


        # Dopo aver letto i metadati DC e prima di ritornare
        # calibre_data = self._parse_calibre_metadata(metadata_elem)
        # for key, value in calibre_data.items():
        #     metadata.custom[f'calibre_{key}'] = value


        # ============================================================
        # 3. DEBUG: stampa i custom trovati
        # ============================================================
        if metadata.custom:
            # logger.debug(f"Custom metadata trovati: {metadata.custom}")
            print(f"Custom metadata trovati: {metadata.custom}")

        return metadata

    def _parse_sections(self, base_path: Path, opf_path: Path) -> list[BookSection]:
        """Parsa le sezioni del libro."""
        sections = []

        # Leggi il manifest dal OPF per trovare i documenti
        tree = etree.parse(str(opf_path))
        root = tree.getroot()

        # Trova il manifest
        manifest = root.find(".//opf:manifest", namespaces=NAMESPACES)
        if manifest is None:
            return sections

        # Raccogli gli ID dei documenti HTML
        html_items = []
        for item in manifest.findall("opf:item", namespaces=NAMESPACES):
            media_type = item.get("media-type", "")
            if media_type in ["application/xhtml+xml", "text/html"]:
                href = item.get("href")
                if href and not href.endswith(".ncx"):
                    html_items.append(
                        {"id": item.get("id"), "href": href, "media_type": media_type}
                    )

        # Ordina per posizione nello spine
        spine = root.find(".//opf:spine", namespaces=NAMESPACES)
        if spine is not None:
            order = 0
            for itemref in spine.findall("opf:itemref", namespaces=NAMESPACES):
                idref = itemref.get("idref")
                for html_item in html_items:
                    if html_item["id"] == idref:
                        html_item["order"] = order
                        order += 1
                        break

        # Leggi il contenuto di ogni file HTML
        for html_item in sorted(html_items, key=lambda x: x.get("order", 999)):
            file_path = base_path / html_item["href"]
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    soup = BeautifulSoup(content, "html.parser")

                    # Estrai testo
                    text = soup.get_text(separator=" ", strip=True)

                    # Cerca titolo
                    title = None
                    if soup.title:
                        title = soup.title.get_text(strip=True)
                    if not title:
                        h1 = soup.find("h1")
                        if h1:
                            title = h1.get_text(strip=True)
                    if not title:
                        h2 = soup.find("h2")
                        if h2:
                            title = h2.get_text(strip=True)

                    sections.append(
                        BookSection(
                            file=html_item["href"],
                            title=title,
                            text=text,
                            order=html_item.get("order", 999),
                        )
                    )
                except Exception as e:
                    # Ignora errori di lettura
                    self.logger.error(
                        "Errore nella lettura del file %s: %s", html_item["href"], e
                    )

        return sections

    # ======================================================================
    # Accesso ai metadati
    # ======================================================================

    @property
    def source_path(self) -> str:
        """Titolo del libro."""
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
        """Tutti i metadati (garantito non None)."""
        return self._metadata

    @property
    def sections(self) -> list[BookSection]:
        """Sezioni del libro."""
        return self._sections



    # ======================================================================
    # Modifica metadati
    # ======================================================================
    def set_title(self, new_title: str) -> bool:
        """Modifica il titolo."""
        self._ensure_loaded()
        self._metadata.title = new_title  # ✅ Nessun errore type-check
        self._metadata.custom["modified_by"] = "EpubManager"
        return True

    def set_author(self, new_author: str) -> bool:
        """Modifica l'autore."""
        self._ensure_loaded()
        self._metadata.creator = new_author  # ✅ Nessun errore type-check
        self._metadata.custom["modified_by"] = "EpubManager"
        return True

    def set_custom_metadata(self, key: str, value: str) -> bool:
        """Imposta un metadata custom."""
        self._ensure_loaded()
        self._metadata.custom[key] = value  # ✅ Nessun errore type-check
        return True

    def get_custom_metadata(self, key: str) -> str | None:
        """Recupera un metadata custom."""
        return self._metadata.custom.get(key)  # ✅ Nessun errore type-check



    def _update_opf_metadata(self) -> bool:
        """Aggiorna il file OPF con i metadati modificati (versione semplificata)."""
        if not self._opf_path or not self._metadata:
            return False

        try:
            tree = etree.parse(str(self._opf_path))
            root = tree.getroot()

            # Trova metadata
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
            dc_ns = NAMESPACES["dc"]
            for dc_key in [ "title",
                            "creator",
                            "language",
                            "publisher",
                            "date",
                            "identifier",
                            "description",
                            "rights",]:
                value = getattr(self._metadata, dc_key, None)
                old_elem = metadata_elem.find(f".//{{{dc_ns}}}{dc_key}")

                if value:
                    if old_elem is None:
                        new_elem = etree.Element(f"{{{dc_ns}}}{dc_key}")
                        new_elem.text = value
                        metadata_elem.append(new_elem)
                    else:
                        old_elem.text = value
                elif old_elem is not None:
                    metadata_elem.remove(old_elem)

            # Rimuovi vecchi custom metadata (tag <meta property="...">)
            for meta in metadata_elem.findall(".//opf:meta", namespaces=NAMESPACES):
                prop = meta.get("property", "")
                if prop and prop.startswith("custom:"):
                    metadata_elem.remove(meta)

            # Aggiungi nuovi custom metadata
            for key, value in self._metadata.custom.items():
                if value:
                    meta = etree.Element(
                        "{http://www.idpf.org/2007/opf}meta",
                        nsmap={"opf": "http://www.idpf.org/2007/opf"},
                    )
                    meta.set("property", f"custom:{key}")
                    meta.text = value
                    metadata_elem.append(meta)

            # Salva
            tree.write(str(self._opf_path), encoding="utf-8", xml_declaration=True, pretty_print=True )

            return True

        except Exception as e:
            self.logger.error( "Errore nell'aggiornamento del OPF: %s", e, show_stack=True )

        return False

    # ======================================================================
    # Salvataggio
    # ======================================================================
    def save(self, output_path: str | Path) -> bool:
        """
        Salva il libro modificato in un nuovo file.
        Non tocca l'originale.
        """
        self._ensure_loaded()
        output_path = Path(output_path)

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Aggiorna il file OPF con i metadati
            self._update_opf_metadata()

            # Crea il nuovo EPUB
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zip_ref:
                temp_path = Path(self._temp_dir)  # type: ignore
                for file_path in temp_path.rglob("*"):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to(temp_path))
                        zip_ref.write(file_path, arcname)

            return True

        except Exception as e:
            self.logger.error("Errore nel salvataggio: %s", e, show_stack=True)
            # raise Exception(f"Errore nel salvataggio: {e}")

        return False


    # ======================================================================
    # Utility
    # ======================================================================

    def get_text(self) -> str:
        """Restituisce tutto il testo del libro."""
        return "\n\n".join(section.text for section in self.sections if section.text)

    def to_text(self, output_file: str | Path, replace: bool = False) -> bool:
        """Esporta il libro come file di testo."""
        output_file = Path(output_file)

        if output_file.exists() and not replace:
            return False

        with open(output_file, "w", encoding="utf-8") as f:
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
                        # f.write(f"{key}: {value}\n")
                        f.writelines(f"{key}: {value}\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write("CONTENUTO\n")
            f.write("=" * 60 + "\n\n")

            for section in self.sections:
                if section.title:
                    f.write(f"\n--- {section.title} ---\n\n")
                f.write(section.text)
                f.write("\n\n")

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
        logger.debug(f"\tTitolo:  {book.title}")
        logger.debug(f"\tAutore:  {book.author}")
        logger.debug(f"\tLingua:  {book.metadata.language if book.metadata else 'N/A'}")
        logger.debug(f"\tEditore: {book.metadata.publisher if book.metadata else 'N/A'}")
        logger.debug(f"\tData:    {book.metadata.date if book.metadata else 'N/A'}")

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
    logger.info(f"  Custom metadata: {book.metadata.custom}")
    logger.info(f"  processed_by: {book.metadata.custom.get('processed_by')}")





def test_epub_operations(epub_path: Path | str):
    """Test completo delle operazioni EPUB."""

    epub_path = Path(epub_path)
    if not epub_path.exists():
        print(f"❌ File non trovato: {epub_path}")
        return False

    print("=" * 70)
    print(f"📚 Test su: {epub_path.name}")
    print("=" * 70)

    try:
        # Usa il context manager per caricamento e pulizia automatica
        with EpubManager(epub_path) as book:
            # 1. Verifica caricamento
            print("\n✅ EPUB caricato con successo")

            # 2. Leggi metadati originali
            print("\n📖 METADATI ORIGINALI:")
            print(f"  Titolo: {book.title}")
            print(f"  Autore: {book.author}")
            print(f"  Lingua: {book.metadata.language if book.metadata else 'N/A'}")
            print(f"  Editore: {book.metadata.publisher if book.metadata else 'N/A'}")
            print(f"  Data: {book.metadata.date if book.metadata else 'N/A'}")

            # 3. Verifica sezioni
            print(f"\n📑 CAPITOLI: {len(book.sections)}")
            for i, section in enumerate(book.sections[:3], 1):  # Mostra solo primi 3
                title = section.title or f"Capitolo {i}"
                print(f"  {i}. {title} ({len(section.text)} caratteri)")
            if len(book.sections) > 3:
                print(f"  ... e altri {len(book.sections) - 3} capitoli")
            print(f"  Custom metadata (before adding): {book.metadata.custom}")

            # 4. Modifica metadati
            print("\n✏️ MODIFICA METADATI:")
            book.set_title("Test Titolo Modificato")
            book.set_author("Test Autore Modificato")
            book.set_custom_metadata("test_key", "test_value")
            book.set_custom_metadata("processed_by", "EpubManager v2.0")

            print(f"  Nuovo titolo: {book.title}")
            print(f"  Nuovo autore: {book.author}")
            print(f"  Custom metadata: {book.metadata.custom}")

            # 5. Salva in nuovo file
            output_file = epub_path.parent / f"test_{epub_path.name}"
            book.save(output_file)
            print(f"\n💾 Salvataggio completato: {output_file}")

            # 6. Esporta come testo
            txt_file = epub_path.parent / f"{epub_path.stem}_estratto.txt"
            if book.to_text(txt_file, replace=True):
                print(f"📄 Esportato come testo: {txt_file}")

            # 7. Verifica che il file salvato abbia i metadati corretti
            print("\n🔍 VERIFICA FILE SALVATO:")
            with EpubManager(output_file) as test_book:
                print(f"  Titolo: {test_book.title}")
                print(f"  Autore: {test_book.author}")
                print(f"  Custom: {test_book.metadata.custom}")
                modified_by = test_book.get_custom_metadata("processed_by")
                print(f"  Modified by: {modified_by}")

                # Verifica che le modifiche siano state applicate
                success = (
                    test_book.title == "Test Titolo Modificato"
                    and test_book.author == "Test Autore Modificato"
                    and test_book.get_custom_metadata("test_key") == "test_value"
                )

                if success:
                    print("  ✅ Tutte le modifiche sono state salvate correttamente!")
                else:
                    print(
                        "  ⚠️ Attenzione: Alcune modifiche potrebbero non essere state salvate"
                    )

            return True

    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback

        traceback.print_exc()
        return False


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

        # breakpoint()

    # if epub_path:
    #     result = test_read_main_metadata(epub_path)
    #     sys.exit("Uscita test")
    #     result = test_epub_operations(epub_path)
    #     print("\n" + "=" * 70)
    #     print("✅ TEST COMPLETATO!" if result else "❌ TEST FALLITO!")
    #     print("=" * 70)




















# ============================================
# Esempio di utilizzo
# ============================================

if __name__ == "__main__xxx":
    import sys

    # Test
    test_file = (
        "/home/loreto/Downloads/test_epubs/Billionaire 02 - Miele - Meghan March.epub"
    )

    print("=" * 60)
    print("TEST EPUB MANAGER (zipfile + lxml)")
    print("=" * 60)

    try:
        with EpubManager(test_file) as book:
            print(f"\n📖 Titolo originale: {book.title}")
            print(f"✍️ Autore originale: {book.author}")
            print(f"📑 Numero capitoli: {len(book.sections)}")

            # Modifica metadati
            print("\n🔄 Modifico titolo e autore...")
            book.set_title("Nuovo Titolo Modificato")
            book.set_author("Nuovo Autore Modificato")
            book.set_custom_metadata("processed_by", "EpubManager v2.0")
            book.set_custom_metadata("processed_date", "2026-08-29")

            print(f"\n📖 Nuovo titolo: {book.title}")
            print(f"✍️ Nuovo autore: {book.author}")

            # Salva
            output_file = "libro_modificato.epub"
            book.save(output_file)
            print(f"\n💾 Libro salvato in: {output_file}")

            # Esporta come testo
            book.to_text("libro_esportato.txt", replace=True)
            print("📄 Esportato come testo in: libro_esportato.txt")

    except Exception as e:
        print(f"❌ Errore: {e}")
        sys.exit(1)

    print("\n✅ Test completato con successo!")
