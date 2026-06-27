#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 27-06-2026 14.28.52
#

import os
import platform
import subprocess
import sys
from ossaudiodev import SOUND_MIXER_SPEAKER
from pathlib import Path, PurePosixPath
from typing import Any, List, Optional, Union

# import pyLnLib
from pyLnLib.context import gVars as ctx

logger = ctx.get_logger()


# Costanti per i suoni predefiniti su Linux
class SoundFiles:
    """Classe con i percorsi dei file audio comuni su Linux."""


    AVAILABLE_SOUNDS: dict[str, str] = {
        "ALARM":  "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga",
        "BELL":  "/usr/share/sounds/freedesktop/stereo/bell.oga",
        "CAMERA_SHUTTER": "/usr/share/sounds/freedesktop/stereo/camera-shutter.oga",
        "COMPLETE":  "/usr/share/sounds/freedesktop/stereo/complete.oga",
        "INFO":  "/usr/share/sounds/freedesktop/stereo/dialog-information.oga",
        "ERROR":  "/usr/share/sounds/freedesktop/stereo/dialog-error.oga",
        "MESSAGE":  "/usr/share/sounds/freedesktop/stereo/message.oga",
        "MESSAGE_NEW":  "/usr/share/sounds/freedesktop/stereo/message-new-instant.oga",
        "WARNING":  "/usr/share/sounds/freedesktop/stereo/dialog-warning.oga",
    }



def playBeep(req_sound: Union[str, Path, PurePosixPath]) -> None:
    """
    Riproduce un suono di notifica in modo cross-platform.

    Args:
        sound_path: Percorso del file audio da riprodurre.
    """
    # logger = get_logger()  # Ottieni il logger globale
    _system: str = platform.system()

    try:
        sound_path: str = str(req_sound)
        paplay_exists: bool = os.path.exists("/usr/bin/paplay")
        if not paplay_exists:
            logger.warning("paplay non trovato, uso beep semplice")
            print("\a")

        if sound_path in SoundFiles.AVAILABLE_SOUNDS.keys():
            sound_path = SoundFiles.AVAILABLE_SOUNDS[sound_path]

        sound_exists: bool = os.path.exists(sound_path)
        if sound_exists:
            logger.info("Riproduzione suono: %s", sound_path)
            subprocess.Popen(["paplay", sound_path])

        else:
            logger.warning("File audio non trovato: %s", sound_path)
            print("\a")

    except Exception as e:
        logger.error("Errore durante la riproduzione del beep: %s", e, exc_info=True)
        print("\a")


def get_beep_types() -> dict:
    """Ritorna la lista dei suoni."""
    return SoundFiles.AVAILABLE_SOUNDS


def play_success_sound() -> None:
    """Riproduce un suono di successo/completamento."""
    playBeep("COMPLETE")


def play_error_sound() -> None:
    """Riproduce un suono di errore/warning."""
    playBeep("WARNING")


def play_notification_sound() -> None:
    """Riproduce un suono di notifica."""
    playBeep("MESSAGE_NEW")
