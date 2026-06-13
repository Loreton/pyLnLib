#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 13-06-2026 17.34.57
#


import sys; sys.dont_write_bytecode = True
import os
from pathlib import Path
import time

import pyLnLib as lnLib
from pyLnLib import gVars as ctx, Color as C



def localSounds():
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

    for sound in sounds:
    # for sound in voice_sounds:
        sound_file = Path('/usr/share/sounds/freedesktop/stereo') / sound
        lnLib.Beep(sound_file=sound_file)
        time.sleep(5)





def soundList():
    # ============================================
    def show_list(ftype: str):
        if ftype=='oga':
            files = list(lnLib.dirList(top_dir='/home/loreto/filu/lnEnv/config/sounds/oga', file_pattern="*.oga", recursive=False))
        elif ftype=='wav':
            files = list(lnLib.dirList(top_dir='/home/loreto/filu/lnEnv/config/sounds/wav', file_pattern="*.wav", recursive=False))
        else:
            return []

        TAB=" "*8
        for index, file_path in enumerate(files, 1):
            print(f"{TAB}{C.yellow}{index:2} - {C.cyanH}{file_path.name}{C.reset}")
            validKeys.append(str(index))
        return sorted(files)
    # ============================================

    validKeys=['oga', "wav"]
    sound_files = show_list("wav")
    keyb_msg=f'\n{C.yellow}select desired sound file or "wav|oga" to get a list{C.reset}'
    while True:
        choice=lnLib.keyboardPrompt(text_msg=keyb_msg, validKeys=validKeys)
        if choice=='oga':
            sound_files = show_list("oga")
        elif choice=='wav':
            sound_files = show_list("wav")
        else:
            lnLib.Beep(sound_file=sound_files[int(choice)-1])




# -------------------------------
# Test
# -------------------------------
if __name__ == "__main__":

    logger=lnLib.lnLogger(name=Path(__file__).stem, console_logger_level="trace"); ctx.logger=logger
    logger.test(logger=logger)
    C = lnLib.Color

    LOCAL = False
    if LOCAL:
        localSounds()

    else:
        soundList()









