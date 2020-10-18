import gettext
import pathlib

# Global variables for translation
localedir = "locales"#resource_path('locales')

# Default language
translate = gettext.translation('acronymate', localedir, languages=['es'], fallback=True)
translate.install()


def change_translation(lang):
    """Updates the locale file to use and installs the _() function globally"""
    global translate
    translate = gettext.translation('acronymate', localedir, languages=[lang], fallback=True)
    translate.install()


def get_locales_list():
    """Returns list of folders in the locale directory"""
    path = pathlib.Path(localedir).glob('*')
    dirs = [x.name for x in path if x.is_dir()]
    return dirs
