from src import acroDictHandler
from src.common.defines import *
from src.docxHandlers import docxExporter, docxReader
from src.cmdInterface import ansiColorHelper as ach, userCmdHandler

# 0. Configure environment
ach.enable_ansi_in_windows_cmd()

# 1. Initialization
userCmdHandler.print_logo()
acro_dict_handler = acroDictHandler.AcroDictHandler()

# 2. Get docx file and process it
docx_input_path = userCmdHandler.get_docx_filepath_from_user()
docxReader.extract_acro_word(docx_input_path, acro_dict_handler)

# 3. Present the user the acronyms found
userCmdHandler.process_acro_found(acro_dict_handler)

# 4. Save changes and generate output document
userCmdHandler.handle_db_save(acro_dict_handler)

obj_output_doc = docxExporter.generate_output_docx(acro_dict_handler)
docx_export_filename = "Acronyms_" + acro_dict_handler.str_file
if docx_export_filename[-5:] != ".docx":
    docx_export_filename += ".docx"
userCmdHandler.save_file(
    config_docx_export_folder, docx_export_filename, False, docxExporter.save_document, obj_output_doc)
