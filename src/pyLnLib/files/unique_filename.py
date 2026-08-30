from pathlib import Path
import hashlib

from pyLnLib.logger import get_logger
logger=get_logger()




# #########################################################à
#   Riassunto della logica finale:
#
#   def get_unique_filename(candidate=filename):
#
#       if candidate.exists()
#           if is_duplicated()
#               ritorna None
#
#           elif path_for_duplicated:
#               Controlla TUTTI i file in duplicated/
#               Se ALMENO uno è identico:
#                   return None
#               else:
#                   cerca il primo indice disponibile
#                   ritornalo come candidate
#           else:
#               ritornalo come candidate
#
#        else:
#            ritornalo come candidate
#
#
# #########################################################à

def file_hash(filepath: Path, chunk_size: int = 8192) -> str:
    """Calculate file hash (SHA-256)."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_unique_filename(source_file: Path|str,
                        dest_dir: Path|str,
                        dest_filename: Path|str|None = None,
                        path_for_duplicated: Path|str|None = None,
                        suffix_pattern: str = "-{:03d}",
                        start_index: int = 0
                        ) -> Path|None:

    # ==============================================
    def is_duplicate(candidate: Path|str) -> bool:
        """
            Check if the candidate file is a duplicate of the source file.
        """
        candidate=Path(candidate)
        if not candidate.exists():
            return False
        if candidate.stat().st_size != source_size:
            return False
        return file_hash(candidate) == source_hash

    # ==============================================
    def get_files_with_prefix(directory, prefix):
        """Restituisce lista di file (fullpath) che iniziano con il prefisso usando pathlib"""
        path = Path(directory)
        files = [path / f.name for f in path.iterdir()
                if f.is_file() and f.name.startswith(prefix)]
        return files

    # ==============================================

    # ----- controlli di base
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


    source_size = source_file.stat().st_size
    source_hash = file_hash(source_file)

    logger.info(f"Source file: {source_file}")
    logger.info(f"Source size: {source_size}")
    logger.info(f"Source hash: {source_hash[:16]}...")

    # ----- verifica sulla destinazione primaria
    dest_dir.mkdir(parents=True, exist_ok=True)
    base_path = dest_dir / dest_filename.name
    logger.debug(f"{base_path = }")
    logger.debug(f"{base_path.exists() = }")


    # ------------------------------------
    # L'obiettivo è quello di non avere file identici salvati
    # ------------------------------------
    # - esiste ma anche duplicato
    if base_path.exists():
        if is_duplicate(base_path):
            logger.notify(f"{base_path} exists and it's IDENTICAL!")
            return None

        elif path_for_duplicated:
            """ Cerchiamo nel duplicate directory"""
            logger.info(f"proviamo nel {path_for_duplicated = }")
            alt_dir = Path(path_for_duplicated)
            alt_dir.mkdir(parents=True, exist_ok=True)

            stem = dest_filename.stem
            suffix = dest_filename.suffix
            parent = alt_dir


            # FASE 1: Cerca se esiste un file identico con QUALSIASI indice
            logger.debug(f"FASE 1 - Cerco file identici in {alt_dir}")
            max_check = 1000


            file_list=get_files_with_prefix(directory=parent, prefix=stem)

            #  ---- vediamo se tra quelli che esistono ce ne è uno identico...
            for file in file_list:
                if is_duplicate(file):
                    logger.notify(f"{file} exists and it's IDENTICAL!")
                    return None

            else:
                # FASE 2: Nessun file identico trovato, cerca il primo indice disponibile
                index = max(1, start_index) if start_index >= 0 else 1
                while True:
                    candidate = parent / f"{stem}{suffix_pattern.format(index)}{suffix}"
                    if not candidate.exists():
                        logger.notify(f"{candidate} doesn't exist, return it as candidate!")
                        return candidate
        else:
            """ non avendo specificato il path_for_duplicate è come se chiedesse un replace..."""
            logger.info(f"{base_path} exists but it's DIFFERENT. return as candidate!")
            return base_path
    else:
        logger.info(f"{base_path} doesn't exist, return it as candidate!")
        return base_path











if __name__ == "__main__":
    import shutil
    # Nel tuo codice epub_process
    source_file1 = Path("/home/loreto/filu/ln-eBooks/lnLibraries/test_01/Rose, Karen/Muori per me (10)/Muori per me - Rose, Karen.epub")  # Il file che stai elaborando
    source_file2 = Path("/home/loreto/filu/ln-eBooks/lnLibraries/test_01/Rose, Karen/Muori per me (24)/Muori per me - Rose, Karen.epub")  # Il file che stai elaborando
    source_file = source_file2
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
