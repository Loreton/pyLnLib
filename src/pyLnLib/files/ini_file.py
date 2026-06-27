#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 12-06-2026 14.14.15
#

import sys
sys.dont_write_bytecode = True
import os
from typing import  Optional

### --------------------
### --- project modules
### --------------------
from ..context    import gVars as gv
from .file_utils import searchFile


###############################################
#    I N I   - I N I   - I N I   -
###############################################

############  INI Files ###############################
def _iniSet():
    import configparser
    ini_config = configparser.ConfigParser(
        allow_no_value=False,
        delimiters=('=', ':'),
        comment_prefixes=('#',';'),
        inline_comment_prefixes=(';',),
        strict=True,          # True: impone unique key/session
        empty_lines_in_values=False,
        default_section='DEFAULT',
        interpolation=configparser.BasicInterpolation()
    )

    # mantiene il case nei nomi delle section e delle Keys ref: https://docs.python.org/3/library/configparser.html
    ini_config.optionxform = str # type: ignore

    return ini_config


###############################################
# Load INI file
###############################################
def loadIni(filepath: Optional[str]=None, content: Optional[str]=None, search_paths: list=[], exit_on_error: bool=True):
    my_search_paths = search_paths
    ini_dict = {}

    if filepath:  ### read content
        result = searchFile(filename=filepath, search_paths=my_search_paths, stacklevel=2)
        content = result.content
        if not result.filepath:
            gv.logger.error(f"File not found: {filepath}", exc_info=exit_on_error)

    if content:
        content = os.path.expandvars(content)
        ### -----------------------------
        ### if it's a ini file
        ### -----------------------------
        ini_config = _iniSet()
        ini_config.read_string(content)
        for section in ini_config.sections():
            ini_dict[section] = {}
            for option in ini_config.options(section):
                ini_dict[section][option] = ini_config.get(section, option)

    return ini_dict


###############################################
# Write INI file from dictionary
###############################################
def writeIni(ini_dict: dict, filepath: str, backup_original: bool = False):
    """
    Write a dictionary to an INI file.

    Args:
        ini_dict (dict): Dictionary with sections as keys and dictionaries of key-value pairs as values
                         Example: {'section1': {'key1': 'value1', 'key2': 'value2'}, 'section2': {...}}
        filepath (str): Path where to save the INI file
        backup_original (bool): If True and file exists, create a backup with .bak extension

    Returns:
        bool: True if successful, False otherwise
    """
    # import configparser
    import shutil
    # from datetime import datetime

    # Validate input
    if not isinstance(ini_dict, dict):
        gv.logger.error(f"Expected dict, got {type(ini_dict)}")
        return False

    if not filepath:
        gv.logger.error("No filepath provided")
        return False

    # Create backup if file exists and backup_original is True
    if backup_original and os.path.exists(filepath):
        try:
            backup_path = f"{filepath}.bak"
            shutil.copy2(filepath, backup_path)
            gv.logger.info(f"Backup created: {backup_path}")
        except Exception as e:
            gv.logger.warning(f"Could not create backup: {e}")

    # Create ConfigParser instance
    ini_config = _iniSet()

    # Populate ConfigParser with dictionary data
    for section, section_data in ini_dict.items():
        if not isinstance(section_data, dict):
            gv.logger.warning(f"Section '{section}' is not a dict, skipping")
            continue

        # Add section if it doesn't exist
        if not ini_config.has_section(section):
            ini_config.add_section(section)

        # Add key-value pairs
        for key, value in section_data.items():
            # Convert value to string (configparser expects strings)
            ini_config.set(section, str(key), str(value) if value is not None else '')

    # Write to file
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            ini_config.write(f)

        gv.logger.info(f"INI file successfully written to: {filepath}")
        return True

    except Exception as e:
        gv.logger.error(f"Error writing INI file {filepath}: {e}")
        return False


###############################################
# Update specific section/key in INI file
###############################################
def updateIniKey(filepath: str, section: str, key: str, value: str, create_backup: bool = True):
    """
    Update a specific key in an INI file without rewriting the entire dictionary.

    Args:
        filepath (str): Path to the INI file
        section (str): Section name
        key (str): Key to update
        value (str): New value
        create_backup (bool): Whether to create a backup before modifying

    Returns:
        bool: True if successful, False otherwise
    """
    # Load existing INI
    ini_dict = loadIni(filepath=filepath, exit_on_error=False)

    if not ini_dict:
        gv.logger.error(f"Could not load INI file: {filepath}")
        return False

    # Update the specific key
    if section not in ini_dict:
        ini_dict[section] = {}

    ini_dict[section][key] = value

    # Write back
    return writeIni(ini_dict, filepath, backup_original=create_backup)


def mergeIni(ini_dict: dict, filepath: str, overwrite_existing: bool = False):
    """Merge dictionary with existing INI file"""
    existing_dict = loadIni(filepath=filepath, exit_on_error=False)

    if existing_dict:
        for section, section_data in ini_dict.items():
            if section not in existing_dict:
                existing_dict[section] = {}
            for key, value in section_data.items():
                if overwrite_existing or key not in existing_dict[section]:
                    existing_dict[section][key] = value
        return writeIni(existing_dict, filepath)
    else:
        return writeIni(ini_dict, filepath)
