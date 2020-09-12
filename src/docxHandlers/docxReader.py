import re
import docx
from src.common.defines import *
from src.common import pathHelpers
from src.cmdInterface import ansiColorHelper, cmdProgressBar


def extract_acro_word(filepath, acro_dict_handler):
    """Main function. Opens a docx file and extracts its acronyms

    :param filepath: Path string to a docx file
    :param acro_dict_handler: Acronym dictionary objects
    """
    # 1. Open file
    doc_obj = docx.Document(filepath)
    acro_dict_handler.str_file = pathHelpers.get_filename_from_path(filepath)

    # 2. Search for acronyms and extract them
    print("Extrayendo acrónimos del documento")
    extract_acro_from_paragraphs(doc_obj, acro_dict_handler)
    extract_acro_from_tables(doc_obj, acro_dict_handler)

    # 3. Perform second search to find acronyms or abbreviates that do not match with the regex and confirm the ones in
    # the document acronym table that have not been found yet (Ej: ExCOMMS, JdP)
    second_regex = "" # All words combined into a regex. It speeds up drastically the search as only one pass is needed

    if config_use_acro_from_doc_table: #todo, quitar acceso directo
        for acro_key in acro_dict_handler.acros_doc_table.keys():
            if acro_key not in acro_dict_handler.acros_found:
                second_regex += re.escape(acro_key) + r'|'

    if config_use_non_matching_acro_from_db:
        for acro_key in acro_dict_handler.list_no_regex:
            if acro_key not in acro_dict_handler.acros_found and acro_key not in second_regex:
                second_regex += re.escape(acro_key) + r'|'

    if second_regex != "":
        print("Repasando la búsqueda con acrónimos especiales")
        # Add word boundries to regex
        second_regex = r'\b(' + second_regex[:-1] + r')(?![\wÁÉÍÓÚ])'
        # The last part fixes abbreviates. \b does not match '. ' as both are non alphanumeric
        # Alternate: r'\b('+second_regex[:-1]+r')(\b|(?=\W))'
        extract_acro_from_paragraphs(doc_obj, acro_dict_handler, second_regex)
        extract_acro_from_tables(doc_obj, acro_dict_handler, second_regex)


def extract_acro_from_str(str_in, acro_dict_handler, regex_in=""):
    """Finds acronyms in a text string and stores them into a dictionary

    :param str_in: Input text string
    :param acro_dict_handler: Acronym dictionary objects
    :param regex_in: Regex string
    """
    # 1. Find Acronyms as regex matches of groups of N Capital Leters. The regex can be changed for other uses
    if regex_in == "":
        regex_in = define_regex_acro_find

    re_results = re.finditer(regex_in, str_in)

    if re_results:
        # 2. Iterate trough all matches (There could be multiple acronyms in a paragraph)
        for re_result in re_results:
            # 3. Save context for user analysis (Only part of the string)
            context_width = 200
            # Ensure the context width is achieved
            prev_context = context_width / 2
            next_context = context_width / 2
            # Check if there are unused characters at front/back after adding/subtracting the context. If so, add them
            # to the opposite side.
            char_diff_ini = re_result.start(0) - context_width / 2
            if char_diff_ini < 0:
                next_context -= char_diff_ini  # Addition, double negative
            char_diff_end = len(str_in) - (re_result.start(0) + context_width / 2)
            if char_diff_end < 0:
                prev_context -= char_diff_end  # Addition, double negative

            context_substr_ini = int(max(re_result.start(0) - prev_context, 0))
            context_substr_end = int(min(re_result.start(0) + next_context, len(str_in)))

            # Context with acronym remarked using ANSI Color Codes
            str_context = ansiColorHelper.highlight_substr(
                str_in[context_substr_ini:context_substr_end],
                (re_result.span()[0] - context_substr_ini, re_result.span()[1] - context_substr_ini),
                ansiColorHelper.AnsiColorCode.CYAN)

            # 4. Create empty dict if acronym is first found
            acro_dict_handler.add_acronym_found(re_result.group(0), str_context)


def extract_acro_from_paragraphs(doc_obj, acro_dict_handler, regex_in=""):
    """ Iterates through all paragraph blocks of the document and stores all acronyms found

    :param doc_obj: Python-docx object
    :param acro_dict_handler: Acronym dictionary objects
    :param regex_in: Regex string
    """
    # Iterate trough all paragraphs
    obj_progress_bar = cmdProgressBar.CmdProgressBar(len(doc_obj.paragraphs), "Párrafos")
    for i in range(len(doc_obj.paragraphs)):
        par_txt = doc_obj.paragraphs[i].text
        extract_acro_from_str(par_txt, acro_dict_handler, regex_in=regex_in)

        obj_progress_bar.update(i + 1)


def extract_acro_from_tables(doc_obj, acro_dict_handler, regex_in=""):
    """ Iterates through all document tables and stores all acronyms found. Processes the acro-table if found

    :param doc_obj: Python-docx object
    :param dict_found_acro: Acronyms found dictionary
    :param dict_acro_table: Acronyms table document dictionary
    :param regex_in: Regex string
    """
    # 1. Iterate trough table objects
    obj_progress_bar = cmdProgressBar.CmdProgressBar(len(doc_obj.tables), "Tablas")
    for i, table in enumerate(doc_obj.tables):
        # 2. Merge all row into a single string
        for j, row in enumerate(table.rows):
            row_cell_list = []
            for cell in row.cells:
                row_cell_list.append(cell.text)
            row_text = config_tb_col_separator.join(row_cell_list)

            if j == 0:
                if is_acronym_table_header(row_text):
                    process_acro_table(table, acro_dict_handler)
                    break  # Do not process acronym table as found acronyms

            # Line breaks are removed to reduce space used when outputting the context string to console
            extract_acro_from_str(row_text.replace('\n', config_new_line_separator), acro_dict_handler, regex_in=regex_in)

        obj_progress_bar.update(i + 1)


def is_acronym_table_header(row_input):
    """Checks if the string matches any document acronyms table header defined

    :param row_input: Header table string
    :return: True if any match is found
    """
    flag_return = False
    for header in config_acronym_table_headers:
        if row_input == header:
            flag_return = True
            break
    return flag_return


def process_acro_table(acro_table, acro_dict_handler):
    """Processes the document acronym table to extract already defined acronyms. Currently the format is set as:
    Acronym | Definitions as "original text (Translated)" separated by line breaks

    :param acro_table: Python-docx table object
    :param acro_dict_handler: Acronyms table document dictionary
    """
    # This function only works if the following format is used:
    # Acronym | Definitions as "original text (Translated)" separated by line breaks
    # When a table is found with a different number of rows it is skiped
    # Todo: Allow for custom tables via configure file
    # Fixme: Prevent explosion if table has merged lines
    if not acro_dict_handler.is_doc_table_processed() and len(acro_table.rows[0].cells) == 2:
        for i, row in enumerate(acro_table.rows):
            if i == 0:  # Skip header
                continue

            # Get raw data
            acronym = row.cells[0].text.strip()
            definitions = row.cells[1].text.split('\n')

            if acronym == "":
                continue

            # Process definitions
            for j in range(len(definitions)):
                main_def = ""
                trans_def = ""

                definition = definitions[j].strip()
                if '(' not in definition:
                    main_def = definition
                else:
                    main_def = ""
                    re_match = re.fullmatch("(.*)\((.*)\)", definition)  # Todo: Fix "Def (Expl) (Def_es (Expl_es))"
                    if re_match:
                        main_def = re_match.group(1).strip()
                        trans_def = re_match.group(2).strip()

            acro_dict_handler.add_acronym_doc_table(acronym, main_def, trans_def)
    acro_dict_handler.set_doc_table_processed()
