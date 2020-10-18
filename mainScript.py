import time
from src.acroHandlers import acroDictHandler
from src.common import configVars as cv
from src.docxHandlers import docxExporter, docxReader
from src.cmdInterface import userCmdHandler, ansiColorHelper as ach


# 0. Configure environment
time_begin_acronymate = time.monotonic()
ach.enable_ansi_in_windows_cmd()

# 1. Initialization
userCmdHandler.print_logo()
userCmdHandler.load_config_data()
acro_dict_handler = acroDictHandler.AcroDictHandler()

# 2. Get docx file and process it
docx_input_path = userCmdHandler.get_docx_filepath_from_user(acro_dict_handler)
docxReader.extract_acro_word(docx_input_path, acro_dict_handler)

# 3. Present the user the acronyms found
userCmdHandler.process_acro_found(acro_dict_handler)
acro_dict_handler.mark_acro_output_as_used()

# 4. Save changes and generate output document
userCmdHandler.handle_db_save(acro_dict_handler)

obj_output_doc = docxExporter.generate_output_docx(acro_dict_handler)
docx_export_filename = "Acronyms_" + acro_dict_handler.str_file
if docx_export_filename[-5:] != ".docx":
    docx_export_filename += ".docx"
userCmdHandler.save_file(
    cv.config_docx_export_folder, docx_export_filename, False, docxExporter.save_document, obj_output_doc)

userCmdHandler.print_ellapsed_time(time.monotonic()-time_begin_acronymate)
time.sleep(cv.config_seconds_before_exit)
