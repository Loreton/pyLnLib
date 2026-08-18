#
# updated by ...: Loreto Notarantonio
#
from dataclasses import dataclass


# ##################################################
# # emoji: https://emojiterra.com/double-exclamation-mark/
# ##################################################
@dataclass(frozen=True)  # "frozen" rende i colori non modificabili per errore
class Emoji:
    """Classe per i codici emoji per il terminale."""

    red_exclamation_mark: str = "❗"
    double_exclamation_mark: str = "‼️"
    red_question_mark: str = "❓"
    white_exclamation_mark: str = "❕"
    warning: str = "⚠️"
    check_mark: str = "✔️"
    check_mark_button: str = "✅"
    thumbs_up: str = "👍"
    ogre: str = "👹"
    skull: str = "💀"
    folder: str = "📁"

    arrow_right: str = "➡️"
    arrow_left: str = "⬅️"

    # rem = red_exclamation_mark
    # dem = double_exclamation_mark
    # rqm = red_question_mark
    # wem = white_exclamation_mark
    # warn = warning
    # cmb = check_mark_button
    # cm = check_mark


# # Funzione comoda per ottenere i Colors
def get_emoji() -> Emoji:
    """Funzione comoda per ottenere i Colors."""
    return Emoji  # type: ignore
