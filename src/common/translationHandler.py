import gettext

# Global variables for translation
localedir = "locales"#resource_path('locales')

# Default language
translate = gettext.translation('acronymate', localedir, languages=['es'], fallback=True)
translate.install()

def change_translation(lang):
    global translate
    translate = gettext.translation('acronymate', localedir, languages=[lang], fallback=True)
    translate.install()
