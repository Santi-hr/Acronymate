import json
from src.common import defines as dv
from src.common import configVars as cv
from src.common import translationHandler

"""Contains the functions that update the config variables to avoid importing them to other files"""
#TODO: I know JSON is not an ideal configuration file. Change to one that allow comments if possible

def save_config_file():
    """Generates a default config file using the variables in configVars. See the file for variable comments.
    This functions needs to manually be updated if new configuration values are added.
    """
    dict_config = {
        "Acronym Search": {
            "Min acronym length": cv.config_min_acro_len,
            "Acronym table headers": cv.config_acronym_table_headers,
        },
        "Paths": {
            "Export folder": cv.config_docx_export_folder,
            "DB folder": cv.config_acro_db_folder,
            "DB filename": cv.config_acro_db_file,
            "DB backup folder": cv.config_acro_db_bkp_folder
        },
        "Localization": {
            "Language": cv.config_locale
        },
        "Output Table": {
            "Font": cv.config_output_font,
            "Font size": cv.config_output_font_size,
            "Font size header": cv.config_output_font_size_header,
        },
        "Flags": {
            "Use acronym document table": cv.config_use_acro_from_doc_table,
            "Use non matching acronyms from DB": cv.config_use_non_matching_acro_from_db,
            "Save backups": cv.config_save_backups,
        },
    }

    with open("acronymate_config.json", 'w', encoding="utf-8") as cfg_file:
        json.dump(dict_config, cfg_file, ensure_ascii=False, sort_keys=False, indent=4)


def read_config_file():
    """Reads a json config file using the variables in configVars. See the file for variable comments.
    This functions needs to manually be updated if new configuration values are added.
    """
    flag_success = True
    try:
        with open("acronymate_config.json", 'r', encoding="UTF-8") as cfg_file:
            dict_config = json.load(cfg_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        flag_success = False

    if flag_success:
        try:
            cv.config_min_acro_len = dict_config["Acronym Search"]["Min acronym length"]
            cv.config_acronym_table_headers = dict_config["Acronym Search"]["Acronym table headers"]

            cv.config_docx_export_folder = dict_config["Paths"]["Export folder"]
            cv.config_acro_db_folder = dict_config["Paths"]["DB folder"]
            cv.config_acro_db_file = dict_config["Paths"]["DB filename"]
            cv.config_acro_db_bkp_folder = dict_config["Paths"]["DB backup folder"]

            cv.config_locale = dict_config["Localization"]["Language"]

            cv.config_output_font = dict_config["Output Table"]["Font"]
            cv.config_output_font_size = dict_config["Output Table"]["Font size"]
            cv.config_output_font_size_header = dict_config["Output Table"]["Font size header"]

            cv.config_use_acro_from_doc_table = dict_config["Flags"]["Use acronym document table"]
            cv.config_use_non_matching_acro_from_db = dict_config["Flags"]["Use non matching acronyms from DB"]
            cv.config_save_backups = dict_config["Flags"]["Save backups"]

            # UPDATE DEFINES
            cv.config_regex_acro_find = dv.define_regex_acro_find_raw.replace(
                "rep_min_acro_len", str(cv.config_min_acro_len))
        except KeyError:
            flag_success = False

    return flag_success


def apply_config():
    """Calls to other functions that need to use the set configuration"""
    translationHandler.change_translation(cv.config_locale)
