#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio


# import sys
# sys.dont_write_bytecode = True
from pathlib import Path
# from typing import Optional #, TYPE_CHECKING

### - project modules
# if TYPE_CHECKING:
from pyLnLib import get_logger

class PyProjectManager:
    """Classe per gestire la lettura e scrittura del file pyproject.toml"""

    def __init__(self, git_root: str|Path):
        """
        Inizializza il manager per pyproject.toml

        Args:
            git_root: Percorso root del repository git
        """
        self.git_root = Path(git_root)
        self.pyproject_path = self.git_root / "pyproject.toml"
        self._data = None
        self.logger = get_logger()

    def read(self) -> dict:
        """
        Legge il file pyproject.toml

        Returns:
            dict: Dati del file pyproject.toml, None se il file non esiste
        """
        if not self.pyproject_path.exists():
            self.logger.error(f"File 'pyproject.toml' NOT found in {self.git_root}")
            return {}

        try:
            import tomllib
            with open(self.pyproject_path, "rb") as f:
                self._data = tomllib.load(f)
            return self._data
        except Exception as e:
            self.logger.error(f"Errore nella lettura di pyproject.toml: {e}")
            return {}

    def write(self, f_execute: bool = True) -> bool:
        """
        Scrive i dati nel file pyproject.toml

        Args:
            f_execute: Se True esegue la scrittura, altrimenti dry-run

        Returns:
            bool: True se la scrittura è avvenuta con successo, False altrimenti
        """
        if self._data is None:
            self.logger.error("Nessun dato da scrivere. Eseguire prima read()")
            return False

        if not self.pyproject_path.parent.exists():
            self.logger.error(f"Directory {self.pyproject_path.parent} non esiste")
            return False

        try:
            if f_execute:
                import tomli_w
                with open(self.pyproject_path, "wb") as f:
                    tomli_w.dump(self._data, f)
                self.logger.info(f"pyproject.toml aggiornato con successo in {self.pyproject_path}")
            else:
                self.logger.notify("DRY-RUN: pyproject.toml will be modified")
            return True
        except Exception as e:
            self.logger.error(f"Errore nella scrittura di pyproject.toml: {e}")
            return False



    def get_version(self) -> str:
        """
        Ottiene la versione corrente dal file pyproject.toml

        Returns:
            str: Versione corrente, "0.0.0" se non trovata
        """
        if self._data is None:
            self.read()

        if self._data is None:
            return "0.0.0"

        return self._data.get("project", {}).get("version", "0.0.0")

    def update_version(self, new_version: str, f_execute: bool = False) -> bool:
        """
        Imposta una nuova versione nel file pyproject.toml

        Args:
            new_version: Nuova versione da impostare
            f_execute: Se True esegue la scrittura, altrimenti dry-run

        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        # Leggi i dati correnti se non sono già stati letti
        if self._data is None:
            if not self.read():
                self.logger.error("Impossibile leggere pyproject.toml")
                return False

        # Ottieni la versione corrente
        cur_version = self.get_version()

        # Assicurati che la struttura "project" esista
        if "project" not in self._data:  # type: ignore
            self._data["project"] = {}  # type: ignore

        # Imposta la nuova versione
        self._data["project"]["version"] = new_version

        # Log delle informazioni
        self.logger.info(f"Versione corrente: {cur_version}")
        self.logger.info(f"Nuova versione: {new_version}")

        # Scrivi il file se richiesto
        return self.write(f_execute)

    @property
    def data(self) -> dict:
        """Proprietà per accedere ai dati letti"""
        if self._data is None:
            self.read()
        return self._data

    @data.setter
    def data(self, value: dict):
        """Setta i dati manualmente"""
        self._data = value

    def exists(self) -> bool:
        """Verifica se il file pyproject.toml esiste"""
        return self.pyproject_path.exists()




# Esempio di utilizzo
if __name__ == "__main__":
    # Utilizzo con la classe
    manager = PyProjectManager(".")
    print(f"Versione corrente: {manager.get_version()}")
    manager.set_version("1.0.0", f_execute=False)  # Dry-run

    # Utilizzo con le funzioni di compatibilità
    data = pyproject_read(".")
    if data:
        print(f"Dati letti: {data}")
        pyproject_version("2.0.0", f_execute=False, git_root=".")
        update_pyproject("3.0.0", f_execute=False, git_root=".")
