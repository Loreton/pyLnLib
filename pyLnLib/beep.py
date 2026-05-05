#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 01-05-2026 13.36.58
#

import sys
import os

from .context import ctx, Colors as C


def play_beep():
    system = platform.system()
    try:
        if system == "Windows":
            import winsound
            winsound.MessageBeep()
        elif system == "Darwin":  # macOS
            subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"])
        elif system == "Linux":
            soundFile="/usr/share/sounds/freedesktop/stereo/message-new-instant.oga"
            soundFile="/usr/share/sounds/freedesktop/stereo/message.oga"
            soundFile="/usr/share/sounds/freedesktop/stereo/camera-shutter.oga"
            soundFile="/usr/share/sounds/freedesktop/stereo/bell.oga"
            if os.path.exists("/usr/bin/paplay") and os.path.exists(soundFile):
                ctx.logger.info("paplay %s", soundFile)
                subprocess.Popen(["paplay", soundFile])
        else:
            print("\a")
    except Exception as e:
        ctxlogger.error("Beep failed:", e)


