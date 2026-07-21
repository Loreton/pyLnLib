#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 19-07-2026 11.25.09
#


# import sys
# sys.dont_write_bytecode = True

# import os
import shlex
import subprocess
from types import SimpleNamespace
# from typing import Optional

### - project modules
from ..colors import get_colors
from ..logger import get_logger
C = get_colors()
logger = get_logger()


# ##################################################
# # lnRun
# ##################################################
def lnRun(
            command: str | list,
            cwd: str|None = None,
            exit_on_error: bool = False,
            stacklevel: int = 0,
            f_execute: bool = False,
            timeout: int = 15,
            logger_level: str = "warning", # questo pervitare di scrivere se non richiesto
            shell: bool = False,
        ) -> tuple[int, str, str]:

    result: SimpleNamespace = SimpleNamespace(rcode=0, stdout="", stderr="")

    command_args = shlex.split(command) if isinstance(command, str) else command
    str_command = " ".join(command_args)

    saved_logger_level = logger.getConsoleLoggerLevel()
    logger.setConsoleLoggerLevel(logger_level)
    logger.notify(f"[{'executing' if f_execute else 'dry-run'}] {str_command}", stacklevel=stacklevel+1)



    if f_execute:
        try:
            p = subprocess.run(
                command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
                timeout=timeout,
                shell=shell,
            )
            result.rcode = p.returncode
            result.stdout = p.stdout
            result.stderr = p.stderr

            # log stdout
            if result.stdout:
                for line in result.stdout.splitlines():
                    logger.debug(line, color=C.blue)

            # log stderr
            if result.stderr:
                logger.error(f"executing: {str(command)}", color=C.blueH, show_caller=True)
                for line in result.stderr.splitlines():
                    logger.error(line, color=C.redH, show_caller=True)

            if result.rcode != 0 and exit_on_error:
                raise SystemExit(result.rcode)

        except Exception as e:
            logger.error(f"Exception: {e}", color=C.redH, show_caller=True)
            if exit_on_error:
                raise SystemExit(1)

    logger.setConsoleLoggerLevel(saved_logger_level)
    return result.rcode, result.stdout, result.stderr


if __name__ == "__main__":
    # from utils.logger_colored_simple import LoggerColoredSimple
    # from utils.logger_types import DummyLogger
    # from utils.colors import Color
    # from utils.subprocess_run import lnRun

    # Creazione di un logger colorato
    # logger = LoggerColoredSimple("MainLogger", level="DEBUG")

    # # Esempio di log dinamico
    # logger.debug("Debug dinamico!", color=Color.cyan)
    # logger.info("Informazione importante", color=Color.green)
    # logger.warning("Attenzione!", color=Color.yellow)
    # logger.error("Errore!", color=Color.red)
    # logger.critical("Critico!", color=Color.magenta)
    # logger.notify("Notifica speciale", color=Color.blue)

    # Esempio di comando
    rc, out, err = lnRun("echo Ciao mondo!", fExecute=True)

    logger.info(f"Return code: {rc}", color=C.cyan)


"""
    # eseguire comandi
    lnRun("ls -l", fExecute=True, toLogger=logger)
"""
