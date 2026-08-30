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





import tempfile
import shutil

def run_comprehensive_test():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Crea il file sorgente
        source_file = temp_path / "source.txt"
        with open(source_file, 'w') as f:
            f.write("Contenuto originale\n")

        # Directory principale
        dest_dir = temp_path / "dest"
        dest_dir.mkdir()

        # Directory per duplicati
        dup_dir = dest_dir / "duplicated"
        dup_dir.mkdir()

        print("=" * 60)
        print("TEST 1: File non esiste")
        result = get_unique_filename(
            source_file=source_file,
            dest_dir=dest_dir,
            dest_filename=Path("test.txt"),
            path_for_duplicated=dup_dir,
            start_index=0
        )
        print(f"RESULT: {result}\n")

        # Copia nella directory principale
        shutil.copy2(source_file, dest_dir / "test.txt")

        print("=" * 60)
        print("TEST 2: File identico in principale → va in duplicated/")
        result = get_unique_filename(
            source_file=source_file,
            dest_dir=dest_dir,
            dest_filename=Path("test.txt"),
            path_for_duplicated=dup_dir,
            start_index=0
        )
        print(f"RESULT: {result}\n")

        # Copia in duplicated/
        shutil.copy2(source_file, dup_dir / "test-001.txt")

        print("=" * 60)
        print("TEST 3: File identico anche in duplicated/ → torna None")
        result = get_unique_filename(
            source_file=source_file,
            dest_dir=dest_dir,
            dest_filename=Path("test.txt"),
            path_for_duplicated=dup_dir,
            start_index=0
        )
        print(f"RESULT: {result}\n")
        # Dovrebbe: None (perché test-001.txt è identico)

        # Crea un file diverso in duplicated/
        with open(dup_dir / "test-002.txt", 'w') as f:
            f.write("Contenuto diverso\n")

        print("=" * 60)
        print("TEST 4: File diverso in duplicated/ → lo usa")
        result = get_unique_filename(
            source_file=source_file,
            dest_dir=dest_dir,
            dest_filename=Path("test.txt"),
            path_for_duplicated=dup_dir,
            start_index=0
        )
        print(f"RESULT: {result}\n")
        # Dovrebbe: duplicated/test-002.txt (sovrascrive il diverso)

        # Crea un altro file diverso in duplicated/
        with open(dup_dir / "test-003.txt", 'w') as f:
            f.write("Contenuto diverso ancora\n")

        print("=" * 60)
        print("TEST 5: File diverso con gap (001 identico, 002 diverso, 003 diverso)")
        result = get_unique_filename(
            source_file=source_file,
            dest_dir=dest_dir,
            dest_filename=Path("test.txt"),
            path_for_duplicated=dup_dir,
            start_index=0
        )
        print(f"RESULT: {result}\n")
        # Dovrebbe: duplicated/test-002.txt (il primo diverso disponibile)

if __name__ == "__main__":
    run_comprehensive_test()
