import json
import re
from datetime import datetime
from pathlib import Path
from src.common.defines import *
from src.cmdInterface import userCmdHandler


class AcroDictHandler:
    """Class to handle all acronym data dictionaries and pass around data between functions"""
    def __init__(self):
        # Get datetime once to keep it constant
        self.str_curr_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.str_prev_date = ""
        self.str_file = "Undefined"  # File path for logging purposes

        self.acros_found = dict()        # Acronyms found in the document
        self.acros_doc_table = dict()    # Acronyms from the document acronyms table
        self.doc_table_processed = False # True if the document acronyms table is found and processed
        self.acros_db = dict()           # Acronyms from the DB
        self.full_db = dict()            # Full DB object. Includes acronyms and administration data
        self.full_db_ori = dict()        # Copy of the full DB object for backuping
        self.acros_output = dict()       # Acronyms to be exported
        self.log_db_changes = {'Added': [], 'Modified': [], 'Deleted': []}
        self.list_no_regex = []  # Todo: Convert to iterable object

        # Load DB
        self.__load_acros_db()

    def search_def_in_doc_table(self, acro_in):
        """Searches for an acronym in the document acronyms table dictionary and returns its definition"""
        definition_list_out = []
        if acro_in in self.acros_doc_table:
            definition_list_out = self.acros_doc_table[acro_in]['Def']
        return definition_list_out

    def search_def_in_db(self, acro_in):
        """Searches for an acronym in the acronym-database dictionary and returns its definition"""
        definition_list_out = []
        if acro_in in self.acros_db:
            definition_list_out = self.acros_db[acro_in]['Def']
        return definition_list_out

    def delete_acro_in_db(self, acro_in):
        """Deletes an acronym from the database. This includes all definitions. Returns True if successful"""
        flag_return = False
        if acro_in in self.acros_db:
            del self.acros_db[acro_in]
            self.log_db_changes['Deleted'].append(acro_in)
            flag_return = True
        return flag_return

    def update_acro_in_db(self, acro_in, def_list_in):
        """Updates or adds an acronym definition on the database"""
        if acro_in not in self.acros_db:
            self.acros_db[acro_in] = {'Def': [], 'Properties': {'Creation': "", 'Last_edit': "", 'Last_uses': []}}
            self.log_db_changes['Added'].append(acro_in)
            self.acros_db[acro_in]['Properties']['Creation'] = self.str_curr_date
        else:
            self.log_db_changes['Modified'].append(acro_in)
        self.acros_db[acro_in]['Def'] = def_list_in
        self.acros_db[acro_in]['Properties']['Last_edit'] = self.str_curr_date

    def update_acro_output(self, acro_in, def_list_in, selection_list_in):
        """Stores the selected acronym definitions for further exportation"""
        self.acros_output[acro_in] = {'Def': []}  # Allows for future dict keys without modifying how defs are accessed
        for i, definition in enumerate(def_list_in):
            if selection_list_in[i]:
                self.acros_output[acro_in]['Def'].append(definition)
        self.__add_db_last_use(acro_in)

    def is_blacklisted(self, acro_in):
        return acro_in in self.full_db['Blacklist']

    def toggle_in_blacklist(self, acro_in):
        if self.is_blacklisted(acro_in):
            idx_found = -1
            for i, bl_entry in enumerate(self.full_db['Blacklist']):
                if bl_entry == acro_in:
                    idx_found = i
                    break
            self.full_db['Blacklist'].pop(idx_found)
        else:
            self.full_db['Blacklist'].append(acro_in)


    def check_db_integrity(self):
        """Returns true if it is safe to overwrite the database"""
        # Currently the check consists on comparing the database ['Admin_data']['Date'] to the one read at the begining
        # If it does not match it means that other user has saved their changes.
        # If the file can not be opened it cant be verified that no changes will be overwriten (This can happen if the
        # acronyms DB file is in a shared folder and conexion is lost)
        flag_is_correct = False
        try:
            db_file_path = Path(config_acro_db_folder) / config_acro_db_file
            with open(db_file_path, 'r', encoding="UTF-8") as db_file:
                aux_full_db = json.load(db_file)
            if aux_full_db['Admin_data']['Date'] == self.str_prev_date:
                flag_is_correct = True
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            userCmdHandler.print_error("No se puede abrir el archivo DB: %s" % str(e))
        except KeyError as e:
            userCmdHandler.print_error("Error al acceder al diccionario: %s" % str(e))
        return flag_is_correct

    def save_db(self, path_output):
        """Saves the database dictionary to a .json file. It also completes the admin data values before saving

        :param path_output: Desired file output path
        """
        # Date with microseconds. Used to know if someone has saved before
        self.__set_admin_data_in_db()
        with open(path_output, 'w', encoding="utf-8") as db_file:
            json.dump(self.full_db, db_file, ensure_ascii=False, sort_keys=True, indent=2)

    def save_db_backup(self, path_output):
        """Saves the original read DB file as a non indented .json

        :param path_output: Desired file output path
        """
        # Backup is not indented to save space. It will get pretty when used again
        with open(path_output, 'w', encoding="utf-8") as db_file:
            json.dump(self.full_db_ori, db_file, ensure_ascii=False, sort_keys=True)

    def __set_admin_data_in_db(self):
        """Sets values asociated to ['Admin_data'] in the DB dictionary"""
        # Add microseconds to allow the possibility of detecting two persons opening the file the same second
        self.full_db['Admin_data']['Date'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S %f")
        self.full_db['Admin_data']['Changelog'] = self.log_db_changes
        self.full_db['Admin_data']['Prev_date'] = self.str_prev_date
        self.full_db['Admin_data']['Version'] = define_acronymate_version

    def __add_db_last_use(self, acro_in):
        """Updates the ['Last_uses'] information of acronym to add the current docx file in use

        :param acro_in: Acronym to be updated
        """
        list_last_uses = self.full_db['Acronyms'][acro_in]['Properties']['Last_uses']
        list_last_uses.append((self.str_file, self.str_curr_date))
        while len(list_last_uses) > 5:
            list_last_uses.pop(0)

    def __load_acros_db(self):
        """Loads the acronyms database file"""
        print("Cargando la base de datos de acrónimos (%s) ..." % config_acro_db_file)
        try:
            db_file_path = Path(config_acro_db_folder) / config_acro_db_file
            with open(db_file_path, 'r', encoding="UTF-8") as db_file:
                self.full_db = json.load(db_file)
                try:
                    self.str_prev_date = self.full_db['Admin_data']['Date']
                except KeyError:
                    self.str_prev_date = "Not found"
                if config_save_backups: #Todo: Perform a deep copy instead of reading two times the file?
                    with open(db_file_path, 'r', encoding="UTF-8") as db_file:
                        self.full_db_ori = json.load(db_file)
        except FileNotFoundError as e:
            userCmdHandler.print_error("Archivo DB no encontrado: %s" % str(e))
        except json.decoder.JSONDecodeError as e:
            userCmdHandler.print_error("Archivo DB no parseable: %s" % str(e))

        self.__check_acros_db()
        self.acros_db = self.full_db['Acronyms']

        if config_use_non_matching_acro_from_db:
            self.__find_non_regex_acronyms()

    def __check_acros_db(self):
        """Checks the loaded database filled. Fixes missing labels if it can"""
        print("Comprobando estado de la base de datos ...")
        flag_status = True
        if 'Acronyms' not in self.full_db:
            userCmdHandler.print_warn("No se encuentran acrónimos, creando diccionario vacío")
            self.full_db['Acronyms'] = dict()
            flag_status = False
        else:
            for key in self.full_db['Acronyms']:
                if 'Def' not in self.full_db['Acronyms'][key]:
                    self.full_db['Acronyms'][key]['Def'] = [{'Main': ""}]
                if self.full_db['Acronyms'][key]['Def'][0]['Main'] == "":
                    userCmdHandler.print_warn("El acrónimo %s está vacío" % key)
                    flag_status = False

                if 'Properties' not in self.full_db['Acronyms'][key]:
                    self.full_db['Acronyms'][key]['Properties'] = {'Creation': "", 'Last_edit': "", 'Last_uses': []}
                if self.full_db['Acronyms'][key]['Properties']['Creation'] == "":
                    self.full_db['Acronyms'][key]['Properties']['Creation'] = self.str_curr_date
                    self.__add_db_last_use(key)
                if self.full_db['Acronyms'][key]['Properties']['Last_edit'] == "":
                    self.full_db['Acronyms'][key]['Properties']['Last_edit'] = \
                        self.full_db['Acronyms'][key]['Properties']['Creation']

        if 'Blacklist' not in self.full_db:
            self.full_db['Blacklist'] = []
            #Todo: Sanitize: Remove blacklist duplicates

        if 'Admin_data' not in self.full_db:
            userCmdHandler.print_warn("No se encuentra la sección Admin_data, no se podrá verificar el guardado seguro")
            self.full_db['Admin_data'] = dict()
            self.__set_admin_data_in_db()
            flag_status = False
        else:
            if 'Date' not in self.full_db['Admin_data']:
                userCmdHandler.print_warn(
                    "No se encuentra la fecha en Admin_data, no se podrá verificar el guardado seguro")
                flag_status = False

        if flag_status:
            userCmdHandler.print_ok("Base de datos correcta")

    def __find_non_regex_acronyms(self):
        """Compiles list of acronyms that do not match the current regex"""
        for acro in self.acros_db.keys():
            if not re.match(define_regex_acro_find, acro):
                self.list_no_regex.append(acro)

    def add_acronym_found(self, acro_in, str_context_in):
        # 4. Create empty dict if acronym is first found
        if acro_in not in self.acros_found:
            self.acros_found[acro_in] = {'Count': 0, 'Context': []}

        # Store data of acronym in dict
        self.acros_found[acro_in]['Count'] += 1
        self.acros_found[acro_in]['Context'].append(str_context_in)

    def is_doc_table_processed(self):
        return self.doc_table_processed

    def set_doc_table_processed(self):
        self.doc_table_processed = True

    def add_acronym_doc_table(self, acro_in, str_main, str_trans):
        # Create dict entry
        if acro_in not in self.acros_doc_table:
            # Some tables have duplicated lines for multiple definitions
            self.acros_doc_table[acro_in] = {'Def': []}

        aux_def = dict()
        aux_def['Main'] = str_main
        if str_trans != "":
            aux_def['Translation'] = str_trans
        self.acros_doc_table[acro_in]['Def'].append(aux_def)