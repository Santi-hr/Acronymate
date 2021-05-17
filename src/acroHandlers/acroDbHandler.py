import json
import re
from datetime import datetime
from pathlib import Path
from src.common import defines as dv
from src.common import configVars as cv
from src.cmdInterface import userCmdHandler


class AcroDbHandler:
    """Class to handle the acronym data base"""
    def __init__(self):
        self.str_curr_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.str_prev_date = ""

        self.acros_db = dict()      # Acronyms from the DB. Helper reference
        self.full_db = dict()       # Full DB object. Includes acronyms and administration data
        self.full_db_ori = dict()   # Copy of the full DB object for backup
        self.log_db_changes = {'Added': [], 'Modified': [], 'Deleted': []}
        self.list_no_regex = []  # Todo: Convert to iterable object?

        self.needs_save = True  # Some processing modes does not change the DB files and saving can be avoided

        # Load DB after object creation
        self.load_acros_db()

    def add_db_last_use(self, acro_in, str_last_use_file):
        """Updates the ['Last_uses'] information of acronym to add the current docx file in use

        :param acro_in: Acronym to be updated
        """
        if acro_in in self.full_db['Acronyms']:
            list_last_uses = self.full_db['Acronyms'][acro_in]['Properties']['Last_uses']
            list_last_uses.append((str_last_use_file, self.str_curr_date))
            while len(list_last_uses) > 5:
                list_last_uses.pop(0)

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

    def is_blacklisted(self, acro_in):
        """Returns True if acronym is in the blacklist"""
        return acro_in in self.full_db['Blacklist']

    def toggle_in_blacklist(self, acro_in):
        """Toggles the acronym blacklist status"""
        if self.is_blacklisted(acro_in):
            idx_found = -1
            for i, bl_entry in enumerate(self.full_db['Blacklist']):
                if bl_entry == acro_in:
                    idx_found = i
                    break
            self.full_db['Blacklist'].pop(idx_found)
        else:
            self.full_db['Blacklist'].append(acro_in)

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

    def check_db_integrity(self):
        """Returns true if it is safe to overwrite the database"""
        # Currently the check consists on comparing the database ['Admin_data']['Date'] to the one read at the begining
        # If it does not match it means that other user has saved their changes.
        # If the file can not be opened it cant be verified that no changes will be overwriten (This can happen if the
        # acronyms DB file is in a shared folder and conexion is lost)
        flag_is_correct = False
        try:
            db_file_path = Path(cv.config_acro_db_path)
            with open(db_file_path, 'r', encoding="UTF-8") as db_file:
                aux_full_db = json.load(db_file)
            if aux_full_db['Admin_data']['Date'] == self.str_prev_date:
                flag_is_correct = True
        except FileNotFoundError as e:
            userCmdHandler.print_db_except_file_not_found(e)
        except json.decoder.JSONDecodeError as e:
            userCmdHandler.print_db_except_decode_error(e)
        except KeyError as e:
            userCmdHandler.print_db_except_key_error(e)
        return flag_is_correct

    def load_acros_db(self):
        """Loads the acronyms database file"""
        userCmdHandler.print_db_loading_info(cv.config_acro_db_path)
        try:
            db_file_path = Path(cv.config_acro_db_path)
            with open(db_file_path, 'r', encoding="UTF-8") as db_file:
                self.full_db = json.load(db_file)
                try:
                    self.str_prev_date = self.full_db['Admin_data']['Date']
                except KeyError:
                    self.str_prev_date = "Not found"
                if cv.config_save_backups: #Todo: Perform a deep copy instead of reading two times the file?
                    with open(db_file_path, 'r', encoding="UTF-8") as db_file:
                        self.full_db_ori = json.load(db_file)
        except FileNotFoundError as e:
            userCmdHandler.print_db_except_file_not_found(e)
        except json.decoder.JSONDecodeError as e:
            userCmdHandler.print_db_except_decode_error(e)

        self.__check_acros_db()
        self.acros_db = self.full_db['Acronyms']

        if cv.config_use_non_matching_acro_from_db:
            self.__find_non_regex_acronyms()

    def __check_acros_db(self):
        """Checks the loaded database filled. Fixes missing labels if it can"""
        userCmdHandler.print_db_checking()
        flag_status = True
        if 'Acronyms' not in self.full_db:
            userCmdHandler.print_db_check_no_acros()
            self.full_db['Acronyms'] = dict()
            flag_status = False
        else:
            for key in self.full_db['Acronyms']:
                if 'Def' not in self.full_db['Acronyms'][key]:
                    self.full_db['Acronyms'][key]['Def'] = [{'Main': ""}]
                if self.full_db['Acronyms'][key]['Def'][0]['Main'] == "":
                    userCmdHandler.print_db_check_empty_acro(key)
                    flag_status = False

                if 'Properties' not in self.full_db['Acronyms'][key]:
                    self.full_db['Acronyms'][key]['Properties'] = {'Creation': "", 'Last_edit': "", 'Last_uses': []}
                if self.full_db['Acronyms'][key]['Properties']['Creation'] == "":
                    self.full_db['Acronyms'][key]['Properties']['Creation'] = self.str_curr_date
                    self.add_db_last_use(key, "Undefined_file")
                if self.full_db['Acronyms'][key]['Properties']['Last_edit'] == "":
                    self.full_db['Acronyms'][key]['Properties']['Last_edit'] = \
                        self.full_db['Acronyms'][key]['Properties']['Creation']

        if 'Blacklist' not in self.full_db:
            self.full_db['Blacklist'] = []
            #Todo: Sanitize: Remove blacklist duplicates

        if 'Admin_data' not in self.full_db:
            userCmdHandler.print_db_check_admin_data_wrong()
            self.full_db['Admin_data'] = dict()
            self.__set_admin_data_in_db()
            flag_status = False
        else:
            if 'Date' not in self.full_db['Admin_data']:
                userCmdHandler.print_db_check_admin_data_wrong()
                flag_status = False

        if flag_status:
            userCmdHandler.print_ok(_("Base de datos correcta"))

    def __set_admin_data_in_db(self):
        """Sets values asociated to ['Admin_data'] in the DB dictionary"""
        # Add microseconds to allow the possibility of detecting two persons opening the file the same second
        self.full_db['Admin_data']['Date'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S %f")
        self.full_db['Admin_data']['Changelog'] = self.log_db_changes
        self.full_db['Admin_data']['Prev_date'] = self.str_prev_date
        self.full_db['Admin_data']['Version'] = dv.define_acronymate_version

    def __find_non_regex_acronyms(self):
        """Compiles list of acronyms that do not match the current regex"""
        self.list_no_regex = [acro for acro in self.acros_db.keys() if not re.fullmatch(cv.config_regex_acro_find, acro)]
