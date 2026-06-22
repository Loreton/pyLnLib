#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 22-06-2026 21.33.29
#


import  sys; sys.dont_write_bytecode=True
import subprocess
import shlex
import sys
import re

from pathlib import Path
from types import SimpleNamespace

'''
    Eliminazione di select e threading:
        Usare iter(process.stdout.readline, "") è il modo standard e più pulito in Python 3 per leggere l'output di un processo
        riga per riga senza bloccare l'interprete o complicare il codice.

    Unificazione degli Stream:
        Ho impostato stderr=subprocess.STDOUT. Questo è fondamentale per rsync o rclone, perché spesso gli errori vengono
        scritti su stderr. Unificandoli, li filtri e li colori con un'unica logica.

    Gestione del Buffer:
        Ho aggiunto bufsize=1 e text=True (che sostituisce universal_newlines).
        Questo garantisce che ogni riga venga processata non appena il comando la genera, evitando ritardi (buffering).

    Uscita Immediata:
        Se viene trovata una stringa in error_strings, il processo viene terminato immediatamente con process.terminate()
        e lo script si interrompe, come avevi chiesto.

    Semplicità:
        Il modulo è ora una singola classe con metodi chiari. La logica di "default" e "override" è gestita direttamente
        dai parametri del metodo run, rendendo il codice molto più lineare.

    Nota su rsync e barre di progresso:
        Se usi rsync --info=progress1, rsync usa caratteri di ritorno carrello (\r) per aggiornare la stessa riga.
        readline() aspetta il carattere newline (\n). Se hai bisogno di vedere la barra di avanzamento fluida,
        dovresti leggere carattere per carattere, ma questo renderebbe il filtraggio delle stringhe molto più complesso.
        Per log di backup, il metodo riga per riga è solitamente la scelta migliore.
'''



import sys
import subprocess
import shlex
from pathlib import Path
from types import SimpleNamespace


from ..colors import Colors as C

class lnRunStream_Class:
    def __init__(self, logger):
        self.logger      = logger
        # self.colors      = logger.Colors
        self.color_map   = {}
        self.ignore_case = False


        self.RSYNC_CHANGE_PATTERN = re.compile(r'^([<>ch*][fdLDS].{9}\s+)')
                                                # [<>ch*]: inviato/ricevuto/cambio locale/hard link/messaggio.
                                                # [fdLDS]: file, directory, symlink, device, special.
                                                # .{9}\s+: altri 9 caratteri dell’itemize + spazi prima del path.
                                                # Così escludi le righe che iniziano con . (nessun aggiornamento).

        self.RCLONE_CHANGE_PATTERN = re.compile(r'^(\s*\*\s+)') ###. riga che inizia con " * "
                                                # ^ = inizio riga
                                                # \s* = eventuali spazi all’inizio
                                                # \* = asterisco (escapato)
                                                # \s+ = uno o più spazi (fino al path)
                                                # (...) = gruppo 1, cioè il pezzo da colorare


    ########################################################################
    #
    ########################################################################
    def _apply_colors(self, line):
        """Applica i colori alle stringhe definite nel color_map."""
        flags = re.IGNORECASE if self.ignore_case else 0

        # Se è attiva la config rsync e la riga indica un cambiamento, colora solo il prefisso (fino al primo blank)
        if self.rsync_change_color:
            change_color = self.rsync_change_color.get("change_color")
            if change_color and self.RSYNC_CHANGE_PATTERN.match(line):
            # if change_color:
                line = re.sub(
                    self.RSYNC_CHANGE_PATTERN,
                    lambda m: f"{change_color[0]}{m.group(1)}{change_color[1]}",
                    line,
                    count=1
                )

        elif self.rclone_change_color:
            change_color = self.rclone_change_color.get("change_color")
            if change_color and self.RCLONE_CHANGE_PATTERN.match(line):
            # if change_color:
                line = re.sub(
                    self.RCLONE_CHANGE_PATTERN,
                    lambda m: f"{change_color[0]}{m.group(1)}{change_color[1]}",
                    line,
                    count=1
                )


        for key, (start_color, end_color) in self.color_map.items():
            # Escapa caratteri speciali della key e cerca key seguito da tutto fino al primo blank
            escaped_key = re.escape(key)


            if True:
                ###. Esempio:
                ###.    key = "INFO",  line = "INFO : file.txt"  → colora "INFO :".
                ###.    key = "ERROR", line = "ERROR: something" → colora "ERROR:".
                # pattern = f"({escaped_key}[^\\s]*)"
                pattern = f"(\\b{escaped_key}[^\\s]*)" ###. metti il boundary alla word quindi non stringhe in mezzo alle parole
            else:
                ### e vuoi colorare solo fino al primo blank dopo la key (escludendo eventuali caratteri non-spazio tra key e blank), usa:
                ###. Questo cattura la key seguita da zero o più caratteri non-spazio (senza includere spazi).
                pattern = f"({escaped_key}\\S*)"

            line = re.sub(pattern, f"{start_color}\\1{end_color}", line, flags=flags)

        return line











    ########################################################################
    #
    ########################################################################
    def processConsoleLine(self, process, line: str):
        # 3. Formattazione e Console (Logica Dashboard)
        stripped_line = line.strip()
        if not stripped_line: ### se vuota...
            return None

        line_lower = line.lower() if self.ignore_case else line ###. per ascoltare ignore_case

        if any(line_lower.startswith(item) for item in self.unnecessary_starting_with):
            return None

        if any(unnecessary in line_lower for unnecessary in self.unnecessary_strings):
            return None

        if any(err in line_lower for err in self.error_strings):
            # if self._last_line_was_status: sys.stdout.write("\n")
            self.logger.error(f"Trovata stringa di errore: {line.strip()}")
            process.terminate()
            sys.stdout.write(self._apply_colors(line))
            sys.stdout.flush()
            sys.exit(1)

        ###. prepare linea con colori
        display_line = self._apply_colors(line)


        return display_line






    ########################################################################
    # parte relativa alle stringhe da controllare per colore o per escludere
    ########################################################################
    def prepareWords(self, process_strings: dict):
        self.color_map             = process_strings.pop("colors", {})
        _error_strings             = process_strings.pop("error", [])
        _unnecessary_strings       = process_strings.pop("unnecessary", [])
        _unnecessary_starting_with = process_strings.pop("unnecessary_starting_with", [])
        # Config per evidenziare le righe rsync che indicano un cambiamento
        self.rsync_change_color = process_strings.pop("rsync", None)  # None oppure {"change_color": [start, end]}
        self.rclone_change_color = process_strings.pop("rclone", None)  # None oppure {"change_color": [start, end]}


        # Normalizza solo se necessario
        if self.ignore_case:
            self.unnecessary_starting_with = [s.lower() for s in _unnecessary_starting_with]
            self.unnecessary_strings       = [s.lower() for s in _unnecessary_strings]
            self.error_strings             = [s.lower() for s in _error_strings]
        else:
            self.unnecessary_starting_with = _unnecessary_starting_with
            self.unnecessary_strings       = _unnecessary_strings
            self.error_strings             = _error_strings







    ############################################################
    # # arguments:
    # #     cmd: str        preferisco avere la stringa compleat e poi la divido. Ho visto che con le list a volte non va bene
    # #     process_strings: dict = {
    # #                     "colors": {"error": [C.redH,    C.reset], }, per colorare alcune stringhe
    # #                     "error": ["FATAL", ],                        esce su stringhe di errore
    # #                     "unnecessary": [],                           linee stringhe non necessarie alla visualizzazione
    # #                     "unnecessary_starting_with": [".f.", ".d.", ], linee starting_with non necessarie alla visualizzazione
    # #                     }
    ############################################################
    def runStream(self, cmd: str, stdout_file=None, to_console=True, get_output=False, dry_run=False, process_strings: dict={}, ignore_case=False):
        self.ignore_case = ignore_case

        self.prepareWords(process_strings)

        result = SimpleNamespace(rcode=-1, output=[])

        ###. Se arriva una lista, la convertiamo in stringa per shlex
        if isinstance(cmd, list):
            cmd = ' '.join(cmd)

        args = shlex.split(cmd)

        if dry_run:
            self.logger.warning(f"[DRY-RUN] Command: {' '.join(args)}")
            result.rcode = 0
            return result

        self.logger.debug(f"Running: {' '.join(args)}")

        captured_output = []
        file_handle = None

        ###. serve per catturare l'output per poi aprirlo e processarlo
        if stdout_file:
            p = Path(stdout_file)
            p.parent.mkdir(parents=True, exist_ok=True)
            file_handle = open(p, "w", buffering=1, encoding="utf-8")

        ###- esecuzione comando
        try:
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1 )

            # =========================================================================================================
            #... Nota tecnica:
            #... Quando usi subprocess.Popen, l'aggiunta di bufsize=1 e text=True aiuta molto,
            #... ma l'iteratore iter(..., "") è la "polizza assicurativa" definitiva contro i ritardi del buffer.
            # =========================================================================================================
            for line in iter(process.stdout.readline, ""):
                if not line: ###. end of output
                    break

                # 2. Salvataggio su file (sempre riga intera)
                if file_handle:
                    file_handle.write(line)

                # 3. Formattazione e Console (Logica Dashboard)
                if to_console:
                    ###. display su stdout
                    if display_line := self.processConsoleLine(process, line):
                        sys.stdout.write(display_line)
                        sys.stdout.flush()

                ###. aggiungiamo riga all'output
                if get_output:
                    captured_output.append(line.rstrip())

            process.wait()
            result.rcode = process.returncode
            result.output = captured_output

        except Exception as e:
            self.logger.error(f"Errore durante l'esecuzione: {e}")
            result.rcode = -1

        finally:
            if file_handle:
                file_handle.close()

        return result







# Mock logger per test (sostituiscilo col tuo)
class MockLogger:
    class Colors:
        redH = "\033[91m"
        yellowH = "\033[93m"
        reset = "\033[0m"
    def info(self, m): print(f"INFO: {m}")
    def error(self, m): print(f"ERROR: {m}")
    def warning(self, m): print(f"WARN: {m}")

moc_logger = MockLogger()



def getGlobalVars():
    return gv

##################################################################################################################################
#   M A I N
##################################################################################################################################

if __name__ == '__main__':
    global gv
    gv=SimpleNamespace()


    sys.path.insert(0, "/home/loreto/filu/Devel/gitREPO/lnPyLib/logger")
    from coloredLogger_Class import setColoredLogger

    logger=setColoredLogger(logger_name="test", console_logger_level='info')
    gv.logger=logger
    gv.color=logger.Colors
    C=logger.Colors

    logger.info('------- Starting -----------')


    C = logger.Colors

    colori = {
        ".py":         [C.yellowH, C.reset],
        "Error":       [C.redH,    C.reset],
        ">f+++++++++": [C.yellowH, C.reset],
        "cd+++++++++": [C.yellowH, C.reset],
        "DRY RUN":     [C.yellowH, C.reset],
    }

    runner = lnRunStream_Class(
        logger=logger,
        color_map=colori,
        error_strings=["FATAL", "Permission denied", "unknown option"]
    )

    # Esempio comando lungo (es: ls -R / oppure rsync)
    cmd = "ls -la"
    result = runner.run(cmd, stdout_file="/tmp/test_output.log", get_output=True)
    print(f"\nCompletato con codice: {result['rcode']}")
    print(f"\n               output: {result['output']}")

    cmd='''/usr/bin/rsync   --archive --verbose --update --partial --itemize-changes --links --times --compress --timeout=15 --exclude-from /tmp/lnSync/rsync/myself/filesystem_exclude_patterns.txt   "/home/loreto/.config/FreeFileSync"   "/home/loreto/filu/lnENV/config/applsSaved/IdeaPadSlim3/FreeFileSync" '''

    cmd='''/usr/bin/rsync  --dry-run   --archive --verbose --update --partial --itemize-changes --links --times --compress --timeout=15 --exclude-from /tmp/lnSync/rsync/myself/filesystem_exclude_patterns.txt   "/home/loreto/.config/qalculate"   "/home/loreto/filu/lnENV/config/appls Saved/IdeaPadSlim3/qalculate"  '''

    #.. quando uso la list non devo usare il DQ nel source o dest altrimenti sbaglai.
    #.. di fatto lo capisce il programma perch' utilizza automaticamente l'item della lista
    cmd=['/usr/bin/rsync', '--dry-run'  '--exclude-from=/tmp/lnSync/rsync/myself/filesystem_exclude_patterns.txt', '--archive', '--verbose', '--update', '--partial', '--itemize-changes', '--links', '--times', '--compress', '--timeout=15', '"/home/loreto/.config/FreeFileSync"', '"/home/loreto/filu/lnENV/config/appls Saved/IdeaPadSlim3/FreeFileSync"']


    result=runner.run(cmd, stdout_file="/tmp/prova01.log", get_output=True)
    print(f"\nCompletato con codice: {result['rcode']}")
    print(f"\n               output: {result['output']}")
