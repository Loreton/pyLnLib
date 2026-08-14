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

def signalHandler(signalLevel, frame):
    ### Ctrl-c
    if int(signalLevel)==2:
        raise AttributeError(f"'__name__' object has no attribute")
        print('\n'*3)
        choice = input("       Ctrl-c was pressed. [c]continue [any-key] quit \n\n")
        if choice != 'c':
            os.kill(int(os.getpid()), signal.SIGTERM)
            os.system("clear")
            sys.exit(1)


def start_signal_handler(start: bool=False) ->None:
    if True:
        signal.signal(signal.SIGINT, signalHandler)
