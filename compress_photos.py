#!/usr/bin/python3
import os
import sys

from PyQt5.QtCore import QThreadPool, Qt, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, QDesktopWidget, QWidget, QFrame, QLineEdit, QListWidget, QVBoxLayout, \
    QLabel, QPushButton, QGridLayout, QMessageBox, QFileDialog, QDialog, QTabWidget, QApplication, QCheckBox, \
    QProgressBar

from compresser import Compresser
from scanner import Scanner
from utils import create_file_dialog


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.resize(1000, 600)
        self.center()
        self.main_widget = MainWidgets()
        self.setCentralWidget(self.main_widget)
        self.create_menu_bar()
        self.setWindowTitle('Compression de Photos')
        self.setWindowIcon(QIcon('icon.png'))

    def create_menu_bar(self):
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu("Fichier")
        help_menu = main_menu.addMenu("Aide")

        exit_button = QAction('Quitter', self)
        exit_button.setShortcut('Ctrl+Q')
        exit_button.setStatusTip('Quitter le logiciel')
        exit_button.triggered.connect(self.close)
        file_menu.addAction(exit_button)

        about_button = QAction('À Propos', self)
        about_button.setShortcut('Ctrl+H')
        about_button.setStatusTip('Voir les informations du logiciel')
        about_button.triggered.connect(self.display_help_dialog)
        help_menu.addAction(about_button)

    def center(self):
        rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        rectangle.moveCenter(center_point)
        self.move(rectangle.topLeft())

    def display_help_dialog(self):
        dialog = HelpDialog(self)
        dialog.exec_()
        dialog.deleteLater()


class MainWidgets(QWidget):

    def __init__(self):
        super().__init__()
        self.dir_select_group = QFrame()
        self.dir_path_line_edit = QLineEdit(os.path.dirname(__file__))
        self.dir_selection_button = QPushButton("Selectionner")
        self.dir_thumb_path_line_edit = QLineEdit(os.path.dirname(__file__) + "_thumb")
        self.dir_thumb_selection_button = QPushButton("Selectionner")
        self.scan_progress_bar = QProgressBar()
        self.scan_progress_text = QLabel("Scan")
        self.dir_list_group = QFrame()
        self.directories_list = QListWidget()
        self.scan_button = QPushButton("Scanner")
        self.stop_scan_button = QPushButton("Stop")
        self.compress_button = QPushButton("Compresser")
        self.stop_compress_button = QPushButton("Stop")
        self.list_title = QLabel("0 images dans 0 dossiers :")
        self.delete_button = QPushButton("Enlever sélectionné")
        self.enable_zip_radio_button = QCheckBox("Créer .zip")
        self.enable_thumb_radio_button = QCheckBox("Créer miniatures")
        self.enable_compress_radio_button = QCheckBox("Compresser photos")
        self.compress_progress_bar = QProgressBar()
        self.compress_progress_text = QLabel("Compression")
        self.zip_progress_bar = QProgressBar()
        self.zip_progress_text = QLabel("Création de .zip")
        self.thumb_progress_bar = QProgressBar()
        self.thumb_progress_text = QLabel("Création de miniatures")
        self.image_list = []
        self.main_layout = QGridLayout()
        self.scanner = Scanner("")
        self.compresser = Compresser([], [], "", "", True, True, True)
        self.thread_pool = QThreadPool()
        self.init_ui()

    def init_ui(self):
        self.setLayout(self.main_layout)

        subtitle = QLabel("Cet utilitaire permet de créer un fichier compressé des images du dossier sélectionné (et "
                          "tout ses sous dossiers)\nainsi que la miniatures de images présentes")
        subtitle.setAlignment(Qt.AlignCenter)

        y = 0
        self.main_layout.addWidget(subtitle, y, 0, 1, 20)
        y += 1
        self.main_layout.addWidget(QLabel("Dossier parent :"), y, 0, 1, 1)
        self.dir_path_line_edit.textChanged.connect(self.directories_list.clear)
        self.main_layout.addWidget(self.dir_path_line_edit, y, 1, 1, 18)
        self.dir_selection_button.clicked.connect(self.open_dir)
        self.main_layout.addWidget(self.dir_selection_button, y, 19, 1, 1)

        y += 1
        self.main_layout.addWidget(QLabel("Dossier miniatures :"), y, 0, 1, 1)
        self.dir_thumb_path_line_edit.textChanged.connect(self.directories_list.clear)
        self.main_layout.addWidget(self.dir_thumb_path_line_edit, y, 1, 1, 18)
        self.dir_thumb_selection_button.clicked.connect(self.open_thumb_dir)
        self.main_layout.addWidget(self.dir_thumb_selection_button, y, 19, 1, 1)

        y += 1
        self.scan_button.clicked.connect(self.scan_click)
        self.main_layout.addWidget(self.scan_button, y, 5, 1, 10)
        self.stop_scan_button.clicked.connect(self.stop_scan)
        self.stop_scan_button.setEnabled(False)
        self.main_layout.addWidget(self.stop_scan_button, y, 15, 1, 1)

        y += 1
        self.main_layout.addWidget(self.scan_progress_text, y, 0, 1, 20)
        self.scan_progress_bar.setTextVisible(False)

        y += 1
        self.main_layout.addWidget(self.scan_progress_bar, y, 0, 1, 20)

        y += 1
        self.main_layout.addWidget(self.list_title, y, 0, 1, 20)

        y += 1
        self.main_layout.addWidget(self.directories_list, y, 0, 10, 19)
        self.delete_button.clicked.connect(self.dir_list_delete_selected)
        self.main_layout.addWidget(self.delete_button, y, 19, 1, 1)

        y += 1
        self.enable_compress_radio_button.toggled.connect(self.set_compress_enabled)
        self.enable_compress_radio_button.setChecked(True)
        self.main_layout.addWidget(self.enable_compress_radio_button, y, 19, 1, 1)

        y += 1
        self.enable_zip_radio_button.toggled.connect(self.set_zip_enabled)
        self.enable_zip_radio_button.setChecked(True)
        self.main_layout.addWidget(self.enable_zip_radio_button, y, 19, 1, 1)

        y += 1
        self.enable_thumb_radio_button.toggled.connect(self.set_thumb_enabled)
        self.enable_thumb_radio_button.setChecked(True)
        self.main_layout.addWidget(self.enable_thumb_radio_button, y, 19, 1, 1)

        y += 7
        self.compress_button.clicked.connect(self.compress_click)
        self.main_layout.addWidget(self.compress_button, y, 5, 1, 10)
        self.stop_compress_button.clicked.connect(self.stop_compress)
        self.stop_compress_button.setEnabled(False)
        self.main_layout.addWidget(self.stop_compress_button, y, 15, 1, 1)

        y += 1
        self.main_layout.addWidget(self.compress_progress_text, y, 0, 1, 20)

        y += 1
        self.compress_progress_bar.setTextVisible(False)
        self.main_layout.addWidget(self.compress_progress_bar, y, 0, 1, 20)

        y += 1
        self.main_layout.addWidget(self.zip_progress_text, y, 0, 1, 20)

        y += 1
        self.zip_progress_bar.setTextVisible(False)
        self.main_layout.addWidget(self.zip_progress_bar, y, 0, 1, 20)

        y += 1
        self.main_layout.addWidget(self.thumb_progress_text, y, 0, 1, 20)

        y += 1
        self.thumb_progress_bar.setTextVisible(False)
        self.main_layout.addWidget(self.thumb_progress_bar, y, 0, 1, 20)

    def dir_list_delete_selected(self):
        for selected_item in self.directories_list.selectedItems():
            self.directories_list.takeItem(self.directories_list.row(selected_item))

    def get_dir_list(self):
        items = []
        for index in range(self.directories_list.count()):
            items.append(self.directories_list.item(index).text())
        return items

    def set_compress_enabled(self, enabled):
        self.compress_progress_bar.setHidden(not enabled)
        self.compress_progress_text.setEnabled(enabled)

    def set_zip_enabled(self, enabled):
        self.zip_progress_bar.setHidden(not enabled)
        self.zip_progress_text.setEnabled(enabled)

    def set_thumb_enabled(self, enabled):
        self.thumb_progress_bar.setHidden(not enabled)
        self.thumb_progress_text.setEnabled(enabled)

    def set_ui_enabled(self, enabled, is_scan):
        self.dir_path_line_edit.setEnabled(enabled)
        self.dir_thumb_path_line_edit.setEnabled(enabled)
        self.stop_compress_button.setEnabled(enabled)
        self.stop_scan_button.setEnabled(enabled)
        self.compress_button.setEnabled(enabled)
        self.scan_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)
        self.enable_zip_radio_button.setEnabled(enabled)
        self.enable_compress_radio_button.setEnabled(enabled)
        self.enable_thumb_radio_button.setEnabled(enabled)
        self.dir_selection_button.setEnabled(enabled)
        self.dir_thumb_selection_button.setEnabled(enabled)
        self.stop_scan_button.setEnabled((not enabled) and is_scan)
        self.stop_compress_button.setEnabled((not enabled) and (not is_scan))

    def scan_click(self):
        self.directories_list.clear()
        # Start scan thread
        self.set_ui_enabled(False, True)
        self.scanner = Scanner(self.dir_path_line_edit.text())
        self.scanner.signals.scanned_dir_signal.connect(self.add_dir_to_list)
        self.scanner.signals.scan_finished_signal.connect(self.scan_finished)
        self.scanner.signals.scanned_dir_finished.connect(self.reset_progress_scan)
        self.scanner.signals.scanned_images_signal.connect(self.add_progress_scan)
        self.scanner.signals.new_scan_task_started.connect(self.scan_progress_text.setText)
        self.thread_pool.start(self.scanner)

    def stop_scan(self):
        self.scanner.stop()

    def add_dir_to_list(self, directory):
        self.directories_list.addItem(directory)

    def scan_finished(self, dir_list, image_list):
        self.set_ui_enabled(True, True)
        self.image_list = image_list
        self.list_title.setText(
            str(len(self.image_list)) + " images dans " + str(len(self.get_dir_list())) + " dossiers :")
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

    def compress_click(self):
        if self.directories_list.count() == 0:
            QMessageBox.warning(self, "Erreur", "Aucun dossier trouvé\nVeuillez vérifier le dossier parent")
        elif (not self.enable_compress_radio_button.checkState()) and (not self.enable_zip_radio_button.checkState()) \
                and (not self.enable_thumb_radio_button.checkState()):
            QMessageBox.warning(self, "Erreur", "Aucune action sélectionnée")
        else:
            self.show_confirmation_dialog()

    def show_confirmation_dialog(self):
        msg = str(len(self.get_dir_list())) + " dossiers contenant " + str(len(self.image_list)) + \
              " images selectionnés\n\nActions à réaliser :"
        if self.enable_compress_radio_button.checkState():
            msg += "\nCompression des images"
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
            self.compresser = Compresser(self.get_dir_list(), self.image_list, self.dir_path_line_edit.text(),
                                         self.dir_thumb_path_line_edit.text(),
                                         self.enable_compress_radio_button.checkState(),
                                         self.enable_zip_radio_button.checkState(),
                                         self.enable_thumb_radio_button.checkState())
            self.compresser.signals.finished_signal.connect(self.compress_finished)
            self.compresser.signals.new_compress_task_started.connect(self.compress_progress_text.setText)
            self.compresser.signals.new_zip_task_started.connect(self.zip_progress_text.setText)
            self.compresser.signals.new_thumb_task_started.connect(self.thumb_progress_text.setText)
            self.compresser.signals.compress_done.connect(self.add_progress_compress)
            self.compresser.signals.zip_done.connect(self.add_progress_zip)
            self.compresser.signals.thumb_done.connect(self.add_progress_thumb)
            self.thread_pool.start(self.compresser)

    def stop_compress(self):
        self.compresser.stop()

    def reset_progress_scan(self):
        self.scan_progress_text.setText("Scan")
        self.scan_progress_bar.setMinimum(0)
        self.scan_progress_bar.setMaximum(len(self.get_dir_list()))
        self.scan_progress_bar.setValue(0)

    def reset_progress_compress(self):
        self.compress_progress_text.setText("Compression")
        self.compress_progress_bar.setMinimum(0)
        self.compress_progress_bar.setMaximum(len(self.image_list))
        self.compress_progress_bar.setValue(0)

    def reset_progress_zip(self):
        self.zip_progress_text.setText("Création de .zip")
        self.zip_progress_bar.setMinimum(0)
        self.zip_progress_bar.setMaximum(len(self.get_dir_list()))
        self.zip_progress_bar.setValue(0)

    def reset_progress_thumb(self):
        self.thumb_progress_text.setText("Création de miniatures")
        self.thumb_progress_bar.setMinimum(0)
        self.thumb_progress_bar.setMaximum(len(self.image_list))
        self.thumb_progress_bar.setValue(0)

    def add_progress_scan(self):
        self.scan_progress_bar.setValue(self.scan_progress_bar.value() + 1)

    def add_progress_compress(self):
        self.compress_progress_bar.setValue(self.compress_progress_bar.value() + 1)

    def add_progress_zip(self):
        self.zip_progress_bar.setValue(self.zip_progress_bar.value() + 1)

    def add_progress_thumb(self):
        self.thumb_progress_bar.setValue(self.thumb_progress_bar.value() + 1)

    def compress_finished(self):
        self.set_ui_enabled(True, False)
        if self.compresser.is_aborted():
            QMessageBox.warning(self, "Annulé", "Compression stoppée")
        else:
            QMessageBox.information(self, "Terminé", "Compression terminée")

    def open_dir(self):
        dialog = create_file_dialog()
        dialog.selectFile(self.dir_path_line_edit.text())
        if dialog.exec_():
            self.dir_path_line_edit.setText(dialog.selectedFiles()[0])

    def open_thumb_dir(self):
        dialog = create_file_dialog()
        dialog.selectFile(self.dir_thumb_path_line_edit.text())
        if dialog.exec_():
            self.dir_thumb_path_line_edit.setText(dialog.selectedFiles()[0])


class HelpDialog(QDialog):
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
        self.tab1.layout = QVBoxLayout(self)
        author = QLabel("(c) 2018 Arnaud VERGNET")
        author.setAlignment(Qt.AlignCenter)
        self.tab1.layout.addWidget(author)

        github = QLabel("Disponible sur GitHub sous license GPLv3")
        github.setAlignment(Qt.AlignCenter)
        self.tab1.layout.addWidget(github)

        gh_link = QLabel()
        gh_link.setOpenExternalLinks(True)
        gh_link.setText("<a href='https://github.com/Keplyx'>https://github.com/Keplyx</a>")
        gh_link.setAlignment(Qt.AlignCenter)
        self.tab1.layout.addWidget(gh_link)
        self.tab1.setLayout(self.tab1.layout)

    def create_libs_tab(self):
        self.tab2.layout = QVBoxLayout(self)
        qt_lib = QLabel("Qt5")
        qt_lib.setAlignment(Qt.AlignCenter)
        self.tab2.layout.addWidget(qt_lib)

        python_lib = QLabel("python3 avec PyQt5")
        python_lib.setAlignment(Qt.AlignCenter)
        self.tab2.layout.addWidget(python_lib)

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
