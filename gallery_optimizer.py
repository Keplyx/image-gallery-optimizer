#!/usr/bin/python3
import os
import sys

from PyQt5.QtCore import QThreadPool, Qt, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, QDesktopWidget, QWidget, QFrame, QLineEdit, QListWidget, QVBoxLayout, \
    QLabel, QPushButton, QGridLayout, QMessageBox, QDialog, QTabWidget, QApplication, QCheckBox, \
    QProgressBar, QGroupBox, QDoubleSpinBox

from optimizer import ImageOptimizer
from scanner import Scanner
from utils import create_file_dialog, remove_images_from_folders


# TODO:
# Export executable

class MainWindow(QMainWindow):
    """
    Main app window containing the widgets
    """
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.resize(1000, 600)
        self.center()
        self.main_widget = MainWidgets()
        self.setCentralWidget(self.main_widget)
        self.create_menu_bar()
        self.setWindowTitle('Optimisateur de Galleries')
        self.setWindowIcon(QIcon('icons/main-icon.png'))

    def create_menu_bar(self):
        """
        Create the app menu bar
        :return:
        """
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu("Fichier")
        help_menu = main_menu.addMenu("Aide")

        exit_button = QAction('Quitter', self)
        exit_button.setShortcut('Ctrl+Q')
        exit_button.setStatusTip('Quitter le logiciel')
        exit_button.setIcon(QIcon("icons/icons8-sortie-96.png"))
        exit_button.triggered.connect(self.close)
        file_menu.addAction(exit_button)

        about_button = QAction('À Propos', self)
        about_button.setShortcut('Ctrl+H')
        about_button.setStatusTip('Voir les informations du logiciel')
        about_button.setIcon(QIcon("icons/icons8-aide-96.png"))
        about_button.triggered.connect(self.display_help_dialog)
        help_menu.addAction(about_button)

    def center(self):
        """
        Center the app window in the screen
        :return:
        """
        rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        rectangle.moveCenter(center_point)
        self.move(rectangle.topLeft())

    def display_help_dialog(self):
        """
        Display the help dialog showing info about the app
        :return:
        """
        dialog = HelpDialog(self)
        dialog.exec_()
        dialog.deleteLater()

    def closeEvent(self, event):
        """
        Display a close confirmation if a task is in progress
        :param event:
        :return:
        """
        if self.main_widget.is_task_in_progress:
            confirmation_dialog = QMessageBox.question(self, "Vraiment Quitter ?",
                                                       "Des opérations sont encore en cours\nVoulez-vous vraiment quitter ?",
                                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirmation_dialog == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()


class MainWidgets(QWidget):
    """
    Widgets to be displayed in the main window
    """
    def __init__(self):
        super().__init__()
        self.dir_path_group = QGroupBox()
        self.dir_path_line_edit = QLineEdit(os.path.dirname(__file__))
        self.dir_selection_button = QPushButton()
        self.dir_thumb_path_group = QGroupBox()
        self.dir_thumb_path_line_edit = QLineEdit(os.path.dirname(__file__) + "_thumb")
        self.dir_thumb_selection_button = QPushButton()
        self.scan_progress_bar = QProgressBar()
        self.scan_progress_text = QLabel("Scan")
        self.dir_list_group = QFrame()
        self.directories_list = QListWidget()
        self.scan_button = QPushButton("Scanner")
        self.stop_scan_button = QPushButton("Stop")
        self.optimize_button = QPushButton("Optimiser")
        self.stop_optimize_button = QPushButton("Stop")
        self.list_title = QLabel("0 images dans 0 dossiers :")
        self.delete_button = QPushButton("Enlever sélectionné")
        self.compress_group = QGroupBox()
        self.compress_quality_label = QLabel("Qualité :")
        self.compress_quality_edit = QDoubleSpinBox()
        self.enable_compress_radio_button = QCheckBox("Compresser photos")
        self.zip_group = QGroupBox()
        self.enable_zip_radio_button = QCheckBox("Créer .zip")
        self.thumb_group = QGroupBox()
        self.enable_thumb_radio_button = QCheckBox("Créer miniatures")
        self.compress_progress_bar = QProgressBar()
        self.compress_progress_text = QLabel("Compression")
        self.zip_progress_bar = QProgressBar()
        self.zip_progress_text = QLabel("Création de .zip")
        self.thumb_progress_bar = QProgressBar()
        self.thumb_progress_text = QLabel("Création de miniatures")
        self.image_list = []
        self.main_layout = QGridLayout()
        self.scanner = Scanner("")
        self.compresser = ImageOptimizer([], [], "", "", True, True, True, 30)
        self.thread_pool = QThreadPool()
        self.is_task_in_progress = False
        self.init_ui()

    def init_ui(self):
        """
        Place UI elements in the window
        :return:
        """
        self.setLayout(self.main_layout)

        subtitle = QLabel("Cet utilitaire permet d'optimiser facilement des galleries d'images pour des sites web\n"
                          "Passez votre curseur au dessus des différents boutons pour avoir plus d'information")
        subtitle.setAlignment(Qt.AlignCenter)

        y = 0
        self.main_layout.addWidget(subtitle, y, 0, 1, 20)
        y += 1
        dir_path_layout = QGridLayout()
        dir_path_layout.addWidget(QLabel("Dossier parent :"), 0, 0, 1, 1)
        self.dir_path_line_edit.textChanged.connect(self.update_parent_dir)
        self.dir_path_line_edit.setToolTip("Chemin vers le dossier contenant la gallerie d'images")
        dir_path_layout.addWidget(self.dir_path_line_edit, 0, 1, 1, 18)
        self.dir_selection_button.clicked.connect(self.open_dir)
        self.dir_selection_button.setIcon(QIcon("icons/icons8-dossier-ouvert-96.png"))
        self.dir_selection_button.setToolTip("Ouvrir l'explorateur de fichiers pour sélectionner le dossier")
        dir_path_layout.addWidget(self.dir_selection_button, 0, 19, 1, 1)
        self.dir_path_group.setLayout(dir_path_layout)
        self.main_layout.addWidget(self.dir_path_group, y, 0, 1, 20)

        y += 1
        dir_thumb_path_layout = QGridLayout()
        dir_thumb_path_layout.addWidget(QLabel("Dossier des miniatures :"), 0, 0, 1, 1)
        self.dir_thumb_path_line_edit.textChanged.connect(self.reset_progress_thumb)
        self.dir_thumb_path_line_edit.setToolTip("Chemin vers le dossier où les miniatures seront enregistreés")
        dir_thumb_path_layout.addWidget(self.dir_thumb_path_line_edit, 0, 1, 1, 18)
        self.dir_thumb_selection_button.clicked.connect(self.open_thumb_dir)
        self.dir_thumb_selection_button.setIcon(QIcon("icons/icons8-dossier-ouvert-96.png"))
        self.dir_thumb_selection_button.setToolTip("Ouvrir l'explorateur de fichiers pour sélectionner le dossier")
        dir_thumb_path_layout.addWidget(self.dir_thumb_selection_button, 0, 19, 1, 1)
        self.dir_thumb_path_group.setLayout(dir_thumb_path_layout)
        self.main_layout.addWidget(self.dir_thumb_path_group, y, 0, 1, 20)

        y += 1
        self.scan_button.clicked.connect(self.scan_click)
        self.scan_button.setIcon(QIcon("icons/icons8-chercher-96.png"))
        self.scan_button.setToolTip("Lancer le scan des sous-dossiers et images contenues dans le dossier parent")
        self.main_layout.addWidget(self.scan_button, y, 5, 1, 10)
        self.stop_scan_button.clicked.connect(self.stop_scan)
        self.stop_scan_button.setIcon(QIcon("icons/icons8-annuler-96.png"))
        self.stop_scan_button.setToolTip("Arrêter le scan")
        self.stop_scan_button.setEnabled(False)
        self.main_layout.addWidget(self.stop_scan_button, y, 15, 1, 1)

        y += 1
        self.scan_progress_text.setToolTip("Tâche en cours d'execution")
        self.main_layout.addWidget(self.scan_progress_text, y, 0, 1, 20)

        y += 1
        self.scan_progress_bar.setTextVisible(False)
        self.scan_progress_bar.setToolTip("Avancement du scan")
        self.main_layout.addWidget(self.scan_progress_bar, y, 0, 1, 20)

        y += 1
        self.main_layout.addWidget(self.list_title, y, 0, 1, 20)

        y += 1
        self.directories_list.setToolTip("Liste des dossiers contenant des images, trouvés dans le dossier parent")
        self.main_layout.addWidget(self.directories_list, y, 0, 10, 19)
        self.delete_button.clicked.connect(self.dir_list_delete_selected)
        self.delete_button.setIcon(QIcon("icons/icons8-effacer-96.png"))
        self.delete_button.setToolTip("Ignorer le dossier sélectionné et toutes ses images lors de l'optimisation")
        self.main_layout.addWidget(self.delete_button, y, 19, 1, 1)

        y += 1
        compress_layout = QGridLayout()
        self.compress_group.setLayout(compress_layout)
        self.enable_compress_radio_button.toggled.connect(self.set_compress_enabled)
        self.enable_compress_radio_button.setChecked(True)
        self.enable_compress_radio_button.setToolTip("Activer la compression des images. "
                                                     "Cela permet de réduire la taille de la gallerie sur le disque "
                                                     "sans perdre trop de qualité")
        compress_layout.addWidget(self.enable_compress_radio_button, 0, 0, 1, 2)
        compress_layout.addWidget(self.compress_quality_label, 1, 0, 1, 1)
        self.compress_quality_edit.setMaximum(100)
        self.compress_quality_edit.setMinimum(10)
        self.compress_quality_edit.setValue(30)  # 30 to reduce filesize by 10 without losing too much quality
        self.compress_quality_edit.setSingleStep(10)
        self.compress_quality_edit.setToolTip("Qualité de l'image après compression. Plus cette valeur est grande "
                                              "plus l'image finale sera de bonne qualité\n30 permet de réduire la "
                                              "taille de l'image d'un facteur proche de 10")
        compress_layout.addWidget(self.compress_quality_edit, 1, 1, 1, 1)
        self.main_layout.addWidget(self.compress_group, y, 19, 1, 1)

        y += 1
        zip_layout = QGridLayout()
        self.enable_zip_radio_button.toggled.connect(self.set_zip_enabled)
        self.enable_zip_radio_button.setChecked(True)
        self.enable_zip_radio_button.setToolTip("Créer un fichier compressé .zip dans chaque dossier, contenant "
                                                "toutes les images de celui-ci")
        zip_layout.addWidget(self.enable_zip_radio_button)
        self.zip_group.setLayout(zip_layout)
        self.main_layout.addWidget(self.zip_group, y, 19, 1, 1)

        y += 1
        thumb_layout = QGridLayout()
        self.enable_thumb_radio_button.toggled.connect(self.set_thumb_enabled)
        self.enable_thumb_radio_button.setChecked(True)
        self.enable_thumb_radio_button.setToolTip("Créer une miniature pour chaque image, sauvegardée dans le dossier "
                                                  "de miniatures ci-dessus\nLa structure des dossiers interne est "
                                                  "respectée, et les miniatures sont en 140x105 (format 4*3)")
        thumb_layout.addWidget(self.enable_thumb_radio_button, y, 19, 1, 1)
        self.thumb_group.setLayout(thumb_layout)
        self.main_layout.addWidget(self.thumb_group, y, 19, 1, 1)

        y += 7
        self.optimize_button.clicked.connect(self.optimize_click)
        self.optimize_button.setIcon(QIcon("icons/icons8-compresse-96.png"))
        self.optimize_button.setToolTip("Optimiser les images contenues dans les dossiers ci-dessus en utilisant les paramètres sélectionnés")
        self.main_layout.addWidget(self.optimize_button, y, 5, 1, 10)
        self.stop_optimize_button.clicked.connect(self.stop_optimize)
        self.stop_optimize_button.setIcon(QIcon("icons/icons8-annuler-96.png"))
        self.stop_optimize_button.setToolTip("Arrêter l'optimisation")
        self.stop_optimize_button.setEnabled(False)
        self.main_layout.addWidget(self.stop_optimize_button, y, 15, 1, 1)

        y += 1
        self.compress_progress_text.setToolTip("Tâche en cours d'execution")
        self.main_layout.addWidget(self.compress_progress_text, y, 0, 1, 20)

        y += 1
        self.compress_progress_bar.setTextVisible(False)
        self.compress_progress_bar.setToolTip("Avancement de la compression")
        self.main_layout.addWidget(self.compress_progress_bar, y, 0, 1, 20)

        y += 1
        self.zip_progress_text.setToolTip("Tâche en cours d'execution")
        self.main_layout.addWidget(self.zip_progress_text, y, 0, 1, 20)

        y += 1
        self.zip_progress_bar.setTextVisible(False)
        self.zip_progress_bar.setToolTip("Avancement de la création des .zip")
        self.main_layout.addWidget(self.zip_progress_bar, y, 0, 1, 20)

        y += 1
        self.thumb_progress_text.setToolTip("Tâche en cours d'execution")
        self.main_layout.addWidget(self.thumb_progress_text, y, 0, 1, 20)

        y += 1
        self.thumb_progress_bar.setTextVisible(False)
        self.thumb_progress_bar.setToolTip("Avancement de la création des miniatures")
        self.main_layout.addWidget(self.thumb_progress_bar, y, 0, 1, 20)

    def update_scan_result_text(self):
        """
        Update scan result text based on the image list and the directories list
        :return:
        """
        self.list_title.setText(
            str(len(self.image_list)) + " images dans " + str(len(self.get_dir_list())) + " dossiers :")

    def update_parent_dir(self):
        """
        Reset UI when updating the parent directory
        :return:
        """
        self.directories_list.clear()
        self.image_list = []
        self.update_scan_result_text()
        self.reset_progress_scan()
        self.reset_progress_compress()
        self.reset_progress_zip()
        self.reset_progress_thumb()

    def dir_list_delete_selected(self):
        """
        Remove the selected directory from the list, and all its images
        :return:
        """
        for selected_item in self.directories_list.selectedItems():
            self.image_list = remove_images_from_folders(selected_item.text(), self.image_list)
            self.directories_list.takeItem(self.directories_list.row(selected_item))
            self.update_scan_result_text()

    def get_dir_list(self):
        """
        Get the directories list from the UI
        :return:
        """
        items = []
        for index in range(self.directories_list.count()):
            items.append(self.directories_list.item(index).text())
        return items

    def set_compress_enabled(self, enabled):
        """
        Toggle UI elements based on the state of the compression button
        :param enabled: Whether to enable UI elements
        :return:
        """
        self.compress_progress_bar.setHidden(not enabled)
        self.compress_progress_text.setEnabled(enabled)
        self.compress_quality_label.setEnabled(enabled)
        self.compress_quality_edit.setEnabled(enabled)

    def set_zip_enabled(self, enabled):
        """
        Toggle UI elements based on the state of the zip button
        :param enabled: Whether to enable UI elements
        :return:
        """
        self.zip_progress_bar.setHidden(not enabled)
        self.zip_progress_text.setEnabled(enabled)

    def set_thumb_enabled(self, enabled):
        """
        Toggle UI elements based on the state of the thumb button
        :param enabled: Whether to enable UI elements
        :return:
        """
        self.thumb_progress_bar.setHidden(not enabled)
        self.thumb_progress_text.setEnabled(enabled)
        self.dir_thumb_path_group.setEnabled(enabled)

    def set_ui_enabled(self, enabled, is_scan):
        """
        Toggle UI state; Stop buttons are reversed: when you disable the UI, they get enabled.
        Specifying if this is a scan controls which stop button to enable.
        If you disable the UI for a scan, everything is disabled and only the stop scn button is enabled
        Tells the UI a task started or ended, necessary for the close confirmation
        :param enabled: Whether to enable the UI
        :param is_scan: Are we disabling the UI because of a scan, or because of an optimisation task ?
        :return:
        """
        self.is_task_in_progress = not enabled
        self.dir_path_line_edit.setEnabled(enabled)
        self.dir_thumb_path_line_edit.setEnabled(enabled)
        self.stop_optimize_button.setEnabled(enabled)
        self.stop_scan_button.setEnabled(enabled)
        self.optimize_button.setEnabled(enabled)
        self.scan_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)
        self.zip_group.setEnabled(enabled)
        self.compress_group.setEnabled(enabled)
        self.thumb_group.setEnabled(enabled)
        self.dir_selection_button.setEnabled(enabled)
        self.dir_thumb_selection_button.setEnabled(enabled)
        self.stop_scan_button.setEnabled((not enabled) and is_scan)
        self.stop_optimize_button.setEnabled((not enabled) and (not is_scan))

    def scan_click(self):
        """
        Start the scan in an other thread and disable the UI
        :return:
        """
        self.directories_list.clear()
        self.set_ui_enabled(False, True)
        # Start scan thread
        self.scanner = Scanner(self.dir_path_line_edit.text())
        self.scanner.signals.scanned_dir_signal.connect(self.add_dir_to_list)
        self.scanner.signals.scan_finished_signal.connect(self.scan_finished)
        self.scanner.signals.scanned_dir_finished.connect(self.reset_progress_scan)
        self.scanner.signals.scanned_images_signal.connect(self.add_progress_scan)
        self.scanner.signals.new_scan_task_started.connect(self.scan_progress_text.setText)
        self.thread_pool.start(self.scanner)

    def stop_scan(self):
        """
        Stop the scan thread
        :return:
        """
        self.scanner.stop()

    def add_dir_to_list(self, directory):
        """
        Add given directory to the UI list
        :param directory: dir to add to the list
        :return:
        """
        self.directories_list.addItem(directory)

    def scan_finished(self, dir_list, image_list):
        """
        Re-enabled the UI and reset progress bars
        Display a recap window of directories and images found, and whether the scan finished properly or was canceled
        :param dir_list: list of directories found
        :param image_list: list of images found
        :return:
        """
        self.set_ui_enabled(True, True)
        self.image_list = image_list
        self.update_scan_result_text()
        self.reset_progress_compress()
        self.reset_progress_zip()
        self.reset_progress_thumb()
        if self.scanner.is_aborted():
            QMessageBox.warning(self, "Scan Annulé", "Scan des dossiers stoppé\n" + str(len(dir_list)) + " dossier et "
                                + str(len(self.image_list)) + " images trouvés")
        else:
            QMessageBox.information(self, "Scan Terminé",
                                    "Scan des dossiers terminé\n" + str(len(dir_list)) + " dossier et "
                                    + str(len(self.image_list)) + " images trouvés")

    def optimize_click(self):
        """
        Display a confirmation window or an eror window if no actions were selected
        :return:
        """
        if self.directories_list.count() == 0:
            QMessageBox.warning(self, "Erreur", "Aucun dossier trouvé\nVeuillez vérifier le dossier parent")
        elif (not self.enable_compress_radio_button.checkState()) and (not self.enable_zip_radio_button.checkState()) \
                and (not self.enable_thumb_radio_button.checkState()):
            QMessageBox.warning(self, "Erreur", "Aucune action sélectionnée")
        else:
            self.show_confirmation_dialog()

    def show_confirmation_dialog(self):
        """
        Display a confirmation window showing a recap of what action the app is about to perform
        Give the user the possibility to cancel the optimisation
        If yes, start the optimisation thread and disable the UI
        :return:
        """
        msg = str(len(self.get_dir_list())) + " dossiers contenant " + str(len(self.image_list)) + \
              " images selectionnés\n\nActions à réaliser :"
        if self.enable_compress_radio_button.checkState():
            msg += "\nCompression des images (Qualité : " + str(int(self.compress_quality_edit.value())) + ")"
        if self.enable_zip_radio_button.checkState():
            msg += "\nCréation de .zip"
        if self.enable_thumb_radio_button.checkState():
            msg += "\nCréation de miniatures"
        msg += "\n\nÊtes-vous sûr de vouloir continuer ?"
        confirmation_dialog = QMessageBox.question(self, 'Confirmation', msg,
                                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirmation_dialog == QMessageBox.Yes:
            # Start compress thread
            self.reset_progress_compress()
            self.reset_progress_zip()
            self.reset_progress_thumb()
            self.set_ui_enabled(False, False)
            self.compresser = ImageOptimizer(self.get_dir_list(), self.image_list, self.dir_path_line_edit.text(),
                                             self.dir_thumb_path_line_edit.text(),
                                             self.enable_compress_radio_button.checkState(),
                                             self.enable_zip_radio_button.checkState(),
                                             self.enable_thumb_radio_button.checkState(),
                                             self.compress_quality_edit.value())
            self.compresser.signals.finished_signal.connect(self.opimize_finished)
            self.compresser.signals.new_compress_task_started.connect(self.compress_progress_text.setText)
            self.compresser.signals.new_zip_task_started.connect(self.zip_progress_text.setText)
            self.compresser.signals.new_thumb_task_started.connect(self.thumb_progress_text.setText)
            self.compresser.signals.compress_done.connect(self.add_progress_compress)
            self.compresser.signals.zip_done.connect(self.add_progress_zip)
            self.compresser.signals.thumb_done.connect(self.add_progress_thumb)
            self.thread_pool.start(self.compresser)

    def stop_optimize(self):
        """
        Stop the optimisation thread
        :return:
        """
        self.compresser.stop()

    def reset_progress_scan(self):
        """
        reset the scan progress bar and text to default values
        if available, set the max value for the progress bar to the number of directories
        :return:
        """
        self.scan_progress_text.setText("Scan")
        self.scan_progress_bar.setMinimum(0)
        if len(self.get_dir_list()) != 0:
            self.scan_progress_bar.setMaximum(len(self.get_dir_list()))
        else:
            self.scan_progress_bar.setMaximum(100)
        self.scan_progress_bar.setValue(0)

    def reset_progress_compress(self):
        """
        reset the compress progress bar and text to default values
        if available, set the max value for the progress bar to the number of images
        :return:
        """
        self.compress_progress_text.setText("Compression")
        self.compress_progress_bar.setMinimum(0)
        if len(self.image_list) != 0:
            self.compress_progress_bar.setMaximum(len(self.image_list))
        else:
            self.compress_progress_bar.setMaximum(100)
        self.compress_progress_bar.setValue(0)

    def reset_progress_zip(self):
        """
        reset the zip progress bar and text to default values
        if available, set the max value for the progress bar to the number of directories
        :return:
        """
        self.zip_progress_text.setText("Création de .zip")
        self.zip_progress_bar.setMinimum(0)
        if len(self.get_dir_list()) != 0:
            self.zip_progress_bar.setMaximum(len(self.get_dir_list()))
        else:
            self.zip_progress_bar.setMaximum(100)
        self.zip_progress_bar.setValue(0)

    def reset_progress_thumb(self):
        """
        reset the thumb progress bar and text to default values
        if available, set the max value for the progress bar to the number of images
        :return:
        """
        self.thumb_progress_text.setText("Création de miniatures")
        self.thumb_progress_bar.setMinimum(0)
        if len(self.image_list) != 0:
            self.thumb_progress_bar.setMaximum(len(self.image_list))
        else:
            self.thumb_progress_bar.setMaximum(100)
        self.thumb_progress_bar.setValue(0)

    def add_progress_scan(self):
        """
        increment the scan progress bar by one
        :return:
        """
        self.scan_progress_bar.setValue(self.scan_progress_bar.value() + 1)

    def add_progress_compress(self):
        """
        increment the compress progress bar by one
        :return:
        """
        self.compress_progress_bar.setValue(self.compress_progress_bar.value() + 1)

    def add_progress_zip(self):
        """
        increment the zip progress bar by one
        :return:
        """
        self.zip_progress_bar.setValue(self.zip_progress_bar.value() + 1)

    def add_progress_thumb(self):
        """
        increment the thumb progress bar by one
        :return:
        """
        self.thumb_progress_bar.setValue(self.thumb_progress_bar.value() + 1)

    def opimize_finished(self):
        """
        Display a recap telling the user whether the optimisation process finished properly or was canceled
        Also re-enables the UI
        :return:
        """
        self.set_ui_enabled(True, False)
        if self.compresser.is_aborted():
            QMessageBox.warning(self, "Annulé", "Compression stoppée")
        else:
            QMessageBox.information(self, "Terminé", "Compression terminée")

    def open_dir(self):
        """
        Open the parent directory selection dialog
        :return:
        """
        dialog = create_file_dialog()
        dialog.selectFile(self.dir_path_line_edit.text())
        if dialog.exec_():
            self.dir_path_line_edit.setText(dialog.selectedFiles()[0])

    def open_thumb_dir(self):
        """
        open the thumbnail parent directory diaog
        :return:
        """
        dialog = create_file_dialog()
        dialog.selectFile(self.dir_thumb_path_line_edit.text())
        if dialog.exec_():
            self.dir_thumb_path_line_edit.setText(dialog.selectedFiles()[0])


class HelpDialog(QDialog):
    """
    help window showing information about thee app
    """
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.resize(300, 100)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        title = QLabel("Compression de photos")
        font = title.font()
        font.setBold(True)
        font.setPixelSize(20)
        title.setFont(font)
        title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tabs.addTab(self.tab1, "À Propos")
        self.tabs.addTab(self.tab2, "Librairies")
        self.create_about_tab()
        self.create_libs_tab()
        self.main_layout.addWidget(self.tabs)

    def create_about_tab(self):
        """
        create a tab showing information about the author and link
        :return:
        """
        self.tab1.layout = QVBoxLayout(self)
        author = QLabel("(c) 2018 Arnaud VERGNET")
        author.setAlignment(Qt.AlignCenter)
        self.tab1.layout.addWidget(author)

        github = QLabel("Disponible sur GitHub sous license GPLv3")
        github.setAlignment(Qt.AlignCenter)
        self.tab1.layout.addWidget(github)

        gh_link = QLabel()
        gh_link.setOpenExternalLinks(True)
        gh_link.setText("<a href='https://github.com/Keplyx/image-gallery-optimizer'>https://github.com/Keplyx/image-gallery-optimizer</a>")
        gh_link.setAlignment(Qt.AlignCenter)
        self.tab1.layout.addWidget(gh_link)
        self.tab1.setLayout(self.tab1.layout)

    def create_libs_tab(self):
        """
        create a tab showing the libraries used in the app
        :return:
        """
        self.tab2.layout = QVBoxLayout(self)
        text = QLabel("Qt5\npython3 avec PyQt5\nIcons8 pour les icônes")
        text.setAlignment(Qt.AlignCenter)
        self.tab2.layout.addWidget(text)
        self.tab2.setLayout(self.tab2.layout)

    @pyqtSlot()
    def on_click(self):
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
