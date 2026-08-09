#!/usr/bin/env python3
# ruff: noqa: I001 Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
# ruff: noqa: RUF022 `__all__` is not sorted help: Apply an isort-style sorting to `__all__` (Ruff RUF022)
# ruff_: noqa: E402 Module level import not at top of file (Ruff E402)

# updated by ...: Loreto Notarantonio
#

import os

"""
Calibre Processor Package
A package for processing EPUB files on calibre metadata db
"""


from .calibre_metadata_reader import CalibreMetadataReader, calibre_test



__all__ = [
    'CalibreMetadataReader',
    "calibre_test",
]
