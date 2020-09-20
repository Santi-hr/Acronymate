from src.common import configVars as cv

"""This file is for non-user configurable defines. Imports the configurable variables"""

# --------- ACRONYM SEARCH -------------
define_regex_acro_find_raw = '[A-ZÁÉÍÓÚÑÇÄËÏÖÜÀÈÌÒÙ]{rep_min_acro_len,}'
define_regex_acro_find = define_regex_acro_find_raw.replace("rep_min_acro_len", str(cv.config_min_acro_len))

# --------- CONTEXT FORMATTING -------------
define_tb_col_separator = "·|·"        # Used to represent a table column when joining a table row into a single string
define_new_line_separator = "·(\\n)·"  # Used to represent a line break

# --------- OTHER -------------
define_acronymate_version = "v0.3.0"
