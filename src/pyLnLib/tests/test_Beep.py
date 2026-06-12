#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 12-06-2026 20.47.36
#

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys; sys.dont_write_bytecode = True
import os
from pathlib import Path
import time



import pyLnLib as lnLib
from pyLnLib import gVars as ctx



# -------------------------------
# Test
# -------------------------------
if __name__ == "__main__":
    voice_sounds = [
        "audio-channel-front-center.oga",
        "audio-channel-front-left.oga",
        "audio-channel-front-right.oga",
        "audio-channel-rear-center.oga",
        "audio-channel-rear-left.oga",
        "audio-channel-rear-right.oga",
        "audio-channel-side-left.oga",
        "audio-channel-side-right.oga",
    ]
    sounds = [
        "alarm-clock-elapsed.oga",
        "audio-test-signal.oga",
        "audio-volume-change.oga",
        "bell.oga",
        "camera-shutter.oga",
        "complete.oga",
        "device-added.oga",
        "device-removed.oga",
        "dialog-information.oga",
        "dialog-warning.oga",
        "message-new-instant.oga",
        "message.oga",
        "onboard-key-feedback.oga",
        "phone-incoming-call.oga",
        "phone-outgoing-busy.oga",
        "phone-outgoing-calling.oga",
        "service-login.oga",
        "service-logout.oga",
        "suspend-error.oga",
        "trash-empty.oga",
    ]

    logger=lnLib.lnLogger(name=Path(__file__).stem, console_logger_level="trace")
    ctx.logger=logger
    logger.test(logger=logger)

    for sound in sounds:
        sound_file = Path('/usr/share/sounds/freedesktop/stereo') / sound
        # logger.info("playing file: %s", sound_file)
        lnLib.Beep(sound_file=sound_file)
        time.sleep(5)








