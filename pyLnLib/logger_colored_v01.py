#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 02-02-2026 15.51.17
#


##########################################################
# colored Logger con anche la creazione di due ulteriori
# livelli di TRACE e NOTIFY
##########################################################
import sys; sys.dont_write_bytecode=True; this=sys.modules[__name__]

import os
import logging
from logging.handlers import RotatingFileHandler
from types import SimpleNamespace
import inspect
import traceback


import colorlog  # https://pypi.org/project/colorlog/



# ==============================================
# - funzione utile per usarla nei display....
# - ref https://tldp.org/HOWTO/Bash-Prompt-HOWTO/x329.html
# ==============================================
def getColors() -> SimpleNamespace:
    _white='\033[0;37m'
    colors=SimpleNamespace(
        red        = '\033[0;31m', redH       = '\033[1;31m',
        green      = '\033[0;32m', greenH     = '\033[1;32m',
        yellow     = '\033[0;33m', yellowH    = '\033[1;33m',
        blue       = '\033[0;34m', blueH      = '\033[1;34m',
        purple     = '\033[0;35m', purpleH    = '\033[1;35m',
        cyan       = '\033[0;36m', cyanH      = '\033[1;36m',

        white      = '\033[0;37m', whiteH     = '\033[1;37m',
        gray       = '\033[0;37m', grayH      = '\033[1;37m',
        grey       = '\033[0;37m', greyH      = '\033[1;37m',

        colorReset = '\033[0m',    reset      = '\033[0m',
    )
    return colors






###############################################################
# Un logger personalizzato
#   Il modulo logging di Python gestisce lui stesso la creazione delle istanze
#   del logger quando chiami logging.getLogger(name).
#   Dopo aver impostato la classe con setLoggerClass(), ogni volta che chiami logging.getLogger('nome_qualunque'),
#   Python fa:
#     1. Crea un'istanza chiamando LoretoLoggerTest('nome_qualunque', logging.NOTSET).
#     2. Ti restituisce l'oggetto logger.
###############################################################
class LoretoLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

        self.logLevels={
            "notset":   logging.NOTSET,     # NOT_MODIFIED - already DEFINED in logging module
            "trace":    logging.DEBUG-1,
            "debug":    logging.DEBUG,     # NOT_MODIFIED - already DEFINED in logging module
            "function": logging.INFO-2,
            "notify":   logging.INFO-1,
            "info":     logging.INFO,     # NOT_MODIFIED - already DEFINED in logging module
            "warning":  logging.WARNING,     # NOT_MODIFIED - already DEFINED in logging module
            "error":    logging.ERROR,     # NOT_MODIFIED - already DEFINED in logging module
            "critical": logging.CRITICAL,     # NOT_MODIFIED - already DEFINED in logging module
        }

        # 1. Aggiungi la flag di controllo al logger
        self.forceFUNCTION=False
        self.forceTRACE=False
        self.forceNOTIFY=False
        self.forceINFO=False
        self.forceDEBUG=False
        self.forceWARNING=False
        self.forceERROR=False
        self.forceCRITICAL=False

        self.addTRACELevel()
        self.addFUNCTIONLevel()
        self.addNOTIFYLevel()

    def setup(self,
            main_logger_level: str='trace',
            console_logger_level: str='critical',
            file_logger_level: str='warning',
            logging_dir: str=None,  # if None NO filehandler...
            create_logging_dir: bool=True,
            lock_log=False,  # da sperimentare
            threads: bool=False,
            prj_log_levels: dict={},
            module_name_length: int=15,
        ): #- lunghezza del nome del modulo nella riga di log

        # -----------------------------------------------------------------
        # Viene impostato quando viene creata l'istanza con il comando
        #   logger=logging.getLogger(logger_name)
        self.logger_name=self.name # solo per ricordarmelo.
        # -----------------------------------------------------------------


        ### per sfruttare i colori dall'esterno....
        self.Colors=getColors()

        ### imposto al massimo TRACE, decidono i singoli handlers
        self.setLevel(main_logger_level.upper()) #
        self.propagate=False # se messo a True mi trovo due righe di log, una colorata e l'altra no.

        ### console logger
        self.consoleHandler = self.set_streamingHandler(module_name_length=module_name_length, threads=threads)
        self.addHandler(self.consoleHandler)
        self.setConsoleLoggerLevel(console_logger_level)

        ### file logger
        if logging_dir:
            self.fileHandler=self.set_fileHandler(logging_dir=logging_dir, create_logging_dir=create_logging_dir)
            self.addHandler(self.fileHandler)
            self.setFileLoggerLevel(file_logger_level)



    #########################################################################
    # Sovrascrive il controllo standard del livello.
    #########################################################################
    def isEnabledFor(self, log_level: int, force_log: bool=False):
        if log_level >= self.consoleHandler.level or force_log:
            return True

        return super().isEnabledFor(log_level)


    #########################################################################
    #
    #########################################################################
    def setLogLevels(self, levels: dict={}):
        if levels:
            self.logLevels.update(levels)

    #########################################################################
    #
    #########################################################################
    def getLogLevels(self):
        return self.logLevels



    #########################################################################
    #
    #########################################################################
    def set_fileHandler(self, logging_dir: str, create_logging_dir: bool):
        logging_file=f"{logging_dir}/{logger_name.lower()}.log"
        if not os.path.exists(logging_dir) and create_logging_dir:
            os.makedirs(logging_dir)
        fileHandler=RotatingFileHandler(logging_file, maxBytes=5*1000*1000, backupCount=5)
        # formatter=logging.Formatter('%(asctime)s %(levelname)-4s  %(funcName)s:%(lineno)4s: %(message)s')
        formatter=logging.Formatter(f"%(asctime)s [%(levelname)4.4s] - [{threads_str}%(module)s.%(funcName)s:%(lineno)4.4s]: %(message)s")
        fileHandler.setFormatter(formatter)
        return fileHandler



    #########################################################################
    #
    #########################################################################
    def set_streamingHandler(self, module_name_length: int=15, threads: bool=False):
        lun=module_name_length
        threads_str="%(threadName)-5.5s." if threads else ''
        fmt = (
            "%(cyan)s%(asctime)s "
            f"%(blue)s[{threads_str}%(module){lun}.{lun}s:%(lineno)-4d] "    # module truncated/padded to 10 chars lineno right-aligned width 4
            "%(log_color)s[%(levelname)-4.4s]: "                         # level name truncated/padded to 4 chars
            "%(log_color)s%(message)s"
            # "%(funcName)-15.15s:"    # function name truncated/padded to 15 chars
            # f"%(blue)s[{threads_str}%(module)15.15s:%(lineno)-4d] "    # module truncated/padded to 10 chars lineno right-aligned width 4
        )
        formatter=colorlog.ColoredFormatter(
            fmt,
            datefmt="%H:%M:%S",
            reset=True,
                            # -------------------------------------------------------------------------------
                            # The following escape codes are made available for use in the format string:
                            #
                            #   {color}, fg_{color}, bg_{color}: Foreground and background colors.
                            #   bold, bold_{color}, fg_bold_{color}, bg_bold_{color}: Bold/bright colors.
                            #   thin, thin_{color}, fg_thin_{color}: Thin colors (terminal dependent).
                            #   reset: Clear all formatting (both foreground and background colors).
                            #
                            #  The available color names are black, red, green, yellow, blue, purple, cyan and white.
                            # -------------------------------------------------------------------------------
            log_colors={
                'TRACE':    'blue',
                'DEBUG':    'cyan',
                'NOTIFY':   'fg_bold_cyan',
                'INFO':     'green',
                'FUNCTION': 'purple',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        )

        consoleHandler=logging.StreamHandler()
        consoleHandler.setFormatter(formatter)
        return consoleHandler



    ################################################################
    # deve individuare due caller
    #   [logCallerFunction:nnn]: [CALLER] writeFile - [called by: colui che ha chiamato logCallerFunction (stacklevel-1)]
    ################################################################
    def callerFunc(self, stacklevel: int=1, fDEBUG: bool=False):
        def getInfo(stack):
            fname=stack.filename.rsplit('.', 1)[0]
            funcname=os.sep.join(fname.split(os.sep)[-2:])
            msg=f"{funcname}:{stack.lineno}"
            return msg

        _stacks=inspect.stack() # changed:  27-02-2024
        n_stacks=len(_stacks) # changed:  27-02-2024

        if stacklevel>=n_stacks: stacklevel=n_stacks-1 # changed:  27-02-2024

        if fDEBUG:
            x=traceback.extract_stack()

            print('-'*40)
            for i in range(len(x)): print(i, inspect.stack()[i].filename, inspect.stack()[i].function, inspect.stack()[i].lineno)

            print('-'*40)
            print("stacklevel:", stacklevel, inspect.stack()[stacklevel].function, inspect.stack()[stacklevel].lineno)
            print('-'*40)



        logcaller = getInfo(_stacks[stacklevel-1]) # colui che ha chiamato il log.caller()
        parentcaller = getInfo(_stacks[stacklevel]) # colui che ha chiamato la logcaller_function

        if fDEBUG:
            print(logcaller)
            print(parentcaller)
        return logcaller, parentcaller




    ###############################################################
    # - print log per i miei added_Levesl
    ###############################################################
    def printMyLog(self, log_level: int, text_message: str, force_level: bool=False, *args, **kwargs):
        forceLog: bool         = kwargs.pop("force_log", False) or force_level
        isConsoleEnabled: bool = (log_level >= self.consoleHandler.level)
        fExit                  = kwargs.pop("exit", False) #. per sicurezza

        if fExit: forceLog=True
        if isConsoleEnabled or forceLog:
            if not 'stacklevel' in kwargs: kwargs['stacklevel'] = 2

            kwargs['stacklevel'] += 1 #- incrementiamo lo stackLevel di 1

            if log_level >= self.consoleHandler.level:
                self._log(log_level, text_message, args, **kwargs)

            elif forceLog:
                saved_level = self.consoleHandler.level
                # --- PARTE CRITICA: FORZATURA DELL'HANDLER ---
                try:
                    # Imposta temporaneamente l'handler al livello CALLER
                    self.consoleHandler.setLevel(log_level)
                    self._log(log_level, text_message, args, **kwargs)
                finally:
                    # Ripristina il livello originale, garantito anche in caso di errore
                    self.consoleHandler.setLevel(saved_level)

        if kwargs.get("exc_info"):
            self.print_stack_trace()
            sys.exit(1)
        if fExit:
            sys.exit(1)

    ###############################################################
    # my kwargs:
    #   exit:       True force exit program
    #   force_log:  True force the log level even not enabled
    ###############################################################


    ###############################################################
    # Sovrascrive il livello standard.
    ###############################################################
    def info(self, message, *args, **kwargs):
        self.printMyLog(logging.INFO, message, self.forceINFO, *args, **kwargs)
        # self.printMyLog(log_level=logging.INFO, text_message=message, force_level=self.forceINFO, *args, **kwargs)


    ###############################################################
    # Sovrascrive il livello standard.
    ###############################################################
    def debug(self, message, *args, **kwargs):
        self.printMyLog(logging.DEBUG, message, self.forceDEBUG, *args, **kwargs)
        # if kwargs.get("exc_info"):
        #     self.print_stack_trace()
        #     sys.exit(1)

    ###############################################################
    # Sovrascrive il livello standard.
    ###############################################################
    def error(self, message, *args, **kwargs):
        forceERROR = True or self.forceERROR
        self.printMyLog(logging.ERROR, message, forceERROR, *args, **kwargs)
        # if kwargs.get("exc_info"):
        #     self.print_stack_trace()
        #     sys.exit(1)

    ###############################################################
    # Sovrascrive il livello standard.
    ###############################################################
    def critical(self, message, *args, **kwargs):
        forceCRITICAL = True or self.forceCRITICAL
        self.printMyLog(logging.CRITICAL, message, forceCRITICAL, *args, **kwargs)
        if kwargs.get("exc_info"):
            self.print_stack_trace()
        self.printMyLog(logging.CRITICAL, message, forceCRITICAL, *args, **kwargs)
        sys.exit(1)

    ###############################################################
    # --------- Adding TRACE level -------------------
    ###############################################################
    def addTRACELevel(self):
        def _trace(logger, message, *args, **kwargs):
            self.printMyLog(logging.TRACE, message, self.forceTRACE, *args, **kwargs)
            # self.printMyLog(log_level=logging.TRACE, text_message=message, force_level=self.forceTRACE, *args, **kwargs)

        logging.TRACE=self.logLevels["trace"]
        logging.Logger.trace = _trace
        logging.addLevelName(logging.TRACE, "TRACE")

    ###############################################################
    # --------- Adding NOTIFY level -------------------
    ###############################################################
    def addNOTIFYLevel(self):
        def _notify(logger, message, *args, **kwargs):
            # fExit=kwargs.pop("exit", False)
            # if fExit: self.forceNOTIFY=True
            self.printMyLog(logging.NOTIFY, message, self.forceNOTIFY, *args, **kwargs)


        logging.NOTIFY=self.logLevels["notify"]
        logging.Logger.notify = _notify
        logging.addLevelName(logging.NOTIFY, "NOTIFY")

    ###############################################################
    # --------- Adding FUNCTION level -------------------
    ###############################################################
    def addFUNCTIONLevel(self):
        def _function(logger, message=None, *args, **kwargs):
            forceLog: bool = kwargs.pop("force_log", False) or self.forceFUNCTION
            isConsoleEnabled: bool = (logging.FUNCTION >= self.consoleHandler.level)

            if isConsoleEnabled or forceLog:
                #- preparazione del messaggio
                STACKLEVEL=2
                if not 'stacklevel' in kwargs: kwargs['stacklevel'] = STACKLEVEL
                logcaller, parentcaller = self.callerFunc(stacklevel=STACKLEVEL+1, fDEBUG=False)
                MSG = f'calledBy: {parentcaller}'
                # if message:
                #     MSG=f'{message} - {MSG}'

                self.printMyLog(logging.FUNCTION, MSG, self.forceFUNCTION, *args, **kwargs)

        logging.FUNCTION=self.logLevels["function"]
        logging.Logger.function = _function
        logging.addLevelName(logging.FUNCTION, "FUNCTION")


    #############################################################
    # Ho creato questa funzione per permettermi di modificare
    # il livello di loggging dinamicamente dall'esterno
    #############################################################
    def setFileLoggerLevel(self, level: str=None):
        self.fileHandler.setLevel(level.upper())
        self.notify("file log level has been set to: %s", level.upper())


    def setConsoleLoggerLevel(self, level: str):
        self.consoleHandler.setLevel(level.upper())
        self.notify("console log level has been set to: %s", level.upper())



    #############################################################
    # #    T  E  S  T      Logger
    #############################################################
    def testLogger(self):
        _sorted_levels = sorted(self.logLevels.items(), key=lambda x:x[1])
        for k, v in _sorted_levels:
            isMainEnabled = self.isEnabledFor(v, False)
            isConsoleEnabled = (v >= self.consoleHandler.level)
            self.warning(f"{k:8}: {v:2} {isMainEnabled = } {isConsoleEnabled = }")

        sorted_levels=dict(_sorted_levels)

        for level_name in sorted_levels:
            if level_name=="notset": continue

            msg=f"this is a {level_name.upper()} messages"
            llog=eval(f"self.{level_name}")
            if level_name == 'critical':
                llog(msg, exit=False)
            else:
                llog(msg)

        print()




    def print_stack_trace(self):
        _stacks=inspect.stack() # changed:  27-02-2024
        # x=traceback.extract_stack()
        C=getColors()
        print("     ", C.blue, '-'*10)
        print(f"    {C.yellowH}Stack trace:")
        for item in _stacks:
            print(f"    {C.redH}{item.filename:20}:{item.lineno} - {C.cyan}[{item.function}]")

        print("     ", C.blue, '-'*10)
        print(C.reset)









#############################################################
# logging_dir: if None, no file logger will be created
#############################################################
def setColoredLogger(logger_name: str,
                        main_logger_level: str='trace',
                        console_logger_level: str='critical',
                        file_logger_level: str='warning',
                        logging_dir: str=None,  # if None NO filehandler...
                        create_logging_dir: bool=True,
                        lock_log=False,  # da sperimentare
                        threads: bool=False,
                        prj_log_levels: dict={},
                        module_name_length: int=15): #- lunghezza del nome del modulo nella riga di log


    # logging.setLoggerClass(LoretoLogger("ciao"))
    logging.setLoggerClass(LoretoLogger)
    logger=logging.getLogger(logger_name)

    if lock_log:
        """okkio che può bloccare alcune applicazioni tipo Telegram"""
        logging._acquireLock() # use the global logging lock for thread safety

    '''
        Il nome finale che identifica l'istanza del logger all'interno del sistema logging di Python
        è quello passato nella chiamata standard:
            logger = logging.getLogger(__name__)
            logger = logging.getLogger(logger_name)
    '''
    logger.setup(main_logger_level=main_logger_level,
                 console_logger_level=console_logger_level,
                 file_logger_level=file_logger_level,
                 logging_dir=logging_dir,
                 create_logging_dir=create_logging_dir,
                 lock_log=lock_log,
                 threads=threads,
                 prj_log_levels=prj_log_levels,
                 module_name_length=module_name_length,
        )


    logger.setLogLevels(prj_log_levels)


    if lock_log:
        logging._releaseLock() # use the global logging lock for thread safety

    return logger






if __name__ == '__main__':
    # ----------------------------
    # ----- logging
    # ----------------------------
    # import coloredLogger

    project_log_levels={
        "notset":       logging.NOTSET,    # DEFINED in logging module
        "trace":        logging.DEBUG-1,
        "debug":        logging.DEBUG,      # DEFINED in logging module
        "notify":       logging.INFO -1,
        "info":         logging.INFO,       # DEFINED in logging module
        "function":     logging.WARNING-1,
        "warning":      logging.WARNING,    # DEFINED in logging module
        "error":        logging.ERROR,      # DEFINED in logging module
        "critical":     logging.CRITICAL,   # DEFINED in logging module
    }


    logger=setColoredLogger(logger_name="test",
                            main_logger_level="trace", ### --- default
                            console_logger_level="debug", ### --- default
                            file_logger_level="critical",
                            logging_dir=None, # no filehandler
                            threads=False,
                            create_logging_dir=False,
                            prj_log_levels=project_log_levels)


    logger.info('------- Starting -----------')
    logger.notify('------- Starting -----------')
    logger.function('------- Starting -----------')
    logger.trace('------- Starting -----------')


    logger.forceCALLER=True
    logger.forceFUNCTION=True
    logger.forceNOTIFY=True
    logger.forceTRACE=True


    logger.testLogger()

    try:
        print(x)
    except:
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)

    ### oppure
    try:
        print(x)
    except (Exception) as e:
        traceback.print_exc()
        # print(e)

    except (Exception) as exc:
        xx=traceback.format_exc()
        logger.error("ERROR: %s", xx)

    except:
        logger.error("error loading file", exc_info=True)
        sys.exit(1)

