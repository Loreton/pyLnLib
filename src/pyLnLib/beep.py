#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 22-06-2026 21.01.56
#

from typing import Optional, Union, List, Any
from pathlib import Path, PurePosixPath
import os
import platform
import subprocess
import sys


import pyLnLib




# Costanti per i suoni predefiniti su Linux
class SoundFiles:
    """Classe con i percorsi dei file audio comuni su Linux."""
    CAMERA_SHUTTER: str = "/usr/share/sounds/freedesktop/stereo/camera-shutter.oga"
    MESSAGE: str = "/usr/share/sounds/freedesktop/stereo/message.oga"
    MESSAGE_NEW: str = "/usr/share/sounds/freedesktop/stereo/message-new-instant.oga"
    BELL: str = "/usr/share/sounds/freedesktop/stereo/bell.oga"
    ALARM: str = "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"
    COMPLETE: str = "/usr/share/sounds/freedesktop/stereo/complete.oga"
    DIALOG_QUESTION: str = "/usr/share/sounds/freedesktop/stereo/dialog-question.oga"
    DIALOG_WARNING: str = "/usr/share/sounds/freedesktop/stereo/dialog-warning.oga"

    AVAILABLE_SOUNDS: List[str] = [
        CAMERA_SHUTTER,
        MESSAGE,
        MESSAGE_NEW,
        BELL,
        ALARM,
        COMPLETE,
        DIALOG_QUESTION,
        DIALOG_WARNING,
    ]


def playBeep(sound_file: Optional[Union[str, Path, PurePosixPath]] = None) -> None:
    """
    Riproduce un suono di notifica in modo cross-platform.

    Args:
        sound_file: Percorso del file audio da riprodurre.
                   Se None, usa il suono predefinito per il sistema.
    """
    logger = get_logger()  # Ottieni il logger globale
    system: str = platform.system()

    try:
        if system == "Windows":
            import winsound
            winsound.MessageBeep()
            if logger:
                logger.debug("Windows beep riprodotto")

        elif system == "Darwin":  # macOS
            mac_sound: str = "/System/Library/Sounds/Glass.aiff"
            subprocess.Popen(["afplay", mac_sound])
            if logger:
                logger.debug("macOS beep riprodotto: %s", mac_sound)

        elif system == "Linux":
            if sound_file is None:
                preferred_sounds: List[str] = [
                    SoundFiles.MESSAGE_NEW,
                    SoundFiles.BELL,
                    SoundFiles.CAMERA_SHUTTER,
                    SoundFiles.MESSAGE,
                ]

                for sf in preferred_sounds:
                    if os.path.exists(sf):
                        sound_file = sf
                        break

                if sound_file is None:
                    sound_file = SoundFiles.AVAILABLE_SOUNDS[0]

            sound_path: str = str(sound_file)
            paplay_exists: bool = os.path.exists("/usr/bin/paplay")
            sound_exists: bool = os.path.exists(sound_path)

            if paplay_exists and sound_exists:
                if logger:
                    logger.info("Riproduzione suono: %s", sound_path)
                subprocess.Popen(["paplay", sound_path])
            elif paplay_exists and not sound_exists:
                if logger:
                    logger.warning("File audio non trovato: %s", sound_path)
                print("\a")
            else:
                if logger:
                    logger.warning("paplay non trovato, uso beep semplice")
                print("\a")

        else:
            print("\a")
            if logger:
                logger.debug("Beep semplice per sistema: %s", system)

    except Exception as e:
        if logger:
            logger.error("Errore durante la riproduzione del beep: %s", e, exc_info=True)
        else:
            print(f"ERROR: {e}")
        print("\a")


def play_success_sound() -> None:
    """Riproduce un suono di successo/completamento."""
    playBeep(SoundFiles.COMPLETE)


def play_error_sound() -> None:
    """Riproduce un suono di errore/warning."""
    playBeep(SoundFiles.DIALOG_WARNING)


def play_notification_sound() -> None:
    """Riproduce un suono di notifica."""
    playBeep(SoundFiles.MESSAGE_NEW)


def test_sounds() -> None:
    """Testa tutti i suoni disponibili su Linux."""
    logger = get_logger()

    if platform.system() != "Linux":
        if logger:
            logger.warning("Test dei suoni disponibile solo su Linux")
        return

    if logger:
        logger.info("Test dei suoni disponibili...")

    available: List[str] = []

    for sound in SoundFiles.AVAILABLE_SOUNDS:
        if os.path.exists(sound):
            available.append(sound)
            if logger:
                logger.info("✓ %s", sound)
        else:
            if logger:
                logger.debug("✗ %s (non trovato)", sound)

    if available:
        if logger:
            logger.info("Suoni disponibili: %s", len(available))
        playBeep(available[0])
    else:
        if logger:
            logger.warning("Nessun suono disponibile")
        playBeep()


def main() -> None:
    """Funzione principale per esecuzione diretta."""
    logger = get_logger()

    print("Testing beep functions...")
    print("1. Default beep")
    playBeep()
    print("2. Success sound")
    play_success_sound()
    print("3. Error sound")
    play_error_sound()
    print("4. Notification sound")
    play_notification_sound()
    print("5. Test sounds")
    test_sounds()
    print("Test completed!")

    if logger:
        logger.info("Beep test completed")


if __name__ == "__main__":
    main()