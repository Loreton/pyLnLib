#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 22-06-2026 21.32.56
#
from __future__ import annotations

from ast import alias
import shlex
import subprocess
from pathlib import Path


class Bash:
    def __init__(self, init_file: str | Path | None = None, cwd: str | Path | None = None):
        self.init_file = Path(init_file).expanduser() if init_file else None
        self.cwd = Path(cwd).expanduser() if cwd else None


    def run(self, command: str, cwd: str | Path | None = None) -> subprocess.CompletedProcess:
        """
        Esegue un comando bash dopo aver eventualmente caricato un file.
        """
        script = ""

        if self.init_file:
            script += f"source {shlex.quote(str(self.init_file))}\n"

        script += command

        return subprocess.run(
            ["bash", "-c", script],
            cwd=cwd or self.cwd,
            capture_output=True,
            text=True,
        )

    def eval(self, command: str) -> str:
        """
        Restituisce stdout oppure solleva RuntimeError.
        """
        result = self.run(command, self.cwd)

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())

        return result.stdout.strip()

    def try_eval(self, command: str, cwd=None) -> tuple[bool, str]:
        result = self.run(command, cwd)

        if result.returncode:
            return False, result.stderr.strip()

        return True, result.stdout.strip()

    def alias(self, name: str) -> str | None:
        result = self.run(f"alias {shlex.quote(name)}")

        if result.returncode:
            return None

        line = result.stdout.strip()

        _, value = line.split("=", 1)

        return shlex.split(value)[0] if False else value.strip("'")

    def variable(self, name: str) -> str | None:
        result = self.run(f'printf "%s" "${{{name}}}"')

        if result.returncode:
            return None

        return result.stdout.strip()

    def function(self, name: str) -> str | None:
        result = self.run(f"declare -f {shlex.quote(name)}")

        if result.returncode:
            return None

        return result.stdout


    def type(self, name: str) -> str:
        return self.eval(f"type {shlex.quote(name)}")


if __name__ == "__main__":
    bash = Bash()
    # import pdb; pdb.set_trace();  # by Loreto
    print(bash.type("ls"))

    bash = Bash("~/.loreto_setup", cwd="/home/loreto/filu/lnEnv")
    cfg_dir = bash.variable("ln_HOST_CONFIG_DIR")
    lnEnv_dir = bash.variable("ln_ENV_DIR")
    ln_SET_LORETO_ENVIRONMENT = bash.variable("ln_SET_LORETO_ENVIRONMENT")
    host = bash.eval("hostname")
    git_root = bash.eval("git rev-parse --show-toplevel")
    print(  f"\t{cfg_dir                   = }\n"
            f"\t{lnEnv_dir                 = }\n"
            f"\t{ln_SET_LORETO_ENVIRONMENT = }\n"
            f"\t{host                      = }\n"
            f"\t{git_root                  = }")


    function_data = bash.function("@createLink")
    # print("function @createLink -->", function_data)

    ok, root = bash.try_eval("git rev-parse --show-toplevel")

    if ok:
        print(root)
    else:
        print("Non sono in un repository Git")

    alias_name = '.zed'
    print(f"alias {alias_name} -->", bash.alias(alias_name))
