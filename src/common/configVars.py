from src.common import defines as dv

"""This file is for user configurable defines. The functions that update this values are in configHandler."""

# --------- ACRONYM SEARCH -------------
# Minimum acronym length (Defined as number of capital letters together)
config_min_acro_len = 2

# Expected/possible document acronym table headers
config_acronym_table_headers = [
    ["Acrónimo", "Definición"], ["Acrónimo", "Significado"], ["Acronym", "Definition"], ["Acronym", "Meaning"]]

# --------- FILE PATHS -------------
config_acro_db_path = "data/acronymate_DB.json"  # Path to database file is stored (You can keep multiple DB files for different projects)
config_docx_export_folder = "output"  # Folder where output acronym docx will be saved
config_acro_db_bkp_rel_folder = "backup/"  # Folder where databases backups will be saved. Relative to db_path

# --------- LOCALIZATION -------------
config_locale = "es"

# --------- OUTPUT TABLE -------------
# Configuration for output table. It is recommended to generate a test document before real use to prevent errors
config_output_font = "Verdana"  # Font name
config_output_font_size = 7  # Font size (points) for the acronym table rows
config_output_font_size_header = 9  # Font size (points) for the acronym table header

# --------- FLAGS -------------
# Acronym processing flags (For best results keep them enabled)
config_use_acro_from_doc_table = True  # Searches non regex matching acronyms from the document
config_use_non_matching_acro_from_db = True  # Adds to the search non regex matching acronyms added to the database
# Storage flags
config_save_backups = True  # Set to True to enable the creation of backups after each run
config_allow_overwriting_exported = False  # Overwriting output files reduce the growth rate of the output folder
# Note: Overwriting might not be possible if the file is in use. In that case the flag is ignored
# Usability flags
config_open_docx_after_export = True  # Opens the generated acronym .docx using the default program (Only for Windows)

# --------- OTHER -------------

# ......... NOT DIRECTLY CONFIGURABLE ..........
""" The following variables are configurable by changing one of the above, they should not appear on the config file """
config_regex_acro_find = dv.define_regex_acro_find_raw.replace("rep_min_acro_len", str(config_min_acro_len))
