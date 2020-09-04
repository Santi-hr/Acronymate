from pathlib import Path


def ensure_directory(directory_in):
    """Check if folder exist and create it otherwise

    :param directory_in: String path to directory
    :return: pathlib object
    """
    Path(directory_in).mkdir(parents=True, exist_ok=True)


def get_filename_from_path(path_in):
    """Returns filename with extension

    :param path_in: String path to file
    :return: Filename with extension
    """
    return Path(path_in).name


def get_not_existing_file(path_in):
    """If file exists it appends a number to ensure it dont

    :param path_in: String path to file
    :return: Updated path without conflicts
    """
    path_in = Path(path_in)
    file_folder = path_in.parent
    file_name = path_in.name[:-len(path_in.suffix)]
    file_suffix = path_in.suffix
    idx = 0
    new_path = path_in
    while new_path.exists():
        idx += 1
        new_path = file_folder / (file_name + "_" + str(idx) + file_suffix)
    return new_path
