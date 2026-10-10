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


# CREATE TABLE IF NOT EXISTS tracked_words (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     word TEXT UNIQUE NOT NULL,
#     original_word TEXT,
#     added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
#
# CREATE TABLE IF NOT EXISTS occurrences (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     book_id INTEGER NOT NULL,
#     word_id INTEGER NOT NULL,
#     count INTEGER NOT NULL,
#     FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
#     FOREIGN KEY (word_id) REFERENCES tracked_words(id) ON DELETE CASCADE,
#     UNIQUE(book_id, word_id)
# );
# CREATE INDEX IF NOT EXISTS idx_books_path ON books(path);
# CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
# CREATE INDEX IF NOT EXISTS idx_occurrences_book ON occurrences(book_id);
# CREATE INDEX IF NOT EXISTS idx_occurrences_word ON occurrences(word_id);
# CREATE INDEX IF NOT EXISTS idx_occurrences_word_count ON occurrences(word_id, count);



class Table:
    """Rappresenta una singola tabella e fornisce i metodi CRUD di base."""

    def __init__(self, db_connection: sqlite3.Connection, table_name: str):
        self.conn = db_connection
        self.name = table_name

    def insert(self, data: dict[str, object]) -> int:
        """Inserisce un dizionario di dati (chiave=colonna, valore=valore)."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        sql = f"INSERT INTO {self.name} ({columns}) VALUES ({placeholders})"

        cursor = self.conn.cursor()
        cursor.execute(sql, list(data.values()))
        self.conn.commit()
        return cursor.lastrowid

    def get_all(self) -> list[dict[str, object]]:
        """Recupera tutti i record dalla tabella come lista di dizionari."""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {self.name}")
        rows = cursor.fetchall()
        # Converte le righe sqlite3.Row in dizionari Python
        return [dict(row) for row in rows]

    def find_by(self, column: str, value: object) -> list[dict[str, object]]:
        """Cerca i record che soddisfano la condizione colonna = valore."""
        cursor = self.conn.cursor()
        sql = f"SELECT * FROM {self.name} WHERE {column} = ?"
        cursor.execute(sql, (value,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def delete(self, row_id: int, id_column: str = "id") -> bool:
        """Elimina un record in base all'ID."""
        cursor = self.conn.cursor()
        sql = f"DELETE FROM {self.name} WHERE {id_column} = ?"
        cursor.execute(sql, (row_id,))
        self.conn.commit()
        return cursor.rowcount > 0


class Database:
    """Classe principale che gestisce la connessione e istanzia le tabelle."""

    def __init__(self, db_path: str = ":memory:"):
        # row_factory permette di accedere ai dati delle query sia per indice che per nome colonna
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._tables: dict[str, Table] = {}

    def table(self, table_name: str) -> Table:
        """Restituisce un'istanza di Table per il nome specificato (con caching)."""
        if table_name not in self._tables:
            self._tables[table_name] = Table(self.conn, table_name)
        return self._tables[table_name]

    def __getitem__(self, table_name: str) -> Table:
        """Permette di usare la sintassi a quadre: db['nome_tabella']"""
        return self.table(table_name)

    def close(self):
        """Chiude la connessione al database."""
        self.conn.close()


if __name__ == "__main__":
    # 1. Inizializza il database
    db = Database("mio_database.db")

    # 2. Crea le tabelle di prova se non esistono
    db.conn.execute(
        "CREATE TABLE IF NOT EXISTS utenti (id INTEGER PRIMARY KEY, nome TEXT, email TEXT)"
    )
    db.conn.execute(
        "CREATE TABLE IF NOT EXISTS prodotti (id INTEGER PRIMARY KEY, titolo TEXT, prezzo REAL)"
    )

    # 3. Ottieni le istanze delle tabelle (puoi usare db.table() o db['nome'])
    utenti = db.table("utenti")
    prodotti = db["prodotti"]  # Sintassi a quadre grazie a __getitem__

    # 4. Operazioni sulla tabella Utenti
    id_utente = utenti.insert(
        {"nome": "Mario Rossi", "email": "mario@example.com"}
    )
    print(f"Utente inserito con ID: {id_utente}")

    # 5. Operazioni sulla tabella Prodotti
    prodotti.insert({"titolo": "Tastiera", "prezzo": 49.90})

    # 6. Lettura dati
    print("Tutti gli utenti:", utenti.get_all())
    print("Cerca utente:", utenti.find_by("nome", "Mario Rossi"))

    # Chiudi la connessione alla fine
    db.close()
