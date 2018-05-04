import os

from PyQt5.QtWidgets import QFileDialog


def get_new_path(img, parent_path, thumb_path):
    """
    Replace the original path to the thumbnail one (replace 'parent_path' by 'thumb_path')
    :param img: original path
    :param parent_path: path to the parent directory
    :param thumb_path: path to the thumbnail path
    :return: modified path
    """
    return img.replace(parent_path, thumb_path, 1)


def is_file_valid_image(file):
    return file.endswith("png") or file.endswith("PNG") or file.endswith("jpg") or file.endswith("JPG") or file.endswith("JPEG") or file.endswith("jpeg")


def is_directory_valid(path, files):
    """
    Check if the given path is not hidden or without images
    :param files:  files in the folder
    :param path: Path to check
    :return: True if path contains a hidden folder or is empty, False otherwise
    """
    directories = path.split(os.sep)
    valid = len(files) > 0
    for dn in directories:  # check if directory or one of its parent are not hidden
        if dn.startswith(".") or not valid:
            valid = False
            break
    if valid:
        valid_files = []
        for fn in files:  # check if directory contains valid images
            if is_file_valid_image(fn):
                valid_files.append(fn)
        valid = len(valid_files) > 0
    return valid


def get_current_dir(path):
    """
    Get the name of the current directory
    :param path: Path to search the name in
    :return: directory name
    """
    return os.path.basename(os.path.normpath(path))


def get_images_in_dir(path):
    """
    get images in the folder specified (hidden and empty folders are ignored)
    sub folders are ignored
    :param path: directory to get images in
    :return: images list
    """
    images_list = []
    files_list = os.listdir(path)
    for fn in files_list:
        if is_file_valid_image(fn):
            images_list.append(os.path.join(path, fn))
    return images_list


def create_file_dialog():
    """
    Create a file dialog object, ready to use
    :return:
    """
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.DirectoryOnly)
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    options |= QFileDialog.ShowDirsOnly
    dialog.setOptions(options)
    return dialog


def remove_images_from_folders(folder: str, images_list: list):
    """
    Remove images in the specified folder, subfolders are ignored
    :param folder: folder to remove images from
    :param images_list: list of images to edit
    :return: edited image list
    """
    new_list = []
    for img in images_list:
        if folder != os.path.dirname(img):
            new_list.append(img)
    return new_list
