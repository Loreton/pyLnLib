#!/usr/bin/env python3

# updated by ...: Loreto Notarantonio
# Date .........: 10-05-2026 09.43.23



import fcntl

##################################################
# verifica se il programma è già attivo:
#       lock = acquire_lock(filename="/tmp/ssh_tunnel_watchdog.lock")
#   Se già attivo → errore immediato.
##################################################
def acquire_lock(filename: str):
    lockfile = open(filename, "w")
    fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return lockfile


