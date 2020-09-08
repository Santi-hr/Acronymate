from datetime import datetime
from pathlib import Path
from src.common.defines import *
from src.common import pathHelpers
from src.cmdInterface import ansiColorHelper as ach


class AuxAcroObj:
    """Class to handle one acronym while user updates it"""
    def __init__(self, acro, dict_handler):
        """Class constructor

        :param acro: Acronym string
        :param dict_handler: Acronym dictionary handler
        """
        self.acro = acro
        self.dict_handler = dict_handler
        self.proposed_def = [{'Main': ""}]
        self.flag_update_db = True # If acro is not found in the db it would need to be added

        # Look acronym in table document
        self.def_list_doc_table = self.dict_handler.search_def_in_doc_table(self.acro)
        if len(self.def_list_doc_table) > 0:
            self.proposed_def = self.def_list_doc_table

        # Look acronym in database
        self.def_list_db = self.dict_handler.search_def_in_db(self.acro)
        # DB has priority
        if len(self.def_list_db) > 0:
            self.proposed_def = self.def_list_db
            self.flag_update_db = False

        # Fill the selected list
        self.selected_def = []
        for i in range(len(self.proposed_def)):
            self.selected_def.append(True)

    def has_multiple_defs(self):
        """Returns True if acronym has multiple definitions"""
        flag_return = False
        if len(self.proposed_def) > 1:
            flag_return = True
        return flag_return

    def is_in_db(self):
        """Returns True if acronym is in database"""
        flag_return = False
        if len(self.def_list_db) > 0:
            flag_return = True
        return flag_return

    def is_blacklisted(self):
        """Returns True if the acronym is in the database blacklist"""
        return self.dict_handler.is_blacklisted(self.acro)

    def toggle_blacklisted_status(self):
        self.dict_handler.toggle_in_blacklist(self.acro)

    def defs_discrepancy(self):
        """Returns True if db definition does not match with the acronym table one. As this means that the acro could
        have different or other def than the one in the db. If def is not found in the acro table the fcn returns False
        """
        flag_return = False
        # Check discrepancy only if definitions found both in db and acro table
        if len(self.def_list_db) > 0 and len(self.def_list_doc_table) > 0:
            if len(self.def_list_db) != len(self.def_list_doc_table):
                flag_return = True
            else:
                for i in range(len(self.def_list_db)):
                    if self.def_list_db[i]['Main'] == self.def_list_doc_table[i]['Main']:
                        # Compare Translations. If its not found the string will be empty
                        str_trans_db, str_trans_doc = "", ""
                        if 'Translation' in self.def_list_db[i]:
                            str_trans_db = self.def_list_db[i]['Translation']
                        if 'Translation' in self.def_list_doc_table[i]:
                            str_trans_doc = self.def_list_doc_table[i]['Translation']
                        if str_trans_db != str_trans_doc:
                            flag_return = True
                    else:
                        # Main definitions not equal
                        flag_return = True
        return flag_return

    def edit_def(self, idx, str_main, str_trans):
        """Edits the acronym definition

        :param idx: Acronym definition to edit
        :param str_main: Acronym definition in original language
        :param str_trans: Acronym definition translated
        """
        idx = idx - 1 # Input is user friendly (Counting starts at 1)
        self.proposed_def[idx]['Main'] = str_main
        if str_trans != "":
            self.proposed_def[idx]['Translation'] = str_trans
        self.flag_update_db = True

    def add_def(self, str_main, str_trans):
        """Adds a new acronym definition

        :param str_main: Acronym definition in original language
        :param str_trans: Acronym definition translated
        """
        if self.proposed_def[0]['Main'] != "": # Only add definitions if there is one already, else edit the first
            aux_def = dict()
            aux_def['Main'] = str_main
            if str_trans != "":
                aux_def['Translation'] = str_trans
            self.proposed_def.append(aux_def)
            self.selected_def.append(True)
            self.flag_update_db = True
        else:
            # If there is no definitions edit the first definition
            self.edit_def(1, str_main, str_trans)

    def delete_def(self, idx):
        """Deletes an acronym definition

        :param idx: Acronym definition to delete
        """
        idx = idx - 1 # Input is user friendly (Counting starts at 1)
        if len(self.proposed_def) == 1:
            self.dict_handler.delete_acro_in_db(self.acro)
        else:
            self.proposed_def.pop(idx)
            self.selected_def.pop(idx)
        self.flag_update_db = True

    def select_def(self, idx):
        """Alternates an acronym slection state

        :param idx: Acronym definition to select/unselect
        """
        self.selected_def[idx-1] = not self.selected_def[idx-1]

    def check_def(self):
        """Returns True if the acronym is valid to be used"""
        flag_return = True
        # Acronym needs at least 1 definition
        if self.proposed_def[0]['Main'] == "":
            flag_return = False
        # Acronym needs at least 1 selected
        for i in range(len(self.selected_def)):
            if self.selected_def[i]:
                break
        else:
            flag_return = False
        return flag_return

    def save_and_use_acro(self):
        """Accepts changes and stores them to DB if needed"""
        if self.flag_update_db:
            self.dict_handler.update_acro_in_db(self.acro, self.proposed_def)
        self.dict_handler.update_acro_output(self.acro, self.proposed_def, self.selected_def)

    def print_dict_coincidences(self):
        """Prints to console the acronym data from DB and document acronyms table"""
        print("Tabla del documento: ", end="")
        print(self.__get_str_sorted_acro_list(self.def_list_doc_table))

        print("      Base de datos: ", end="")
        print(self.__get_str_sorted_acro_list(self.def_list_db))

        if self.defs_discrepancy():
            print_warn("Discrepancia detectada entre base de datos y tabla del documento")

    def __get_str_sorted_acro_list(self, def_list):
        """Return formatted string with all definition ordered"""
        str_out = ""
        if len(def_list):
            str_out += "["
            for i, definition in enumerate(def_list):
                if i != 0:
                    str_out += ", "
                str_out += "{'Main': '%s'" % definition['Main']
                if 'Translation' in definition:
                    str_out += ", 'Translation': '%s'" % definition['Translation']
                str_out += "}"
            str_out += "]"
        else:
            str_out = ach.color_str("No encontrado", ach.AnsiColorCode.GRAY)
        return str_out

    def get_def_strings(self):
        """Returns pretty definition strings to be output to console

        :return: Tuple with main and translation strings
        """
        str_def_main, str_def_trans = "", ""
        if len(self.proposed_def) == 1:
            str_def_main = self.proposed_def[0]['Main']
            if 'Translation' in self.proposed_def[0]:
                str_def_trans = self.proposed_def[0]['Translation']
        else:
            # Show list with index of there is multiple definitions. Unselected definitions are shown in gray
            str_def_main, str_def_trans = "[", "["
            for i, definition in enumerate(self.proposed_def):
                i_ = i + 1
                color = ach.AnsiColorCode.DEFAULT
                if not self.selected_def[i]:
                    color = ach.AnsiColorCode.GRAY
                str_def_main += ach.color_str("%d: %s" % (i_, definition['Main']), color) + ", "
                str_aux_trans = ""
                if 'Translation' in definition:
                    str_aux_trans += definition['Translation']
                str_def_trans += ach.color_str("%d: %s" % (i_, str_aux_trans), color) + ", "
            str_def_main = str_def_main[:-2] + "]"
            str_def_trans = str_def_trans[:-2] + "]"

        return str_def_main, str_def_trans

    ################ AuxAcroObj END #################

def get_docx_filepath_from_user():
    """Asks the user for a word document and returns it"""
    flag_finish = False
    while not flag_finish:
        print_warn("¡Recuerda usar una copia del documento con todos los cambios aceptados!")
        input_path = input("Copia la ruta de la carpeta donde se encuentra el archivo a procesar: ")
        try:
            files_in_path = Path(input_path).glob('*.docx')
            path_list = []
            for i, f in enumerate(files_in_path):
                print("  %d -" % (i+1), pathHelpers.get_filename_from_path(f))
                path_list.append(f) #Todo: No mostrar los que empiecen por ~?
            if len(path_list) == 0:
                print_error("ERROR - No se encuentran archivos '.docx' en la ruta seleccionada'")
            else:
                flag_finish = True
        except OSError:
            print_error("ERROR - El nombre de archivo, el nombre de directorio o la sintaxis de la etiqueta del volumen no son correctos")
    user_num = get_num_from_user("Seleciona el archivo a procesar", lower=1, upper=len(path_list))

    filepath = path_list[user_num-1]

    return filepath


def process_acro_found(acro_dict_handler):
    """Main interface, process acronyms one by one asking the user what to do

    :param acro_dict_handler: Acronym dictionary objects
    """
    flag_auto_command = get_user_confirmation("¿Quieres procesar en modo semi-automático?") #todo: add info
    for i, acro in enumerate(sorted(acro_dict_handler.acros_found.keys())):
        # Create an auxilary object for each acronym
        aux_acro_obj = AuxAcroObj(acro, acro_dict_handler)

        # Generate header and prints it
        max_acros = len(acro_dict_handler.acros_found.keys())
        str_header = (" %s (%d/%d) " % (acro, i+1, max_acros)).center(80,'-')
        str_half_header = "_"*round(len(str_header)/2)

        print("")
        print(str_header)

        # Print acronym matches
        print(ach.color_str("Coincidencias:", ach.AnsiColorCode.BOLD), acro_dict_handler.acros_found[acro]['Count']) # Matches
        for context in acro_dict_handler.acros_found[acro]['Context']:
            print("     ", context)

        print(str_half_header)
        aux_acro_obj.print_dict_coincidences()

        # Ask the user for commands
        print(str_half_header)
        flag_finish = False
        while not flag_finish:
            str_def_main, str_def_trans = aux_acro_obj.get_def_strings()
            print(ach.color_str("  Acrónimo:", ach.AnsiColorCode.BOLD), acro, end="")
            if aux_acro_obj.is_blacklisted():
                print(ach.color_str(" (EN LISTA NEGRA)", ach.AnsiColorCode.DARK_YELLOW))
            else:
                print("")
            print(ach.color_str(" Principal:", ach.AnsiColorCode.BOLD), str_def_main)
            print(ach.color_str("Traducción:", ach.AnsiColorCode.BOLD), str_def_trans)

            # Obtain user command or process automatic selection
            user_command = ""
            if flag_auto_command:
                if aux_acro_obj.is_blacklisted():
                    user_command = 'n'  # Skip blacklisted acronym
                else:
                    if aux_acro_obj.is_in_db() and not aux_acro_obj.has_multiple_defs() and not aux_acro_obj.defs_discrepancy():
                        user_command = 'y'
            aux_acro_obj.defs_discrepancy()
            if user_command == "":
                user_command = input("Introduce comando (y/n/e/a/s/b/d/h): ").lower()

            # -- ACCEPT CHANGES --
            if user_command == 'y':
                if aux_acro_obj.check_def():
                    aux_acro_obj.save_and_use_acro()
                    print_ok("Se guarda el acrónimo")
                    flag_finish = True
                else:
                    print_error(
                        "ERROR - Comprueba que el acrónimo está definido y que al menos 1 definición está seleccionada")
            # -- DISCARD ACRONYM --
            elif user_command == 'n':
                print_ok("Se descarta el acrónimo")
                flag_finish = True
            # -- EDIT --
            elif user_command == 'e':
                idx_def_to_edit = 1
                if aux_acro_obj.has_multiple_defs():
                    idx_def_to_edit = get_num_from_user("¿Cual quieres editar?",
                                                        lower=1, upper=len(aux_acro_obj.proposed_def))
                user_def_main, user_def_trans = get_def_str_from_user()
                aux_acro_obj.edit_def(idx_def_to_edit, user_def_main, user_def_trans)
            # -- ADD --
            elif user_command == 'a':
                user_def_main, user_def_trans = get_def_str_from_user()
                aux_acro_obj.add_def(user_def_main, user_def_trans)
            # -- SELECT --
            elif user_command == 's':
                if aux_acro_obj.has_multiple_defs():
                    idx_def_to_edit = get_num_from_user("Elige un acrónimo para alternar su estado de selección",
                                                        lower=1, upper=len(aux_acro_obj.proposed_def))
                    aux_acro_obj.select_def(idx_def_to_edit)
                else:
                    print("Esta opción solo está disponible para acrónimos con múltiples definiciones")
            # -- BLACKLIST --
            elif user_command == 'b':
                aux_acro_obj.toggle_blacklisted_status()
            # -- DELETE --
            elif user_command == 'd':
                print_warn("ATENCIÓN - El borrado eliminará la definición de la base de datos (si está en esta).\n"
                           "Para no usar el acrónimo usa el comando 'n', si hay múltiples definiciones usa 's' para "
                           "elegir cuales usar.")
                if get_user_confirmation():
                    idx_def_to_edit = 1
                    if aux_acro_obj.has_multiple_defs():
                        idx_def_to_edit = get_num_from_user("¿Cual quieres eliminar?",
                                                            lower=1, upper=len(aux_acro_obj.proposed_def))
                    else:
                        print_ok("Se elimina el acrónimo")
                        flag_finish = True # If we delete the last definition continue with the next acronym
                    aux_acro_obj.delete_def(idx_def_to_edit)
            # -- HELP --
            elif user_command == 'h':
                print_process_acro_found_help()
            # -- default --
            else:
                print_error("ERROR - Comando no reconocido. Usa el comando 'h' para obtener ayuda")


def print_process_acro_found_help():
    """Prints acronym handling user commands help"""
    print("  y: Aceptar     - Guarda el acrónimo con la información mostrada y actualiza la base de datos.")
    print("  n: Saltar      - Descarta el acrónimo y se pasa al siguiente.")
    print("  e: Editar      - Modifica una definición. En principal se indica la definición en el idioma de origen.")
    print("                   En traducción se indica la definición en Español. Dejar vacío si no es necesaria.")
    print("  a: Añadir      - Añade una definición adicional.")
    print("  s: Seleccionar - Alterna la selección de una definición. Las definiciones en gris se guardarán en la base")
    print("                   de datos, pero no se incluirán en la tabla de acrónimos de salida.")
    print("  b: Blacklist   - Alterna el estado del acrónimo en la lista negra. Si está en esta lista se saltará ")
    print("                   automáticamente al procesar en modo semi-automático.")
    print("  d: Eliminar    - Elimina el acrónimo o una de sus definiciónes de la base de datos.")
    print("  h: Ayuda       - Muestra esta información.")


def handle_db_save(acro_dict_handler):
    """Handles interface for the update of the database

    :param acro_dict_handler: Acronym dictionary objects
    """
    print("Guardando ")
    print("Resumen de cambios en la base de datos:", acro_dict_handler.log_db_changes)
    folder_output = Path(config_acro_db_folder)
    db_filename = config_acro_db_file
    flag_overwrite = True
    # Get a valid folder
    if folder_output.exists():
        path_output = folder_output / db_filename
        if path_output.exists(): # Skip checks if db file does't exist yet
            if not acro_dict_handler.check_db_integrity(): # Check if file was updated by another user before saving
                print_warn("ATENCIÓN - Es posible que otro usuario haya modificado el archivo de base de datos. Se recomienda "
                           "guardar con otro nombre y revisar los cambios manualmente (Opción merge próximamente)")
                if get_user_confirmation("¿Guardar con otro nombre?"):
                    db_filename_list = db_filename.split('.')
                    db_filename = db_filename_list[0]+"_unverfied."+db_filename_list[1]
                    flag_overwrite = False
    else:
        print_error("La ruta %s no es accesible" % folder_output)
        folder_output = get_existing_folder_from_user()
    save_file(folder_output, db_filename, flag_overwrite, acro_dict_handler.save_db)

    # Same simplified logic for the backup file. Backups are not overwriten, less checks needed
    if config_save_backups: #todo, delete older files?
        flag_overwrite = False
        bak_folder_output = Path(config_acro_db_bkp_folder)
        aux_filename_list = config_acro_db_file.split('.')
        bak_db_filename = aux_filename_list[0] + "_backup(" + datetime.now().strftime("%Y%m%d") + ")." + aux_filename_list[1]

        pathHelpers.ensure_directory(bak_folder_output)
        if not bak_folder_output.exists():
            print_error("La ruta %s no es accesible" % bak_folder_output)
            bak_folder_output = get_existing_folder_from_user()

        save_file(bak_folder_output, bak_db_filename, flag_overwrite, acro_dict_handler.save_db_backup)


def save_file(folder, filename, overwrite, save_fcn, *args):
    """Function that performs a safe generic save

    :param folder: Folder String
    :param filename: Filename String
    :param overwrite: If false the filename will be change to avoid overwrite
    :param save_fcn: Function called if the folder and filename is correct
    :param args: Arguments passed to save_fcn
    """
    flag_finish = False
    while not flag_finish:
        path_output = Path(folder)
        if path_output.exists():
            path_output = path_output / filename
            if not overwrite:
                if path_output.exists():
                    path_output = pathHelpers.get_not_existing_file(path_output)
            try:
                if args: # Assume good use of args by developer
                    save_fcn(path_output, args[0])
                else:
                    save_fcn(path_output)
                flag_finish = True
            except PermissionError as e: #OSError [Errno 13] Permission denied
                print_warn("Error de permisos al guardar. Se intentará con otro nombre")
                overwrite = False  # Disable overwrite and try again
            except (IOError, OSError) as e:
                print_error("Se ha producido un error al guardar %s" % str(e))
                if not get_user_confirmation("¿Quieres volver a intentar?"):
                    flag_finish = True
        else:
            print_error('ERROR - Carpeta "%s" no encontrada al guardar' % path_output)
            folder = get_existing_folder_from_user()
    print_ok("Se ha guardado el fichero: %s" % path_output)


def get_existing_folder_from_user():
    """Asks and returns a folder inputted by the user. The folder will always exist"""
    flag_finish = False
    folder_return = ""
    while not flag_finish:
        user_input = input("Introduce la ruta de una carpeta: ")

        folder_return = Path(user_input)
        if folder_return.exists() and folder_return.is_dir():
            flag_finish = True
        else:
            print_error("ERROR - La ruta introducida no existe o no es una carpeta")
    return folder_return


def get_def_str_from_user():
    """Asks and returns two strings from the user related to the acronym definition"""
    flag_finish = False
    while not flag_finish:
        str_def_main = input("Introduce definición: ")
        if str_def_main == "":
            print("ERROR - La definición no puede estar vacía")
        else:
            flag_finish = True
    str_def_trans = input("Introduce traducción: ")
    return str_def_main, str_def_trans


def get_num_from_user(str_info, lower, upper):
    """Ask and returns a integer inputted by the user from a set range.

    :param str_info: Text shown to the user
    :param lower: Inferior range limit
    :param upper: Superior range limit
    :return: Integer from the user
    """
    flag_finish = False
    aux_input = 0
    while not flag_finish:
        try:
            aux_input = int(input("%s [%d - %d]: " % (str_info, lower, upper)))
            if lower <= aux_input <= upper:
                flag_finish = True
            else:
                print("ERROR - Introduce un número entero en el rango especificado")
        except ValueError:
            print("ERROR - Formato incorrecto. Introduce número entero")
    return aux_input


def get_user_confirmation(str_in="¿Desea continuar?"):
    """Ask and returns confirmation from user

    :param str_in: Text shown to the user
    :return: True if user confirms
    """
    flag_return = False
    flag_finish = False
    while not flag_finish:
        user_command = input(str_in + " (y/n): ").lower()
        if user_command == 'y':
            flag_return = True
            flag_finish = True
        elif user_command == 'n':
            flag_finish = True
        else:
            print_error("ERROR - Comando no reconocido. Elige entre sí('y') y no('n')")
    return flag_return


def print_ellapsed_time(elapsed_f_sec):
    """Prints time as hours minutes and seconds since the begining of the programm"""
    hours, minutes = 0, 0
    while elapsed_f_sec >= 3600:
        elapsed_f_sec -= 3600
        hours += 1
    while elapsed_f_sec >= 60:
        elapsed_f_sec -= 60
        minutes += 1
    seconds = int(elapsed_f_sec)
    print("Han transcurrido %s:%s:%s desde el inicio del programa" %
          (str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2)))


def print_error(str_in):
    """Prints a red string"""
    print(ach.color_str(str_in, ach.AnsiColorCode.RED))


def print_warn(str_in):
    """Prints a yellow string"""
    print(ach.color_str(str_in, ach.AnsiColorCode.YELLOW))


def print_ok(str_in):
    """Prints a green string"""
    print(ach.color_str(str_in, ach.AnsiColorCode.GREEN))


def print_logo():
    """Prints the program starting logo"""
    color = ach.AnsiColorCode.DARK_YELLOW
    print("")
    print(ach.color_str("      db       .g8\"\"\"bgd `7MM\"\"\"Mq.   .g8\"\"8q. `7MN.   `7MF`YMM'   `MM`7MMM.     ,MMF'     db  MMP\"\"MM\"\"YMM `7MM\"\"\"YMM ", color))
    print(ach.color_str("     ;MM:    .dP'     `M   MM   `MM..dP'    `YM. MMN.    M   VMA   ,V   MMMb    dPMM      ;MM: P'   MM   `7   MM    `7 ", color))
    print(ach.color_str("    ,V^MM.   dM'       `   MM   ,M9 dM'      `MM M YMb   M    VMA ,V    M YM   ,M MM     ,V^MM.     MM        MM   d   ", color))
    print(ach.color_str("   ,M  `MM   MM            MMmmdM9  MM        MM M  `MN. M     VMMP     M  Mb  M' MM    ,M  `MM     MM        MMmmMM   ", color))
    print(ach.color_str("   AbmmmqMA  MM.           MM  YM.  MM.      ,MP M   `MM.M      MM      M  YM.P'  MM    AbmmmqMA    MM        MM   Y  ,", color))
    print(ach.color_str("  A'     VML `Mb.     ,'   MM   `Mb.`Mb.    ,dP' M     YMM      MM      M  `YM'   MM   A'     VML   MM        MM     ,M", color))
    print(ach.color_str(".AMA.   .AMMA. `\"bmmmd'  .JMML. .JMM. `\"bmmd\"' .JML.    YM    .JMML.  .JML. `'  .JMML.AMA.   .AMMA.JMML.    .JMMmmmmMMM", color))
    print("Acronymate", define_acronymate_version, " - SAHR Projects 2020 -  Versión para docx solo en Español")
    print("")
