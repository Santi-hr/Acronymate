import unicodedata

def remove_accents(input_str):
    """Removes accents from the input string and returns it"""
    # Fixme: Not working for ø
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii

def acro_ordering(input_str):
    """Prepares input for being ordered alphabetically without capitalization, accents or punctuation signs"""
    output_str = remove_accents(input_str).upper()
    output_str = str(output_str).replace(".", "")  # Remove points for ordering abbreviations
    return output_str
