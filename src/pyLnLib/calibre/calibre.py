#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import json
from pathlib import Path
from datetime import datetime

class CalibreMetadataReader:
    """Lettore di metadati Calibre con campi personalizzati dinamici"""

    def __init__(self, library_path: str):
        self.library_path = Path(library_path)
        self.db_path = self.library_path / "metadata.db"

        if not self.db_path.exists():
            raise FileNotFoundError(f"Database non trovato: {self.db_path}")

        # Mappa per i campi personalizzati (verrà popolata automaticamente)
        self.custom_columns: dict[str, str] = {}
        self._load_custom_columns()

        # Campi standard
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
                    field_name = f"#{name}"
                    table_name = f"custom_column_{col_id}"
                    self.custom_columns[field_name] = table_name

        except sqlite3.OperationalError:
            # La tabella custom_columns potrebbe non esistere
            pass

    def _build_custom_subquery(self, table_name: str) -> str:
        """
        Costruisce una subquery per un campo personalizzato.
        Gestisce il fatto che la colonna potrebbe chiamarsi 'book' o 'id'
        """
        # Prova a determinare il nome della colonna
        # In Calibre, la colonna che linka al libro si chiama 'book'
        # Ma in alcune versioni potrebbe chiamarsi 'id'
        return f"""(
            SELECT value
            FROM {table_name}
            WHERE {table_name}.book = b.id
            LIMIT 1
        )"""

    def get_custom_fields(self) -> list[str]:
        """Restituisce la lista dei campi personalizzati disponibili"""
        return list(self.custom_columns.keys())

    def get_books(self, fields: list[str] | None = None) -> list[dict[str, any]]:
        """
        Recupera i libri con i campi specificati.
        """
        if fields is None:
            fields = ['id', 'title', 'authors', 'publisher', 'isbn']

        # Costruisci la SELECT
        select_parts = []
        select_parts.append("b.id AS _id")

        for field in fields:
            if field.startswith('#'):
                # Campo personalizzato
                if field in self.custom_columns:
                    table_name = self.custom_columns[field]
                    # Usa la subquery generica
                    select_parts.append(self._build_custom_subquery(table_name) + f' AS "{field}"')
                else:
                    print(f"⚠️  Campo personalizzato '{field}' non riconosciuto")
                    print(f"   Campi disponibili: {', '.join(self.get_custom_fields())}")
            elif field in self.field_queries:
                select_parts.append(f"{self.field_queries[field]} AS {field}")
            else:
                print(f"⚠️  Campo '{field}' non riconosciuto")

        # Costruisci la query finale
        query = f"""
            SELECT {', '.join(select_parts)}
            FROM books b
            ORDER BY b.id
        """

        # DEBUG: stampa la query
        # print("\n🔍 DEBUG - Query SQL:")
        # print(query)
        # print()

        results: list[dict[str, any]] = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query)

                for row in cursor.fetchall():
                    book_dict = dict(row)
                    if '_id' in book_dict:
                        if 'id' not in book_dict:
                            book_dict['id'] = book_dict.pop('_id')
                        else:
                            del book_dict['_id']
                    results.append(book_dict)
        except sqlite3.OperationalError as e:
            print(f"❌ Errore SQL: {e}")
            print("\n   Query che ha causato l'errore:")
            print(query)
            raise

        return results

    def get_book_by_id(self, book_id: int) -> dict[str, any] | None:
        """Recupera un singolo libro per ID"""
        books = self.get_books()
        for book in books:
            if book.get('id') == book_id:
                return book
        return None

    def get_all_ids(self) -> list[int]:
        """Recupera tutti gli ID dei libri"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id FROM books ORDER BY id")
            return [row[0] for row in cursor.fetchall()]

    def get_book_file_path(self, book_metadata: dict[str, any]) -> Path | None:
        """Trova il percorso del file ebook"""
        if 'path' not in book_metadata:
            return None

        book_path = self.library_path / book_metadata['path']

        if book_path.exists():
            for ext in ['.epub', '.mobi', '.pdf', '.azw3', '.txt']:
                for file in book_path.glob(f"*{ext}"):
                    return file

        return None

    def get_available_fields(self) -> dict[str, str]:
        """Restituisce tutti i campi disponibili con una breve descrizione"""
        return {
            **self.field_queries,
            **{k: f"Campo personalizzato ({self.custom_columns[k]})"
               for k in self.custom_columns}
        }


# ============================================================
# VERSIONE ALTERNATIVA: Query separata per campi personalizzati
# ============================================================

class CalibreMetadataReaderAlt:
    """
    Versione alternativa che legge i campi personalizzati con una query separata.
    Questo è più lento ma più robusto.
    """

    def __init__(self, library_path: str):
        self.library_path = Path(library_path)
        self.db_path = self.library_path / "metadata.db"

        if not self.db_path.exists():
            raise FileNotFoundError(f"Database non trovato: {self.db_path}")

        self.custom_columns: dict[str, str] = {}
        self._load_custom_columns()

        # Campi standard (stessi di sopra)
        self.field_queries = {
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

    def _load_custom_columns(self) -> None:
        """Carica automaticamente i campi personalizzati"""
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
            pass

    def get_custom_fields(self) -> list[str]:
        return list(self.custom_columns.keys())

    def get_books(self, fields: list[str] | None = None) -> list[dict[str, any]]:
        """Versione robusta con query separate"""
        if fields is None:
            fields = ['id', 'title', 'authors']

        # Separa campi standard e personalizzati
        standard_fields = [f for f in fields if not f.startswith('#')]
        custom_fields = [f for f in fields if f.startswith('#')]

        # Costruisci query per campi standard
        select_parts = ["b.id AS _id"]
        for field in standard_fields:
            if field in self.field_queries:
                select_parts.append(f"{self.field_queries[field]} AS {field}")

        query = f"""
            SELECT {', '.join(select_parts)}
            FROM books b
            ORDER BY b.id
        """

        results: list[dict[str, any]] = []

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Ottieni i dati base
            cursor = conn.execute(query)
            for row in cursor.fetchall():
                book_dict = dict(row)
                if '_id' in book_dict:
                    book_dict['id'] = book_dict.pop('_id')
                results.append(book_dict)

            # Per ogni campo personalizzato, fai una query separata
            for field in custom_fields:
                if field in self.custom_columns:
                    table_name = self.custom_columns[field]
                    try:
                        # Prova con 'book'
                        cursor = conn.execute(f"""
                            SELECT book, value
                            FROM {table_name}
                        """)
                    except sqlite3.OperationalError:
                        try:
                            # Prova con 'id'
                            cursor = conn.execute(f"""
                                SELECT id, value
                                FROM {table_name}
                            """)
                        except sqlite3.OperationalError:
                            print(f"⚠️  Impossibile leggere la tabella {table_name}")
                            continue

                    # Costruisci un dizionario per lookup veloce
                    lookup = {row[0]: row[1] for row in cursor.fetchall()}

                    # Aggiungi il campo a ogni libro
                    for book in results:
                        book[field] = lookup.get(book.get('id'))

        return results


# ============================================================
# MAIN
# ============================================================

def main(calibre_path: str | None = None) -> None:
    if calibre_path is None:
        calibre_path = "/home/loreto/filu/Library"  # MODIFICA QUI

    print("=" * 70)
    print("📚 LETTURA METADATI DA CALIBRE")
    print("=" * 70)

    # Usa la versione alternativa (più robusta)
    reader = CalibreMetadataReaderAlt(calibre_path)

    print("\n📋 Campi disponibili:")
    print("\n   Campi standard:")
    for field in sorted(reader.field_queries.keys()):
        print(f"     - {field}")

    print("\n   Campi personalizzati:")
    for field in sorted(reader.get_custom_fields()):
        print(f"     - {field}")

    # ===== 1. Tutti i libri =====
    print("\n" + "=" * 70)
    print("1️⃣  Tutti i libri (campi principali):")
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
        print(f"   Tags: {book.get('tags', 'N/D')}")

        # Mostra i campi personalizzati
        for field in reader.get_custom_fields():
            if book.get(field):
                print(f"   {field}: {book.get(field)}")
        print()

    # ===== 2. Esporta =====
    print("=" * 70)
    print("2️⃣  Esportazione in JSON:")
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

    print("\n" + "=" * 70)
    print("✅ Completato!")
    print("=" * 70)



if __name__ == "__main__":
    CALIBRE_PATH = "/home/loreto/filu/ln-eBooks/lnLibraries/Others"  # MODIFICA QUI
    CALIBRE_PATH = "/home/loreto/filu/ln-eBooks/lnLibraries/allInOne"  # MODIFICA QUI
    main(calibre_path=CALIBRE_PATH)



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


def vedere_i_campi_disponibili();
    # Per vedere tutti i campi disponibili
    reader = CalibreMetadataReaderAlt("/home/loreto/filu/Library")
    print(reader.get_available_fields())

    # Per ottenere solo alcuni campi
    campi_ridotti = ['id', 'title', '#Status']
    books = reader.get_books(campi_ridotti)

    # Per filtrare per status
    books_letti = [b for b in books if b.get('#Status') == 'Letto']
