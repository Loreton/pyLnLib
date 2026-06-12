#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 12-06-2026 20.45.18
#

import sys
import os
import platform
import subprocess

from .context import gVars


def playBeep(sound_file: str=None):
    logger = gVars.logger
    system = platform.system()

    try:

        if system == "Windows":
            import winsound
            winsound.MessageBeep()

        elif system == "Darwin":  # macOS
            subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"])

        elif system == "Linux":
            if not sound_file:
                sound_file="/usr/share/sounds/freedesktop/stereo/camera-shutter.oga"
                sound_file="/usr/share/sounds/freedesktop/stereo/message.oga"
                sound_file="/usr/share/sounds/freedesktop/stereo/message-new-instant.oga"
                sound_file="/usr/share/sounds/freedesktop/stereo/bell.oga"

            if os.path.exists("/usr/bin/paplay") and os.path.exists(sound_file):
                logger.info("paplay %s", sound_file)
                subprocess.Popen(["paplay", sound_file])
        else:
            print("\a")
    except Exception as e:
        logger.error("Beep failed:", e)


