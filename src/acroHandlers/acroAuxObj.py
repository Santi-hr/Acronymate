from src.cmdInterface import ansiColorHelper as ach


class acroAuxObj:
    """Class to handle one acronym while user updates it"""
    def __init__(self, acro, dict_handler):
        """Class constructor

        :param acro: Acronym string
        :param dict_handler: Acronym dictionary handler
        """
        self.acro = acro
        self.dict_handler = dict_handler
        self.proposed_def = [{'Main': ""}]
        self.flag_update_db = True # If acro is not found in the db it would need to be added

        # Look acronym in table document
        self.def_list_doc_table = self.dict_handler.search_def_in_doc_table(self.acro)
        if len(self.def_list_doc_table) > 0:
            self.proposed_def = self.def_list_doc_table

        # Look acronym in database
        self.def_list_db = self.dict_handler.obj_db.search_def_in_db(self.acro)
        # DB has priority
        if len(self.def_list_db) > 0:
            self.proposed_def = self.def_list_db
            self.flag_update_db = False

        # Fill the selected list
        self.selected_def = []
        for i in range(len(self.proposed_def)):
            self.selected_def.append(True)

    def has_multiple_defs(self):
        """Returns True if acronym has multiple definitions"""
        flag_return = False
        if len(self.proposed_def) > 1:
            flag_return = True
        return flag_return

    def is_in_db(self):
        """Returns True if acronym is in database"""
        flag_return = False
        if len(self.def_list_db) > 0:
            flag_return = True
        return flag_return

    def is_blacklisted(self):
        """Returns True if the acronym is in the database blacklist"""
        return self.dict_handler.obj_db.is_blacklisted(self.acro)

    def toggle_blacklisted_status(self):
        """Toggles blacklist status in the db"""
        self.dict_handler.obj_db.toggle_in_blacklist(self.acro)

    def defs_discrepancy(self):
        """Returns True if db definition does not match with the acronym table one. As this means that the acro could
        have different or other def than the one in the db. If def is not found in the acro table the fcn returns False
        """
        flag_return = False
        # Check discrepancy only if definitions found both in db and acro table
        if len(self.def_list_db) > 0 and len(self.def_list_doc_table) > 0:
            if len(self.def_list_db) != len(self.def_list_doc_table):
                flag_return = True
            else:
                for i in range(len(self.def_list_db)):
                    if self.def_list_db[i]['Main'] == self.def_list_doc_table[i]['Main']:
                        # Compare Translations. If its not found the string will be empty
                        str_trans_db, str_trans_doc = "", ""
                        if 'Translation' in self.def_list_db[i]:
                            str_trans_db = self.def_list_db[i]['Translation']
                        if 'Translation' in self.def_list_doc_table[i]:
                            str_trans_doc = self.def_list_doc_table[i]['Translation']
                        if str_trans_db != str_trans_doc:
                            flag_return = True
                    else:
                        # Main definitions not equal
                        flag_return = True
        return flag_return

    def edit_def(self, idx, str_main, str_trans):
        """Edits the acronym definition

        :param idx: Acronym definition to edit
        :param str_main: Acronym definition in original language
        :param str_trans: Acronym definition translated
        """
        idx = idx - 1 # Input is user friendly (Counting starts at 1)
        self.proposed_def[idx]['Main'] = str_main
        if str_trans != "":
            self.proposed_def[idx]['Translation'] = str_trans
        else:
            if  'Translation' in self.proposed_def[idx]:
                del self.proposed_def[idx]['Translation']
        self.flag_update_db = True

    def add_def(self, str_main, str_trans):
        """Adds a new acronym definition

        :param str_main: Acronym definition in original language
        :param str_trans: Acronym definition translated
        """
        if self.proposed_def[0]['Main'] != "": # Only add definitions if there is one already, else edit the first
            aux_def = dict()
            aux_def['Main'] = str_main
            if str_trans != "":
                aux_def['Translation'] = str_trans
            self.proposed_def.append(aux_def)
            self.selected_def.append(True)
            self.flag_update_db = True
        else:
            # If there is no definitions edit the first definition
            self.edit_def(1, str_main, str_trans)

    def delete_def(self, idx):
        """Deletes an acronym definition

        :param idx: Acronym definition to delete
        """
        idx = idx - 1 # Input is user friendly (Counting starts at 1)
        if len(self.proposed_def) == 1:
            self.dict_handler.obj_db.delete_acro_in_db(self.acro)
        else:
            self.proposed_def.pop(idx)
            self.selected_def.pop(idx)
        self.flag_update_db = True

    def select_defs(self, idx_list):
        """Alternates an acronym slection state

        :param idx: Acronyms to be selected
        """
        n_defs = len(self.selected_def)
        for i in range(n_defs):
            self.selected_def[i] = False
        for i in range(len(idx_list)):
            if 0 <= idx_list[i] - 1 < n_defs:
                self.selected_def[idx_list[i] - 1] = True

    def check_def(self):
        """Returns True if the acronym is valid to be used"""
        flag_return = True
        # Acronym needs at least 1 definition
        if self.proposed_def[0]['Main'] == "":
            flag_return = False
        # Acronym needs at least 1 selected
        for i in range(len(self.selected_def)):
            if self.selected_def[i]:
                break
        else:
            flag_return = False
        return flag_return

    def save_and_use_acro(self):
        """Accepts changes and stores them to DB if needed"""
        if self.flag_update_db:
            self.dict_handler.obj_db.update_acro_in_db(self.acro, self.proposed_def)
        self.dict_handler.update_acro_output(self.acro, self.proposed_def, self.selected_def)

    def get_str_pretty_definition_list(self, def_list):
        """Return formatted string with all definition ordered"""
        str_out = ""
        if len(def_list):
            str_out += "["
            for i, definition in enumerate(def_list):
                if i != 0:
                    str_out += ", "
                str_out += "{'Main': '%s'" % definition['Main']
                if 'Translation' in definition:
                    str_out += ", 'Translation': '%s'" % definition['Translation']
                str_out += "}"
            str_out += "]"
        else:
            str_out = ach.color_str("No encontrado", ach.AnsiColorCode.GRAY)
        return str_out

    def get_def_strings(self):
        """Returns pretty definition strings to be output to console

        :return: Tuple with main and translation strings
        """
        str_def_main, str_def_trans = "", ""
        if len(self.proposed_def) == 1:
            str_def_main = self.proposed_def[0]['Main']
            if 'Translation' in self.proposed_def[0]:
                str_def_trans = self.proposed_def[0]['Translation']
        else:
            # Show list with index of there is multiple definitions. Unselected definitions are shown in gray
            str_def_main, str_def_trans = "[", "["
            for i, definition in enumerate(self.proposed_def):
                i_ = i + 1
                color = ach.AnsiColorCode.DEFAULT
                if not self.selected_def[i]:
                    color = ach.AnsiColorCode.GRAY
                str_def_main += ach.color_str("%d: %s" % (i_, definition['Main']), color) + ", "
                str_aux_trans = ""
                if 'Translation' in definition:
                    str_aux_trans += definition['Translation']
                str_def_trans += ach.color_str("%d: %s" % (i_, str_aux_trans), color) + ", "
            str_def_main = str_def_main[:-2] + "]"
            str_def_trans = str_def_trans[:-2] + "]"

        return str_def_main, str_def_trans
