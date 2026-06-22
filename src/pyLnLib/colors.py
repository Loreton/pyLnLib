#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 22-06-2026 21.08.03
#
from dataclasses import dataclass

# ##################################################
# # colori
# ##################################################
@dataclass(frozen=True)  # "frozen" rende i colori non modificabili per errore
class Colors:
    """Classe per i codici colore ANSI per il terminale."""
    red: str = "\033[31m"
    redH: str = "\033[91m"
    green: str = "\033[32m"
    greenH: str = "\033[92m"
    yellow: str = "\033[33m"
    yellowH: str = "\033[93m"
    blue: str = "\033[34m"
    blueH: str = "\033[94m"
    purple: str = "\033[35m"
    purpleH: str = "\033[95m"
    magenta: str = "\033[35m"
    magentaH: str = "\033[95m"
    cyan: str = "\033[36m"
    cyanH: str = "\033[96m"
    white: str = "\033[37m"
    whiteH: str = "\033[97m"
    reset: str = "\033[0m"

    # Costanti per stili aggiuntivi
    bold: str = "\033[1m"
    underline: str = "\033[4m"
    blink: str = "\033[5m"
    reverse: str = "\033[7m"
    hidden: str = "\033[8m"

    # Background colors
    bg_red: str = "\033[41m"
    bg_green: str = "\033[42m"
    bg_yellow: str = "\033[43m"
    bg_blue: str = "\033[44m"
    bg_magenta: str = "\033[45m"
    bg_cyan: str = "\033[46m"
    bg_white: str = "\033[47m"