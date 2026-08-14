#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# ruff: noqa I001 -Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
#


#################################
#    Ctrl-C capture
###################################################
import sys
import signal
import os
import inspect
import traceback


def _show_stack():
    frames: list[inspect.FrameInfo] = inspect.stack()
    n_levels = len(frames)
    # ---------------------------
    # - lvl: 0 self._caller()
    # - lvl: 1 self._log()
    # - lvl: 2 self.info()...self.trace()...
    # - lvl: 3 call to log
    # - lvl: 4 caller of lev.3
    # ---------------------------
    stacklevel=1
    x = traceback.extract_stack()
    print("-" * 40)
    print(f"required stacklevel: {stacklevel}")
    for i in range(len(x)):
        filename = inspect.stack()[i].filename
        _function = inspect.stack()[i].function
        lineno = inspect.stack()[i].lineno
        print("\t", i, filename, lineno)


def signalHandler(signalLevel, frame):
    ### Ctrl-c
    if int(signalLevel)==2:
        _show_stack()
        # raise AttributeError(f"{__name__} object has no attribute")
        print('\n'*1)
        choice = input("       Ctrl-c was pressed. [c]continue [any-key] quit \n\n")
        if choice != 'c':
            os.kill(int(os.getpid()), signal.SIGTERM)
            os.system("clear")
            sys.exit(1)


def start_signal_handler(start: bool=False) ->None:
    if True:
        signal.signal(signal.SIGINT, signalHandler)
