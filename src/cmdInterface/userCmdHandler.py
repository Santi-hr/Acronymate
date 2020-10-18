from datetime import datetime
from pathlib import Path
from src.common import defines as dv
from src.common import configVars as cv
from src.common import configHandler
from src.common import pathHelpers
from src.common import stringHelpers as strHlprs
from src.common import translationHandler
from src.cmdInterface import ansiColorHelper as ach
from src.acroHandlers import acroAuxObj


def load_config_data():
    """Loads config data and ask the user for actions in case the loading fails"""
    if not configHandler.read_config_file():
        print_error(_("ERROR - No se ha podido cargar el fichero de configuración"))
        if get_user_confirmation(_("¿Crear nuevo fichero de configuración con valores por defecto?")):
            configHandler.save_config_file()
        else:
            print(_("Saliendo ..."))
            exit(-15)
    configHandler.apply_config()


def get_docx_filepath_from_user(acro_dict_handler):
    """Asks the user for a word document and returns it"""
    flag_finish = False
    print("")
    print(ach.color_str(_("INFO: Escribe 'config' como ruta para acceder al menú de configuración rápida"),
                        ach.AnsiColorCode.DARK_CYAN))
    while not flag_finish:
        input_path = input(_("Copia la ruta de la carpeta donde se encuentra el archivo a procesar: "))
        if input_path.strip() == "config":
            config_menu(acro_dict_handler)
        else:
            try:
                files_in_path = Path(input_path).glob('*.docx')
                path_list = []
                counter = 0
                for f in files_in_path:
                    filename = pathHelpers.get_filename_from_path(f)
                    if filename[0] != '~':
                        print("  %d -" % (counter+1), pathHelpers.get_filename_from_path(f))
                        path_list.append(f)
                        counter += 1
                if len(path_list) == 0:
                    print_error(_("ERROR - No se encuentran archivos '.docx' en la ruta seleccionada"))
                else:
                    flag_finish = True
            except OSError:
                print_error(_("ERROR - El nombre de archivo, el nombre de directorio o la sintaxis de la etiqueta del volumen no son correctos"))
    user_num = get_num_from_user(_("Seleciona el archivo a procesar"), lower=1, upper=len(path_list))

    filepath = path_list[user_num-1]

    return filepath


def config_menu(acro_dict_handler):
    print("")
    print(_("Menú de configuración rápida")) # Todo: actualizar
    print_warn(_("Este menú solo contiene algunas de las opciones. Para el resto de configuración, modificar manualmente el archivo 'config.json' que acompaña al ejecutable"))

    flag_finish = False
    flag_db_path_updated = False
    while not flag_finish:
        print(_("Opciones:"))
        config_print_options()
        option = get_num_from_user(_("Selecciona que quieres modificar"), 0, 4)
        if option == 1:
            config_locale()
        elif option == 2:
            config_db_path()
            flag_db_path_updated = True
        elif option == 3:
            config_min_acro_len()
        elif option == 4:
            config_backup()

        if not get_user_confirmation(_("¿Desea hacer algún otro cambio?")):
            flag_finish = True

    config_print_options()
    if get_user_confirmation(_("¿Desea guardar los cambios?")):
        configHandler.save_config_file()

        configHandler.apply_config()
        if flag_db_path_updated:
            acro_dict_handler.obj_db.load_acros_db()
    else:
        load_config_data()

    print("")


def config_print_options():
    print(_("  1 - Idioma:"), cv.config_locale)
    print(_("  2 - Ruta de la DB:"), cv.config_acro_db_path)
    print(_("  3 - Longitud mínima de acrónimo:"), cv.config_min_acro_len)
    print(_("  4 - Guardar backups:"), cv.config_save_backups)


def config_locale():
    """Allows user to select between the available locales"""
    locale_list = translationHandler.get_locales_list()
    cv.config_locale = locale_list[get_user_option_from_list(locale_list)]
    config_show_configuration_result(cv.config_locale)


def config_db_path():
    flag_finish = False
    while not flag_finish:
        print(_("Introduce la ruta de la carpeta donde se encuentra el fichero de base de datos de acrónimos o la ruta directa al fichero"))
        try:
            input_path = Path(input(_("Introduce ruta: ")).strip())
            if input_path.exists():
                if input_path.is_file():
                    if input_path.suffix != ".json":
                        print_error(_("ERROR - El fichero debe acabar en '.json'"))
                    else:
                        new_path = input_path
                        flag_finish = True
                else:
                    print("Ruta a carpeta")
                    list_files = [x.name for x in input_path.glob("*.json") if x.is_file()]
                    new_path = input_path / list_files[get_user_option_from_list(list_files)]
                    flag_finish = True
            else:
                raise OSError
        except OSError:
            print_error(_("ERROR - La ruta o fichero introducido no existe"))

    cv.config_acro_db_path = new_path
    config_show_configuration_result(cv.config_acro_db_path)


def config_min_acro_len():
    print(_("Un acrónimo se detecta como N letras mayúsculas seguidas. Se recomienda una longitud mínima de 2 o 3"))
    cv.config_min_acro_len = get_num_from_user(_("Introduce la longitud mínima"), 2, 10)
    config_show_configuration_result(cv.config_min_acro_len)


def config_backup():
    cv.config_save_backups = get_user_confirmation("¿Activar el guardado de copias de seguridad?")
    config_show_configuration_result(cv.config_save_backups)


def config_show_configuration_result(configured_var):
    print_ok(_("Se ha configurado el siguiente valor: %s") % str(configured_var))

def process_acro_found(acro_dict_handler):
    """Main interface, asks first how the acronyms should be processed"""
    flag_finish = False
    while not flag_finish:
        user_command = input(_("¿Como procesar los acrónimos?") + " (m/s/e/a/h): ").lower()
        if user_command == 'm':  # -- MANUAL --
            process_acro_found_one_by_one(acro_dict_handler, flag_auto_command=False)
            flag_finish = True
        elif user_command == 's':  # -- SEMIAUTOMATIC --
            process_acro_found_one_by_one(acro_dict_handler, flag_auto_command=True)
            flag_finish = True
        elif user_command == 'e':  # -- EXPORT ONLY --
            process_acro_found_to_export_empty(acro_dict_handler)
            flag_finish = True
        elif user_command == 'a':  # -- ABOUT --
            print_about_info()
        elif user_command == 'h':  # -- HELP --
            print_process_acro_found_modes_help()
        # -- default --
        else:
            print_error_unrecognized_command()


def print_process_acro_found_modes_help():
    """Prints acronym processing modes help"""
    print(_("  m: Manual    - Se procesa uno a uno cada acrónimo de forma manual."))
    print(_("  s: Semi-auto - Automáticamente se aceptan los acrónimos que están en la base de datos y se saltan los que"))
    print(_("                 están añadidos a la Blacklist. Se procesan manualmente aquellos no definidos, con múltiples"))
    print(_("                 definiciones o cuando la definición de base de datos no coincida con la del documento."))
    print(_("  e: Exportar  - Exporta todos los acrónimos encontrados sin incluir sus definiciones."))
    print(_("  a: Acerca de - Muestra información del programa."))
    print(_("  h: Ayuda     - Muestra esta información."))


def print_about_info():
    """Prints about info"""
    print("Acronymate", dv.define_acronymate_version, " - SAHR Projects 2020")
    print(_("Dependencias:"))
    print("    python-docx: Copyright (c) 2013 Steve Canny, https://github.com/scanny")
    print("    lxml: Copyright (c) 2004 Infrae. All rights reserved.")


def process_acro_found_to_export_empty(acro_dict_handler):
    for i, acro in enumerate(sorted(acro_dict_handler.acros_found.keys(), key=strHlprs.remove_accents)):
        aux_acro_obj = acroAuxObj.acroAuxObj(acro, acro_dict_handler)
        aux_acro_obj.use_empty_acro()


def process_acro_found_one_by_one(acro_dict_handler, flag_auto_command):
    """Main interface, process acronyms one by one asking the user what to do

    :param acro_dict_handler: Acronym dictionary objects
    :param flag_auto_command: Set to true to enter in semiautomatic mode
    """
    acro_list = sorted(acro_dict_handler.acros_found.keys(), key=strHlprs.remove_accents)
    acro_idx = 0
    flag_undo = False  # If True the acronym will try to be reverted
    while acro_idx < len(acro_list):
        # Create an auxilary object for each acronym
        aux_acro_obj = acroAuxObj.acroAuxObj(acro_list[acro_idx], acro_dict_handler)
        if flag_undo:
            aux_acro_obj.remove_used_acro()
        flag_undo = False

        # Generate header and prints it
        max_acros = len(acro_dict_handler.acros_found.keys())
        str_header = (" %s (%d/%d) " % (acro_list[acro_idx], acro_idx+1, max_acros)).center(80, '-')
        str_half_header = "_"*round(len(str_header)/2)

        print("")
        print(str_header)

        # Print acronym matches
        print(ach.color_str(_("Coincidencias:"),
                            ach.AnsiColorCode.BOLD), acro_dict_handler.acros_found[acro_list[acro_idx]]['Count'])
        for context in acro_dict_handler.acros_found[acro_list[acro_idx]]['Context']:
            print("     ", context)

        # Print found definitions
        print(str_half_header)

        print(_("Tabla del documento: "), end="")
        print(aux_acro_obj.get_str_pretty_definition_list(aux_acro_obj.def_list_doc_table))
        print(_("      Base de datos: "), end="")
        print(aux_acro_obj.get_str_pretty_definition_list(aux_acro_obj.def_list_db))
        if aux_acro_obj.defs_discrepancy():
            print_warn(_("Discrepancia detectada entre base de datos y tabla del documento"))

        # Ask the user for commands
        print(str_half_header)
        flag_finish = False
        while not flag_finish:
            str_def_main, str_def_trans = aux_acro_obj.get_def_strings()
            print(ach.color_str(_("  Acrónimo:"), ach.AnsiColorCode.BOLD), acro_list[acro_idx], end="")
            if aux_acro_obj.is_blacklisted():
                print(ach.color_str(_(" (EN LISTA NEGRA)"), ach.AnsiColorCode.DARK_YELLOW))
            else:
                print("")
            print(ach.color_str(_(" Principal:"), ach.AnsiColorCode.BOLD), str_def_main)
            print(ach.color_str(_("Traducción:"), ach.AnsiColorCode.BOLD), str_def_trans)

            # Obtain user command or process automatic selection
            user_command = ""
            if flag_auto_command:
                if aux_acro_obj.is_blacklisted():
                    user_command = 'n'  # Skip blacklisted acronym
                else:
                    if aux_acro_obj.is_in_db() and not aux_acro_obj.has_multiple_defs() and not aux_acro_obj.defs_discrepancy():
                        user_command = 'y'
            if user_command == "":
                user_command = input(_("Introduce comando") + " (y/n/e/a/s/b/d/z/m/h): ").lower()

            if user_command == 'y':  # -- ACCEPT CHANGES --
                flag_finish = process_acro_command_accept(aux_acro_obj)
            elif user_command == 'n':  # -- DISCARD ACRONYM --
                flag_finish = process_acro_command_skip()
            elif user_command == 'e':  # -- EDIT --
                flag_finish = process_acro_command_edit(aux_acro_obj)
            elif user_command == 'a':  # -- ADD --
                flag_finish = process_acro_command_add(aux_acro_obj)
            elif user_command == 's':  # -- SELECT --
                flag_finish = process_acro_command_select(aux_acro_obj)
            elif user_command == 'b':  # -- BLACKLIST --
                flag_finish = process_acro_command_blacklist(aux_acro_obj)
            elif user_command == 'd':  # -- DELETE --
                flag_finish = process_acro_command_delete(aux_acro_obj)
            elif user_command == 'z':  # -- UNDO --
                flag_finish, acro_idx, flag_undo = process_acro_undo(acro_idx)
            elif user_command == 'm':  # -- MODE --
                flag_auto_command = process_acro_change_mode(flag_auto_command)
            elif user_command == 'h':  # -- HELP --
                print_process_acro_found_help()
            # -- default --
            else:
                print_error_unrecognized_command()
        acro_idx = acro_idx + 1


#------ process_acro_found command functions ------#
def process_acro_command_accept(aux_acro_obj):
    flag_finish = False
    if aux_acro_obj.check_def():
        aux_acro_obj.save_and_use_acro()
        print_ok(_("Se guarda el acrónimo"))
        flag_finish = True
    else:
        print_error(
            _("ERROR - Comprueba que el acrónimo está definido y que al menos 1 definición está seleccionada"))
    return flag_finish


def process_acro_command_skip():
    print_ok(_("Se descarta el acrónimo"))
    flag_finish = True
    return flag_finish


def process_acro_command_edit(aux_acro_obj):
    flag_finish = False
    idx_def_to_edit = 1
    if aux_acro_obj.has_multiple_defs():
        idx_def_to_edit = get_num_from_user(_("¿Cual quieres editar?"),
                                            lower=1, upper=len(aux_acro_obj.proposed_def))
    user_def_main, user_def_trans = get_def_str_from_user()
    aux_acro_obj.edit_def(idx_def_to_edit, user_def_main, user_def_trans)
    return flag_finish


def process_acro_command_add(aux_acro_obj):
    flag_finish = False
    user_def_main, user_def_trans = get_def_str_from_user()
    aux_acro_obj.add_def(user_def_main, user_def_trans)
    return flag_finish


def process_acro_command_select(aux_acro_obj):
    flag_finish = False
    if aux_acro_obj.has_multiple_defs():
        idx_list = get_user_idx_list(_("Elige que definiciones seleccionar (Ej: 1,2,4): "))
        aux_acro_obj.select_defs(idx_list)
    else:
        print(_("Esta opción solo está disponible para acrónimos con múltiples definiciones"))
    return flag_finish


def process_acro_command_blacklist(aux_acro_obj):
    flag_finish = False
    aux_acro_obj.toggle_blacklisted_status()
    return flag_finish


def process_acro_command_delete(aux_acro_obj):
    flag_finish = False
    print_warn(_("ATENCIÓN - El borrado eliminará la definición de la base de datos (si está en esta)\n") +
               _("Para no usar el acrónimo usa el comando 'n', si hay múltiples definiciones usa 's' para elegir cuales usar"))
    if get_user_confirmation():
        idx_def_to_edit = 1
        if aux_acro_obj.has_multiple_defs():
            idx_def_to_edit = get_num_from_user(_("¿Cual quieres eliminar?"),
                                                lower=1, upper=len(aux_acro_obj.proposed_def))
        else:
            print_ok(_("Se elimina el acrónimo"))
            flag_finish = True  # If we delete the last definition continue with the next acronym
        aux_acro_obj.delete_def(idx_def_to_edit)
    return flag_finish


def process_acro_undo(acro_idx):
    """Returns to previous acronym and marks it to be removed from the used list"""
    acro_idx = max(acro_idx - 2, -1)  # Index always increments 1 after command
    flag_finish = True
    flag_undo = True

    return flag_finish, acro_idx, flag_undo


def process_acro_change_mode(flag_auto_command):
    """Alternates between manual and semiauto modes after getting user confirmation"""
    flag_output = flag_auto_command
    if get_user_confirmation(_("¿Cambiar de modo de procesamiento?")):
        if flag_auto_command:
            flag_output = False
            print(_("Se cambia a modo manual"))
        else:
            flag_output = True
            print(_("Se cambia a modo semiautomático"))
    return flag_output


def print_process_acro_found_help():
    """Prints acronym handling user commands help"""
    print(_("  y: Aceptar     - Guarda el acrónimo con la información mostrada y actualiza la base de datos."))
    print(_("  n: Saltar      - Descarta el acrónimo y continúa al siguiente."))
    print(_("  e: Editar      - Modifica una definición. En principal se indica la definición en el idioma de origen."))
    print(_("                   En traducción se indica la definición en Español. Dejar vacío si no es necesaria."))
    print(_("  a: Añadir      - Añade una definición adicional."))
    print(_("  s: Seleccionar - Selecciona las definiciones a usar. Aquellas deseleccionadas (en gris) no se incluirán en la tabla "))
    print(_("                   de acrónimos de salida. La diferencia con eliminar es que la definición se mantiene en la base de datos."))
    print(_("  b: Blacklist   - Alterna el estado del acrónimo en la lista negra. Si está en esta lista se saltará "))
    print(_("                   automáticamente al procesar en modo semi-automático."))
    print(_("  d: Eliminar    - Elimina el acrónimo o una de sus definiciónes de la base de datos."))
    print(_("  z: Deshacer    - Retrocede al acrónimo anterior."))
    print(_("  m: Modo        - Alterna entre modos de procesamiento manual y semiautomático."))
    print(_("  h: Ayuda       - Muestra esta información."))


########### SAVE FUNCTIONS WITH USER HANDLING #############

def handle_db_save(acro_dict_handler):
    """Handles interface for the update of the database

    :param acro_dict_handler: Acronym dictionary objects
    """
    print(_("Guardando\nResumen de cambios en la base de datos:"), acro_dict_handler.obj_db.log_db_changes)
    path_output = Path(cv.config_acro_db_path)
    folder_output = path_output.parent
    db_filename = path_output.name

    flag_overwrite = True
    # Get a valid folder
    if folder_output.exists():
        if path_output.exists():  # Skip checks if db file does't exist yet
            if not acro_dict_handler.obj_db.check_db_integrity():  # Check if file was updated by another user before saving
                print_warn(_("ATENCIÓN - Es posible que otro usuario haya modificado el archivo de base de datos. Se recomienda guardar con otro nombre y revisar los cambios manualmente."))
                if get_user_confirmation("¿Guardar con otro nombre?"):
                    db_filename_list = db_filename.split('.')
                    db_filename = db_filename_list[0]+"_unverfied."+db_filename_list[1]
                    flag_overwrite = False
    else:
        print_error(_("La ruta %s no es accesible") % folder_output)
        folder_output = get_existing_folder_from_user()
    save_file(folder_output, db_filename, flag_overwrite, acro_dict_handler.obj_db.save_db)

    # Same simplified logic for the backup file. Backups are not overwriten, less checks needed
    if cv.config_save_backups:  # todo, delete older files?
        flag_overwrite = False
        bak_folder_output = Path(cv.config_acro_db_bkp_folder)
        aux_filename_list = Path(cv.config_acro_db_path).name.split('.')
        bak_db_filename = aux_filename_list[0] + "_backup(" + datetime.now().strftime("%Y%m%d") + ")." + aux_filename_list[1]

        pathHelpers.ensure_directory(bak_folder_output)
        if not bak_folder_output.exists():
            print_error(_("La ruta %s no es accesible") % bak_folder_output)
            bak_folder_output = get_existing_folder_from_user()

        save_file(bak_folder_output, bak_db_filename, flag_overwrite, acro_dict_handler.obj_db.save_db_backup)


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
                if args:  # Assume good use of args by developer
                    save_fcn(path_output, args[0])
                else:
                    save_fcn(path_output)
                flag_finish = True
            except PermissionError:  # OSError [Errno 13] Permission denied
                print_warn(_("Error de permisos al guardar. Se intentará con otro nombre"))
                overwrite = False  # Disable overwrite and try again
            except (IOError, OSError) as e:
                print_error(_("Se ha producido un error al guardar %s") % str(e))
                if not get_user_confirmation(_("¿Quieres volver a intentar?")):
                    flag_finish = True
        else:
            print_error(_('ERROR - Carpeta "%s" no encontrada al guardar') % path_output)
            folder = get_existing_folder_from_user()
    print_ok(_("Se ha guardado el fichero: %s") % path_output)


########### GET USER INPUT FCNS #############

def get_existing_folder_from_user():
    """Asks and returns a folder inputted by the user. The folder will always exist"""
    flag_finish = False
    folder_return = ""
    while not flag_finish:
        user_input = input(_("Introduce la ruta de una carpeta: "))

        folder_return = Path(user_input)
        if folder_return.exists() and folder_return.is_dir():
            flag_finish = True
        else:
            print_error(_("ERROR - La ruta introducida no existe o no es una carpeta"))
    return folder_return


def get_def_str_from_user():
    """Asks and returns two strings from the user related to the acronym definition"""
    flag_finish = False
    while not flag_finish:
        str_def_main = input(_("Introduce definición: "))
        if str_def_main == "":
            print(_("ERROR - La definición no puede estar vacía"))
        else:
            flag_finish = True
    str_def_trans = input(_("Introduce traducción: "))
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
                print(_("ERROR - Introduce un número entero en el rango especificado"))
        except ValueError:
            print(_("ERROR - Formato incorrecto. Introduce número entero"))
    return aux_input


def get_user_confirmation(str_in=_("¿Desea continuar?")):
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
            print_error(_("ERROR - Comando no reconocido. Elige entre sí('y') y no('n')"))
    return flag_return


def get_user_idx_list(str_in=_("Introduce enteros separados por comas: ")):
    """Ask and returns a list of ints separated by commas

    :param str_in: Text shown to the user
    :return: List of integers
    """
    return_list = []
    flag_finish = False
    while not flag_finish:
        user_input = input(str_in)
        flag_finish = True
        return_list = []
        for substr in user_input.split(","):
            try:
                return_list.append(int(substr.strip()))
            except ValueError:
                flag_finish = False
                print_error(_("ERROR - Formato incorrecto. Introduce números enteros separados por comas"))
                break
    return return_list


def get_user_option_from_list(list_in):
    """Shows the user all the items of a list and ask him to chose one

    :param list_in: List with options
    :return: User selected index
    """
    for i, loc in enumerate(list_in):
        print("  %d - %s" % (i+1, loc))
    return (get_num_from_user(_("Selecciona opción"), 1, len(list_in)))-1  # Return index starting from 0


########### MULTIPLE USED PRINTS #############
def print_error_unrecognized_command():
    print(_("ERROR - Comando no reconocido. Usa el comando 'h' para obtener ayuda"))


########### PRINT HELPER FCNS #############

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
    print(_("Han transcurrido %s:%s:%s desde el inicio del programa") %
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
    # Georgia 11
    color = ach.AnsiColorCode.DARK_YELLOW
    print("")
    print(ach.color_str("      db       .g8\"\"\"bgd `7MM\"\"\"Mq.   .g8\"\"8q. `7MN.   `7MF`YMM'   `MM`7MMM.     ,MMF'     db  MMP\"\"MM\"\"YMM `7MM\"\"\"YMM ", color))
    print(ach.color_str("     ;MM:    .dP'     `M   MM   `MM..dP'    `YM. MMN.    M   VMA   ,V   MMMb    dPMM      ;MM: P'   MM   `7   MM    `7 ", color))
    print(ach.color_str("    ,V^MM.   dM'       `   MM   ,M9 dM'      `MM M YMb   M    VMA ,V    M YM   ,M MM     ,V^MM.     MM        MM   d   ", color))
    print(ach.color_str("   ,M  `MM   MM            MMmmdM9  MM        MM M  `MN. M     VMMP     M  Mb  M' MM    ,M  `MM     MM        MMmmMM   ", color))
    print(ach.color_str("   AbmmmqMA  MM.           MM  YM.  MM.      ,MP M   `MM.M      MM      M  YM.P'  MM    AbmmmqMA    MM        MM   Y  ,", color))
    print(ach.color_str("  A'     VML `Mb.     ,'   MM   `Mb.`Mb.    ,dP' M     YMM      MM      M  `YM'   MM   A'     VML   MM        MM     ,M", color))
    print(ach.color_str(".AMA.   .AMMA. `\"bmmmd'  .JMML. .JMM. `\"bmmd\"' .JML.    YM    .JMML.  .JML. `'  .JMML.AMA.   .AMMA.JMML.    .JMMmmmmMMM", color))
    print("Acronymate", dv.define_acronymate_version, " - SAHR Projects 2020")
    print("")


########### PRINT FUNCTIONS FOR OTHER SCRIPTS #############
""" These functions are here to unify the console outputs in order to reduce the translation objects to be created 
and managed"""

#### DocxReader ####
def print_acronym_search_start():
    print(_("Extrayendo acrónimos del documento"))

def print_acronym_search_second_pass():
    print(_("Repasando la búsqueda con acrónimos especiales"))

def get_translated_str_tables():
    return _("Tablas")

def get_translated_str_paragraphs():
    return _("Párrafos")

def get_translated_str_sections():
    return _("Secciones")

#### acroDbHandler ####
def print_db_except_file_not_found(e):
    print_error(_("No se encuentra el archivo DB: %s") % str(e))

def print_db_except_decode_error(e):
    print_error(_("Archivo DB no parseable: %s") % str(e))

def print_db_except_key_error(e):
    print_error(_("Error al acceder al diccionario: %s") % str(e))

def print_db_loading_info(db_file_name):
    print(_("Cargando la base de datos de acrónimos (%s) ...") % db_file_name)

def print_db_checking():
    print(_("Comprobando estado de la base de datos ..."))

def print_db_check_no_acros():
    print_warn(_("No se encuentran acrónimos, creando diccionario vacío"))

def print_db_check_empty_acro(key):
    print_warn(_("El acrónimo %s está vacío") % str(key))

def print_db_check_admin_data_wrong():
    print_warn(_("La sección Admin_data no es correcta, no se podrá verificar el guardado seguro"))
