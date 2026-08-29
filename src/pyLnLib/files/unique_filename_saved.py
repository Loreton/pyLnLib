#!/usr/bin/env python3
# ruff: noqa: SIM102 Use a single `if` statement instead of nested `if` statements help: Combine `if` statements using `and` (Ruff SIM102)
# ruff: noqa: I001 Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
#
# updated by ...: Loreto Notarantonio

#
from __future__ import annotations

import sys

import os
# import stat
import zipfile
from pathlib import Path
from hashlib import sha256








def file_hash(filename: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 hash of a file."""

    digest = sha256()

    with filename.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()


def get_unique_filename_2( filename: Path, suffix_pattern: str = "-{:03d}", start_index:int = 0 ) -> Path | None:
    """Return a unique filename, or None if an identical file exists.

    The original filename is returned if it does not exist.

    If the filename already exists, existing files with the same
    stem/suffix are checked:

    1. Files with a different size are ignored.
    2. Files with the same size are compared using SHA-256.
    3. If an identical file is found, None is returned.
    4. Otherwise, the first available filename is returned.

    Example:
        report.txt
        report-001.txt
        report-002.txt
        ...
    """
    filename = Path(filename)

    if start_index > 0:
        """
            nel folder "duplicated" mi fa comodo partire da 1,
            per distinguerlo dal primo file nella dir di sopra        filename = filename.parent / (
        """
        index = start_index
        candidate = filename.parent / (
            filename.stem +
            suffix_pattern.format(index) +
            filename.suffix
        )
    else:
        index = 1
        candidate = filename

    if not candidate.exists():
        return candidate

    file_size = candidate.stat().st_size
    file_digest = file_hash(candidate)

    stem = candidate.stem
    suffix = candidate.suffix
    parent = candidate.parent

    first_run: bool = True
    while True:
        if first_run:
            first_run = False
        else:
            candidate = parent / (
                stem +
                suffix_pattern.format(index) +
                suffix
            )

        if not candidate.exists():
            return candidate

        # Fast check: different size means different content
        if candidate.stat().st_size != file_size:
            index += 1
            continue

        # Same size: now perform the definitive comparison
        if file_hash(candidate) == file_digest:
            return None

        index += 1



def get_unique_filename_on_alternative_path(filename: Path|str, suffix_pattern: str = "-{:03d}", start_index: int = 0) -> Path | None:
    """Return a unique filename, or None if an identical file exists.

    Args:
        filename: Original filename.
        suffix_pattern: Pattern used for generated filenames.
        start_index: Starting index.
            0 checks the original filename first.
            1 starts with the first generated filename.

    Returns:
        The first available filename, or None if an identical file already exists.

    Example:
        start_index=0:
            report.txt
            report-001.txt
            report-002.txt

        start_index=1:
            report-001.txt
            report-002.txt
            report-003.txt
    """

    if isinstance(filename, str):
        filename = Path(filename)

    if not filename.exists():
        return filename

    if start_index < 0:
        raise ValueError("start_index must be >= 0")

    file_size = filename.stat().st_size
    file_digest = file_hash(filename)

    stem = filename.stem
    suffix = filename.suffix
    parent = filename.parent

    index = start_index

    while True:
        if index == 0:
            candidate = filename
        else:
            candidate = parent / ( stem + suffix_pattern.format(index) + suffix )

        if not candidate.exists():
            return candidate

        # Fast check: different size means different content
        if candidate.stat().st_size == file_size:
            # Same size: definitive comparison
            if file_hash(candidate) == file_digest: # it's identical/same file
                return None

        index += 1





def get_unique_filename(filename: Path|str, path_for_duplicated: Path|str|None=None, suffix_pattern: str = "-{:03d}", start_index: int = 0) -> Path | None:
    """Return a unique filename, or None if an identical file exists.

    Args:
        filename: Original filename.
        suffix_pattern: Pattern used for generated filenames.
        start_index: Starting index.
            0 checks the original filename first.
            1 starts with the first generated filename.

    Returns:
        The first available filename, or None if an identical file already exists.

    Example:
        start_index=0:
            report.txt
            report-001.txt
            report-002.txt

        start_index=1:
            report-001.txt
            report-002.txt
            report-003.txt
    """

    if isinstance(filename, str):
        filename = Path(filename)

    if not filename.exists():
        return filename

    if start_index < 0:
        raise ValueError("start_index must be >= 0")

    file_size = filename.stat().st_size
    file_digest = file_hash(filename)

    stem = filename.stem
    suffix = filename.suffix
    parent = filename.parent

    index = start_index

    while True:
        if index == 0:
            candidate = filename
        else:
            candidate = parent / ( stem + suffix_pattern.format(index) + suffix )

        if not candidate.exists():
            return candidate

        # Fast check: different size means different content
        if candidate.stat().st_size == file_size:
            # Same size: definitive comparison
            if file_hash(candidate) == file_digest: # it's identical/same file
                if path_for_duplicated:
                    return  get_unique_filename_on_alternative_path(
                                    filename=Path(path_for_duplicated) / filename.name,
                                    suffix_pattern=suffix_pattern,
                                    start_index=1)
                # return None

        index += 1


def get_unique_filename_ok(filename: Path|str, suffix_pattern: str = "-{:03d}", start_index: int = 0) -> Path | None:
    """Return a unique filename, or None if an identical file exists.

    Args:
        filename: Original filename.
        suffix_pattern: Pattern used for generated filenames.
        start_index: Starting index.
            0 checks the original filename first.
            1 starts with the first generated filename.

    Returns:
        The first available filename, or None if an identical file already exists.

    Example:
        start_index=0:
            report.txt
            report-001.txt
            report-002.txt

        start_index=1:
            report-001.txt
            report-002.txt
            report-003.txt
    """

    if isinstance(filename, str):
        filename = Path(filename)

    if not filename.exists():
        return filename

    if start_index < 0:
        raise ValueError("start_index must be >= 0")

    file_size = filename.stat().st_size
    file_digest = file_hash(filename)

    stem = filename.stem
    suffix = filename.suffix
    parent = filename.parent

    index = start_index

    while True:
        if index == 0:
            candidate = filename
        else:
            candidate = parent / ( stem + suffix_pattern.format(index) + suffix )

        if not candidate.exists():
            return candidate

        # Fast check: different size means different content
        if candidate.stat().st_size == file_size:
            # Same size: definitive comparison
            if file_hash(candidate) == file_digest: # it's identical/same file
                return None

        index += 1
