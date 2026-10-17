# /home/loreto/filu/Programming/gitREPO/pyLnLib/src/pyLnLib/sqlite/SQLite_Class_LnNew.py
#
# ruff: noqa: I001 Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
#

from __future__ import annotations


import sqlite3
from _collections_abc import Sequence


# from pyLnLib.colors import get_colors
from pyLnLib.logger import get_logger
from pyLnLib.system.clean_doc import clean_doc

# C=get_colors()
# logger=get_logger()

# from eBooks.input.library_scan_options import logger

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




class Database:
    """Classe principale per la connessione e la gestione dello schema."""

    def __init__(self, db_path: str, schema_sql: str | None = None):
        self.logger=get_logger()
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._tables: dict[str, Table] = {}
        self.path=db_path

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
        """Permette di usare la sintassi a quadre: db['nome_tabella']"""
        return self.table(table_name)

    def close(self) -> None:
        self.conn.close()



class Table:

    def __init__(self, db_connection: sqlite3.Connection, table_name: str):
        self.logger=get_logger()
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

    def _run_query( self, sql: str, params: list[object], fExecute: bool ) -> int | None:
        """Helper interno per gestire l'esecuzione o il dry-run (fExecute=False)."""
        if not fExecute:
            _params = '\n'.join(params)
            # self.logger.info(clean_doc(f"""[DRY-RUN / NO-EXECUTE]
            #                             SQL:\n {sql.strip()}
            #                             PARAMS:\n {_params}"
            #                 """))
            # self.logger.info(clean_doc("""[DRY-RUN / NO-EXECUTE]\n  SQL:\n%s\n  PARAMS:\n%s
            #                 """, sql.strip(), _params))
            self.logger.info("SELECT:\n%s", sql)
            self.logger.info("PARAMS:\n%s", params)
            return None


        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        self.conn.commit()
        return cursor.lastrowid

    def insert( self, data: dict[str, object], fExecute: bool = True ) -> int | None:
        """Inserimento semplice."""
        if not data:
            return None

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        sql = f"INSERT INTO {self.name} ({columns}) VALUES ({placeholders})"

        return self._run_query(sql, list(data.values()), fExecute)


    # ===============================================
    def recordPreProcess(self, data: dict[str, object], skip_nulls: bool=True) ->dict[str, object]:
        """ Provvede a ripulire il nuovo record da tutte le colonne
             che non nono presenti nella tabella.
             Compara con self.struct_dict

             :data:   Dizionario con i dati da inserire/aggiornare.
             :skip_nulls:   if True -> Ignora le colonne che hanno un valore null
             :return: record dict only with right columns
        """
        new_rec:dict[str,object] = {}
        valid_col_names=list(self.struct_dict.keys())
        for col_name, value in data.items():
            if not value and skip_nulls:
                continue
            if col_name in valid_col_names:
                new_rec[col_name] = value
            else:
                self.logger.info(f"skipping attibute: %s", col_name)

        return new_rec


    # ===============================================
    def upsert( self, data: dict[str, object],
                conflict_target: str | Sequence[str] = ("author", "title"),
                fExecute: bool = True,
            ) -> int | None:
        """Inserisce un record o aggiorna solo i campi forniti in caso di conflitto.

        :param data: Dizionario con i dati da inserire/aggiornare.
        :param conflict_column: Nome della colonna con vincolo UNIQUE (es.
        'path').
        """
        record = self.recordPreProcess(data, skip_nulls=True)

        if isinstance(conflict_target, str):
            target_cols = [conflict_target]
            target_str = conflict_target
        else:
            target_cols = list(conflict_target)
            target_str = ", ".join(target_cols)

        # Verifica che i campi di conflitto siano presenti nei dati
        for col in target_cols:
            if col not in record:
                raise ValueError(
                    f"Colonna di conflitto '{col}' mancante nei dati forniti."
                )

        columns = list(record.keys())
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

        return self._run_query(sql, list(record.values()), fExecute)




    # ===============================================
    def _selectRecord( self,
                        whereString: str = "",
                        to_dict: bool = True,
                        fExecute: bool = True,
                        params: tuple[object, ...] | list[object] = (),
                    ) -> list[dict[str, object]] | list[tuple[object, ...]] | None:
        """Esegue una SELECT sulla tabella filtrando tramite una whereString.

        :param whereString: Condizione SQL WHERE (es. "author = ? AND year > ?") o
        stringa vuota per tutti i record.
        :param to_dict: Se True, ritorna una lista di dizionari. Se False, righe
        grezze/tuple.
        :param fExecute: Se False, fa il display della query e dei parametri
        senza eseguirla.
        :param params: Parametri opzionali per la whereString per prevenire SQL
        injection.
        """
        # Costruisce la query di base
        sql = f"SELECT * FROM {self.name}"

        if whereString.strip():
            # Aggiunge WHERE se non è già presente all'inizio della stringa
            if not whereString.strip().upper().startswith("WHERE"):
                sql += f" WHERE {whereString}"
            else:
                sql += f" {whereString}"

        # Gestione fExecute = False (Dry-Run / Display della select)
        if not fExecute:
            self.logger.info("DRY-RUN:", sql, params)
            # print("\n[DRY-RUN / SELECT PREVIEW]")
            # print(f"SQL    : {sql.strip()}")
            # print(f"PARAMS : {params}\n")
            return None

        print(sql, params)
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        if to_dict:
            # Converte ogni riga sqlite3.Row in un dizionario Python
            return [dict(row) for row in rows]
        else:
            return [tuple(row) for row in rows]



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














































def test_01(db_path: str):
    # Inizializzazione DB con schema
    db = Database(db_path, schema_sql=SCHEMA_SQL)
    books = db["books"]

    # Punto 5: Verifica tipo colonna dalla struttura dinamica
    if books.struct_dict["author"]["type"] == "TEXT":
        print("La colonna 'author' è di tipo TEXT")

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

    test: int = 1
    fill_char='*'
    nchars=50

    print(f"\n{f' {test} upsert() ':{fill_char}^{nchars}}")
    # 1. Test fExecute=False (Dry-Run: Stampa solo la query senza modificare il DB)
    record: dict[str, object] = {
            "author": "George Orwell",
            "title": "1984",
            "path": "/books/1984.epub",
            "status": "da leggere",
        }
    book_id = books.upsert(record, conflict_target=("author", "title"),
                        fExecute=False,  # <--- Non esegue il comando
                    )
    print(f"updated libro con ID: {book_id}")

    # 2. Inserimento Reale (Chave composita author + title)
    test+=1;     print(f"\n{f' {test} upsert() ':{fill_char}^{nchars}}")
    record = {
            "author": "George Orwell",
            "title": "1984",
            "path": "/books/1984.epub",
            "status": "in lettura",
        }
    book_id = books.upsert(record,  conflict_target=("author", "title"), fExecute=True, )
    print(f"updated libro con ID: {book_id}")

    # 3. Upsert su chiave singola (file_hash)
    test+=1;     print(f"\n{f' {test} upsert() ':{fill_char}^{nchars}}")
    record = {
            "file_hash": "a1b2c3d4e5",
            "path": "/books/1984_v2.epub",
            "word_count": 88000,
        }
    book_id = books.upsert( record, conflict_target="file_hash", fExecute=True, )
    print(f"updated libro con ID: {book_id}")

    # 4. Retrieve all records:
    test+=1;     print(f"\n{f' {test} get_all() ':{fill_char}^{nchars}}")
    # records: list[dict[str, object]] = books.get_all()
    records = books.get_all()
    print("records: ",  len(records), '\n', records)

    # 5. Retrieve all records:
    test+=1;     print(f"\n{f' {test} find_by() ':{fill_char}^{nchars}}")
    records = books.find_by(column="author", value="George Orwell")
    print("records: ",  len(records), '\n', records)


    # 6. Test fExecute=False (Display della select senza eseguirla)
    # ... da vitare per sql_injections
    test+=1;     print(f"\n{f' {test} _selectRecord() ':{fill_char}^{nchars}}")
    books._selectRecord( whereString="author = 'George Orwell'", to_dict=True, fExecute=False )

    # 7. Select reale con parametri sicuri per evitare SQL Injection
    test+=1;     print(f"\n{f' {test} _selectRecord() ':{fill_char}^{nchars}}")
    records = books._selectRecord(
        whereString="author = ? AND status IS NOT NULL",
        params=("George Orwell",),
        to_dict=True,
        fExecute=True,
    )
    print("records: ",  len(records), '\n', records)
    # print("Risultati trovati:", risultati)


    # 8. Select senza where (prende tutto) come get_all()
    test+=1;     print(f"\n{f' {test} _selectRecord() ':{fill_char}^{nchars}}")
    records = books._selectRecord(to_dict=True)
    print("records: ",  len(records), '\n', records)
    # print(tutti_i_libri)


    # 9. Cerca tutti i libri il cui autore contiene "james" (case-insensitive per l'alfabeto ASCII)
    # Case-insensitive:
        # Per impostazione predefinita in SQLite, l'operatore LIKE è case-insensitive per i caratteri ASCII.
        # Quindi %james% troverà "James", "JAMES", "james", "St. James", ecc.
    test+=1;     print(f"\n{f' {test} _selectRecord() ':{fill_char}^{nchars}}")
    records = books._selectRecord(
        whereString="author LIKE ? AND author LIKE ?", params=("%orge%","%wel%",), to_dict=True
    )
    print("records: ",  len(records), '\n', records)
    # print(risultati)


if __name__ == "__main__":
    # test_01('/tmp/library.db')
    test_02('/tmp/library.db')
