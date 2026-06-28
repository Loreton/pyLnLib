#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 30-04-2026 17.44.50
#

import sys; sys.dont_write_bytecode=True; this=sys.modules[__name__]
import re
import os
import copy

class LnDictResolver():
    TAG_REGEX = re.compile(r"\(\(\s*(\w+)\s*->\s*(.+?)\s*\)\)")

    def __init__(self, lndict_instance):
        self.target = lndict_instance
        self.sep = lndict_instance.separator
        self.errors = []
        self.resolving = set()

    def _deep_merge(self, target, source, overwrite=False):
        for k, v in source.items():
            if k not in target:
                target[k] = copy.deepcopy(v)
            elif isinstance(target[k], dict) and isinstance(v, dict):
                self._deep_merge(target[k], v, overwrite=overwrite)
            elif isinstance(target[k], list) and isinstance(v, list):
                if overwrite: target[k] = copy.deepcopy(v)
                else:
                    for item in v:
                        if item not in target[k]: target[k].append(copy.deepcopy(item))
            elif overwrite:
                target[k] = copy.deepcopy(v)

    def _parse_subpath(self, path_str):
        """
        Normalizza il percorso trasformando tutti i / in separatori interni (es. punti)
        e rimuovendo parti vuote.
        """
        if not path_str:
            return []
        # Trasforma / in . (o qualunque sia il tuo self.sep)
        normalized = path_str.replace('/', self.sep)
        return [p for p in normalized.split(self.sep) if p]



    def _parse_instruction(self, content, current_stack):
        """
        Analizza l'istruzione e logga il processo di risoluzione del path.
        """
        parts = [p.strip() for p in content.split(',', 1)]
        instr_type = "ASSOLUTO"
        steps = 0

        # --- LOGICA DI RISOLUZIONE ---
        if len(parts) == 2:
            # Caso: -4, subpath
            instr_type = "SALTO NUMERICO"
            jump, subpath_str = parts[0], parts[1]
            steps = jump.count('..') if '..' in jump else abs(int(jump))
            base = current_stack[:-steps] if steps > 0 else current_stack
            target_parts = base + self._parse_subpath(subpath_str)
        else:
            path_str = parts[0]
            if path_str.startswith('/'):
                # Caso: /templates/...
                target_parts = self._parse_subpath(path_str)
            elif path_str.startswith('..'):
                # Caso: ../../subpath
                instr_type = "SALTO RELATIVO (..)"
                temp_path = path_str
                while temp_path.startswith('../'):
                    steps += 1
                    temp_path = temp_path[3:]
                base = current_stack[:-steps] if steps > 0 else current_stack
                target_parts = base + self._parse_subpath(temp_path)
            else:
                # Caso: subpath (relativo semplice)
                instr_type = "RELATIVO SEMPLICE"
                target_parts = current_stack + self._parse_subpath(path_str)

        final_path = self.sep.join(target_parts)

        # --- LOG DI DEBUG ---
        # Questo ti permette di vedere esattamente come calcola il percorso
        stack_str = self.sep.join(current_stack)
        msg = (f"[RESOLVER] Tipo: {instr_type} | "
               f"Origine: [{stack_str}] | "
               f"Salti: {steps} | "
               f"Target finale: [{final_path}]")

        # Uso debug così non sporca il log normale, a meno che non alzi il livello
        if hasattr(self.target, 'logger'):
            self.target.logger.debug(msg)
        else:
            print(f"DEBUG: {msg}")

        return final_path


    def _walk(self, node, path_stack):
        curr_path = self.sep.join(path_stack)
        if curr_path in self.resolving:
            self.errors.append(f"Circolarità rilevata: {curr_path}")
            return
        self.resolving.add(curr_path)

        if isinstance(node, dict):
            for key, value in list(node.items()):
                if isinstance(value, str):
                    value = os.path.expandvars(value)
                    node[key] = value
                    match = self.TAG_REGEX.search(value)
                    if match:
                        cmd, content = match.groups()
                        final_target = self._parse_instruction(content, path_stack + [key])
                        if final_target == "__OUT_OF_BOUNDS__":
                            self.errors.append(f"Out of bounds: {content} in {curr_path}")
                            continue

                        source_data = self.target.get_keypath(final_target, default=object())
                        # if source_data is object():
                        #     msg = f"ERRORE CRITICO: Il path '{final_target}' richiesto da '{key}' non esiste!"
                        #     self.errors.append(msg)
                        #     self.target.logger.error(msg) # Così lo vedi subito in console
                        #     continue
                            # self.errors.append(f"Non trovato: {final_target} richiesto da {key}")
                            # continue


                        if source_data is object() or source_data is None:
                            msg = f"ERRORE CRITICO: Il target '{final_target}' (richiesto da '{self.sep.join(current_stack + [key])}') non esiste o è vuoto!"
                            self.errors.append(msg)
                            if hasattr(self.target, 'logger'):
                                self.target.logger.error(msg)

                            # Invece di 'continue', potresti voler lanciare un'eccezione
                            # se vuoi bloccare l'intero programma immediatamente:
                            # raise ValueError(msg)
                            continue

                        if cmd == "include":
                            node[key] = copy.deepcopy(source_data)
                        elif cmd in ["merge", "merge_no_ovwr"]:
                            if isinstance(source_data, dict):
                                self._deep_merge(node, source_data, overwrite=(cmd=="merge"))
                                del node[key]
                            else: self.errors.append(f"Merge fallito: {final_target} non è un dict")

                if key in node: self._walk(node[key], path_stack + [key])

        elif isinstance(node, list):
            for i, item in enumerate(node):
                if isinstance(item, str): node[i] = os.path.expandvars(item)
                self._walk(node[i], path_stack + [str(i)])


        self.resolving.remove(curr_path)

    def run(self):
        self._walk(self.target, [])
        if self.errors:
            for err in self.errors: self.target.logger.error(err)
        return self.target
