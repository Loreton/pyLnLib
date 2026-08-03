"""
Calibre Processor Package
A package for processing EPUB files on calibre metadata db
"""


from .calibre import CalibreMetadataReader

__all__ = [
    'CalibreMetadataReader',
]
