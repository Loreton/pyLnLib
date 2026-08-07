#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
#
from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path, PurePosixPath
from typing import ClassVar, Dict

from pyLnLib.logger import get_logger

logger = get_logger()


class BeepPlayer:
    """Classe per la riproduzione di suoni di notifica cross-platform."""

    # Attributo di classe immutabile (per risolvere RUF012)
    # Usiamo ClassVar per indicare che è un attributo di classe
    DEFAULT_SOUNDS: ClassVar[dict[str, str]] = {
        "ALARM": "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga",
        "BELL": "/usr/share/sounds/freedesktop/stereo/bell.oga",
        "CAMERA_SHUTTER": "/usr/share/sounds/freedesktop/stereo/camera-shutter.oga",
        "COMPLETE": "/usr/share/sounds/freedesktop/stereo/complete.oga",
        "INFO": "/usr/share/sounds/freedesktop/stereo/dialog-information.oga",
        "ERROR": "/usr/share/sounds/freedesktop/stereo/dialog-error.oga",
        "MESSAGE": "/usr/share/sounds/freedesktop/stereo/message.oga",
        "MESSAGE_NEW": "/usr/share/sounds/freedesktop/stereo/message-new-instant.oga",
        "WARNING": "/usr/share/sounds/freedesktop/stereo/dialog-warning.oga",
    }

    def __init__(self, custom_sounds: dict[str, str] | None = None):
        """
        Inizializza il player audio.

        Args:
            custom_sounds: Dizionario personalizzato di suoni (opzionale)
        """
        # Se vengono forniti suoni personalizzati, li fondiamo con quelli predefiniti
        self.sounds = self.DEFAULT_SOUNDS.copy()
        if custom_sounds:
            self.sounds.update(custom_sounds)

        self._system = platform.system()
        self._paplay_path = "/usr/bin/paplay"
        self._paplay_exists = os.path.exists(self._paplay_path)

        # Inizializza il logger
        self.logger = logger or get_logger()

    def play(self, sound_req: str | Path | PurePosixPath) -> bool:
        """
        Riproduce un suono di notifica.

        Args:
            sound_req: Nome del suono predefinito o percorso del file audio

        Returns:
            bool: True se la riproduzione è riuscita, False altrimenti
        """
        try:
            sound_path = str(sound_req)

            # Controlla se è un nome predefinito
            if sound_path in self.sounds:
                sound_path = self.sounds[sound_path]

            # Verifica esistenza del file
            if os.path.exists(sound_path):
                self.logger.debug("Riproduzione suono: %s", sound_path)

                # Usa paplay se disponibile, altrimenti beep semplice
                if self._paplay_exists:
                    subprocess.Popen([self._paplay_path, sound_path])
                else:
                    self._fallback_beep()
                return True
            else:
                self.logger.warning("File audio non trovato: %s", sound_path)
                self._fallback_beep()
                return False

        except Exception as e:
            self.logger.error(
                "Errore durante la riproduzione del beep: %s", e, exc_info=True
            )
            self._fallback_beep()
            return False

    def _fallback_beep(self) -> None:
        """Metodo di fallback per il beep base."""
        if not self._paplay_exists:
            self.logger.warning("paplay non trovato, uso beep semplice")
        print("\a", flush=True)

    # Metodi di comodo per suoni specifici
    def play_success(self) -> bool:
        """Riproduce un suono di successo/completamento."""
        return self.play("COMPLETE")

    def play_error(self) -> bool:
        """Riproduce un suono di errore/warning."""
        return self.play("WARNING")

    def play_notification(self) -> bool:
        """Riproduce un suono di notifica."""
        return self.play("MESSAGE_NEW")

    def play_info(self) -> bool:
        """Riproduce un suono di informazione."""
        return self.play("INFO")

    def play_alarm(self) -> bool:
        """Riproduce un suono di allarme."""
        return self.play("ALARM")

    def get_sound_types(self) -> dict[str, str]:
        """
        Ritorna la lista dei suoni disponibili.

        Returns:
            Dict[str, str]: Dizionario con i suoni disponibili
        """
        return self.sounds.copy()

    @classmethod
    def get_default_sound_types(cls) -> dict[str, str]:
        """
        Ritorna la lista dei suoni predefiniti (senza copia).

        Returns:
            Dict[str, str]: Dizionario con i suoni predefiniti
        """
        return cls.DEFAULT_SOUNDS.copy()


# Funzioni di compatibilità per mantenere l'API esistente
# (opzionale, se vuoi mantenere la compatibilità con codice esistente)


def playBeep(req_sound: str | Path | PurePosixPath) -> None:
    """Funzione di compatibilità."""
    player = BeepPlayer()
    player.play(req_sound)


def get_beep_types() -> dict[str, str]:
    """Funzione di compatibilità."""
    return BeepPlayer.get_default_sound_types()


def play_success_sound() -> None:
    """Funzione di compatibilità."""
    player = BeepPlayer()
    player.play_success()


def play_error_sound() -> None:
    """Funzione di compatibilità."""
    player = BeepPlayer()
    player.play_error()


def play_notification_sound() -> None:
    """Funzione di compatibilità."""
    player = BeepPlayer()
    player.play_notification()


# Istanza singleton opzionale
# default_player = BeepPlayer()
