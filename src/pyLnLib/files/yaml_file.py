#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# ruff: noqa: I001 - Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
#

import sys; sys.dont_write_bytecode = True
import yaml
from pathlib import Path
from datetime import datetime


### --------------------
### --- project modules
### --------------------
from ..logger    import get_logger
logger = get_logger()

###############################################
#    Y A M L  -  Y A M L  -  Y A M L  -
###############################################


def dictToYaml(data: dict, filepath: str | Path) -> str:
    yaml_string = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, )

    Path(filepath).write_text(yaml_string, encoding="utf-8")

    logger.notify("file: [%s] has been written", filepath)
    return yaml_string


def dictToYaml(mydict: dict, title: str="", filepath: Path|str="", **kwargs) -> str:
    """Converte lnDict in una stringa YAML pulita.
        title: se valorizzato viene messo come main_key in testa al dict
    """
    # d={title: d.to_dict()} if title else d.to_dict()
    d={title: mydict} if title else mydict
    replace            = kwargs.pop("replace", False)
    indent             = kwargs.pop("indent", 4)
    sort_keys          = kwargs.pop("sort_keys", False)
    default_flow_style = kwargs.pop("default_flow_style", False)

    yaml_string = yaml.safe_dump(d, indent=indent, sort_keys=sort_keys,  default_flow_style=default_flow_style, **kwargs)
    if filepath:
        filepath=Path(filepath)
        # ruff: noqa: DTZ005 `datetime.datetime.now()` called without a `tz` argument help: Pass a `datetime.timezone` object to the `tz` parameter (Ruff DTZ005)
        now = datetime.now().strftime("%d-%m-%Y_%H:%M")
        _cmnt=f"#{'-'*20}"
        yaml_string = f"{_cmnt}\n#- {now}\n{_cmnt}\n{yaml_string}"
        if not filepath.exists():
            replace=True

        if replace:
            Path(filepath).write_text(yaml_string, encoding="utf-8")
            # with open(filepath, 'w', encoding='utf-8') as f:
            #     f.write(yaml_data)


        # self.logger.notify("lnd_file: [%s] has been written", filepath, stacklevel=stacklevel, show_stack=False)
        logger.notify("file: [%s] has been written", filepath, show_stack=False)


# #############################################################################
# # title: se valorizzato viene messo in testa al dict
# #  utile per avere un'idea di massima del contenuto del dictionary
# #############################################################################
# def saveDictAsYaml(filepath, mydict: dict, title: str='', **kwargs) -> None:
#     """Salva lo lnDict in un file .yaml."""
#     yaml_data = dictToYaml(mydict=mydict, title=title, **kwargs)
#     now = datetime.now(tz=datetime.UTC).strftime("%d-%m-%Y_%H:%M")
#     _cmnt=f"#{'-'*20}"
#     yaml_data = f"{_cmnt}\n#- {now}\n{_cmnt}\n{yaml_data}"
#     with open(filepath, 'w', encoding='utf-8') as f:
#         f.write(yaml_data)

#     # self.logger.notify("lnd_file: [%s] has been written", filepath, stacklevel=stacklevel, show_stack=False)
#     logger.notify("file: [%s] has been written", filepath, show_stack=False)
