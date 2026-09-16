# by Loreto Notarantonio


# ruff: noqa: I001 - Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
from __future__ import annotations
from pathlib import Path
import os
from posix import link


from ..logger import get_logger
logger = get_logger()


def is_valid_link(source_file: str|Path, link_name: str|Path, log_it: int=logger.log_NOLOG) -> tuple(int, bool):
    link_name=Path(link_name)
    source_file=Path(source_file)
    f_is_valid: bool = False
    r_code: int = 0

    # Leggi il target attuale del symlink (così com'è salvato su disco)
    relative_target = os.path.relpath(source_file, start=link_name.parent)
    STACK_LEVEL = 1
    # Se esiste già qualcosa (file o symlink)  link_name.exist()
    if link_name.is_symlink():

        # Confronto "raw" (stringa salvata) + confronto "risolto" (path reale)
        current_target = os.readlink(link_name)
        if current_target == relative_target or link_name.resolve() == source_file.resolve():
            logger.info("link is already pointing right:\n%s -> %s", link_name, current_target, stacklevel=STACK_LEVEL, log_it=log_it)
            f_is_valid = True

        else:
            logger.warning("skipping, already exists pointing to a different target: %s", link_name, stacklevel=STACK_LEVEL, log_it=log_it)
            r_code = 1

    elif link_name.is_file():
        logger.warning("link name already exists but it is a file: %s", link_name, stacklevel=STACK_LEVEL, log_it=log_it)
        r_code = 2

    elif link_name.is_dir():
        logger.warning("link name already exists but it is a directory: %s", link_name, stacklevel=STACK_LEVEL, log_it=log_it)
        r_code = 3

    elif link_name.exists():
        logger.warning("link name already exists but it is something else: %s", link_name, stacklevel=STACK_LEVEL, log_it=log_it)
        r_code = 4

    else:
        logger.warning("link name not exists: %s", link_name, stacklevel=STACK_LEVEL, log_it=log_it)
        # breakpoint()
        r_code = 0

    return r_code, f_is_valid



def create_link(source_file: str|Path, link_name: str|Path, replace: bool, log_it: int=logger.log_NOLOG) -> bool:
    link_name=Path(link_name)
    source_file=Path(source_file)
    STACK_LEVEL=1
    # Leggi il target attuale del symlink (così com'è salvato su disco)
    relative_target = os.path.relpath(source_file, start=link_name.parent)
    rcode, is_valid = is_valid_link(source_file=source_file, link_name=link_name, log_it=log_it)
    if rcode==0 and is_valid is False:
        link_name.parent.mkdir(parents=True, exist_ok=True)
        link_name.symlink_to(relative_target)
        logger.notify("link name as been created: %s", link_name, stacklevel=STACK_LEVEL, log_it=log_it)
        return True
    else:
        logger.error("error creating link: %s", link_name)
    return False



# def create_link_(source_file: str|Path, link_name: str|Path, replace: bool, log_it: int=logger.log_NOLOG) -> bool:
#     link_name=Path(link_name)
#     source_file=Path(source_file)
#     fCreate = False

#     # Leggi il target attuale del symlink (così com'è salvato su disco)
#     relative_target = os.path.relpath(source_file, start=link_name.parent)

#     # Se esiste già qualcosa (file o symlink)  link_name.exist()
#     if link_name.is_symlink():

#         # Confronto "raw" (stringa salvata) + confronto "risolto" (path reale)
#         current_target = os.readlink(link_name)

#         if current_target == relative_target or link_name.resolve() == source_file.resolve():
#             logger.info("link is already pointing right:\n%s -> %s", link_name, current_target, log_it=log_it)

#         if replace:
#             link_name.unlink()
#             fCreate = True
#         else:
#             logger.warning("skipping, already exists pointing to a different target: %s", link_name, log_it=log_it)

#     elif link_name.exists():
#         logger.warning("link name already exists but is not a symlink: %s", link_name, log_it=log_it)

#     if fCreate:
#         link_name.parent.mkdir(parents=True, exist_ok=True)
#         link_name.symlink_to(relative_target)
#         logger.warning("link name as been created: %s", link_name, log_it=log_it)
#         breakpoint()

#     return fCreate
