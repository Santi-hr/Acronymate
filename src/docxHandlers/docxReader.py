import re
import docx
import lxml
from src.common import defines as dv
from src.common import configVars as cv
from src.common import pathHelpers
from src.cmdInterface import ansiColorHelper, cmdProgressBar, userCmdHandler

class DocxReader:
    """Class to process the input document to find its acronyms"""
    def __init__(self, acro_dict_handler):
        self.acro_dict_handler = acro_dict_handler
        self.document = None


    def extract_acro_word(self, filepath, acro_dict_handler, filename_overwrite=None):
        """Main function. Opens a docx file and extracts its acronyms

        :param filepath: Path string to a docx file
        :param acro_dict_handler: Acronym dictionary objects
        :param filename_overwrite: String that overwrites the loaded file name stored in the acro handler
        """
        # 1. Open file
        self.document = docx.Document(filepath)
        acro_dict_handler.str_file = pathHelpers.get_filename_from_path(filepath)
        # Overwrite filename if needed. This is used with the word extension to keep only one temp file
        if filename_overwrite:
            acro_dict_handler.str_file = filename_overwrite

        # 2. Search for acronyms and extract them
        userCmdHandler.print_acronym_search_start()
        self.search_and_process_acro_table(self.document, acro_dict_handler)
        # extract_acro_from_paragraphs(self.document, acro_dict_handler)
        # extract_acro_from_tables(self.document, acro_dict_handler)
        # extract_acro_from_sections(self.document, acro_dict_handler)

        # 3. Perform second search to find acronyms or abbreviates that do not match with the regex and confirm the ones in
        # the document acronym table that have not been found yet (Ej: ExCOMMS, JdP)
        brute_regex = "" # All words combined into a regex. It speeds up drastically the search as only one pass is needed
        # fixme: probably not the best use of regex, but if not many "special" acronyms it will work flawlessly
        if cv.config_use_acro_from_doc_table:  # todo, revisar acceso directo a dict handler
            for acro_key in acro_dict_handler.acros_doc_table.keys():
                brute_regex += re.escape(acro_key) + r'|'
                # if acro_key not in acro_dict_handler.acros_found: # todo Quitar los que hacen match
                #     brute_regex += re.escape(acro_key) + r'|'

        if cv.config_use_non_matching_acro_from_db:
            for acro_key in acro_dict_handler.obj_db.list_no_regex:
                if acro_key not in acro_dict_handler.acros_found and acro_key not in brute_regex:
                    brute_regex += re.escape(acro_key) + r'|'

        # second_regex = "temp" #fixme: Remove unused code
        # if second_regex != "":
        # userCmdHandler.print_acronym_search_second_pass()
        # Add word boundries to regex
        second_regex = cv.config_regex_acro_find
        if brute_regex != "":
            second_regex = r'\b(' + brute_regex[:-1] + r')(?![\wÁÉÍÓÚ])|' + second_regex #Add first matches to brute forced acronyms
            # todo: this also prevents finding two times acronyms like ExCOMMS could be match as COMMS like in previous versions
        print(second_regex)
        # The last part fixes abbreviates. \b does not match '. ' as both are non alphanumeric
        # Alternate: r'\b('+second_regex[:-1]+r')(\b|(?=\W))'
        self.extract_acro_from_paragraphs(self.document, acro_dict_handler, second_regex)
        self.extract_acro_from_tables(self.document, acro_dict_handler, second_regex)
        self.extract_acro_from_sections(self.document, acro_dict_handler, second_regex)
        a=4


    def _accepted_text(self, docx_elem, docx_elem_xml, doc_nsmap):
        str_accepted_text = ""
        if "w:ins" in docx_elem_xml:
            target = lxml.etree.XML(docx_elem_xml)
            # Search all paragraphs in the XML
            for paragraph in target.xpath('//w:p', namespaces=doc_nsmap):
                # Search all runs and inserted runs (Tack Changes). Deleted runs (w:del) are skipped
                for text_run in paragraph.xpath('w:r | w:ins/w:r', namespaces=doc_nsmap):
                    # Handle linebreaks first. It seems that appear in their own run or before text
                    if text_run.xpath('w:br', namespaces=doc_nsmap):
                        str_accepted_text += '\n'
                    for text_tag in text_run.xpath('w:t', namespaces=doc_nsmap):
                        str_accepted_text += text_tag.text
                str_accepted_text += "\n"  # Append new line between paragraphs (There can be multiple pgphs in tables)
            str_accepted_text = str_accepted_text[:-1]  # Remove last paragraph new line char
        else:
            # Use python docx when possible as it has the text already extracted
            str_accepted_text = docx_elem.text
        return str_accepted_text


    def extract_acro_from_str(self, str_in_raw, acro_dict_handler, regex_in=""):
        """Finds acronyms in a text string and stores them into a dictionary

        :param str_in_raw: Input text string
        :param acro_dict_handler: Acronym dictionary objects
        :param regex_in: Regex string
        """
        # 1. Find Acronyms as regex matches of groups of N Capital Leters. The regex can be changed for other uses
        if regex_in == "":
            regex_in = cv.config_regex_acro_find

        # Line breaks are removed to reduce space used when outputting the context string to console
        str_in = str_in_raw.replace('\n', dv.define_new_line_separator)
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


    def extract_acro_from_paragraphs(self, doc_obj, acro_dict_handler, regex_in=""):
        """ Iterates through all paragraph blocks of the document and stores all acronyms found

        :param doc_obj: Python-docx object
        :param acro_dict_handler: Acronym dictionary objects
        :param regex_in: Regex string
        """
        # Iterate trough all paragraphs
        obj_progress_bar = cmdProgressBar.CmdProgressBar(len(doc_obj.paragraphs), userCmdHandler.get_translated_str_paragraphs())
        for i, paragraph in enumerate(doc_obj.paragraphs):
            str_accepted_text = self._accepted_text(paragraph, paragraph._p.xml, doc_obj.element.nsmap)
            self.extract_acro_from_str(str_accepted_text, acro_dict_handler, regex_in=regex_in)

            obj_progress_bar.update(i + 1)


    def extract_acro_from_tables(self, doc_obj, acro_dict_handler, regex_in=""):
        """ Iterates through all document tables and stores all acronyms found. Processes the acro-table if found

        :param doc_obj: Python-docx object
        :param acro_dict_handler: Acronym dictionary objects
        :param regex_in: Regex string
        """
        # 1. Iterate trough table objects
        obj_progress_bar = cmdProgressBar.CmdProgressBar(len(doc_obj.tables), userCmdHandler.get_translated_str_tables())
        for i, table in enumerate(doc_obj.tables):
            # 2. Merge all row into a single string
            for j, row in enumerate(table.rows):
                row_cell_list = []
                for cell in row.cells:
                    row_cell_list.append(self._accepted_text(cell, cell._tc.xml, doc_obj.element.nsmap))
                row_text = dv.define_tb_col_separator.join(row_cell_list)

                if j == 0:
                    if self.is_acronym_table_header(row_text):
                        # process_acro_table(table, acro_dict_handler)
                        break  # Do not process acronym table as found acronyms

                self.extract_acro_from_str(row_text, acro_dict_handler, regex_in=regex_in)

            obj_progress_bar.update(i + 1)

    def search_and_process_acro_table(self, doc_obj, acro_dict_handler, regex_in=""):
        """ Iterates through all document tables and stores all acronyms found. Processes the acro-table if found

        :param doc_obj: Python-docx object
        :param acro_dict_handler: Acronym dictionary objects
        :param regex_in: Regex string
        """
        # 1. Iterate trough table objects
        for i, table in enumerate(doc_obj.tables):
            # 2. Merge header into a single string
            row_cell_list = []
            for cell in table.rows[0].cells:
                row_cell_list.append(self._accepted_text(cell, cell._tc.xml, doc_obj.element.nsmap))
            row_text = dv.define_tb_col_separator.join(row_cell_list)

            if self.is_acronym_table_header(row_text):
                self.process_acro_table(table, acro_dict_handler)
                break  # Do not process acronym table as found acronyms



    def is_acronym_table_header(self, row_input):
        """Checks if the string matches any document acronyms table header defined

        :param row_input: Header table string
        :return: True if any match is found
        """
        flag_return = False
        for header_columns in cv.config_acronym_table_headers:
            header = dv.define_tb_col_separator.join(header_columns)
            if row_input == header:
                flag_return = True
                break
        return flag_return


    def process_acro_table(self, acro_table, acro_dict_handler):
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
        if not acro_dict_handler.flag_doc_table_processed and len(acro_table.rows[0].cells) == 2:
            for i, row in enumerate(acro_table.rows[1:]):  # Skipping header (Row 1)
                # Get raw data
                acronym = row.cells[0].text.strip()
                definitions = row.cells[1].text.split('\n')

                if acronym == "":  # Skip empty rows
                    continue

                # Process definitions
                for raw_def in definitions:
                    main_def = raw_def.strip()
                    trans_def = ""

                    if ')' in main_def:
                        # Finds the opening and closing parenthesis of the translated part to slice the definition
                        opening_par = -1
                        closing_par = main_def.rfind(')')
                        groups_open = 1  # Group = (). Assumes proper closing of parenthesis
                        for idx in range(closing_par - 1, 0, -1):
                            char = main_def[idx]
                            if main_def[idx] == ')':
                                groups_open += 1
                            elif main_def[idx] == '(':
                                groups_open -= 1
                            if groups_open == 0:
                                opening_par = idx
                                break
                        trans_def = main_def[opening_par + 1:closing_par].strip()
                        main_def = main_def[:opening_par - 1].strip()

                    acro_dict_handler.add_acronym_doc_table(acronym, main_def, trans_def)
        acro_dict_handler.flag_doc_table_processed = True


    def extract_acro_from_sections(self, doc_obj, acro_dict_handler, regex_in=""):
        """ Iterates through all sections blocks of the document and stores all acronyms found

        :param doc_obj: Python-docx object
        :param acro_dict_handler: Acronym dictionary objects
        :param regex_in: Regex string
        """
        obj_progress_bar = cmdProgressBar.CmdProgressBar(len(doc_obj.sections), userCmdHandler.get_translated_str_sections())
        nsmap = doc_obj.element.nsmap
        for i, section in enumerate(doc_obj.sections):
            # Sections include headers and footers
            self.extract_acro_from_header(section.header, acro_dict_handler, nsmap, regex_in)
            self.extract_acro_from_header(section.footer, acro_dict_handler, nsmap, regex_in)

            obj_progress_bar.update(i + 1)


    def extract_acro_from_header(self, docx_section_obj, acro_dict_handler, nsmap, regex_in=""):
        """ Processes all paragraphs and tables of a header or footer object

        :param docx_section_obj: Python-docx object (section.header or section.footer)
        :param acro_dict_handler: Acronym dictionary objects
        :param regex_in: Regex string
        """
        for paragraph in docx_section_obj.paragraphs:
            str_accepted_text = self._accepted_text(paragraph, paragraph._p.xml, nsmap)
            self.extract_acro_from_str(str_accepted_text, acro_dict_handler, regex_in=regex_in)

        for table in docx_section_obj.tables:
            for j, row in enumerate(table.rows):
                row_cell_list = []
                for cell in row.cells:
                    row_cell_list.append(self._accepted_text(cell, cell._tc.xml, nsmap))
                row_text = dv.define_tb_col_separator.join(row_cell_list)
                # Acronym table not expected in header/footers
                self.extract_acro_from_str(row_text, acro_dict_handler, regex_in=regex_in)