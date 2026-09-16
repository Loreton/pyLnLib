#
# by ...: Loreto Notarantonio


import sys; sys.dont_write_bytecode = True
import time
from functools import wraps

from pyLnLib.logger import get_logger
logger = get_logger()


def timing_base(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} ha impiegato {end - start:.4f} secondi")
        return result
    return wrapper


def timing_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            logger.warning(f"{func.__name__} ha impiegato {elapsed:.4f}s")
    return wrapper



if __name__ == "__main__":
    @timing_logger
    def lenta():
        time.sleep(1.5)
        return "fatto"

    lenta()
    # Output: lenta ha impiegato 1.5003 secondi
