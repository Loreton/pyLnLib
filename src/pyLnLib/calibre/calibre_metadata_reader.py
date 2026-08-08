#!/usr/bin/env python

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from pyLnLib.logger import get_logger
from pyLnLib.emoji import get_emoji
from pyLnLib.lndict import lnDict
E=get_emoji()


@dataclass(frozen=True)  # "frozen" rende i colori non modificabili per errore
class BookData:
    id: int


class CalibreMetadataReader:
    """
    Lettore di metadati Calibre.
    Versione robusta che gestisce i campi personalizzati con query separate.
    """

    def __init__(self, library_path: str):
        self.library_path = Path(library_path)
        self.db_path = self.library_path / "metadata.db"
        self.logger=get_logger()

        if not self.db_path.exists():
            raise FileNotFoundError(f"Database non trovato: {self.db_path}")

        # Carica i campi personalizzati
        self.custom_columns: dict[str, str] = {}
        self._load_custom_columns()

        # Campi standard con le relative query
        self.field_queries: dict[str, str] = {
            'id': 'b.id',
            'title': 'b.title',
            'sort': 'b.sort',
            'timestamp': 'b.timestamp',
            'pubdate': 'b.pubdate',
            'series_index': 'b.series_index',
            'author_sort': 'b.author_sort',
            'path': 'b.path',
            'uuid': 'b.uuid',
            'has_cover': 'b.has_cover',
            'last_modified': 'b.last_modified',
            'authors': """(SELECT group_concat(a.name, ', ')
                          FROM books_authors_link bal
                          JOIN authors a ON bal.author = a.id
                          WHERE bal.book = b.id)""",
            'publisher': """(SELECT group_concat(p.name, ', ')
                           FROM books_publishers_link bpl
                           JOIN publishers p ON bpl.publisher = p.id
                           WHERE bpl.book = b.id)""",
            'isbn': """(SELECT val
                       FROM identifiers
                       WHERE identifiers.book = b.id AND type = 'isbn'
                       LIMIT 1)""",
            'identifiers': """(SELECT group_concat(type || ': ' || val, ', ')
                             FROM identifiers
                             WHERE identifiers.book = b.id)""",
            'tags': """(SELECT group_concat(t.name, ', ')
                       FROM books_tags_link btl
                       JOIN tags t ON btl.tag = t.id
                       WHERE btl.book = b.id)""",
            'series': """(SELECT s.name
                         FROM books_series_link bsl
                         JOIN series s ON bsl.series = s.id
                         WHERE bsl.book = b.id
                         LIMIT 1)""",
            'language': """(SELECT lang_code
                           FROM books_languages_link bll
                           WHERE bll.book = b.id
                           LIMIT 1)""",
            'rating': """(SELECT r.name
                         FROM books_ratings_link brl
                         JOIN ratings r ON brl.rating = r.id
                         WHERE brl.book = b.id
                         LIMIT 1)""",
        }



    # ================================
    def _load_custom_columns(self) -> None:
        """Carica automaticamente i campi personalizzati dal database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, name
                    FROM custom_columns
                    ORDER BY id
                """)
                for col_id, name in cursor.fetchall():
                    self.custom_columns[f"#{name}"] = f"custom_column_{col_id}"
        except sqlite3.OperationalError:
            # La tabella custom_columns potrebbe non esistere
            pass



    # ================================
    def get_custom_fields(self) -> list[str]:
        """Restituisce la lista dei campi personalizzati disponibili"""
        return list(self.custom_columns.keys())



    # ================================
    def get_available_fields(self) -> dict[str, str]:
        """Restituisce tutti i campi disponibili con una breve descrizione"""
        return {
            **self.field_queries,
            **{k: f"Campo personalizzato ({self.custom_columns[k]})"
               for k in self.custom_columns}
        }



    # ================================
    def _fetch_books(self, fields: list[str] | None = None) -> list[dict[str, any]]:
        """Recupera i libri come lista (logica comune)"""
        if fields is None:
            fields = ['id', 'title', 'authors']

        standard_fields = [f for f in fields if not f.startswith('#')]
        custom_fields = [f for f in fields if f.startswith('#')]

        select_parts = ["b.id AS _id"]
        for field in standard_fields:
            if field in self.field_queries:
                select_parts.append(f"{self.field_queries[field]} AS {field}")
            else:
                self.logger.warning(f"Campo standard '{field}' non riconosciuto")

        query = f"SELECT {', '.join(select_parts)} FROM books b ORDER BY b.id"
        results: list[dict[str, any]] = []

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)

            for row in cursor.fetchall():
                book_dict = lnDict(row)
                if '_id' in book_dict:
                    book_dict['id'] = book_dict.pop('_id')
                results.append(book_dict)

            # Campi personalizzati e file info
            for field in custom_fields:
                if field in self.custom_columns:
                    self._add_custom_field_to_books(conn, results, field)
                else:
                    self.logger.warning(f"Campo personalizzato '{field}' non riconosciuto")

            # Aggiungi info file a tutti i libri
            for book in results:
                exists, path = self._get_book_file_path(book)
                book["file_exists"] = exists
                book["file_path"] = path

        return results

    # ================================
    def _add_custom_field_to_books(self, conn, books: list, field: str) -> None:
        """Aggiunge un campo personalizzato a tutti i libri"""
        table_name = self.custom_columns[field]
        try:
            cursor = conn.execute(f"SELECT book, value FROM {table_name}")
            lookup = {row[0]: row[1] for row in cursor.fetchall()}
        except sqlite3.OperationalError:
            try:
                cursor = conn.execute(f"SELECT id, value FROM {table_name}")
                lookup = {row[0]: row[1] for row in cursor.fetchall()}
            except sqlite3.OperationalError as e:
                self.logger.warning(f"Impossibile leggere {table_name}: {e}")
                return

        for book in books:
            book[field] = lookup.get(book.get('id'))




    # ================================
    def get_books(self, fields: list[str] | None = None) -> list[dict[str, any]]:
        return self._fetch_books(fields)




    # ================================
    def get_books_dict(self, fields: list[str] | None = None) -> dict[str, any]:
        books = self._fetch_books(fields)
        return lnDict({str(book['id']): book for book in books})



    # ================================
    def get_book_by_id(self, book_id: int, fields: list[str] | None = None) -> dict[str, any] | None:
        if fields is None:
            fields = ['id', 'title', 'authors', 'publisher', 'isbn', 'pubdate', 'series', 'tags', 'path']
            fields.extend(self.get_custom_fields())

        books_dict = self.get_books_dict(fields)
        return books_dict.get(str(book_id))

    # ================================
    # def get_book_by_id(self, book_id: int, fields: list[str] | None = None) -> dict[str, any] | None:
    #     """Recupera un singolo libro per ID"""
    #     if fields is None:
    #         fields = ['id', 'title', 'authors', 'publisher', 'isbn', 'pubdate', 'series', 'tags', 'path']
    #         fields.extend(self.get_custom_fields())

    #     books = self.get_books(fields)
    #     for book in books:
    #         if book.get('id') == book_id:
    #             return book
    #     return None




    # ================================
    def get_all_ids(self) -> list[int]:
        """Recupera tutti gli ID dei libri"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id FROM books ORDER BY id")
            return [row[0] for row in cursor.fetchall()]




    # ================================
    def _get_book_file_path(self, book_metadata: dict[str, any], debug: bool = False) -> tuple[bool, Path | None]:
    # def get_book_file_path(self, book_metadata: dict[str, any], debug: bool = False) -> tuple[bool, Path|str|None]:
        """
        Trova il percorso del file ebook.

        Args:
            book_metadata: Dizionario con i metadati del libro (deve contenere 'path' e 'id')
            debug: Se True, stampa informazioni di debug
        """
        file_exists: bool = False
        file_path: Path|str|None = None
        if 'path' not in book_metadata:
            # if debug:
            self.logger.warning(f"Nessun campo 'path' nel libro {book_metadata.get('id')}")
            return file_exists, file_path

        # Il path in Calibre è relativo alla libreria
        rel_path = book_metadata['path']
        book_path = self.library_path / rel_path
        dir_exists = book_path.exists()

        self.logger.debug(f"{E.folder} Exists?        {dir_exists}")
        self.logger.debug(f"{E.folder} Path relativo: {rel_path}")
        self.logger.debug(f"{E.folder} Path assoluto: {book_path}")

        if not dir_exists:
            self.logger.warning("la cartella:\n%s\nnon esiste!", book_path)
            parent = book_path.parent
            if parent.exists():
                self.logger.warning(f"{E.folder} Contenuto di {parent}:")
                for item in parent.iterdir():
                    self.logger.warning(f"\t- {item.name}")
            return file_exists, file_path

        # Cerca file con estensioni comuni
        estensioni = ['.epub', '.mobi', '.pdf', '.azw3', '.txt', '.azw', '.prc', '.docx']
        for ext in estensioni:
            files = list(book_path.glob(f"*{ext}"))
            if files:
                self.logger.success(f"Trovato: {files[0]}")
                return True, files[0]


        # Se non trova con le estensioni, cerca qualsiasi file
        all_files = list(book_path.iterdir())
        for file in all_files:
            if file.is_file() and file.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.opf', '.xml']:
                if debug:
                    self.logger.notify(f"Trovato possibile ebook: {file}")
                return True, file  # <-- CORRETTO: restituisce True e il file

        return False, None






















# ============================================================
# UTILIZZO
# ============================================================

def test_calibre(calibre_path: str | None = None) -> None:
    if calibre_path is None:
        calibre_path = "/home/loreto/filu/Library"  # MODIFICA QUI

    print("=" * 70)
    print("📚 LETTURA METADATI DA CALIBRE")
    print("=" * 70)

    try:
        reader = CalibreMetadataReader(calibre_path)
    except FileNotFoundError as e:
        print(f"❌ Errore: {e}")
        return

    # Mostra campi disponibili
    print("\n📋 Campi disponibili:")
    print("\n   Campi standard:")
    for field in sorted(reader.field_queries.keys()):
        print(f"     - {field}")

    print("\n   Campi personalizzati:")
    for field in sorted(reader.get_custom_fields()):
        print(f"     - {field}")

    # ===== 1. Tutti i libri =====
    print("\n" + "=" * 70)
    print("1️⃣  Tutti i libri:")
    print("=" * 70)

    campi_principali = [
        'id',
        'title',
        'authors',
        'publisher',
        'isbn',
        'pubdate',
        'series',
        'tags',
        'path',
        '#Status',
        '#ReadDate',
        '#Comments',
        '#Tipologia'
    ]

    books = reader.get_books(campi_principali)
    print(f"\n📚 Trovati {len(books)} libri\n")

    # Mostra i primi 3
    for i, book in enumerate(books[:3], 1):
        print(f"📖 Libro {i}: {book.get('title', 'Senza titolo')}")
        print(f"   Autori: {book.get('authors', 'N/D')}")
        print(f"   Editore: {book.get('publisher', 'N/D')}")
        print(f"   ISBN: {book.get('isbn', 'N/D')}")
        print(f"   Path: {book.get('path', 'N/D')}")

        for field in reader.get_custom_fields():
            if book.get(field):
                if field == '#Comments' and len(str(book[field])) > 100:
                    print(f"   {field}: {str(book[field])[:100]}...")
                else:
                    print(f"   {field}: {book.get(field)}")
        print()

    # ===== 2. Dettaglio libro specifico =====
    print("=" * 70)
    print("2️⃣  Dettaglio libro (ID 1):")
    print("=" * 70)

    book = reader.get_book_by_id(1)
    if book:
        for key, value in book.items():
            if value:
                if key == '#Comments' and isinstance(value, str) and len(value) > 200:
                    print(f"   {key}: {value[:200]}...")
                else:
                    print(f"   {key}: {value}")
    else:
        print("   ❌ Libro con ID 1 non trovato")
        print("   💡 I libri partono da ID 1? Vediamo i primi ID:")
        first_ids = reader.get_all_ids()[:5]
        print(f"   📌 Primi ID disponibili: {first_ids}")

    # ===== 3. Esporta in JSON =====
    print("\n" + "=" * 70)
    print("3️⃣  Esportazione in JSON:")
    print("=" * 70)

    export_file = Path("metadati_export.json")

    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode('utf-8', errors='ignore')
        raise TypeError(f"Type {type(obj)} not serializable")

    try:
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(books, f, indent=2, ensure_ascii=False, default=json_serializer)
        print(f"   ✅ Dati esportati in: {export_file}")
        print(f"   📏 Dimensione: {export_file.stat().st_size / 1024:.1f} KB")
    except Exception as e:
        print(f"   ❌ Errore nell'esportazione: {e}")

    # ===== 4. Percorsi file con DEBUG =====
    print("\n" + "=" * 70)
    print("4️⃣  Debug percorsi file (primi 2 libri):")
    print("=" * 70)

    for book in books[:2]:
        print(f"\n📁 Verifica per: {book.get('title')}")
        file_path = reader.get_book_file_path(book, debug=True)
        if file_path:
            print(f"   ✅ FILE TROVATO: {file_path}")
        else:
            print(f"   ❌ Nessun file trovato")

    # ===== 5. Statistiche =====
    print("\n" + "=" * 70)
    print("5️⃣  Statistiche:")
    print("=" * 70)

    # Conta libri per Status (gestendo i None)
    status_count: dict[str, int] = {}
    for book in books:
        status = book.get('#Status')
        if status is None:
            status = 'Senza status'
        status_count[status] = status_count.get(status, 0) + 1

    print("\n   📊 Libri per Status:")
    # Ordina mettendo 'Senza status' per ultimo
    for status, count in sorted(status_count.items(), key=lambda x: (x[0] == 'Senza status', x[0])):
        print(f"     - {status}: {count}")

    # Conta libri per Tipologia (gestendo i None)
    tipologia_count: dict[str, int] = {}
    for book in books:
        tipologia = book.get('#Tipologia')
        if tipologia is None:
            tipologia = 'Senza tipologia'
        tipologia_count[tipologia] = tipologia_count.get(tipologia, 0) + 1

    print("\n   📊 Libri per Tipologia:")
    for tipologia, count in sorted(tipologia_count.items(), key=lambda x: (x[0] == 'Senza tipologia', x[0])):
        print(f"     - {tipologia}: {count}")

    # Libri con file
    print("\n   📊 Verifica file (primi 20 libri):")
    with_file = 0
    for book in books[:20]:
        if reader.get_book_file_path(book):
            with_file += 1
    print(f"     Primi 20 libri: {with_file}/20 hanno un file associato")

    print("\n" + "=" * 70)
    print("✅ Completato!")
    print("=" * 70)


if __name__ == "__main__":
    CALIBRE_PATH = "/home/loreto/filu/ln-eBooks/lnLibraries/Others"  # MODIFICA QUI
    CALIBRE_PATH = "/home/loreto/filu/ln-eBooks/lnLibraries/allInOne"  # MODIFICA QUI
    test_calibre(calibre_path=CALIBRE_PATH)

def come_usarlo():
    # Nel tuo programma principale
    from read_calibre_v3 import CalibreMetadataReaderAlt

    # Inizializza
    reader = CalibreMetadataReaderAlt("/home/loreto/filu/Library")

    # Ottieni i libri con i campi che ti servono
    campi = ['id', 'title', 'authors', 'path', '#Status', '#ReadDate']
    books = reader.get_books(campi)

    # Per ogni libro
    for book in books:
        # Trova il file
        file_path = reader.get_book_file_path(book)
        if file_path:
            # Estrai il testo (con la tua funzione)
            testo = estrai_testo(file_path)

            # Usa i metadati per arricchire l'output
            salva_con_metadati(
                testo=testo,
                titolo=book['title'],
                autore=book['authors'],
                status=book.get('#Status', ''),
                read_date=book.get('#ReadDate', '')
            )


def vedere_i_campi_disponibili():
    # Per vedere tutti i campi disponibili
    reader = CalibreMetadataReaderAlt("/home/loreto/filu/Library")
    print(reader.get_available_fields())

    # Per ottenere solo alcuni campi
    campi_ridotti = ['id', 'title', '#Status']
    books = reader.get_books(campi_ridotti)

    # Per filtrare per status
    books_letti = [b for b in books if b.get('#Status') == 'Letto']
