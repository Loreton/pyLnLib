#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 27-06-2026 14.26.28
#


import os
import sys
import time
from pathlib import Path

os.environ["LN_PROJECT_NAME"] = "beep_test"
import pyLnLib as lnLib
from pyLnLib import Colors as C
from pyLnLib import gVars as ctx

sys.dont_write_bytecode = True


def localSounds():
    _voice_sounds: list = [
        "audio-channel-front-center.oga",
        "audio-channel-front-left.oga",
        "audio-channel-front-right.oga",
        "audio-channel-rear-center.oga",
        "audio-channel-rear-left.oga",
        "audio-channel-rear-right.oga",
        "audio-channel-side-left.oga",
        "audio-channel-side-right.oga",
    ]
    sounds: list = [
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
        sound_file = Path("/usr/share/sounds/freedesktop/stereo") / sound
        lnLib.Beep(sound_file=sound_file)
        time.sleep(5)


def soundList():
    # ============================================
    def show_list(ftype: str):
        if ftype == "oga":
            files = list(
                lnLib.dirList(
                    top_dir="/home/loreto/filu/lnEnv/config/sounds/oga",
                    file_pattern="*.oga",
                    recursive=False,
                )
            )
        elif ftype == "wav":
            files = list(
                lnLib.dirList(
                    top_dir="/home/loreto/filu/lnEnv/config/sounds/wav",
                    file_pattern="*.wav",
                    recursive=False,
                )
            )
        else:
            return []

        TAB = " " * 8
        for index, file_path in enumerate(files, 1):
            print(f"{TAB}{C.yellow}{index:2} - {C.cyanH}{file_path.name}{C.reset}")
            validKeys.append(str(index))
        return sorted(files)

    # ============================================

    validKeys = ["oga", "wav"]
    sound_files = show_list("wav")
    keyb_msg = (f'\n{C.yellow}select desired sound file or "wav|oga" to get a list{C.reset}' )
    while True:
        choice = lnLib.keyboardPrompt(text_msg=keyb_msg, validKeys=validKeys)
        if choice == "oga":
            sound_files = show_list("oga")
        elif choice == "wav":
            sound_files = show_list("wav")
        else:
            lnLib.Beep(sound_file=sound_files[int(choice) - 1])


def beepTypes():
    sounds: dict = lnLib.get_beep_types()

    # ============================================
    # --- start display sound names and create array of valid keys
    validKeys: list[str] = []
    soundKeys: list[str] = []
    TAB: str = " " * 8
    sound_names: list[str] = sorted(sounds.keys())

    for (index, name ) in enumerate(sound_names, 1):
        print(f"{TAB}{C.yellow}{index:2} - {C.cyanH}{name:20}: {sounds[name]}{C.reset}")
        validKeys.append(str(index))
        soundKeys.append(name)
    # --- end display sound names and create array of valid keys
    # ============================================

    keyb_msg: str= f"\n{C.yellow}select desired sound type{C.reset}"
    while True:
        choice = lnLib.keyboardPrompt(text_msg=keyb_msg, validKeys=validKeys)
        beep_name = soundKeys[int(choice) - 1]  # type: ignore
        print(beep_name)
        lnLib.playBeep(sounds[beep_name])


# -------------------------------
# Test
# -------------------------------
if __name__ == "__main__":
    logger = ctx.get_logger()
    logger.test(logger=logger)
    C = lnLib.Colors
    beepTypes()
    # sounds = lnLib.get_beep_types()

    # logger=lnLib.lnLogger(name=Path(__file__).stem, console_logger_level="trace")
    # ctx.logger=logger

    # LOCAL = False
    # if LOCAL:
    #     localSounds()

    # else:
    #     soundList()
