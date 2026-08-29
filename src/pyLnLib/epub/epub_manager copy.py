#!/usr/bin/env python3
"""
epub_manager.py - Gestione EPUB con zipfile + lxml
"""

import zipfile
import tempfile
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from lxml import etree
from bs4 import BeautifulSoup

# Namespace EPUB
NAMESPACES = {
    'dc': 'http://purl.org/dc/elements/1.1/',
    'opf': 'http://www.idpf.org/2007/opf',
    'xhtml': 'http://www.w3.org/1999/xhtml',
    'xml': 'http://www.w3.org/XML/1998/namespace'
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
    """Gestore EPUB che usa zipfile + lxml per operazioni sui metadati."""

    def __init__(self, filename: str | Path):
        self._source_path = Path(filename)
        self._temp_dir: str | None = None
        self._opf_path: Path | None = None
        self._metadata: EpubMetadata = EpubMetadata()
        self._sections: list[BookSection] = []
        self._is_loaded = False

        if not self._source_path.exists():
            raise FileNotFoundError(f"File non trovato: {self._source_path}")

    # ======================================================================
    # Caricamento e parsing
    # ======================================================================

    def load(self) -> bool:
        """Carica l'EPUB in una directory temporanea."""
        try:
            self._temp_dir = tempfile.mkdtemp(prefix='epub_')
            temp_path = Path(self._temp_dir)

            with zipfile.ZipFile(self._source_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)

            self._opf_path = self._find_opf(temp_path)
            if not self._opf_path:
                raise Exception("File OPF non trovato")

            self._metadata = self._parse_metadata(self._opf_path)
            self._sections = self._parse_sections(temp_path, self._opf_path)
            self._is_loaded = True
            return True

        except Exception as e:
            raise Exception(f"Errore nel caricamento dell'EPUB: {e}")

    def _find_opf(self, base_path: Path) -> Path | None:
        """Trova il file OPF nel container.xml o per estensione."""
        container = base_path / 'META-INF' / 'container.xml'
        if container.exists():
            try:
                tree = etree.parse(str(container))
                root = tree.getroot()
                for elem in root.iter():
                    if 'full-path' in elem.attrib:
                        return base_path / elem.attrib['full-path']
            except:
                pass

        # Cerca file .opf
        for file in base_path.rglob('*.opf'):
            return file

        return None

    def _parse_metadata(self, opf_path: Path) -> EpubMetadata:
        """Parsa i metadati dal file OPF."""
        tree = etree.parse(str(opf_path))
        root = tree.getroot()

        metadata = EpubMetadata()

        # Trova il tag metadata
        metadata_elem = root.find('.//opf:metadata', namespaces=NAMESPACES)
        if metadata_elem is None:
            return metadata

        # 1. Leggi metadati DC (Dublin Core)
        dc_ns = NAMESPACES['dc']

        dc_mapping = {
            'title': 'title',
            'creator': 'creator',
            'language': 'language',
            'publisher': 'publisher',
            'date': 'date',
            'identifier': 'identifier',
            'description': 'description',
            'rights': 'rights'
        }

        for tag, attr in dc_mapping.items():
            elem = metadata_elem.find(f'.//{{{dc_ns}}}{tag}')
            if elem is not None and elem.text:
                setattr(metadata, attr, elem.text.strip())

        # Subject (multi)
        subjects = metadata_elem.findall(f'.//{{{dc_ns}}}subject')
        if subjects:
            metadata.subject = [s.text.strip() for s in subjects if s.text]

        # 2. Leggi metadati custom
        # Cerca tag <meta property="custom:key">
        for meta in metadata_elem.findall('.//opf:meta', namespaces=NAMESPACES):
            prop = meta.get('property', '')
            if prop and prop.startswith('custom:'):
                key = prop.split(':', 1)[1] if ':' in prop else prop
                if meta.text:
                    metadata.custom[key] = meta.text.strip()

        # Cerca tag con namespace custom
        for elem in metadata_elem:
            if '}' in elem.tag:
                namespace = elem.tag.split('}')[0].strip('{')
                if 'custom' in namespace.lower() or 'example' in namespace.lower():
                    tag_name = elem.tag.split('}')[-1]
                    if elem.text:
                        metadata.custom[tag_name] = elem.text.strip()

        return metadata

    def _parse_sections(self, base_path: Path, opf_path: Path) -> list[BookSection]:
        """Parsa le sezioni del libro."""
        sections = []

        tree = etree.parse(str(opf_path))
        root = tree.getroot()

        # Trova il manifest
        manifest = root.find('.//opf:manifest', namespaces=NAMESPACES)
        if manifest is None:
            return sections

        # Raccogli gli ID dei documenti HTML
        html_items = []
        for item in manifest.findall('opf:item', namespaces=NAMESPACES):
            media_type = item.get('media-type', '')
            if media_type in ['application/xhtml+xml', 'text/html']:
                href = item.get('href')
                if href and not href.endswith('.ncx'):
                    html_items.append({
                        'id': item.get('id'),
                        'href': href,
                        'media_type': media_type
                    })

        # Ordina per posizione nello spine
        spine = root.find('.//opf:spine', namespaces=NAMESPACES)
        if spine is not None:
            order = 0
            for itemref in spine.findall('opf:itemref', namespaces=NAMESPACES):
                idref = itemref.get('idref')
                for html_item in html_items:
                    if html_item['id'] == idref:
                        html_item['order'] = order
                        order += 1
                        break

        # Leggi il contenuto di ogni file HTML
        for html_item in sorted(html_items, key=lambda x: x.get('order', 999)):
            file_path = base_path / html_item['href']
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    soup = BeautifulSoup(content, 'html.parser')

                    # Estrai testo
                    text = soup.get_text(separator=' ', strip=True)

                    # Cerca titolo
                    title = None
                    if soup.title:
                        title = soup.title.get_text(strip=True)
                    if not title:
                        h1 = soup.find('h1')
                        if h1:
                            title = h1.get_text(strip=True)
                    if not title:
                        h2 = soup.find('h2')
                        if h2:
                            title = h2.get_text(strip=True)

                    sections.append(BookSection(
                        file=html_item['href'],
                        title=title,
                        text=text,
                        order=html_item.get('order', 999)
                    ))
                except Exception:
                    pass

        return sections

    # ======================================================================
    # Accesso ai metadati
    # ======================================================================

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
        """Tutti i metadati."""
        return self._metadata

    @property
    def sections(self) -> list[BookSection]:
        """Sezioni del libro."""
        return self._sections

    def get_custom_metadata(self, key: str) -> str | None:
        """Recupera un metadata custom."""
        return self._metadata.custom.get(key)

    # ======================================================================
    # Modifica metadati
    # ======================================================================

    def set_title(self, new_title: str) -> bool:
        """Modifica il titolo."""
        if not self._is_loaded:
            return False
        self._metadata.title = new_title
        self._metadata.custom['modified_by'] = 'EpubManager'
        return True

    def set_author(self, new_author: str) -> bool:
        """Modifica l'autore."""
        if not self._is_loaded:
            return False
        self._metadata.creator = new_author
        self._metadata.custom['modified_by'] = 'EpubManager'
        return True

    def set_custom_metadata(self, key: str, value: str) -> bool:
        """Imposta un metadata custom."""
        if not self._is_loaded:
            return False
        self._metadata.custom[key] = value
        return True

    def _update_opf_metadata(self) -> bool:
        """Aggiorna il file OPF con i metadati modificati."""
        if not self._opf_path:
            return False

        try:
            tree = etree.parse(str(self._opf_path))
            root = tree.getroot()

            # Trova metadata
            metadata_elem = root.find('.//opf:metadata', namespaces=NAMESPACES)
            if metadata_elem is None:
                metadata_elem = etree.Element(
                    '{http://www.idpf.org/2007/opf}metadata',
                    nsmap={
                        'dc': 'http://purl.org/dc/elements/1.1/',
                        'opf': 'http://www.idpf.org/2007/opf'
                    }
                )
                root.insert(0, metadata_elem)

            # Aggiorna DC metadata
            dc_ns = NAMESPACES['dc']
            dc_fields = ['title', 'creator', 'language', 'publisher',
                        'date', 'identifier', 'description', 'rights']

            for dc_key in dc_fields:
                value = getattr(self._metadata, dc_key, None)
                old_elem = metadata_elem.find(f'.//{{{dc_ns}}}{dc_key}')

                if value:
                    if old_elem is None:
                        new_elem = etree.Element(f'{{{dc_ns}}}{dc_key}')
                        new_elem.text = value
                        metadata_elem.append(new_elem)
                    else:
                        old_elem.text = value
                elif old_elem is not None:
                    metadata_elem.remove(old_elem)

            # Rimuovi vecchi custom metadata
            for meta in metadata_elem.findall('.//opf:meta', namespaces=NAMESPACES):
                prop = meta.get('property', '')
                if prop and prop.startswith('custom:'):
                    metadata_elem.remove(meta)

            # Aggiungi nuovi custom metadata
            for key, value in self._metadata.custom.items():
                if value:
                    meta = etree.Element(
                        '{http://www.idpf.org/2007/opf}meta',
                        nsmap={'opf': 'http://www.idpf.org/2007/opf'}
                    )
                    meta.set('property', f'custom:{key}')
                    meta.text = value
                    metadata_elem.append(meta)

            # Salva
            tree.write(
                str(self._opf_path),
                encoding='utf-8',
                xml_declaration=True,
                pretty_print=True
            )

            return True

        except Exception as e:
            raise Exception(f"Errore nell'aggiornamento del OPF: {e}")

    # ======================================================================
    # Salvataggio
    # ======================================================================

    def save(self, output_path: str | Path) -> bool:
        """Salva il libro modificato in un nuovo file. Non tocca l'originale."""
        if not self._is_loaded or not self._temp_dir:
            raise Exception("Libro non caricato")

        output_path = Path(output_path)

        try:
            self._update_opf_metadata()

            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                temp_path = Path(self._temp_dir)
                for file_path in temp_path.rglob('*'):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to(temp_path))
                        zip_ref.write(file_path, arcname)

            return True

        except Exception as e:
            raise Exception(f"Errore nel salvataggio: {e}")

    # ======================================================================
    # Pulizia
    # ======================================================================

    def cleanup(self):
        """Rimuove i file temporanei."""
        if self._temp_dir and Path(self._temp_dir).exists():
            shutil.rmtree(self._temp_dir)

    def __del__(self):
        self.cleanup()

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    # ======================================================================
    # Utility
    # ======================================================================

    def get_text(self) -> str:
        """Restituisce tutto il testo del libro."""
        return '\n\n'.join(section.text for section in self.sections if section.text)

    def to_text(self, output_file: str | Path, replace: bool = False) -> bool:
        """Esporta il libro come file di testo."""
        output_file = Path(output_file)

        if output_file.exists() and not replace:
            return False

        with open(output_file, 'w', encoding='utf-8') as f:
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

            f.write("\n" + "=" * 60 + "\n")
            f.write("CONTENUTO\n")
            f.write("=" * 60 + "\n\n")

            for section in self.sections:
                if section.title:
                    f.write(f"\n--- {section.title} ---\n\n")
                f.write(section.text)
                f.write("\n\n")

        return True






# !/usr/bin/env python3

# from pathlib import Path
# from epub_manager import EpubManager

# ============================================
# Esempio di utilizzo
# ============================================
"""
test_epub_manager.py - Script di test per EpubManager
"""
def test_epub_operations(epub_path: str):
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

            # 4. Modifica metadati
            print("\n✏️ MODIFICA METADATI:")
            book.set_title('Test Titolo Modificato')
            book.set_author('Test Autore Modificato')
            book.set_custom_metadata('test_key', 'test_value')
            book.set_custom_metadata('processed_by', 'EpubManager v2.0')

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
                modified_by = test_book.get_custom_metadata('processed_by')
                print(f"  Modified by: {modified_by}")

                # Verifica che le modifiche siano state applicate
                success = (test_book.title == 'Test Titolo Modificato' and
                          test_book.author == 'Test Autore Modificato' and
                          test_book.get_custom_metadata('test_key') == 'test_value')

                if success:
                    print("  ✅ Tutte le modifiche sono state salvate correttamente!")
                else:
                    print("  ⚠️ Attenzione: Alcune modifiche potrebbero non essere state salvate")

            return True

    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Path del tuo EPUB di test
    test_epub = "/home/loreto/Downloads/test_epubs/Billionaire 02 - Miele - Meghan March.epub"

    if test_epub:
        result = test_epub_operations(test_epub)
        print("\n" + "=" * 70)
        print("✅ TEST COMPLETATO!" if result else "❌ TEST FALLITO!")
        print("=" * 70)

# ============================================
# Esempio di utilizzo
# ============================================

if __name__ == "__main__xxx":
    import sys

    # Test
    test_file = '/home/loreto/Downloads/test_epubs/Billionaire 02 - Miele - Meghan March.epub'

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
            book.set_title('Nuovo Titolo Modificato')
            book.set_author('Nuovo Autore Modificato')
            book.set_custom_metadata('processed_by', 'EpubManager v2.0')
            book.set_custom_metadata('processed_date', '2026-08-29')

            print(f"\n📖 Nuovo titolo: {book.title}")
            print(f"✍️ Nuovo autore: {book.author}")

            # Salva
            output_file = 'libro_modificato.epub'
            book.save(output_file)
            print(f"\n💾 Libro salvato in: {output_file}")

            # Esporta come testo
            book.to_text('libro_esportato.txt', replace=True)
            print("📄 Esportato come testo in: libro_esportato.txt")

    except Exception as e:
        print(f"❌ Errore: {e}")
        sys.exit(1)

    print("\n✅ Test completato con successo!")
