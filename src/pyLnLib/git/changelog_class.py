#!/usr/bin/env python3
# ruff: noqa I001 - Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
# updated by ...: Loreto Notarantonio
# Date .........: 17-07-2026 13.44.49
#

# import sys
# sys.dont_write_bytecode = True
from datetime import datetime
from pathlib import Path
# from typing import TYPE_CHECKING

### - project modules
# if TYPE_CHECKING:
from ..logger import get_logger
from ..system import lnRun



class ChangeLogManager:
    """Gestisce la generazione e aggiornamento di CHANGELOG.md secondo Conventional Commits"""



    # def __init__(self, git_root: str, new_version: str, last_tag: str|None = None):
    def __init__(self, git_root: str, last_tag: str | None = None):
        """
        Inizializza il manager del changelog

        Args:
            git_root: Percorso della root del repository git
            new_version: Nuova versione da rilasciare
            last_tag: Ultimo tag (opzionale, se non fornito verrà ricavato)
        """
        # Tipi che NON devono apparire nel changelog (di solito)
        self.IGNORE_TYPES = ["chore", "style", "ci", "build"]  # opzionale, puoi escluderli

        # Mappatura dei tipi di commit alle sezioni del changelog
        self.COMMIT_TYPES = {
            "feat": "## 🚀 New Features",
            "fix": "## 🐛 Bug Fixes",
            "perf": "## ⚡ Performance Improvements",
            "refactor": "## 🔧 Code Refactoring",
            "docs": "## 📚 Documentation",
            "style": "## 🎨 Code Style",
            "test": "## ✅ Tests",
            "chore": "## 🔨 Maintenance",
            "ci": "## 🏗️ CI/CD",
            "build": "## 📦 Build System",
            "revert": "## ↩️ Reverts",
            "breaking": "## 💥 Breaking Changes",  # Speciale per breaking changes
        }
        self.git_root = git_root
        self.changelog_path = Path(git_root) / "CHANGELOG.md"
        self.logger = get_logger()

    def _get_last_tag(self) -> str | None:
        """Recupera l'ultimo tag dal repository git"""
        _rcode, stdout, _stderr = lnRun(
            "git describe --tags --abbrev=0", cwd=self.git_root, f_execute=True
        )
        if _rcode == 0 and stdout:
            return stdout.strip()
        return None

    def _commits_since_last_tag(self) -> list[str]:
        """
        Recupera i commit dall'ultimo tag fino a HEAD
        Esclude i commit di merge
        """
        if self.last_tag:
            log_range = f"{self.last_tag}..HEAD"
        else:
            # Se non c'è un tag, prendi tutti i commit
            log_range = "HEAD"
            self.logger.warning("Nessun tag trovato, prendo tutti i commit dalla storia")

        # Comando git: prendiamo anche l'hash per eventuale debug
        _rcode, stdout, _stderr = lnRun(
            f'git log {log_range} --pretty=format:"%h|%s" --no-merges',
            cwd=self.git_root,
            f_execute=True,
        )
        if stdout:
            return stdout.splitlines()
        return []

    def _parse_commit(self, commit_line: str) -> tuple[str | None, str]:
        """
        Parsa un commit nel formato "hash|messaggio"
        Restituisce (tipo, messaggio_clean)
        """
        if "|" not in commit_line:
            return None, commit_line.strip()

        _hash, message = commit_line.split("|", 1)
        message = message.strip()

        # Cerca il tipo di commit (formato conventional commits)
        # Esempi: "feat: add new feature" o "fix(api): resolve bug"
        import re

        match = re.match(r"^(\w+)(?:\([^)]+\))?:\s*(.*)$", message)

        if match:
            commit_type = match.group(1).lower()
            commit_message = match.group(2).strip()
            return commit_type, commit_message

        # Se non è conventional commit, lo mettiamo come "other"
        return "other", message

    def _categorize_commits(self, commits: list[str]) -> dict[str, list[str]]:
        """
        Categorizza i commit per tipo
        """
        categorized = {}

        for commit_line in commits:
            commit_type, message = self._parse_commit(commit_line)

            # Se il tipo è da ignorare, salta
            if commit_type in self.IGNORE_TYPES:
                continue

            # Se è un breaking change, lo segnaliamo
            if "!" in commit_type:  # Esempio: "feat!: breaking change"
                commit_type = "breaking"  # tyne

            if commit_type not in categorized:
                categorized[commit_type] = []
            categorized[commit_type].append(message)

        return categorized

    def _generate_section(self, categorized: dict[str, list[str]]) -> str:
        """
        Genera la sezione del changelog per la nuova versione
        """
        today = datetime.now().strftime("%Y-%m-%d")
        section = f"## [{self.new_version}] - {today}\n\n"

        # Ordine di priorità per le sezioni
        priority_order = [
            "breaking",
            "feat",
            "fix",
            "perf",
            "refactor",
            "docs",
            "test",
            "other",
        ]

        for commit_type in priority_order:
            if commit_type in categorized and categorized[commit_type]:
                # Prendi il titolo della sezione dalla mappatura
                title = self.COMMIT_TYPES.get(
                    commit_type, f"## {commit_type.capitalize()}"
                )
                section += f"{title}\n\n"
                for message in categorized[commit_type]:
                    section += f"- {message}\n"
                section += "\n"

        # Aggiungi i tipi non gestiti
        for commit_type, messages in categorized.items():
            if commit_type not in priority_order:
                title = self.COMMIT_TYPES.get(
                    commit_type, f"## {commit_type.capitalize()}"
                )
                section += f"{title}\n\n"
                for message in messages:
                    section += f"- {message}\n"
                section += "\n"

        return section

    def update(
        self, new_version: str, last_tag: str | None = None, f_execute: bool = True
    ) -> bool:
        """
        Aggiorna il file CHANGELOG.md con i commit dall'ultimo tag

        Args:
            f_execute: Se True scrive il file, altrimenti dry-run

        Returns:
            bool: True se l'operazione è riuscita
        """
        self.new_version = new_version
        self.last_tag = last_tag

        # Se non abbiamo il tag, proviamo a ricavarlo
        if self.last_tag is None:
            self.last_tag = self._get_last_tag()

        # 1. Recupera i commit
        commits = self._commits_since_last_tag()

        if not commits:
            self.logger.info("Nessun commit trovato dall'ultimo tag")
            return False

        # 2. Categorizza i commit
        categorized = self._categorize_commits(commits)

        if not categorized:
            self.logger.info("Nessun commit significativo trovato (tutti ignorati)")
            return False

        # 3. Genera la nuova sezione
        new_section = self._generate_section(categorized)

        # 4. Preview o scrittura
        if not f_execute:
            self.logger.info("=== CHANGELOG.md preview (dry-run) ===")
            self.logger.info(f"Version: {self.new_version}")
            self.logger.info(f"Last_tag: {self.last_tag}")
            self.logger.info(f"Commit found: {len(commits)}")
            self.logger.debug("\n" + new_section)
            self.logger.info("=== CHANGELOG.md end (dry-run) ===")
            return True

        # 5. Leggi il contenuto esistente o crea nuovo file
        if self.changelog_path.exists():
            old_content = self.changelog_path.read_text(encoding="utf-8")
        else:
            # Se il file non esiste, creiamo un'intestazione
            old_content = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"

        # 6. Scrivi il nuovo contenuto (la nuova sezione in cima)
        new_content = new_section + old_content
        self.changelog_path.write_text(new_content, encoding="utf-8")

        self.logger.notify(f"✅ CHANGELOG.md aggiornato con versione {self.new_version}")
        return True

    def get_summary(self) -> dict[str, int]:
        """
        Ottiene un riepilogo dei commit per tipo (utile per debug)
        """
        commits = self._commits_since_last_tag()
        categorized = self._categorize_commits(commits)

        summary = {}
        for commit_type, messages in categorized.items():
            summary[commit_type] = len(messages)

        return summary


# Funzione di compatibilità con il tuo codice esistente
def generate_changelog(git_prj, f_execute: bool = True) -> bool:
    """
    Funzione di compatibilità per generare il changelog

    Args:
        git_prj: Oggetto con attributi path, new_version, last_tag
        f_execute: Se True esegue la scrittura
    """
    manager = ChangeLogManager(
        git_root=git_prj.path,
        new_version=git_prj.new_version,
        last_tag=getattr(git_prj, "last_tag", None),
    )
    return manager.update(f_execute)


# Esempio di utilizzo
if __name__ == "__main__":
    # Utilizzo con la classe
    manager = ChangeLogManager(".", "1.2.0")

    # Preview (dry-run)
    manager.update(f_execute=False)

    # Stampa riepilogo
    summary = manager.get_summary()
    self.logger.info(f"Riepilogo commit: {summary}")

    # Esecuzione reale
    # manager.update(f_execute=True)
