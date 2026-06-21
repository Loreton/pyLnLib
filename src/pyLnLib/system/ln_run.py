#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 09-06-2026 18.46.39
#


import sys

sys.dont_write_bytecode = True
import os
import shlex
import subprocess
from types import SimpleNamespace
from typing import Any, Callable, Optional

### - project modules
# from pyLnLib import DummyPrintLogger
# from pyLnLib import Color
from ..colors import Color
from ..logger.dummy_logger import DummyPrintLogger


# ##################################################
# # lnRun
# ##################################################
def lnRun(
    command: str | list,
    cwd: Optional[str] = None,
    exit_on_error: bool = False,
    stacklevel: int = 0,
    fExecute: bool = False,
    timeout: int = 15,
    toLogger: Optional[DummyPrintLogger] = None,
) -> tuple[int, str, str]:

    lnRun_STACKLEVEL = stacklevel
    lnRun_STACKLEVEL = 0
    logger: LoggerLike = toLogger or DummyPrintLogger()
    result: SimpleNamespace = SimpleNamespace(rcode=0, stdout="", stderr="")

    command_args = shlex.split(command) if isinstance(command, str) else command
    str_command = " ".join(command_args)

    # logger.info(f"[{'executing' if fExecute else 'dry-run'}] {str_command}", color=Color.blueH)
    logger.info(str_command, dry_run=(not fExecute))

    if fExecute:
        try:
            p = subprocess.run(
                command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
                timeout=timeout,
            )
            result.rcode = p.returncode
            result.stdout = p.stdout
            result.stderr = p.stderr

            # log stdout
            if result.stdout:
                for line in result.stdout.splitlines():
                    logger.debug(line, color=Color.blue)

            # log stderr
            if result.stderr:
                for line in result.stderr.splitlines():
                    logger.error(line, color=Color.redH)

            if result.rcode != 0 and exit_on_error:
                raise SystemExit(result.rcode)

        except Exception as e:
            logger.error(f"Exception: {e}", color=Color.redH)
            if exit_on_error:
                raise SystemExit(1)

    return result.rcode, result.stdout, result.stderr


if __name__ == "__main__":
    from utils.logger_colored_simple import LoggerColoredSimple
    # from utils.logger_types import DummyLogger
    # from utils.colors import Color
    # from utils.subprocess_run import lnRun

    # Creazione di un logger colorato
    logger = LoggerColoredSimple("MainLogger", level="DEBUG")

    # Esempio di log dinamico
    logger.debug("Debug dinamico!", color=Color.cyan)
    logger.info("Informazione importante", color=Color.green)
    logger.warning("Attenzione!", color=Color.yellow)
    logger.error("Errore!", color=Color.red)
    logger.critical("Critico!", color=Color.magenta)
    logger.notify("Notifica speciale", color=Color.blue)

    # Esempio di comando
    rc, out, err = lnRun("echo Ciao mondo!", fExecute=True, toLogger=logger)

    logger.info(f"Return code: {rc}", color=Color.cyan)


"""
    Come usarlo nei tuoi moduli
    from utils import LoggerColoredSimple, DummyLogger, Color, lnRun

    # fallback logger
    logger = DummyLogger()

    # o logger colorato
    logger = LoggerColoredSimple("ModuloX", level="INFO")

    logger.info("Messaggio con colore dinamico", color=Color.greenH)

    # eseguire comandi
    lnRun("ls -l", fExecute=True, toLogger=logger)
"""
