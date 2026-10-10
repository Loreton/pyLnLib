#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# updated by ...: Loreto Notarantonio
# Date .........: 29-02-2024 08.35.50
#
# ####################################################################################################################

import  sys; sys.dont_write_bytecode=True
import os
from types import SimpleNamespace

import sqlite3
import inspect
import json

import collections
from pathlib import Path
from benedict import benedict

INFO = 1



#####################################
# gVars is benedict dictionary
#####################################
def setup(gVars):
    global gv, C
    gv=gVars
    C=gv.logger.getColors()
    gv.logger.info('Entering in function...')




###############################################################################
# DB_Class - DB_Class - DB_Class - DB_Class - DB_Class - DB_Class - DB_Class -
###############################################################################
class SQLite_Class:
    dbFiles={"field_file_name": "value_connection"}

    def __init__(self, *, db_filename: str, logger, create: bool=False):
        self.logger=logger
        self.logger.caller('Entering in function...')
        self.dbfilename=Path(db_filename).resolve()


        self.connection=self.openDB(create=create)



        # ***********************************************
        # * OpenDBase
        # - Connecting to the database file
        # ***********************************************
    def openDB(self, create: bool=False):
        self.logger.caller('Entering in function...')

        #================================================
        def checkDBFile(create: bool):
            self.logger.caller('Entering in function...')
            dbDir = self.dbfilename.parent
            if not dbDir.is_dir():
                self.logger.error('La directory: %s non esiste. Crearla prima di proseguire.', dbDir)
                sys.exit(1)

            if self.dbfilename.is_file():
                self.logger.info("DBFile already exists: %s", self.dbfilename)
                if create==True:
                    msg = f"""      DBFile {self.dbfilename} already exists - are you sure to replace it\n\n      [Y]es"""
                    choice = self.keyb_prompt(text_msg=msg, validKeys=["y", "pass_back"], exitKeys=["q", "x"])
                    if choice.lower() == 'y':
                        self.logger.info("deleting: %s", self.dbfilename )
                        self.dbfilename.unlink()
        #================================================



        checkDBFile(create=create)
        self.logger.info("connecting to DBase: %s", self.dbfilename)
        try:
            connection = sqlite3.connect(self.dbfilename)
            # connection = sqlite3.connect(self.dbfilename, detect_types=sqlite3.PARSE_DECLTYPES)
        except Exception as why:
            print (str(why))
            sys.exit()


        return connection



    # ***********************************************
    # * struct  = create table if not exists ${Table.name} (
    # *                    "Type"              STRING  NOT NULL,
    # *                    "Author Name"       STRING  NOT NULL
    # *                )
    # * tested on: 25-02-2024 17.13.55
    # ***********************************************
    def createTable(self, *, table_name: str, struct: str, create: bool=False):
        self.logger.caller('Entering in function...')
        tables=self.getTableList()

        fCreate=create
        if table_name in tables and create==True:
            msg = f"""      {table_name} table already exists - are you sure to replace it?\n      [Y]es"""
            choice = self.keyb_prompt(text_msg=msg, validKeys=["y", "pass_back"], exitKeys=["q", "x"])
            if choice.lower() != 'y':
                fCreate=False
                self.logger.info("table: %s has not been replaced!", table_name)

        if fCreate:
            self.Execute(f"DROP TABLE if exists  {table_name}")
            self.Execute(f"CREATE TABLE if not exists {table_name} {struct}")

        self.Commit()           #  aggiorna il dictionary della struttura


    # ***********************************************
    # *
    # ***********************************************
    def getTableClass(self, table_name: str, primary_key: str, struct: str="", create: bool=False):
        self.logger.caller('Entering in function...')
        tables=self.getTableList()

        if create:
            self.createTable(table_name=table_name, struct=struct, create=create)

        elif table_name in tables:
            pass

        else:
            self.logger.error("table: %s not found in database", table_name)
            sys.exit(1)

        return SqLiteTable_Class(DB=self, table_name=table_name, primary_key=primary_key)



    # ***********************************************
    # *
    # ***********************************************
    def _dictType(self):
        self.logger.caller('Entering in function...')
        return benedict(keyattr_enabled=True, keyattr_dynamic=False)

    # ***********************************************
    # *
    # ***********************************************
    def _getCursor(self):
        self.logger.caller('Entering in function...')
        return self.connection.cursor()

    # ***********************************************
    # *
    # ***********************************************
    def getTableList(self):
        self.logger.caller('Entering in function...')
        tableListQuery = "SELECT * FROM sqlite_master WHERE type='table' ORDER BY Name"

        cur = self._getCursor()
        cur.execute(tableListQuery)
        tables = cur.fetchall()
            # --- Get struct of Tables:
        _list=[]
        for table in tables:
            _list.append(table[1])
        return _list


    # ***********************************************
    # *
    # ***********************************************
    def Commit(self):
        self.logger.caller('Entering in function...')
        self.logger.info('Committing...')
        self.connection.commit()

    # ***********************************************
    # *
    # ***********************************************
    def Execute(self, command: str, fCOMMIT: bool=False, ignoreCase: bool=False, stacklevel: int=1):
        self.logger.caller('Entering in function...')
            # ============================================================
        def execute_sql_command(sql_command, stacklevel: int=2):
            self.logger.caller('Entering in function...')
            self.logger.info("command: %s", sql_command, stacklevel=stacklevel+1)

            try:
                cur=self._getCursor()
                data=cur.execute(sql_command)
                rcode=False

            except (Exception) as why:
                self.logger.error("... problem: %s", why)
                rcode=True
                data=None

            if data:
                totalChanges = self.connection.total_changes

                self.logger.info('returned_data: %s', data)
                self.logger.info('totalChanges:  %s', totalChanges)


            ret=SimpleNamespace(
                    rcode=rcode,
                    cursor=cur,
                    data=data,
                    total_changes=self.connection.total_changes)
            return ret
            # ============================================================


        ret=execute_sql_command(command, stacklevel=stacklevel+1)
        if fCOMMIT:
            self.Commit()
        return ret





        # ***********************************************
        # *
        # ***********************************************
    def Close(self):
        self.logger.caller('Entering in function...')
        self.Commit()
        self.connection.close()



    #######################################################
    # validKeys["pass_back"] pass any choice to back bat exitKeys
    #######################################################
    def keyb_prompt(self, *, text_msg: str, validKeys: list=["y", "n"], exitKeys: list=["x", "q"]):
        self.logger.caller('Entering in function...')
        text_msg+= " - [" + '|'.join(exitKeys) + "]quit ->: "
        if "ENTER" in exitKeys  or "enter" in exitKeys: exitKeys.append("")
        if "ENTER" in validKeys or "enter" in validKeys: validKeys.append("")

        while True:
            choice=input(text_msg).lower()
            if choice in exitKeys: # diamo priorità all'uscita
                print("Exiting on user request.")
                sys.exit(0)

            elif choice in validKeys:
                break

            elif "pass_back" in validKeys:
                break

            else:
                print('\n... please enter some valid key:', validKeys, "or exit key:", exitKeys)

        return choice



        # ***********************************************
        # *
        # ***********************************************
    def Version(self, fPRINT=False):
        self.logger.caller('Entering in function...')
        cur = self._getCursor()
        cur.execute('SELECT SQLITE_VERSION()')
        version = cur.fetchone()
        if fPRINT:
            print ("SQLite version: {VERSION}".format(VERSION=version))

        return version





    ##############################################################
    # # return:
    # #     primary_keys
    # #     column_names
    # #     struct_dict
    ##############################################################
    def _TableStruct(self, table_name: str):
        self.logger.caller('Entering in function...')

            # --------------------------
            # - get structure
            #    = (FieldNO, fieldName, columnType, NOT_NULL, DEF_VALUE, PRI_KEY)
            # --------------------------
        ret=self.Execute(f"PRAGMA TABLE_INFO({table_name})")
        struct=ret.data

        primary_keys=[]
        column_names=[]
        struct_dict=self.db._dictType()

        for field in struct:
            self.logger.info(field)
            seq, NAME, TYPE, NOT_NULL, DEFAULT, PRI_KEY = field
            column_names.append(NAME)
            if PRI_KEY>0:
                primary_keys.append(NAME)


            struct_dict[NAME] = self.db._dictType()
            ptr                      = struct_dict[NAME]
            ptr['name']              = NAME
            ptr['type']              = TYPE
            ptr['canBeNULL']         = not NOT_NULL
            ptr['defaultVAL']        = DEFAULT
            ptr['isPrimaryKey']      = PRI_KEY


        ret=self.Execute(f"SELECT Count() FROM {table_name}")
        numberOfRows  = ret.cursor.fetchone()[0]
        return column_names, primary_keys, struct_dict




    # sono arrivato qui ##############################################################
    # sono arrivato qui ##############################################################
    # sono arrivato qui ##############################################################
    # sono arrivato qui ##############################################################
    # sono arrivato qui ##############################################################
    # sono arrivato qui ##############################################################




    # ###################################################################
    # - Inserisce una riga in una tabella.
    # - Se row==[LIST di [LIST]] allora fa una massInsert/executeMany
    # - INSERT into LOGTABLE (ts, level, message)   VALUES (111, "autoinc test", "autoinc test");
    # - INSERT into LOGTABLE                        VALUES (111, "autoinc test", "autoinc test");
    # ###################################################################
    def updateRow_(self, *, table_name: str, row: dict, fCOMMIT=False):
        self.logger.caller('Entering in function...')

        cols=[]
        values=[]
        for k,v in row.items():
            cols.append(k)
            values.append(v)

        import pdb; pdb.set_trace();trace=True # by Loreto
        cols = tuple(cols)
        nFields = len(cols)   # TESTED OK
        fields = '?'
        for inx in range(1, nFields):
            fields += ',?'


        whereString, setString = self._WhereAndSet_Clause(tblName, cols=cols, values=values)
        # import pdb; pdb.set_trace(); pass # by Loreto
        updCommand = 'UPDATE {TABLE} SET {SET} WHERE {WHERE})'.format(TABLE=tblName, SET=setString, WHERE=whereString)

        # InsertCommand = 'UPDATE or IGNORE  {TABLE} {COLS} VALUES ({FIELDS})'.format(TABLE=tblName, FIELDS=fields, COLS=cols)
        self.logger.info(updCommand)

        # InsertCommand = 'INSERT or IGNORE into {TABLE} {COLS} VALUES ({FIELDS}) WHERE (Select Changes() = 0);'.format(TABLE=tblName, FIELDS=fields, COLS=cols)
        InsertCommand = 'INSERT or IGNORE into {TABLE} {COLS} SELECT {VALUES} WHERE (Select Changes() = 0);'.format(TABLE=tblName, VALUES=values, COLS=cols)
        self.logger.info('%s %s', InsertCommand, values)

        self._sqlExecute(InsertCommand, fCOMMIT=fCOMMIT)







        # ***********************************************
        # * Ritorna la struttura e dati del DB
        # * suddivisi in tabelle.
        # * LnDict può essere:
        #   -  gv.Ln.LnDict
        #   -  {}
        #   -  collections.OrderedDict
        # ***********************************************
    def read_DBStruct(self):
        self.logger.caller('Entering in function...')

        import pdb; pdb.set_trace();trace=True # by Loreto
        # --- Get List of Tables:
        cur = self.connection.cursor()
        # tableListQuery = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY Name"
        tableListQuery = "SELECT * FROM sqlite_master WHERE type='table' ORDER BY Name"
        cur.execute(tableListQuery)
        tables = cur.fetchall()                          # Loreto

            # --- Get struct of Tables:
        for table in tables:
            tblName = table[1]
            if not tblName in self.dbDict:
                self.dbDict[tblName] = self.db._dictType()
            self.dbDict[tblName]['createCommand'] = table[4]
            self._TableStruct(tblName)

        return self.dbDict



















##################################################################################################
##################################################################################################
##################################################################################################
# tableClasse
# tableClasse
# tableClasse
##################################################################################################
##################################################################################################
##################################################################################################

# class SqLiteTable_Class(SqLiteDB_Class):
class SqLiteTable_Class():
    profile="Tabella"

    def __init__(self, *, DB, table_name: str, primary_key: str):
        # super().__init__(db_filename=db_filename, logger=logger, create=create)

        self.db=DB
        self.logger=DB.logger
        self.logger.caller('Entering in function...')

        self.primary_key=primary_key

        ### impostazione caratteristiche della tabella
        self.table_name=table_name
        self.column_names, self.primary_keys, self.struct_dict = self._calculateStruct()




    ##############################################################
    # # return:
    # #     primary_keys
    # #     column_names
    # #     struct_dict
    ##############################################################
    def _calculateStruct(self):
        self.logger.caller('Entering in function...')

        # --------------------------
        # -  = (FieldNO, fieldName, columnType, NOT_NULL, DEF_VALUE, PRI_KEY)
        # --------------------------
        ret=self.db.Execute(f"PRAGMA TABLE_INFO({self.table_name})")
        struct=ret.data

        primary_keys=[]
        column_names=[]
        struct_dict=self.db._dictType()

        for field in struct:
            self.logger.info(field)
            seq, NAME, TYPE, NOT_NULL, DEFAULT, PRI_KEY = field
            column_names.append(NAME)
            if PRI_KEY>0:
                primary_keys.append(NAME)


            struct_dict[NAME] = self.db._dictType()
            ptr                      = struct_dict[NAME]
            ptr['name']              = NAME
            ptr['type']              = TYPE
            ptr['canBeNULL']         = not NOT_NULL
            ptr['defaultVAL']        = DEFAULT
            ptr['isPrimaryKey']      = PRI_KEY

        if not self.primary_key in primary_keys:
            self.logger.error("Primary Key: %s not found in table structure", self.primary_key)
            sys.exit(1)

        ret=self.db.Execute(f"SELECT Count() FROM {self.table_name}")
        numberOfRows  = ret.cursor.fetchone()[0]
        return column_names, primary_keys, struct_dict



    ##############################################################
    # #
    ##############################################################
    def totalChanges(self):
        return self.db.connection.total_changes


    ##############################################################
    # #
    ##############################################################
    def _defaultRow(self):
        self.logger.caller('Entering in function...')
        row={}
        for colname, data in self.struct_dict.items():
            row[colname]=data["defaultVAL"]
        return row



    ##############################################################
    # #
    ##############################################################
    def _from_dict_to_cols(self, new_record: dict):
        self.logger.caller('Entering in function...')
        cols=[]
        values=[]

        for colname in self.column_names:
            if colname in new_record:
                new_val=new_record[colname]
                if isinstance(new_val, str):
                    if new_val.lower() not in ["null", "-"]:
                        cols.append(colname)
                        values.append(new_val)
                elif isinstance(new_val, (dict)):
                        cols.append(colname)
                        # values.append(new_val.to_pickle())
                        json_data=new_val.to_json()
                        # values.append(f"json({json_data}")
                        values.append(json_data)

                elif isinstance(new_val, (list)):
                        cols.append(colname)
                        values.append(",".join(new_val))
                else:
                    pass ### skip column ---will bi filled with NULL


        return tuple(cols), tuple(values)




        # ###################################################################
        # - Creiamo una WHERE clause con i dati delle colonne
        # ###################################################################
    def _WhereAndSet_Clause(self, table_name, cols, values):
        self.logger.caller('Entering in function...')
        setList   = []
        whereList = []
        for colname, value in zip(cols, values):
            string=f'"{colname.strip()}"="{value}"'
            setList.append(string)
            if colname in self.primary_keys:
                whereList.append(string)

        setString = ', '.join(setList)
        whereString = ' and '.join(whereList)

        return whereString, setString



        # ###################################################################
        # - verifica se il record identificato dal whereString esiste
        # - tested:  27-02-2024
        # ###################################################################
    def _RowExists(self, whereString: str, ignoreCase=True):
        self.logger.caller('Entering in function...')

        ret=self.db.Execute(f'SELECT Count() from {self.table_name} WHERE {whereString} COLLATE NOCASE')
        nRowsFound=ret.cursor.fetchone()[0]

        return nRowsFound



        # ###################################################################
        # - ritorna il record identificato dal whereString
        # - tested:  27-02-2024
        # ###################################################################
    def _selectRecord(self, whereString: str, to_dict: True):
        self.logger.caller('Entering in function...')

        sql_command=f'SELECT * from {self.table_name} WHERE {whereString} COLLATE NOCASE'
        ret=self.db.Execute(sql_command)

        records=ret.cursor.fetchall()

        if len(records)==0:
            self.logger.warning("NO records found")
            return None

        elif len(records)>1:
            self.logger.error("more than one record were found. Should NOT occur")
            self.logger.error("command: %s", sql_command)
            sys.exit(1)

        if to_dict: ### convert records to dict
            d_records=[]
            """https://copyprogramming.com/howto/sqlite-and-python-return-a-dictionary-using-fetchone"""
            record=dict(zip([c[0] for c in ret.cursor.description], records[0]))
            for item in records:
                d_records.append(dict(zip([c[0] for c in ret.cursor.description], item)))
            records=d_records


        return record




        # ###################################################################
        # - ritorna tutti i records della tabella
        # ###################################################################
    def _selectAllRows(self, whereString: str, ignoreCase=True):
        self.logger.caller('Entering in function...')

        ret=self.db.Execute(f'SELECT * from {self.table_name}')
        records=ret.cursor.fetchall()
        return records

        print("Total rows are:  ", len(records))
        print("Printing each row")
        for row in records:
            print(row)



            rowDict = dict(zip([c[0] for c in cur.description], record))



    def get_diff_fields(self, curr_record, new_record):
        self.logger.caller('Entering in function...')
        cols=[]
        values=[]
        for colname in self.column_names:
            if colname in new_record:

                new_val=new_record[colname]
                curr_val=curr_record[colname]

                if self.struct_dict[colname]["type"]=="TEXT":
                    if new_val==curr_val:
                        print("equals = True", new_val)
                        new_record.pop(colname)
                        continue

                elif self.struct_dict[colname]["type"]=="INTEGER":
                    if int(new_val)==int(curr_val):
                        print("equals = True", new_val)
                        new_record.pop(colname)
                        continue


                else:
                    if isinstance(new_val, str):
                        if new_val.lower() not in ["null", "-"]:
                            cols.append(colname)
                            values.append(new_val)

                    elif isinstance(new_val, (dict)):
                            cols.append(colname)
                            # values.append(new_val.to_pickle())
                            json_data=new_val.to_json()
                            # values.append(f"json({json_data}")
                            values.append(json_data)

                    elif isinstance(new_val, (list)):
                            cols.append(colname)
                            values.append(",".join(new_val))

                    else:
                        pass ### skip column ---will bi filled with NULL




        return tuple(cols), tuple(values)





        # ###################################################################
        # - Inserisce una riga (se non esiste) oppure fa update
        # - tested:  27-02-2024
        # ###################################################################
    def insertUpdateRow(self, new_record, fCOMMIT: bool=False):
        self.logger.caller('Entering in function...')

        cols, values=self._from_dict_to_cols(new_record=new_record)
        whereString, setString = self._WhereAndSet_Clause(self.table_name, cols=cols, values=values)

        # curr_record=self._selectRecord(whereString=whereString, to_dict=True)

        # import pdb; pdb.set_trace();trace=True # by Loreto

        # self._from_dict_to_cols_diff(curr_record, new_record)

        # read record ... if exists
        if curr_record:=self._selectRecord(whereString=whereString, to_dict=True):
            cols, values=self.get_diff_fields(curr_record, new_record)

            import pdb; pdb.set_trace();trace=True # by Loreto
            self.logger.info("updating record WHERE: %s", whereString)
            # sqlCommand = f'UPDATE {self.table_name} SET {setString} WHERE {whereString} COLLATE NOCASE'
            sqlCommand = f'INSERT or REPLACE into {self.table_name} {cols} VALUES {values}'
            self.db.Execute(sqlCommand, fCOMMIT=fCOMMIT)

        else:
            self.logger.info("inserting record WHERE: %s", whereString)
            sqlCommand = f'INSERT into {self.table_name} {cols} VALUES {values}'
            self.db.Execute(sqlCommand, fCOMMIT=fCOMMIT)





    ##############################################################
    # #
    ##############################################################
    def getStruct(self):
        self.logger.caller('Entering in function...')
        return self.struct_dict

    ##############################################################
    # #
    ##############################################################
    def columnNames(self):
        self.logger.caller('Entering in function...')
        return self.column_names

    ##############################################################
    # #
    ##############################################################
    def primaryKeys(self):
        self.logger.caller('Entering in function...')
        return self.primary_keys




def simple_logger():
    self.logger.caller('Entering in function...')
    import logging
    # Enable logging
    logging.basicConfig(
        # filename='/tmp/xxxxx.log',
        # encoding='utf-8', # solo dal 3.9
        level=logging.DEBUG,
        # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        format='%(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    return logger




##########################################################################
# https://github.com/borntyping/python-colorlog/blob/main/doc/example.py
##########################################################################
def setup_logger(logger_name: str="simple_logger", logger_level: str="info", colored=True):
    self.logger.caller('Entering in function...')
    import logging

    my_levels={
        "critical": 50,
        "caller": 45,
        "error": 40,
        "notify": 33,
        "warning": 30,
        "function": 25,
        "info": 20,
        "debug": 10,
        "trace": 5,
        "notset": 0,
    }


    # --------- Adding NOTIFY level -------------------
    def addNotifyLevel(level):
        self.logger.caller('Entering in function...')
        logging.NOTIFY=level
        def _notify(logger, message, *args, **kwargs):
            self.logger.caller('Entering in function...')
            if logger.isEnabledFor(logging.NOTIFY):
                logger._log(logging.NOTIFY, message, args, **kwargs)
        logging.Logger.notify = _notify
        logging.addLevelName(logging.NOTIFY, "NOTIFY")
    # --------- Adding NOTIFY level -------------------

    # create logging formatter
    if colored:
        from colorlog import ColoredFormatter
        formatter = ColoredFormatter(
            "%(cyan)s%(asctime)s %(blue)s[%(module)s.%(funcName)s:%(lineno)4s] %(log_color)s[%(levelname)4s] : %(log_color)s%(message)s",
            datefmt="%H:%M:%S",
            reset=True,
            log_colors={
                'TRACE':    'blue',
                'DEBUG':    'cyan',
                'NOTIFY':   'fg_bold_cyan',
                'INFO':     'green',
                'FUNCTION': 'fg_bold_yellow',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CALLER':   'red',
                'CRITICAL': 'red,bg_white',
            },
        )


    else:
        formatter=logging.Formatter(
            fmt="%(asctime)s [%(module)s.%(funcName)s:%(lineno)4s] [%(levelname)4s] : %(message)s",
            datefmt="%H:%M:%S",
            style="%"
            )


    addNotifyLevel(level=my_levels["notify"])

    # create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel("DEBUG")

    # create console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    consoleHandler.setLevel(logger_level.upper())

    # Add console handler to logger
    logger.addHandler(consoleHandler)

    logger.propagate = False # se messo a True mi trovo due righe di log, una colorata e l'altra no.

    return logger


def createDevicesDB(db_filename):
    self.logger.caller('Entering in function...')
    table_name = 'devicesDB'
    table_struct='''(
            "name"          TEXT,
            "mac"           TEXT,
            "ip"            TEXT,
            "type"          TEXT,
            "dhcp_action"   TEXT,
            "leasetime"     TEXT,
            "chat_id"       INTEGER,
            "bot_name"      TEXT,
            "descr"         TEXT,
            primary key ("name"),
        )
        '''


    #================= create DB and Table ==================
    myDB=SqLiteDB_Class(db_filename=db_filename, create=True, logger=logger)
    myDB.Version(fPRINT=True)
    myTable=myDB.createTable(table_name=table_name, struct=table_struct)
    myDB.Close()


#################################################################
#   M   A   I   N
#################################################################

if __name__ == '__main__':
    '''
    ref: https://www.sqlitetutorial.net/sqlite-unique-constraint/
        UNIQUE constraint can have multiple NULL values.
        Primary keys must contain unique values. A primary key column cannot have NULL values.
    '''


    import yaml
    file1=Path("/tmp/resolved_devices_01.yaml")
    file2=Path("/tmp/resolved_devices_02.yaml")
    with file1.open(mode="r") as f:
        content1=f.read() # single string
    with file2.open(mode="r") as f:
        content2=f.read() # single string


    d1=yaml.load(content1, Loader=yaml.FullLoader)
    d2=yaml.load(content2, Loader=yaml.FullLoader)
    print(d1==d2)
    sys.exit()

    logger=setup_logger()
    db_filename=os.path.expandvars("$HOME/Downloads/SQLite_test/Test02.db")

    createDevicesDB(db_filename)



    import pdb; pdb.set_trace();trace=True # by Loreto




















    Recs = (myDB.TableToList(TableName))
    nRows = myDB.nRows(TableName)
    print("TableName1 Records:", len(Recs), "nRows:", nRows)
    # print (Recs)
    new_record={'last_update': None,
                'device_name': 'test_for_update_Yx',
                'device_type': f'device_{_time}',
                'host_name': None,
                'ip_address': '192.168.5.99',
                'mac': 'XX:4F:22:D5:6B:Yx',
                'bot_name': f'no_Bot_{_time}',
                'room': f'Vano Test_{_time}',
                'description': f'test descr_{_time}'}

    where_items=[   {'mac': new_record['mac']},
                    "OR",
                    {'device_name': new_record['device_name']},
                ]

    where_items=[f'mac=={new_record["mac"]}', "OR", f'device_name=={new_record["device_name"]}']
    where_items=[f'mac=={new_record["mac"]}', "OR", {'device_name': new_record['device_name']}]

    curr_rec=devicesDB.updateRec(where_items=where_items, new_record=new_record, insert_on_NFND=True)
    print(curr_rec)




    myDB.Describe()
    myDB.Close()
    sys.exit()
