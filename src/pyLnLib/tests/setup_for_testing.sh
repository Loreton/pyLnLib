#!/bin/bash
#
# updated by ...: Loreto Notarantonio
# Date .........: 22-06-2026 19.50.16
#


# setup_for_testing.sh

# Usa export per esportare la variabile
export PYTHONPATH="/home/loreto/filu/Programming/gitREPO/pyLnLib/src:$PYTHONPATH"

# Verifica
echo "PYTHONPATH set to: $PYTHONPATH"
echo "Environment variable PYTHONPATH:"
env | grep PYTHONPATH