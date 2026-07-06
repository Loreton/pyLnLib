#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 06-07-2026 14.26.42
#
"""
Modulo per inizializzare il logger.
Separato da context.py per evitare dipendenze circolari.
"""

import sys ; sys.dont_write_bytecode=True
from pathlib import Path
from typing import Optional, Any

from pyLnLib.logger import lnLogger, testLogger
from pyLnLib.context import gVars


# Variabile globale per il logger
_logger: Optional[Any] = None
_logger_initialized: bool = False


def init_logger(
    project_name: Optional[str] = None,
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    log_dir: Optional[Path] = None,
    force: bool = False,
) -> Any:
    """
    Inizializza il logger.

    Args:
        project_name: Nome del progetto (usa gVars.project_name se None)
        console_level: Livello per console
        file_level: Livello per file
        log_dir: Directory per i log (usa gVars.get_log_dir() se None)
        force: Forza la reinizializzazione

    Returns:
        Logger configurato
    """
    global _logger, _logger_initialized

    if _logger_initialized and not force:
        return _logger

    # Usa i valori da context se non specificati
    if project_name is None:
        project_name = gVars.project_name

    if log_dir is None:
        log_dir = gVars.get_log_dir()

    # Crea la directory se non esiste
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Crea il logger
    _logger = lnLogger(
        name=project_name,
        console_logger_level=console_level,
        file_logger_level=file_level,
        logging_dir=str(log_dir),
        threads=False,
    )

    # Configura
    _logger.setNameLength(dynamic=True, length=0)

    # Test
    testLogger(_logger)

    _logger_initialized = True

    print("*" * 20)
    print(f"Logger inizializzato: {project_name}")
    print(f"Log directory: {log_dir}")
    print("*" * 20)

    return _logger


def get_logger(create: bool = True) -> Any:
    """
    Ottieni il logger.

    Args:
        create: Se True e il logger non esiste, lo crea automaticamente.

    Returns:
        Il logger o None se non esiste e create=False
    """
    global _logger

    if _logger is None and create:
        init_logger()

    return _logger


def set_logger(logger: Any) -> None:
    """Imposta un logger esterno (override)."""
    global _logger, _logger_initialized
    _logger = logger
    _logger_initialized = True


def is_logger_initialized() -> bool:
    """Verifica se il logger è stato inizializzato."""
    return _logger_initialized