#!/usr/bin/env python

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Any
from collections import defaultdict

from pyLnLib.logger import get_logger
from pyLnLib.emoji import get_emoji
from pyLnLib.lndict import lnDict

E = get_emoji()


class CalibreMetadataReader:
    """
    Lettore di metadati Calibre con accesso lazy e rilevamento duplicati.
    All'avvio carica solo gli indici (ID e autori) e rileva duplicati.
    """

    def __init__(self, library_path: str):
        """
        Args:
            library_path: Percorso della libreria Calibre
        """
        self.library_path = Path(library_path)
        self.db_path = self.library_path / "metadata.db"
        self.logger = get_logger()

        if not self.db_path.exists():
            raise FileNotFoundError(f"Database non trovato: {self.db_path}")

        # Cache e campi personalizzati
        self._cache: dict[int, dict] = {}
        self.custom_columns: dict[str, str] = {}
        self._load_custom_columns()

        # Campi standard
        self.field_queries: dict[str, str] = {}
        self._init_field_queries()

        # ===== INDICI (caricati all'avvio) =====
        self._load_indices()

        # ===== RILEVAMENTO DUPLICATI =====
        self._detect_duplicates()

    # ================================
    def _init_field_queries(self) -> None:
        """Inizializza le query per i campi standard"""
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
            'authors': self._get_authors_query(),
            'publisher': self._get_publisher_query(),
            'isbn': self._get_isbn_query(),
            'identifiers': self._get_identifiers_query(),
            'tags': self._get_tags_query(),
            'series': self._get_series_query(),
            'language': self._get_language_query(),
            'rating': self._get_rating_query(),
        }

    # ================================
    def _get_rating_query(self) -> str:
        """Recupera il rating in modo robusto"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='ratings'"
                )
                if not cursor.fetchone():
                    return "NULL AS rating"

                cursor = conn.execute("PRAGMA table_info(ratings)")
                columns = [col[1] for col in cursor.fetchall()]

                if 'name' in columns:
                    col = 'name'
                elif 'rating' in columns:
                    col = 'rating'
                elif 'value' in columns:
                    col = 'value'
                else:
                    col = 'id'

                return f"""(
                    SELECT CAST(r.{col} AS TEXT)
                    FROM books_ratings_link brl
                    JOIN ratings r ON brl.rating = r.id
                    WHERE brl.book = b.id
                    LIMIT 1
                )"""
        except sqlite3.OperationalError:
            return "NULL AS rating"

    # ================================
    def _get_authors_query(self) -> str:
        return """(SELECT group_concat(a.name, ', ')
                  FROM books_authors_link bal
                  JOIN authors a ON bal.author = a.id
                  WHERE bal.book = b.id)"""

    def _get_publisher_query(self) -> str:
        return """(SELECT group_concat(p.name, ', ')
                  FROM books_publishers_link bpl
                  JOIN publishers p ON bpl.publisher = p.id
                  WHERE bpl.book = b.id)"""

    def _get_isbn_query(self) -> str:
        return """(SELECT val
                  FROM identifiers
                  WHERE identifiers.book = b.id AND type = 'isbn'
                  LIMIT 1)"""

    def _get_identifiers_query(self) -> str:
        return """(SELECT group_concat(type || ': ' || val, ', ')
                  FROM identifiers
                  WHERE identifiers.book = b.id)"""

    def _get_tags_query(self) -> str:
        return """(SELECT group_concat(t.name, ', ')
                  FROM books_tags_link btl
                  JOIN tags t ON btl.tag = t.id
                  WHERE btl.book = b.id)"""

    def _get_series_query(self) -> str:
        return """(SELECT s.name
                  FROM books_series_link bsl
                  JOIN series s ON bsl.series = s.id
                  WHERE bsl.book = b.id
                  LIMIT 1)"""

    def _get_language_query(self) -> str:
        return """(SELECT lang_code
                  FROM books_languages_link bll
                  WHERE bll.book = b.id
                  LIMIT 1)"""

    # ================================
    def _load_indices(self) -> None:
        """Carica gli indici all'avvio"""
        self.logger.info("Caricamento indici...")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, title FROM books ORDER BY id")
            self.ids: list[int] = []
            self.titles: dict[int, str] = {}
            for book_id, title in cursor.fetchall():
                self.ids.append(book_id)
                self.titles[book_id] = title

            cursor = conn.execute("""
                SELECT a.name, bal.book
                FROM authors a
                JOIN books_authors_link bal ON bal.author = a.id
                ORDER BY a.name, bal.book
            """)

            self.authors: dict[str, list[int]] = {}
            for author, book_id in cursor.fetchall():
                if author not in self.authors:
                    self.authors[author] = []
                self.authors[author].append(book_id)

        self.logger.info(f"✅ Caricati {len(self.ids)} libri e {len(self.authors)} autori")

    # ================================
    def _detect_duplicates(self) -> None:
        """
        Rileva libri duplicati (stesso titolo).
        Popola:
        - self.duplicates: dict {title: [list of IDs]}
        - self.duplicate_report: stringa con il report
        """
        self.logger.info("Rilevamento duplicati...")

        # Raggruppa per titolo (case-insensitive)
        title_groups: dict[str, list[int]] = defaultdict(list)
        for book_id, title in self.titles.items():
            if title:
                # Normalizza il titolo: lowercase, rimuovi spazi multipli
                normalized = ' '.join(title.lower().split())
                title_groups[normalized].append(book_id)

        # Filtra solo i gruppi con più di un libro
        self.duplicates: dict[str, list[int]] = {
            title: ids for title, ids in title_groups.items()
            if len(ids) > 1
        }

        # Crea un report dettagliato
        self.duplicate_report = self._generate_duplicate_report()

        if self.duplicates:
            self.logger.warning(
                f"⚠️ Trovati {len(self.duplicates)} titoli duplicati "
                f"({sum(len(v) for v in self.duplicates.values())} libri coinvolti)"
            )
            self.logger.warning("Usa get_duplicate_report() per i dettagli")
        else:
            self.logger.info("✅ Nessun duplicato trovato")

    # ================================
    def _generate_duplicate_report(self) -> str:
        """Genera un report dettagliato dei duplicati"""
        if not self.duplicates:
            return "Nessun duplicato trovato."

        lines = [
            "=" * 70,
            f"📋 REPORT DUPLICATI ({len(self.duplicates)} titoli)",
            "=" * 70,
            ""
        ]

        for idx, (title, ids) in enumerate(sorted(self.duplicates.items()), 1):
            lines.append(f"{idx}. 📖 '{title}' ({len(ids)} copie)")
            lines.append(f"   IDs: {ids}")

            # Per ogni ID, cerca di recuperare autore e path
            for book_id in ids[:5]:  # Mostra solo i primi 5 per non essere troppo verboso
                try:
                    book = self._load_book(book_id, ['id', 'title', 'authors', 'path'])
                    if book:
                        authors = book.get('authors', 'N/D')
                        path = book.get('path', 'N/D')
                        lines.append(f"     - ID {book_id}: {authors} - {path}")
                except Exception:
                    lines.append(f"     - ID {book_id}: (impossibile caricare)")

            if len(ids) > 5:
                lines.append(f"     ... e altri {len(ids) - 5} ID")
            lines.append("")

        lines.append("=" * 70)
        lines.append("💡 Per risolvere:")
        lines.append("   1. Usa get_duplicate_ids_by_title(title) per ottenere gli ID")
        lines.append("   2. Usa Calibre per rimuovere/mergare i duplicati")
        lines.append("   3. Oppure usa get_books_by_ids(ids) per esaminarli")
        lines.append("=" * 70)

        return "\n".join(lines)

    # ================================
    def _load_custom_columns(self) -> None:
        """Carica i campi personalizzati (solo nomi)"""
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

    # ================================
    @property
    def count(self) -> int:
        """Numero totale di libri"""
        return len(self.ids)

    @property
    def has_duplicates(self) -> bool:
        """True se ci sono duplicati"""
        return bool(self.duplicates)

    @property
    def duplicate_count(self) -> int:
        """Numero di titoli duplicati"""
        return len(self.duplicates)

    # ================================
    def get_duplicate_titles(self) -> list[str]:
        """Restituisce la lista dei titoli duplicati"""
        return sorted(self.duplicates.keys())

    # ================================
    def get_duplicate_ids_by_title(self, title: str) -> list[int]:
        """
        Restituisce gli ID dei duplicati per un titolo specifico.

        Args:
            title: Titolo del libro (case-insensitive)

        Returns:
            Lista di ID o lista vuota se non trovato
        """
        normalized = ' '.join(title.lower().split())
        return self.duplicates.get(normalized, [])

    # ================================
    def get_duplicate_report(self) -> str:
        """Restituisce il report dei duplicati"""
        return self.duplicate_report

    # ================================
    def print_duplicate_report(self) -> None:
        """Stampa il report dei duplicati"""
        print(self.duplicate_report)

    # ================================
    def get_books_by_author(self, author: str) -> list[int]:
        """Restituisce tutti gli ID dei libri di un autore"""
        if author in self.authors:
            return self.authors[author].copy()

        author_lower = author.lower()
        results: list[int] = []
        for name, ids in self.authors.items():
            if author_lower in name.lower():
                results.extend(ids)

        return sorted(set(results))

    # ================================
    def get_authors(self) -> list[str]:
        """Restituisce la lista di tutti gli autori"""
        return sorted(self.authors.keys())

    # ================================
    def get_author_count(self) -> dict[str, int]:
        """Restituisce il numero di libri per autore"""
        return {author: len(ids) for author, ids in self.authors.items()}

    # ================================
    def get_book(self, book_id: int, fields: list[str] | None = None) -> dict[str, object] | None:
        """Recupera un libro con cache"""
        if book_id in self._cache:
            return self._cache[book_id]

        book = self._load_book(book_id, fields)
        if book:
            self._cache[book_id] = book
        return book

    # ================================
    def _load_book(self, book_id: int, fields: list[str] | None = None) -> dict[str, object] | None:
        """Carica un singolo libro dal database"""
        if fields is None:
            fields = ['id', 'title', 'authors', 'publisher', 'isbn', 'pubdate',
                     'series', 'series_index', 'tags', 'path', 'uuid',
                     'has_cover', 'timestamp', 'last_modified', 'language']
            fields.extend(self.get_custom_fields())

        standard_fields = [f for f in fields if not f.startswith('#')]
        custom_fields = [f for f in fields if f.startswith('#')]

        select_parts = ["b.id AS _id"]
        for field in standard_fields:
            if field in self.field_queries:
                select_parts.append(f"{self.field_queries[field]} AS {field}")

        query = f"""
            SELECT {', '.join(select_parts)}
            FROM books b
            WHERE b.id = ?
        """

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (book_id,))
            row = cursor.fetchone()

            if not row:
                self.logger.warning(f"Libro con ID {book_id} non trovato")
                return None

            book_dict = lnDict(row)
            if '_id' in book_dict:
                book_dict['id'] = book_dict.pop('_id')

            for field in custom_fields:
                if field in self.custom_columns:
                    table_name = self.custom_columns[field]
                    try:
                        cursor2 = conn.execute(f"""
                            SELECT value
                            FROM {table_name}
                            WHERE book = ?
                            LIMIT 1
                        """, (book_id,))
                        val = cursor2.fetchone()
                        book_dict[field] = val[0] if val else None
                    except sqlite3.OperationalError:
                        book_dict[field] = None
                else:
                    book_dict[field] = None

            file_exists, file_path = self.get_book_file_path(book_dict)
            book_dict["file_exists"] = file_exists
            book_dict["file_path"] = file_path
            book_dict["library_path"] = str(self.library_path)

            return book_dict

    # ================================
    def get_books_batch(self, book_ids: list[int], fields: list[str] | None = None) -> dict[int, dict[str, object]]:
        """Recupera multipli libri in una sola query"""
        if not book_ids:
            return {}

        book_ids = list(set(book_ids))

        result: dict[int, dict[str, object]] = {}
        to_load: list[int] = []

        for bid in book_ids:
            if bid in self._cache:
                result[bid] = self._cache[bid]
            else:
                to_load.append(bid)

        if not to_load:
            return result

        if fields is None:
            fields = ['id', 'title', 'authors', 'publisher', 'isbn', 'pubdate',
                     'series', 'series_index', 'tags', 'path', 'uuid',
                     'has_cover', 'timestamp', 'last_modified']
            fields.extend(self.get_custom_fields())

        standard_fields = [f for f in fields if not f.startswith('#')]
        custom_fields = [f for f in fields if f.startswith('#')]

        select_parts = ["b.id AS _id"]
        for field in standard_fields:
            if field in self.field_queries:
                select_parts.append(f"{self.field_queries[field]} AS {field}")

        placeholders = ','.join('?' * len(to_load))
        query = f"""
            SELECT {', '.join(select_parts)}
            FROM books b
            WHERE b.id IN ({placeholders})
            ORDER BY b.id
        """

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, to_load)

            books_data: dict[int, dict[str, object]] = {}
            for row in cursor.fetchall():
                book_dict = lnDict(row)
                if '_id' in book_dict:
                    book_dict['id'] = book_dict.pop('_id')
                books_data[book_dict['id']] = book_dict

            for field in custom_fields:
                if field in self.custom_columns:
                    table_name = self.custom_columns[field]
                    try:
                        cursor2 = conn.execute(f"""
                            SELECT book, value
                            FROM {table_name}
                            WHERE book IN ({placeholders})
                        """, to_load)
                        lookup = {row[0]: row[1] for row in cursor2.fetchall()}
                    except sqlite3.OperationalError:
                        lookup = {}

                    for book_id, book_dict in books_data.items():
                        book_dict[field] = lookup.get(book_id)

            for book_id, book_dict in books_data.items():
                file_exists, file_path = self.get_book_file_path(book_dict)
                book_dict["file_exists"] = file_exists
                book_dict["file_path"] = file_path
                book_dict["library_path"] = str(self.library_path)

                result[book_id] = book_dict
                self._cache[book_id] = book_dict

        return result

    # ================================
    def get_books_by_ids(self, book_ids: list[int], fields: list[str] | None = None) -> list[dict[str, object]]:
        """Recupera multipli libri come lista"""
        batch = self.get_books_batch(book_ids, fields)
        return [batch[bid] for bid in book_ids if bid in batch]

    # ================================
    def get_all_ids(self) -> list[int]:
        """Restituisce tutti gli ID"""
        return self.ids.copy()

    # ================================
    def get_custom_fields(self) -> list[str]:
        """Restituisce la lista dei campi personalizzati disponibili"""
        return list(self.custom_columns.keys())

    # ================================
    def get_available_fields(self) -> dict[str, str]:
        """Restituisce tutti i campi disponibili"""
        return {
            **self.field_queries,
            **{k: f"Campo personalizzato ({self.custom_columns[k]})"
               for k in self.custom_columns}
        }

    # ================================
    def get_book_file_path(self, book_metadata: dict[str, object]) -> tuple[bool, Path | None]:
        """Trova il percorso del file ebook"""
        if 'path' not in book_metadata:
            return False, None

        rel_path = book_metadata['path']
        if not isinstance(rel_path, str):
            return False, None

        book_path = self.library_path / rel_path

        if not book_path.exists():
            return False, None

        estensioni = ['.epub', '.mobi', '.pdf', '.azw3', '.txt', '.azw', '.prc', '.docx']
        for ext in estensioni:
            files = list(book_path.glob(f"*{ext}"))
            if files:
                return True, files[0]

        all_files = list(book_path.iterdir())
        for file in all_files:
            if file.is_file() and file.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.opf', '.xml']:
                return True, file

        return False, None

    # ================================
    def clear_cache(self) -> None:
        """Svuota la cache"""
        self._cache.clear()
        self.logger.info("Cache svuotata")

    # ================================
    def reload_indices(self) -> None:
        """Ricarica gli indici e ricalcola i duplicati"""
        self.clear_cache()
        self._load_indices()
        self._detect_duplicates()










'''
Metodi principali che puoi usare:
    reader = CalibreMetadataReader("/path/to/library")

    # Info base
    reader.count                    # numero libri
    reader.ids                      # tutti gli ID
    reader.authors                  # tutti gli autori

    # Duplicati
    reader.has_duplicates           # True/False
    reader.get_duplicate_titles()   # lista titoli duplicati
    reader.print_duplicate_report() # report dettagliato

    # Ricerche
    reader.get_books_by_author("Asimov")  # IDs per autore

    # Lettura
    reader.get_book(book_id)              # singolo libro
    reader.get_books_by_ids([1,2,3])      # multipli come lista

    # Gestione
    reader.clear_cache()            # svuota cache
    reader.reload_indices()         # ricarica tutto
Se in futuro avrai bisogno di altre funzionalità (es. ricerca per tags, filtro per data, esportazione in CSV, ecc.), fammi sapere!

Buon coding! 📚💻
'''




# ============================================================
# ESEMPIO DI UTILIZZO
# ============================================================

def calibre_test(calibre_path: str):
    # CALIBRE_PATH = "/home/loreto/filu/ln-eBooks/lnLibraries/Ale"

    print("=" * 70)
    print("📚 CALIBRE READER - ACCESSO LAZY")
    print("=" * 70)

    reader = CalibreMetadataReader(calibre_path)

    # ===== 1. Indici caricati all'avvio =====
    print("\n📊 Libreria:")
    print(f"   Totale libri: {reader.count}")
    print(f"   Totale autori: {len(reader.authors)}")
    print(f"   Primi 10 ID: {reader.ids[:10]}")
    print(f"   Duplicati trovati: {reader.duplicate_count}")

    # ===== 2. Cerca libri per autore =====
    print("\n🔍 Ricerca per autore 'Maurizio de Giovanni':")
    author_ids = reader.get_books_by_author("Giovanni")
    print(f"   Trovati {len(author_ids)} libri di Maurizio de Giovanni")
    print(f"   ID: {author_ids[:5]}...")

    # ===== 3. Leggi un singolo libro =====
    if author_ids:
        id=2
        if id>=len(author_ids):
            id = 0
        print(f"\n📖 Lettura libro ID {author_ids[id]}:")
        book = reader.get_book(author_ids[id])
        if book:
            print(f"   Titolo: {book.get('title')}")
            print(f"   Autori: {book.get('authors')}")
            print(f"   Editore: {book.get('publisher')}")
            print(f"   ISBN: {book.get('isbn')}")
            print(f"   Path: {book.get('path')}")
            print(f"   File esiste: {book.get('file_exists')}")
            if book.get('file_path'):
                print(f"   File path: {book.get('file_path')}")

    # ===== 4. Leggi multipli libri =====
    print("\n📚 Lettura batch dei primi 5 libri:")
    first_ids = reader.ids[:5]
    books = reader.get_books_by_ids(first_ids)

    for book in books:
        print(f"   - {book.get('id')}: {book.get('title')} ({book.get('authors')})")

    # ===== 5. Statistiche autori =====
    print("\n📊 Top 5 autori per numero di libri:")
    author_counts = reader.get_author_count()
    top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for author, count in top_authors:
        print(f"   - {author}: {count} libri")

    print("\n" + "=" * 70)
    print("✅ Completato!")
    print("=" * 70)


    # ===== 2. Report duplicati =====
    if reader.has_duplicates:
        print("\n📋 DUPLICATI TROVATI:")
        reader.print_duplicate_report()

        # Mostra i primi 3 titoli duplicati
        print("\n🔍 Primi 3 titoli duplicati:")
        for i, title in enumerate(reader.get_duplicate_titles()[:3], 1):
            ids = reader.get_duplicate_ids_by_title(title)
            print(f"   {i}. '{title}' -> IDs: {ids}")

        # Esempio: analizza un duplicato specifico
        if reader.get_duplicate_titles():
            first_title = reader.get_duplicate_titles()[0]
            ids = reader.get_duplicate_ids_by_title(first_title)

            print(f"\n📖 Analisi duplicato: '{first_title}'")
            books = reader.get_books_by_ids(ids)
            for book in books:
                print(f"   ID {book['id']}:")
                print(f"     Titolo: {book.get('title')}")
                print(f"     Autori: {book.get('authors')}")
                print(f"     Path: {book.get('path')}")
                print(f"     File esiste: {book.get('file_exists')}")




if __name__ == "__main__":
    calibre_test(calibre_path="/home/loreto/filu/ln-eBooks/lnLibraries/Ale")
    # detect_duplicate_test(calibre_path="/home/loreto/filu/ln-eBooks/lnLibraries/Ale")
