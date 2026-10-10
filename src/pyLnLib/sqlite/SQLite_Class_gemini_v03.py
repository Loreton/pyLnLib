import sqlite3
from _collections_abc import Sequence

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT  NOT NULL,
    author TEXT,
    title TEXT,
    status TEXT DEFAULT NULL,
    tipologia TEXT,
    narrante TEXT,
    language TEXT,
    word_count INTEGER,
    file_hash TEXT,
    file_size INTEGER,
    topologia TEXT DEFAULT NULL,
    commento TEXT DEFAULT NULL,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(author, title),
    UNIQUE(file_hash),
    UNIQUE(path)
);
"""



class Table:

    def __init__(self, db_connection: sqlite3.Connection, table_name: str):
        self.conn = db_connection
        self.name = table_name
        self.struct_dict: dict[str, dict[str, object]] = {}
        self._load_structure()

    def _load_structure(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info('{self.name}')")
        rows = cursor.fetchall()

        self.struct_dict = {
            row["name"]: {
                "cid": row["cid"],
                "type": row["type"],
                "notnull": bool(row["notnull"]),
                "default_value": row["dflt_value"],
                "pk": bool(row["pk"]),
            }
            for row in rows
        }

    def _run_query(
        self, sql: str, params: list[object], fExecute: bool
    ) -> int | None:
        """Helper interno per gestire l'esecuzione o il dry-run (fExecute=False)."""
        if not fExecute:
            print("\n[DRY-RUN / NO-EXECUTE]")
            print(f"SQL    : {sql.strip()}")
            print(f"PARAMS : {params}\n")
            return None

        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        self.conn.commit()
        return cursor.lastrowid

    def insert(
        self, data: dict[str, object], fExecute: bool = True
    ) -> int | None:
        """Inserimento semplice."""
        if not data:
            return None

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        sql = f"INSERT INTO {self.name} ({columns}) VALUES ({placeholders})"

        return self._run_query(sql, list(data.values()), fExecute)

    def upsert(
        self,
        data: dict[str, object],
        conflict_target: str | Sequence[str] = ("author", "title"),
        fExecute: bool = True,
    ) -> int | None:
        """Upsert supportando colonne singole o target compositi (es.

        ('author', 'title')).
        """
        if isinstance(conflict_target, str):
            target_cols = [conflict_target]
            target_str = conflict_target
        else:
            target_cols = list(conflict_target)
            target_str = ", ".join(target_cols)

        # Verifica che i campi di conflitto siano presenti nei dati
        for col in target_cols:
            if col not in data:
                raise ValueError(
                    f"Colonna di conflitto '{col}' mancante nei dati forniti."
                )

        columns = list(data.keys())
        cols_str = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(columns))

        # Escludiamo le colonne del vincolo di conflitto dall'UPDATE
        update_cols = [c for c in columns if c not in target_cols]

        if update_cols:
            update_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)
            on_conflict = (
                f"ON CONFLICT({target_str}) DO UPDATE SET {update_clause}"
            )
        else:
            on_conflict = f"ON CONFLICT({target_str}) DO NOTHING"

        sql = f"INSERT INTO {self.name} ({cols_str}) VALUES ({placeholders}) {on_conflict}"

        return self._run_query(sql, list(data.values()), fExecute)


class Database:
    """Classe principale per la connessione e la gestione dello schema."""

    def __init__(self, db_path: str, schema_sql: str | None = None):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._tables: dict[str, Table] = {}

        # 1. Inizializza il DB se viene passato uno schema
        if schema_sql:
            self._init_schema(schema_sql)

    def _init_schema(self, schema_sql: str) -> None:
        """Esegue le istruzioni DDL per creare le tabelle iniziali."""
        cursor = self.conn.cursor()
        cursor.executescript(schema_sql)
        self.conn.commit()

    def table(self, table_name: str) -> Table:
        """Ritorna l'istanza della classe Table per la tabella richiesta."""
        if table_name not in self._tables:
            self._tables[table_name] = Table(self.conn, table_name)
        return self._tables[table_name]

    def __getitem__(self, table_name: str) -> Table:
        return self.table(table_name)

    def close(self) -> None:
        self.conn.close()

































def test_01(db_path: str):
    # Inizializzazione DB con schema
    db = Database(db_path, schema_sql=SCHEMA_SQL)
    books = db["books"]

    # Punto 5: Verifica tipo colonna dalla struttura dinamica
    if books.struct_dict["author"]["type"] == "TEXT":
        print("La colonna 'author' è di tipo TEXT")

    books = db["books"]


    # Punto 2: Inserimento parziale (solo alcuni campi)
    book_id = books.insert(
        {
            "path": "/books/python_guide.epub",
            "title": "Guida a Python 3.14",
            "author": "Guido van Rossum",
            "word_count": 10000,
        }
    )
    print(f"Inserito libro con ID: {book_id}")


    # Viene creato il nuovo record con ID 2
    book_id = books.insert(
        {
            "path": "/libri/dune.epub",
            "title": "Dune",
            "author": "Frank Herbert",
            "word_count": 110000,
        }
    )
    print(f"Inserito libro con ID: {book_id}")


    # Il path esiste già: aggiorna solo status e word_count
    book_id = books.upsert(
        {
            "path": "/libri/dune.epub", # colonna di conflitto
            "title": "Dune",
            "author": "Frank Herbert",
            "status": "letto",
            "word_count": 180000,
        }
    )
    print(f"updated libro con ID: {book_id}")


def test_02(db_path: str):
    db = Database(db_path, schema_sql=SCHEMA_SQL)
    books = db["books"]

    # 1. Test fExecute=False (Dry-Run: Stampa solo la query senza modificare il DB)
    book_id = books.upsert(
        {
            "author": "George Orwell",
            "title": "1984",
            "path": "/books/1984.epub",
            "status": "da leggere",
        },
        conflict_target=("author", "title"),
        fExecute=False,  # <--- Non esegue la query
    )
    print(f"updated libro con ID: {book_id}")

    # 2. Inserimento Reale (Chave composita author + title)
    book_id = books.upsert(
        {
            "author": "George Orwell",
            "title": "1984",
            "path": "/books/1984.epub",
            "status": "in lettura",
        },
        conflict_target=("author", "title"),
        fExecute=True,
    )
    print(f"updated libro con ID: {book_id}")

    # 3. Upsert su chiave singola (file_hash)
    book_id = books.upsert(
        {
            "file_hash": "a1b2c3d4e5",
            "path": "/books/1984_v2.epub",
            "word_count": 88000,
        },
        conflict_target="file_hash",
        fExecute=True,
    )
    print(f"updated libro con ID: {book_id}")



if __name__ == "__main__":
    # test_01('/tmp/library.db')
    test_02('/tmp/library.db')
