#!/usr/bin/env python3

# updated by ...: Loreto Notarantonio
# Date .........: 15-05-2026 18.05.33


import sys
import fcntl

##################################################
# verifica se il programma è già attivo:
#       lock = acquire_lock(filename="/tmp/ssh_tunnel_watchdog.lock")
#   Se già attivo → errore immediato.
##################################################
def acquire_lock(filename: str):
    # lockfile = open(filename, "w")
    # fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
    # return lockfile

    try:
        lockfile = open(filename, "w")
        fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lockfile

    except BlockingIOError as e:
        print(f"\tERROR: {str(e)}")
        print(f"\tERROR: probabilmente un'altra istanza è già attiva!")
        sys.exit(1)

    except Exception as e:
        print(f"\tERROR: {str(e)}")
        sys.exit(1)

    # close(lockfile)
    # return lockfile
