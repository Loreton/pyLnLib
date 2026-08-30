from pathlib import Path
from typing import Optional, Union
import hashlib

def file_hash(filepath: Path, chunk_size: int = 8192) -> str:
    """Calculate file hash (SHA-256)."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def get_unique_filename_01(
    source_file: Union[Path, str],
    dest_dir: Union[Path, str],
    dest_filename: Optional[Union[Path, str]] = None,
    path_for_duplicated: Optional[Union[Path, str]] = None,
    suffix_pattern: str = "-{:03d}",
    start_index: int = 0
) -> Optional[Path]:
    """
    Return a unique filename for saving a file, checking for duplicates.

    Args:
        source_file: Path to the existing source file.
        dest_dir: Main destination directory.
        dest_filename: Optional destination filename (default: source_file.name).
        path_for_duplicated: If provided and file is duplicate, save in this directory.
        suffix_pattern: Pattern used for generated filenames.
        start_index: Starting index.
            0 checks the original filename first.
            1 starts with the first generated filename.

    Returns:
        The first available filename, or None if an identical file already exists.
    """

    if isinstance(source_file, str):
        source_file = Path(source_file)
    if isinstance(dest_dir, str):
        dest_dir = Path(dest_dir)
    if dest_filename is None:
        dest_filename = source_file.name
    elif isinstance(dest_filename, str):
        dest_filename = Path(dest_filename)

    if start_index < 0:
        raise ValueError("start_index must be >= 0")

    if not source_file.exists():
        raise FileNotFoundError(f"Source file not found: {source_file}")

    dest_dir.mkdir(parents=True, exist_ok=True)

    source_size = source_file.stat().st_size
    source_hash = file_hash(source_file)

    def is_duplicate(candidate: Path) -> bool:
        if not candidate.exists():
            return False
        if candidate.stat().st_size != source_size:
            return False
        return file_hash(candidate) == source_hash

    base_path = dest_dir / dest_filename.name

    if not base_path.exists():
        return base_path

    if is_duplicate(base_path):
        if path_for_duplicated is not None:
            alt_dir = Path(path_for_duplicated)
            alt_dir.mkdir(parents=True, exist_ok=True)

            stem = dest_filename.stem
            suffix = dest_filename.suffix
            parent = alt_dir

            index = max(1, start_index) if start_index >= 0 else 1

            while True:
                candidate = parent / f"{stem}{suffix_pattern.format(index)}{suffix}"

                if not candidate.exists():
                    return candidate

                if is_duplicate(candidate):
                    index += 1
                    continue

                return candidate
        else:
            return None
    else:
        return base_path






from pathlib import Path
from typing import Optional, Union
import hashlib

def file_hash(filepath: Path, chunk_size: int = 8192) -> str:
    """Calculate file hash (SHA-256)."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def get_unique_filename(
    source_file: Union[Path, str],
    dest_dir: Union[Path, str],
    dest_filename: Optional[Union[Path, str]] = None,
    path_for_duplicated: Optional[Union[Path, str]] = None,
    suffix_pattern: str = "-{:03d}",
    start_index: int = 0
) -> Optional[Path]:

    if isinstance(source_file, str):
        source_file = Path(source_file)
    if isinstance(dest_dir, str):
        dest_dir = Path(dest_dir)
    if dest_filename is None:
        dest_filename = source_file.name
    elif isinstance(dest_filename, str):
        dest_filename = Path(dest_filename)

    if start_index < 0:
        raise ValueError("start_index must be >= 0")

    if not source_file.exists():
        raise FileNotFoundError(f"Source file not found: {source_file}")

    dest_dir.mkdir(parents=True, exist_ok=True)

    source_size = source_file.stat().st_size
    source_hash = file_hash(source_file)

    print(f"DEBUG: Source file: {source_file}")
    print(f"DEBUG: Source size: {source_size}")
    print(f"DEBUG: Source hash: {source_hash[:16]}...")

    def is_duplicate(candidate: Path) -> bool:
        if not candidate.exists():
            return False
        if candidate.stat().st_size != source_size:
            return False
        return file_hash(candidate) == source_hash

    base_path = dest_dir / dest_filename.name
    print(f"DEBUG: base_path = {base_path}")
    print(f"DEBUG: base_path.exists() = {base_path.exists()}")

    if not base_path.exists():
        print(f"DEBUG: {base_path} non esiste, lo restituisco")
        return base_path

    if is_duplicate(base_path):
        print(f"DEBUG: {base_path} è IDENTICO!")
        if path_for_duplicated is not None:
            print(f"DEBUG: Uso path_for_duplicated = {path_for_duplicated}")
            alt_dir = Path(path_for_duplicated)
            alt_dir.mkdir(parents=True, exist_ok=True)

            stem = dest_filename.stem
            suffix = dest_filename.suffix
            parent = alt_dir

            start_idx = max(1, start_index) if start_index >= 0 else 1

            # FASE 1: Cerca se esiste un file identico con QUALSIASI indice
            print(f"DEBUG: FASE 1 - Cerco file identici in {alt_dir}")
            max_check = 1000

            for i in range(start_idx, start_idx + max_check):
                candidate = parent / f"{stem}{suffix_pattern.format(i)}{suffix}"
                if candidate.exists():
                    print(f"DEBUG: Checking: {candidate}")
                    if is_duplicate(candidate):
                        print(f"DEBUG: {candidate} è IDENTICO! Torno None")
                        return None
                    else:
                        print(f"DEBUG: {candidate} esiste ma è DIVERSO")

            # FASE 2: Nessun file identico trovato, cerca il primo indice disponibile
            print(f"DEBUG: FASE 2 - Nessun file identico trovato, cerco indice disponibile")
            index = start_idx
            while True:
                candidate = parent / f"{stem}{suffix_pattern.format(index)}{suffix}"
                print(f"DEBUG: Checking: {candidate}")
                print(f"DEBUG: candidate.exists() = {candidate.exists()}")

                if not candidate.exists():
                    print(f"DEBUG: {candidate} non esiste, lo restituisco")
                    return candidate
                else:
                    print(f"DEBUG: {candidate} esiste ma è DIVERSO, lo restituisco (sovrascrivo)")
                    return candidate
        else:
            print(f"DEBUG: path_for_duplicated è None, torno None")
            return None
    else:
        print(f"DEBUG: {base_path} esiste ma è DIVERSO, lo restituisco")
        return base_path


def get_unique_filename_02(
    source_file: Union[Path, str],
    dest_dir: Union[Path, str],
    dest_filename: Optional[Union[Path, str]] = None,
    path_for_duplicated: Optional[Union[Path, str]] = None,
    suffix_pattern: str = "-{:03d}",
    start_index: int = 0
) -> Optional[Path]:
    """
    Return a unique filename for saving a file, checking for duplicates.

    Args:
        source_file: Path to the existing source file.
        dest_dir: Main destination directory.
        dest_filename: Optional destination filename (default: source_file.name).
        path_for_duplicated: If provided and file is duplicate, save in this directory.
        suffix_pattern: Pattern used for generated filenames.
        start_index: Starting index.
            0 checks the original filename first.
            1 starts with the first generated filename.

    Returns:
        The first available filename, or None if an identical file already exists.
    """

    if isinstance(source_file, str):
        source_file = Path(source_file)
    if isinstance(dest_dir, str):
        dest_dir = Path(dest_dir)
    if dest_filename is None:
        dest_filename = source_file.name
    elif isinstance(dest_filename, str):
        dest_filename = Path(dest_filename)

    if start_index < 0:
        raise ValueError("start_index must be >= 0")

    if not source_file.exists():
        raise FileNotFoundError(f"Source file not found: {source_file}")

    dest_dir.mkdir(parents=True, exist_ok=True)

    source_size = source_file.stat().st_size
    source_hash = file_hash(source_file)

    def is_duplicate(candidate: Path) -> bool:
        if not candidate.exists():
            return False
        if candidate.stat().st_size != source_size:
            return False
        return file_hash(candidate) == source_hash

    base_path = dest_dir / dest_filename.name

    # CASO 1: Il file non esiste nella directory principale
    if not base_path.exists():
        return base_path

    # CASO 2: Il file esiste nella directory principale
    if is_duplicate(base_path):
        # È IDENTICO!
        if path_for_duplicated is not None:
            alt_dir = Path(path_for_duplicated)
            alt_dir.mkdir(parents=True, exist_ok=True)

            stem = dest_filename.stem
            suffix = dest_filename.suffix
            parent = alt_dir

            start_idx = max(1, start_index) if start_index >= 0 else 1

            # FASE 1: Cerca se esiste un file identico con QUALSIASI indice
            max_check = 1000
            found_duplicate = False

            for i in range(start_idx, start_idx + max_check):
                candidate = parent / f"{stem}{suffix_pattern.format(i)}{suffix}"
                if candidate.exists() and is_duplicate(candidate):
                    found_duplicate = True
                    break

            if found_duplicate:
                return None

            # FASE 2: Nessun file identico trovato, cerca il primo indice disponibile
            index = start_idx
            while True:
                candidate = parent / f"{stem}{suffix_pattern.format(index)}{suffix}"

                if not candidate.exists():
                    return candidate

                # Il file esiste ma è diverso (sappiamo che non è identico)
                return candidate
        else:
            return None
    else:
        # Il file esiste ma è DIVERSO, possiamo sovrascriverlo
        return base_path


if __name__ == "__main__":
    import shutil
    # Nel tuo codice epub_process
    source_file = Path("/home/loreto/filu/ln-eBooks/lnLibraries/test_01/Rose, Karen/Muori per me (10)/Muori per me - Rose, Karen.epub")  # Il file che stai elaborando
    dest_dir = Path("/home/loreto/filu/ln-eBooks/lnCollection/new/Karen, Rose")
    dest_filename = Path("Muori per me.epub")

    save_path = get_unique_filename(
        source_file=source_file,
        dest_dir=dest_dir,
        dest_filename=dest_filename,
        path_for_duplicated=dest_dir / "duplicated",
        start_index=0
    )

    if save_path is None:
        print("File identico già esistente, skip!")
    else:
        print(f"Saving to: {save_path}")
        # Copia/scrive il file in save_path
        shutil.copy2(source_file, save_path)
