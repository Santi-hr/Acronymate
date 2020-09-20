import unicodedata

def remove_accents(input_str):
    """Removes accents from the input string and returns it"""
    # Fixme: Not working for ø
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii
