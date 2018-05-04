import os
import sys
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

from utils import is_file_valid_image, get_current_dir, get_new_path


class CompresserSignals(QObject):
    finished_signal = pyqtSignal()  # thread has finished
    new_zip_task_started = pyqtSignal(str)  # tell ui what to display
    new_thumb_task_started = pyqtSignal(str)  # tell ui what to display
    new_compress_task_started = pyqtSignal(str) # tell ui what to display
    zip_done = pyqtSignal()  # finished zipping a folder
    thumb_done = pyqtSignal()  # finished creating a thumbnail
    compress_done = pyqtSignal()  # finished compressing an image


class Compresser(QRunnable):

    def __init__(self, dir_list, image_list, parent_path, thumb_path, is_compress, is_zip, is_thumb, quality):
        super(Compresser, self).__init__()
        self.dir_list = dir_list
        self.image_list = image_list
        self.parent_path = parent_path
        self.thumb_path = thumb_path
        self.is_compress = is_compress
        self.is_zip = is_zip
        self.is_thumb = is_thumb
        self.quality = quality
        self.signals = CompresserSignals()
        self.should_stop = False

    def stop(self):
        self.should_stop = True

    def is_aborted(self):
        return self.should_stop

    def compress_images(self):
        """
        Compress images in jpg format to reduce their file size

        :return:
        """
        print("Compressing images...")
        for current_img in self.image_list:
            self.signals.new_compress_task_started.emit("Compression de '" + current_img + "' ...")
            if self.is_aborted():
                break
            img = Image.open(current_img)
            img.save(current_img, optimize=True, quality=int(self.quality))
            self.signals.compress_done.emit()
        print("COMPRESSION FINISHED")
        if self.is_aborted():
            self.signals.new_compress_task_started.emit("Compression annulée")
        else:
            self.signals.new_compress_task_started.emit("Compression terminée")

    def zip_dir_list(self):
        """
        Compress images in all the specified directories
        Create one zip per folder

        :return:
        """
        for path in self.dir_list:
            if self.is_aborted():
                break
            self.zip_dir(path)
        print("ZIPPING FINISHED")
        if self.is_aborted():
            self.signals.new_zip_task_started.emit("Compression en .zip annulée")
        else:
            self.signals.new_zip_task_started.emit("Compression en .zip terminée")

    def zip_dir(self, path):
        """
        Compress images in the specified directory
        Sub directories are ignored
        Create one zip per folder

        :param path: directory to get files in
        :return:
        """
        files_list = os.listdir(path)
        print("Creating .zip '" + path + "'", end="")
        self.signals.new_zip_task_started.emit("Création du .zip pour '" + path + "' ...")
        with ZipFile(os.path.join(path, get_current_dir(path)) + ".zip", "w", ZIP_DEFLATED) as zip_file:
            for fn in files_list:
                if not fn.endswith("zip") and is_file_valid_image(fn):
                    print(".", end="")
                    absolute_file_name = os.path.join(path, fn)
                    zippped_file_name = absolute_file_name[len(path) + len(os.sep):]  # XXX: relative path
                    zip_file.write(absolute_file_name, zippped_file_name)
        print("done")
        self.signals.zip_done.emit()

    def create_thumbs(self):
        """
        Compress images to a 140x105 format, cropping in the middle if needed

        :return:
        """
        print("Creating thumbnails...")
        size = 140, 105  # 4/3 format
        for current_img in self.image_list:
            self.signals.new_thumb_task_started.emit("Création de la miniature pour '" + current_img + "' ...")
            if self.is_aborted():
                break
            # If height is higher we resize vertically, if not we resize horizontally
            img = Image.open(current_img)
            # Get current and desired ratio for the images
            img_ratio = img.size[0] / float(img.size[1])
            ratio = size[0] / float(size[1])
            # The image is scaled/cropped vertically or horizontally depending on the ratio
            if ratio > img_ratio:
                img = img.resize((size[0], round(size[0] * img.size[1] / img.size[0])), Image.BILINEAR)
                # Crop in the middle
                box = (0, round((img.size[1] - size[1]) / 2), img.size[0], round((img.size[1] + size[1]) / 2))
                img = img.crop(box)
            elif ratio < img_ratio:
                img = img.resize((round(size[1] * img.size[0] / img.size[1]), size[1]), Image.BILINEAR)
                # Crop in the middle
                box = (round((img.size[0] - size[0]) / 2), 0, round((img.size[0] + size[0]) / 2), img.size[1])
                img = img.crop(box)
            else:
                img = img.resize((size[0], size[1]), Image.BILINEAR)
                # If the scale is the same, we do not need to crop
            filename = get_new_path(current_img, self.parent_path, self.thumb_path)
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError:
                    sys.exit(
                        "Fatal : Directory '" + os.path.dirname(filename) + "' does not exist and cannot be created")

            img.save(filename, "JPEG")
            self.signals.thumb_done.emit()
        print("THUMBNAILS FINISHED")
        if self.is_aborted():
            self.signals.new_thumb_task_started.emit("Miniatures annulées")
        else:
            self.signals.new_thumb_task_started.emit("Miniatures terminées")

    @pyqtSlot()
    def run(self):
        if self.is_compress:
            self.compress_images()
        if self.is_zip:
            self.zip_dir_list()
        if self.is_thumb:
            self.create_thumbs()
        self.signals.finished_signal.emit()
