import sqlite3

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
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
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class Table:
    """Gestisce le operazioni su una specifica tabella."""

    def __init__(self, db_connection: sqlite3.Connection, table_name: str):
        self.conn = db_connection
        self.name = table_name
        self.struct_dict: dict[str, dict[str, object]] = {}
        self._load_structure()

    def _load_structure(self) -> None:
        """Carica la struttura della tabella in self.struct_dict.

        Esempio di struttura generata:
        self.struct_dict['author']['type'] -> 'TEXT'
        self.struct_dict['id']['pk'] -> 1
        """
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

    def insert(self, data: dict[str, object]) -> int | None:
        """Inserisce un record passando solo le colonne desiderate.

        I campi non passati assumeranno il valore DEFAULT o NULL.
        """
        if not data:
            return None

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        sql = f"INSERT INTO {self.name} ({columns}) VALUES ({placeholders})"

        cursor = self.conn.cursor()
        cursor.execute(sql, list(data.values()))
        self.conn.commit()
        return cursor.lastrowid


    def upsert( self, data: dict[str, object], conflict_column: str = "path" ) -> int | None:
        """Inserisce un record o aggiorna solo i campi forniti in caso di conflitto.

        :param data: Dizionario con i dati da inserire/aggiornare.
        :param conflict_column: Nome della colonna con vincolo UNIQUE (es.
        'path').
        """
        if not data or conflict_column not in data:
            raise ValueError( f"I dati devono contenere la colonna di conflitto '{conflict_column}'." )

        columns = list(data.keys())
        cols_str = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(columns))

        # Prepariamo la clausola UPDATE escludendo la colonna di conflitto stessa
        update_cols = [col for col in columns if col != conflict_column]

        if update_cols:
            # es. "author = EXCLUDED.author, title = EXCLUDED.title"
            update_clause = ", ".join( f"{col} = EXCLUDED.{col}" for col in update_cols )
            on_conflict_stmt = f"ON CONFLICT({conflict_column}) DO UPDATE SET {update_clause}"
        else:
            # Se viene passato solo il path, non fa nulla se esiste già
            on_conflict_stmt = f"ON CONFLICT({conflict_column}) DO NOTHING"

        sql = f"""
            INSERT INTO {self.name} ({cols_str})
            VALUES ({placeholders})
            {on_conflict_stmt}
        """

        cursor = self.conn.cursor()
        cursor.execute(sql, list(data.values()))
        self.conn.commit()

        return cursor.lastrowid



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


if __name__ == "__main__":

    # Inizializzazione DB con schema
    db = Database("/tmp/library.db", schema_sql=SCHEMA_SQL)
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
