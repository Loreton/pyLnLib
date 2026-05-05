#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 01-05-2026 15.07.17
#

import sys; sys.dont_write_bytecode=True; this=sys.modules[__name__]
#!/usr/bin/env python3
import sys; sys.dont_write_bytecode=True
import json
import yaml
import copy
from pathlib import Path
from datetime   import datetime



# Tentativo di importare il logger globale
from pyLnLib import gVars as ctx
# except ImportError:
#     class DummyLogger:
#         def error(self, msg, *args, **kwargs): print(f"ERROR: {msg % args}")
#         def notify(self, msg, *args, **kwargs): print(f"INFO: {msg % args}")
#     getGlobalVars = lambda: type('obj', (object,), {'logger': DummyLogger()})


### --------------------
### --- project modules
### --------------------
# if not __name__ == '__main__':
#     from Source  import getGlobalVars


class lnDict(dict):
    def __init__(self, data=None, separator='.'):
        # Inizializziamo prima gli attributi interni per evitare loop con __setattr__
        super().__setattr__('_sep', separator)
        # Se hai bisogno del logger, inizializzalo qui
        # if ctx.logger:
        super().__setattr__('logger', ctx.logger)
        # else:
        #     super().__setattr__('logger', getGlobalVars().logger)

        super().__init__()
        #... carica self con i dati dict
        if data:
            self.update(data)
        # import pdb; pdb.set_trace(); # by Loreto



    @property
    def separator(self):
        return self._sep

    # Il setter ora è semplice e non propaga,
    # mantenendo la stabilità che cercavi.
    @separator.setter
    def separator(self, value):
        self._sep = value




    # #############################################################################
    # # Per rendere lo sviluppo più piacevole, potresti aggiungere questo metodo
    # # per vedere lo lnDict stampato in modo leggibile (formattato)
    # # invece che come una stringa infinita:
    # #############################################################################
    def __repr__(self):
        return f"lnDict({json.dumps(self.to_dict(), indent=4, default=str)})" #- default=str mi server perché json non gestisce i PosixPath
        return f"lnDict({json.dumps(self.to_dict(), indent=4)})"
        return f"lnDict({yaml.dump(self.to_dict(), sort_keys=False, default_flow_style=False)})"


    # #############################################################################
    # # utile per debug pdb
    # # print yaml
    # #############################################################################
    @property
    def yamlp(self):
        print(f"lnDict({yaml.dump(self.to_dict(), sort_keys=False, default_flow_style=False)})")

    # #############################################################################
    # # utile per debug pdb
    # # print json
    # #############################################################################
    @property
    def jsonp(self):
        print(f"lnDict({json.dumps(self.to_dict(), indent=4, default=str)})") #- default=str mi server perché json non gestisce i PosixPath




    # #############################################################################
    # #
    # #############################################################################
    def __setitem__(self, key, value):
        """
        Permette l'uso di config["path.nuovo"] = valore.
        Se la chiave contiene punti, crea i livelli intermedi necessari.
        """
        if isinstance(value, dict) and not isinstance(value, lnDict):
            value = lnDict(value, separator=self._sep)
        elif isinstance(value, list):
            value = [lnDict(i, separator=self._sep) if isinstance(i, dict)
                     and not isinstance(i, lnDict) else i for i in value]

        if isinstance(key, str) and self._sep in key:
            if super().__contains__(key):
                super().__setitem__(key, value)
            else:
                self.set_keypath(key, value)
        else:
            super().__setitem__(key, value)













    # #############################################################################
    # #
    # #############################################################################
    def __getitem__(self, key):
        """
        Permette l'uso di config["path.della.chiave"].
        Se la chiave non contiene punti, si comporta come un dict normale.
        """
        if isinstance(key, str) and self._sep in key:
            # 1. Controlliamo se esiste una chiave letterale con il punto (raro ma possibile)
            if super().__contains__(key):
                return super().__getitem__(key)

            # 2. Altrimenti, usiamo la logica del keypath
            # Usiamo un marker univoco per distinguere tra valore None e chiave non trovata
            not_found = object()
            result = self.get_keypath(key, default=not_found)
            if result is not_found:
                raise KeyError(f"Path '{key}' non trovato (sep: '{self._sep}')")
            return result
        return super().__getitem__(key)




    # #############################################################################
    # #
    # #############################################################################
    def __contains__(self, key):
        """Permette l'uso di 'path.chiave' in config."""
        if isinstance(key, str) and self._sep in key:
            if super().__contains__(key):
                return True
            return self.get_keypath(key, default=object()) is not object()
        return super().__contains__(key)



    # #############################################################################
    # # Per rendere lo sviluppo più piacevole, potresti aggiungere questo metodo
    # # per vedere lo lnDict stampato in modo leggibile (formattato)
    # # invece che come una stringa infinita:
    # #############################################################################
    def __getattr__(self, item):
        # 1. Fondamentale: se Python cerca metodi magici (come __deepcopy__, __setstate__, ecc.)
        # dobbiamo dire "non ce l'ho" sollevando AttributeError immediatamente.
        if item.startswith('__'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")

        try:
            return self[item]
        except KeyError:
            # Logghiamo l'errore se vuoi, ma dobbiamo SEMPRE sollevare AttributeError
            # per essere conformi al comportamento atteso da Python
            self.logger.error("lnDict non ha la chiave/attributo '%s'", item)
            raise AttributeError(f"lnDict non ha l'attributo '{item}'") from None


    def __copy__(self):
        """Supporto per copy.copy(obj)"""
        return type(self)(self, separator=self._sep)

    def __deepcopy__(self, memo):
        """Supporto per copy.deepcopy(obj)"""
        # Creiamo una nuova istanza dello stesso tipo
        new_instance = type(self)(separator=self._sep)
        memo[id(self)] = new_instance

        for k, v in self.items():
            # Usiamo copy.deepcopy ricorsivo per i valori
            new_instance[copy.deepcopy(k, memo)] = copy.deepcopy(v, memo)

        return new_instance

    def clone(self):
        """Metodo helper per una copia profonda veloce"""
        return copy.deepcopy(self)



    # #############################################################################
    # #
    # #############################################################################
    def __setattr__(self, key, value):
        """
        Rende 'config.chiave = valore' identico a 'config["chiave"] = valore'.
        # Proteggiamo gli attributi interni che iniziano con '_'
        # o quelli che sono già definiti come proprietà/attributi reali
        """
        if key.startswith('_') or key == 'logger':
            super().__setattr__(key, value)
        else:
            # Reindirizziamo tutto il resto a __setitem__
            # Così config.user = "Loreto" diventa config["user"] = "Loreto"
            self[key] = value




    # #############################################################################
    # #
    # #############################################################################
    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v


    # #############################################################################
    # #
    # #############################################################################
    def update_keypath(self, keypath, value):
        """
        Modifica un valore esistente.
        Solleva KeyError se il percorso (o l'ultimo elemento) non esiste.
        """
        hasModified = False
        parts = keypath.split(self._sep)
        curr = self

        # 1. Navigazione attraverso i livelli intermedi
        for i in range(len(parts) - 1):
            part = parts[i]
            partial_path = self._sep.join(parts[0:i+1])

            if isinstance(curr, list) and part.isdigit():
                idx = int(part)
                if idx >= len(curr):
                    # raise KeyError(f"Indice {idx} fuori range nel percorso '{keypath}'")
                    self.logger.error("Indice %s fuori range nel key_path [%s]", idx, partial_path)
                    return hasModified

                curr = curr[idx]

            elif isinstance(curr, dict) and part in curr:
                curr = curr[part]

            else:
                self.logger.error("Livello '%s' non trovato nel key_path [%s]", part, partial_path)
                return hasModified

        # 2. Modifica dell'ultimo elemento (solo se esiste)
        last_part = parts[-1]
        if isinstance(curr, list) and last_part.isdigit():
            idx = int(last_part)
            if idx >= len(curr):
                self.logger.error("Indice %s fuori range nel key_path [%s]", idx, partial_path)
                return hasModified
            curr[idx] = value

        elif isinstance(curr, dict) and last_part in curr:
            curr[last_part] = value
            hasModified = True

        else:
            self.logger.error("Chiave '%s' non trovato nel key_path [%s]", part, partial_path)
            return hasModified

        self.logger.notify("key_path [%s] updated with value: %s", keypath, value)
        return hasModified


    # #############################################################################
    # #
    # #############################################################################
    def get_keypath(self, keypath, default=None):
        """Recupera un valore tramite dot-notation (es: 'users.0.name')."""
        if not keypath: return self
        parts = keypath.split(self._sep)
        curr = self
        for part in parts:
            try:
                if isinstance(curr, list):
                    curr = curr[int(part)]
                else:
                    key = int(part) if (part.isdigit() and int(part) in curr) else part
                    curr = curr[key]
            except (IndexError, ValueError, KeyError, TypeError):
                return default
        return curr



    # Esempio: data.set_keypath("deep.level.new_key", 100) -> Crea automaticamente i dizionari deep e level se mancano.
    # #############################################################################
    # #
    # #############################################################################
    # def set_keypath(self, keypath, value, create: bool=False):
    def set_keypath(self, keypath, value):
        parts = keypath.split(self._sep)
        curr = self
        for part in parts[:-1]:
            if part not in curr or not isinstance(curr[part], dict):
                curr[part] = lnDict(separator=self._sep)
            curr = curr[part]
        curr[parts[-1]] = value
        ...



    """ ##############################################################################
        Deep Merge (Fusione Profonda)
        Il metodo update() standard di Python è "shallow": se fondi due dizionari,
        quello nuovo sovrascrive completamente le chiavi esistenti.
        Un Deep Merge invece unisce i sotto-dizionari senza cancellare le altre chiavi.
    ############################################################################## """
    def merge(self, other):
        """Unisce ricorsivamente un altro dizionario in questo lnDict."""
        for k, v in other.items():
            if k in self and isinstance(self[k], dict) and isinstance(v, dict):
                # Se entrambi sono dict, scendi in profondità
                if not isinstance(self[k], lnDict):
                    self[k] = lnDict(self[k])
                self[k].merge(v)
            else:
                # Altrimenti sovrascrivi o aggiungi
                self[k] = v





    def ln_flatten(self, with_leaves=True, sep=None):
        """
        Appiattisce il dizionario.
        :param sep: Se specificato, usa questo separatore per i percorsi di output.
                    Altrimenti usa il separatore predefinito dell'istanza.
        """
        # Se l'utente non specifica un 'sep', usiamo quello interno dell'oggetto
        output_sep = sep if sep is not None else self._sep
        return self._recursive_flatten(self, '', with_leaves, output_sep)

    def _recursive_flatten(self, data, parent_key, with_leaves, output_sep):
        paths = []
        if isinstance(data, dict):
            if not with_leaves and parent_key:
                paths.append(parent_key)
            if not data and with_leaves:
                paths.append((parent_key, {}))
            else:
                for k, v in data.items():
                    new_key = f"{parent_key}{output_sep}{k}" if parent_key else k
                    paths.extend(self._recursive_flatten(v, new_key, with_leaves, output_sep))
        elif isinstance(data, list):
            if not data and with_leaves:
                paths.append((parent_key, []))
            else:
                for i, v in enumerate(data):
                    new_key = f"{parent_key}{output_sep}{i}" if parent_key else str(i)
                    paths.extend(self._recursive_flatten(v, new_key, with_leaves, output_sep))
        else:
            if with_leaves:
                paths.append((parent_key, data))
        return paths

    def to_dict_base(self):
        out = {}
        for k, v in self.items():
            if isinstance(v, lnDict): out[k] = v.to_dict()
            elif isinstance(v, list):
                out[k] = [i.to_dict() if isinstance(i, lnDict) else i for i in v]
            else: out[k] = v
        return out



    # #############################################################################
    # # Modificato per la gestione dei PosixPath e convertirli in str
    # #############################################################################
    def to_dict(self):
        out = {}
        for k, v in self.items():
            if isinstance(v, lnDict):
                out[k] = v.to_dict()
            elif isinstance(v, list):
                # Gestiamo liste che contengono lnDict o oggetti Path
                out[k] = [
                    i.to_dict() if isinstance(i, lnDict) else
                    str(i) if isinstance(i, Path) else i
                    for i in v
                ]
            elif isinstance(v, Path):
                out[k] = str(v)
            else:
                out[k] = v
        return out

    # def clone(self):
    #     """
    #     Crea una copia profonda (deep copy) dello lnDict.
    #     Le modifiche al clone non influenzeranno l'originale.
    #     """
    #     # Creiamo un nuovo lnDict partendo dai dati "puliti" del vecchio
    #     # Mantenendo lo stesso separatore
    #     return lnDict(self.to_dict(), separator=self._sep)






    # #############################################################################
    # # riconverte un flat_data in dictionary
    # # gestisce sia (keypath, value)
    # #          che  (keypath)
    # #############################################################################
    @staticmethod
    def unflatten(flat_data, separator='.'):
        """
        Ricostruisce la struttura originale.
        Accetta sia una lista di tuple (path, value) che una lista di soli path.
        """
        if not flat_data:
            return {}

        # 1. Normalizzazione dell'input:
        # Se riceviamo solo stringhe (with_leaves=False), le trasformiamo in tuple con {}
        if isinstance(flat_data[0], str):
            normalized = [(p, {}) for p in flat_data]
        else:
            normalized = flat_data

        # Determiniamo se la radice è una lista o un dizionario
        first_path = normalized[0][0]
        root = [] if first_path.split(separator)[0].isdigit() else {}

        for path, value in normalized:
            parts = path.split(separator)
            curr = root

            for i, part in enumerate(parts):
                # Capisce se la chiave è un indice di lista o una chiave di dizionario
                key = int(part) if part.isdigit() else part

                # Se siamo all'ultimo segmento del path, assegniamo il valore
                if i == len(parts) - 1:
                    if isinstance(curr, list):
                        while len(curr) <= key: curr.append(None)
                        curr[key] = value
                    else:
                        curr[key] = value
                else:
                    # Sbirciamo il prossimo segmento per decidere se creare [] o {}
                    next_part = parts[i+1]
                    next_is_list = next_part.isdigit()

                    if isinstance(curr, list):
                        while len(curr) <= key: curr.append(None)
                        if curr[key] is None:
                            curr[key] = [] if next_is_list else {}
                        curr = curr[key]
                    else:
                        if key not in curr:
                            curr[key] = [] if next_is_list else {}
                        curr = curr[key]

        return lnDict(root)


    ###################################################################################
    # -Immagina di avere un dizionario enorme e di non ricordare esattamente dove si trovi
    # -una chiave (es. "apiKey") o di voler trovare tutti i record che hanno un certo valore (es. "admin").
    ###################################################################################
    def find_paths(self, query, search_in='path'):
        """
        Cerca all'interno dei percorsi o dei valori.
        search_in: 'path' per cercare nelle chiavi, 'value' per i valori.
        """
        all_leaves = self.flatten(with_leaves=True)
        if search_in == 'path':
            return [p for p, v in all_leaves if query.lower() in p.lower()]
        elif search_in == 'value':
            return [p for p, v in all_leaves if query.lower() in str(v).lower()]
        return []





    # #############################################################################
    # #  J S O N
    # #############################################################################
    @classmethod
    def from_json(cls, json_str):
        """Crea uno lnDict da una stringa JSON."""
        return cls(json.loads(json_str))

    def to_json(self, indent=4):
        """Esporta lo lnDict in una stringa JSON pulita."""
        return json.dumps(self.to_dict(), indent=indent)



    # #############################################################################
    # #  Y A M L
    # #############################################################################
    @classmethod
    def from_yaml(cls, yaml_str):
        """Crea uno lnDict da una stringa YAML."""
        data = yaml.safe_load(yaml_str)
        return cls(data) if data else cls()

    @classmethod
    def load_yaml(cls, filepath):
        """Carica uno lnDict direttamente da un file .yaml."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls(yaml.safe_load(f))




    # #############################################################################
    # # title: se valorizzato viene messo in testa al dict
    # #############################################################################
    def to_yaml(self, title: str=None, sort_keys=False, **kwargs):
        """Converte lo lnDict in una stringa YAML pulita."""
        # Usiamo to_dict() per esportare solo dati standard
        indent = kwargs.pop("indent", 4)
        d={title: self.to_dict()} if title else self.to_dict()
        return yaml.dump(d, sort_keys=sort_keys, indent=indent, default_flow_style=False, **kwargs)


    # #############################################################################
    # # title: se valorizzato viene messo in testa al dict
    # #  utile per avere un'idea di massima del contenuto del dictionary
    # #############################################################################
    def save_yaml(self, filepath, title: str=None, **kwargs):
        """Salva lo lnDict in un file .yaml."""
        stacklevel = kwargs.pop("stacklevel", 1)
        yaml_data = self.to_yaml(title=title, **kwargs)
        now = datetime.now().strftime("%d-%m-%Y_%H:%M")
        _cmnt=f"#{'-'*20}"
        yaml_data = f"{_cmnt}\n#- {now}\n{_cmnt}\n{yaml_data}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(yaml_data)

        self.logger.notify("file: [%s] has been written", filepath, stacklevel=stacklevel+1)



    # --- Collegamento al Resolver ---
    def resolve_all(self):
        from pyLnLib import LnDictResolver
        resolver = LnDictResolver(self)
        return resolver.run()