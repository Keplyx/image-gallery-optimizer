import os

from PyQt5.QtCore import pyqtSlot, QRunnable, pyqtSignal, QObject

from utils import is_directory_valid, get_images_in_dir


class ScannerSignals(QObject):
    """
    Store thread signal for communication with the UI
    """
    scan_finished_signal = pyqtSignal(list, list)  # thread has finished
    scanned_dir_signal = pyqtSignal(str)  # thread scanned a directory
    scanned_dir_finished = pyqtSignal()  # all directories scanned
    scanned_images_signal = pyqtSignal(str)  # scanned a folder for images
    new_scan_task_started = pyqtSignal(str)  # update ui


class Scanner(QRunnable):
    """
    Scan operations thread
    """
    def __init__(self, path):
        super(Scanner, self).__init__()
        self.path = path
        self.signals = ScannerSignals()
        self.should_stop = False

    def stop(self):
        """
        stop the scanning thread
        :return:
        """
        self.should_stop = True

    def is_aborted(self):
        """
        Check if the scanning thread was aborted
        :return: True is the thread was aborted, false otherwise
        """
        return self.should_stop

    @pyqtSlot()
    def get_directories_list(self, path):
        """
        Tell the user which folders will be compressed, and asks for confirmation
        :param path: Root path for search
        :return: True if user confirmed, False otherwise
        """
        dir_list = []
        self.signals.new_scan_task_started.emit("Scan des sous dossiers...")
        for root, dirs, files in os.walk(path):
            if self.is_aborted():
                break

            if is_directory_valid(root, files):
                dir_list.append(root)
                self.signals.scanned_dir_signal.emit(root)
        self.signals.scanned_dir_finished.emit()
        return dir_list

    @pyqtSlot()
    def get_images_in_dir_list(self, dir_list):
        """
        get images in the folder list specified

        :param dir_list: list of directories to look for images in
        :return: images list
        """
        images_list = []
        for path in dir_list:
            if self.is_aborted():
                break
            print("Finding images in '" + path + "'", end="")
            self.signals.new_scan_task_started.emit("Recherche d'images dans le dossier '" + path + "'...")
            images_list += get_images_in_dir(path)
            print("done")
            self.signals.scanned_images_signal.emit(path)

        return images_list

    @pyqtSlot()
    def run(self):
        dir_list = self.get_directories_list(self.path)
        image_list = self.get_images_in_dir_list(dir_list)
        if self.is_aborted():
            self.signals.new_scan_task_started.emit("Scan Annulé")
        else:
            self.signals.new_scan_task_started.emit("Scan Terminé")
        self.signals.scan_finished_signal.emit(dir_list, image_list)
