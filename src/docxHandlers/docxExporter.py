import docx
from src.common.defines import *
from src.common import stringHelpers as strHlprs
from src.cmdInterface import cmdProgressBar


def generate_output_docx(acro_dict_handler):
    """Generates a docx document with the user accepted acronyms

    :param acro_dict_handler: Acronym dictionary objects
    :return: python-docx generated document object
    """
    print("Generando word con tabla de acrónimos")
    obj_progress_bar = cmdProgressBar.CmdProgressBar(len(acro_dict_handler.acros_output.keys()), "Acrónimos")

    document = docx.Document()

    # --- Define styles ---
    obj_normal_style = document.styles['Normal']
    font = obj_normal_style.font
    font.name = 'Calibri'
    font.size = docx.shared.Pt(10)
    paragraph_format = obj_normal_style.paragraph_format
    paragraph_format.space_after = docx.shared.Pt(0)
    paragraph_format.space_before = docx.shared.Pt(2)

    obj_header_style = document.styles.add_style('HeaderStyle', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
    hdr_font = obj_header_style.font
    hdr_font.size = docx.shared.Pt(12)
    hdr_font.name = 'Calibri'
    paragraph_format = obj_header_style.paragraph_format
    paragraph_format.space_after = docx.shared.Pt(0)
    paragraph_format.space_before = docx.shared.Pt(2)

    # --- Footer ---
    section_footer = document.sections[0].footer
    section_footer.paragraphs[0].text = "ACRONYMATE " + define_acronymate_version + " - SAHR Projects 2020"
    section_footer.paragraphs[0].alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.RIGHT

    # --- Document ---
    document.add_paragraph('Acrónimos extraidos de: %s' % acro_dict_handler.str_file)

    # --- Table ---
    table = document.add_table(rows=1, cols=2)
    # table.obj_normal_style = 'LightShading-Accent1'
    table.autofit = True
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Acrónimo'
    hdr_cells[1].text = 'Definición'
    for i in range(len(hdr_cells)):
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True
        hdr_cells[i].paragraphs[0].style = obj_header_style
    # Set parameter in cells for auto width
    for cell in table.rows[0].cells:
        cell._tc.tcPr.tcW.type = 'auto'

    for n_acro, acro in enumerate(sorted(acro_dict_handler.acros_output.keys(), key=strHlprs.remove_accents)):
        row_cells = table.add_row().cells
        row_cells[0].text = acro
        row_cells[0].paragraphs[0].runs[0].font.bold = True
        for i in range(len(acro_dict_handler.acros_output[acro]['Def'])):
            if i > 0:
                row_cells[1].add_paragraph()
            run_main_def = row_cells[1].paragraphs[i].add_run(acro_dict_handler.acros_output[acro]['Def'][i]['Main'])
            if 'Translation' in acro_dict_handler.acros_output[acro]['Def'][i]:
                run_main_def.italic = True
                row_cells[1].paragraphs[i].add_run(
                    " (" + acro_dict_handler.acros_output[acro]['Def'][i]['Translation'] + ")")
        # Set parameter in cells for auto width
        for cell in row_cells:
            cell._tc.tcPr.tcW.type = 'auto'

        obj_progress_bar.update(n_acro+1)

    return document


def save_document(filepath_output, document):
    """Function that saves an python-docx object

    :param filepath_output: Desired path
    :param document: python-docx document object
    """
    document.save(filepath_output)
