# from itertools import combinations, chain
from itertools import permutations


# SOLO PERMUTAZIONI (tutti gli ordini, SENZA ripetizioni)
# Numero totale: per 4 parole: 4!/(4-1)! + 4!/(4-2)! + 4!/(4-3)! + 4! = 4 + 12 + 24 + 24 = 64 permutazioni
def list_permutations(lista_parole, reverse=False):
    """Genera tutte le permutazioni di tutte le lunghezze senza ripetizioni."""
    if reverse:
        """Genera tutte le permutazioni di tutte le lunghezze, partendo da quelle più lunghe."""
        for r in range(len(lista_parole), 0, -1):  # Da n a 1
            for perm in permutations(lista_parole, r):
                yield perm
    else:
        for r in range(1, len(lista_parole) + 1):
            for perm in permutations(lista_parole, r):
                yield perm





if __name__ == '__main__':
    lista_parole = ['cane', 'gatto', 'topo', 'uccello']

    print("---")
    for permutazione in list_permutations(lista_parole, reverse=False):
        print(permutazione)
