
"""This file is for user configurable defines. Feel free to change them as you like"""

# --------- ACRONYM SEARCH -------------
# Minimum acronym length (Defined as number of capital letters together)
config_min_acro_len = 2

# Context formatting
config_tb_col_separator = "·|·"        # Used to represent a table column when joining a table row into a single string
config_new_line_separator = "·(\\n)·"  # Used to represent a line break

# Expected/possible document acronym table headers
config_acronym_table_headers = [
    config_tb_col_separator.join(["Acrónimo", "Definición"]),
    config_tb_col_separator.join(["Acrónimo", "Significado"])]

# Acronym processing flags (For best results keep them enabled)
config_use_acro_from_doc_table = True        # Searches non regex matching acronyms from the document
config_use_non_matching_acro_from_db = True  # Adds to the search non regex matching acronyms added to the database

# --------- FILE PATHS -------------
config_acro_db_folder = "data/"             # Folder where database file is stored
config_acro_db_file = "acronymate_DB.json"  # Database filename (You can keep multiple DB files for multiple projects
                                            # in the same folder and use this define to load one or the other)

config_docx_export_folder = "output"        # Folder where output acronym docx will be saved

config_acro_db_bkp_folder = "data/backup/"  # Folder where databases backups will be saved
config_save_backups = True                  # Set to True to enable the creation of backups after each usage
