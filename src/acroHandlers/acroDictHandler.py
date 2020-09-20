from src.acroHandlers import acroDbHandler


class AcroDictHandler:
    """Class to handle all acronym data dictionaries and pass around data between functions"""
    def __init__(self):
        # Get datetime once to keep it constant
        self.str_file = "Undefined"             # File path for logging purposes

        self.acros_found = dict()               # Acronyms found in the document

        self.acros_doc_table = dict()           # Acronyms from the document acronyms table
        self.flag_doc_table_processed = False   # True if the document acronyms table is found and processed

        self.acros_output = dict()              # Acronyms to be exported

        self.obj_db = acroDbHandler.AcroDbHandler()  # Object to handle DB

    ############# ACRONYM FOUND FUNCTIONS #############
    def add_acronym_found(self, acro_in, str_context_in):
        # Create empty dict if acronym is first found
        if acro_in not in self.acros_found:
            self.acros_found[acro_in] = {'Count': 0, 'Context': []}

        # Store data of acronym in dict
        self.acros_found[acro_in]['Count'] += 1
        self.acros_found[acro_in]['Context'].append(str_context_in)

    ############# ACRONYM DOC TABLE FUNCTIONS #############
    def search_def_in_doc_table(self, acro_in):
        """Searches for an acronym in the document acronyms table dictionary and returns its definition"""
        definition_list_out = []
        if acro_in in self.acros_doc_table:
            definition_list_out = self.acros_doc_table[acro_in]['Def']
        return definition_list_out

    def add_acronym_doc_table(self, acro_in, str_main, str_trans):
        # Create dict entry
        if acro_in not in self.acros_doc_table:
            # Some tables have duplicated lines for multiple definitions
            self.acros_doc_table[acro_in] = {'Def': []}

        aux_def = {'Main': str_main}
        if str_trans != "":
            aux_def['Translation'] = str_trans
        self.acros_doc_table[acro_in]['Def'].append(aux_def)

    ############# ACRONYM OUTPUT FUNCTIONS #############
    def update_acro_output(self, acro_in, def_list_in, selection_list_in):
        """Stores the selected acronym definitions for further exportation"""
        self.acros_output[acro_in] = {
            'Def': []}  # Allows for future dict keys without modifying how defs are accessed
        for i, definition in enumerate(def_list_in):
            if selection_list_in[i]:
                self.acros_output[acro_in]['Def'].append(definition)
        self.obj_db.add_db_last_use(acro_in, self.str_file)