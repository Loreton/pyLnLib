#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 01-05-2026 09.54.12
#


#################################
#    Ctrl-C capture
###################################################
import signal, os, sys
def signalHandler(signalLevel, frame):
    ### Ctrl-c
    if int(signalLevel)==2:
        print('\n'*3)
        choice = input("       Ctrl-c was pressed. [q]quit [any-key] restart \n\n")
        if choice == 'q':
            os.kill(int(os.getpid()), signal.SIGTERM)
            os.system("clear")
            sys.exit(1)

if False: ###. disabilitato perché non funziona bene
    signal.signal(signal.SIGINT, signalHandler)
