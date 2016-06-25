# Copyright (C) 2011-2016 Ilias Stamatis <stamatis.iliass@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import platform
import textwrap
import logging
import webbrowser

from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import (
        PYQT_VERSION_STR, QCoreApplication, QLocale, QSettings, Qt,
        QTranslator, QT_VERSION_STR
        )
from PyQt5.QtWidgets import (
        QAbstractItemView, QApplication, QCheckBox, QFileDialog, QLabel,
        QLineEdit, QMainWindow, QMessageBox, QPushButton, QShortcut, QTabWidget,
        QToolButton, QWidget
        )

import ffmulticonverter as ffmc
from ffmulticonverter import utils
from ffmulticonverter import config
from ffmulticonverter import about_dlg
from ffmulticonverter import preferences_dlg
from ffmulticonverter import presets_dlgs
from ffmulticonverter import progress
from ffmulticonverter import qrc_resources
from ffmulticonverter.audiovideotab import AudioVideoTab
from ffmulticonverter.imagetab import ImageTab
from ffmulticonverter.documenttab import DocumentTab


class ValidationError(Exception):
    pass


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.fnames = []  # list of file names to be converted
        self.office_listener_started = False

        self.parse_cla()

        addQPB = QPushButton(self.tr('Add'))
        delQPB = QPushButton(self.tr('Delete'))
        clearQPB = QPushButton(self.tr('Clear'))
        vlayout1 = utils.add_to_layout('v', addQPB, delQPB, clearQPB, None)

        self.filesList = utils.FilesList()
        self.filesList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        hlayout1 = utils.add_to_layout('h', self.filesList, vlayout1)

        outputQL = QLabel(self.tr('Output folder:'))
        self.toQLE = QLineEdit()
        self.toQLE.setReadOnly(True)
        self.toQTB = QToolButton()
        self.toQTB.setText('...')
        hlayout2 = utils.add_to_layout('h', outputQL, self.toQLE, self.toQTB)

        self.audiovideo_tab = AudioVideoTab(self)
        self.image_tab = ImageTab(self)
        self.document_tab = DocumentTab(self)

        self.tabs = [self.audiovideo_tab, self.image_tab, self.document_tab]
        tab_names = [self.tr('Audio/Video'), self.tr('Images'),
                     self.tr('Documents')]

        self.tabWidget = QTabWidget()
        for num, tab in enumerate(tab_names):
            self.tabWidget.addTab(self.tabs[num], tab)
        self.tabWidget.setCurrentIndex(0)

        self.origQCB = QCheckBox(
                self.tr('Save each file in the same\nfolder as input file'))
        self.deleteQCB = QCheckBox(self.tr('Delete original'))
        convertQPB = QPushButton(self.tr('&Convert'))

        hlayout3 = utils.add_to_layout('h', self.origQCB, self.deleteQCB, None)
        hlayout4 = utils.add_to_layout('h', None, convertQPB)
        final_layout = utils.add_to_layout(
                'v', hlayout1, self.tabWidget, hlayout2, hlayout3, hlayout4)

        self.dependenciesQL = QLabel()
        self.statusBar().addPermanentWidget(self.dependenciesQL, stretch=1)

        widget = QWidget()
        widget.setLayout(final_layout)
        self.setCentralWidget(widget)

        openAction = utils.create_action(
                self, self.tr('Open'), QKeySequence.Open, None,
                self.tr('Open a file'), self.filesList_add
                )
        convertAction = utils.create_action(
                self, self.tr('Convert'), 'Ctrl+C', None,
                self.tr('Convert files'), self.start_conversion
                )
        quitAction = utils.create_action(
                self, self.tr('Quit'), 'Ctrl+Q', None,
                self.tr('Quit'), self.close
                )
        edit_presetsAction = utils.create_action(
                self, self.tr('Edit Presets'), 'Ctrl+P', None,
                self.tr('Edit Presets'), self.open_dialog_presets
                )
        importAction = utils.create_action(
                self, self.tr('Import'), None, None,
                self.tr('Import presets'), self.import_presets
                )
        exportAction = utils.create_action(
                self, self.tr('Export'), None, None,
                self.tr('Export presets'), self.export_presets
                )
        resetAction = utils.create_action(
                self, self.tr('Reset'), None, None,
                self.tr('Reset presets'), self.reset_presets
                )
        syncAction = utils.create_action(
                self, self.tr('Synchronize'), None, None,
                self.tr('Synchronize presets'), self.sync_presets
                )
        removeoldAction = utils.create_action(
                self, self.tr('Remove old'), None, None,
                self.tr('Remove old presets'), self.removeold_presets
                )
        clearallAction = utils.create_action(
                self, self.tr('Clear All'), None, None,
                self.tr('Clear form'), self.clear_all
                )
        preferencesAction = utils.create_action(
                self, self.tr('Preferences'), 'Alt+Ctrl+P',
                None, self.tr('Preferences'), self.open_dialog_preferences
                )
        trackerAction = utils.create_action(
                self, 'Issue tracker', None, None, None,
                lambda: webbrowser.open(
                    "https://github.com/Ilias95/FF-Multi-Converter/issues")
                )
        wikiAction = utils.create_action(
                self, 'Wiki', None, None, None,
                lambda: webbrowser.open(
                    "https://github.com/Ilias95/FF-Multi-Converter/wiki")
                )
        ffmpegdocAction = utils.create_action(
                self, 'FFmpeg ' + self.tr('documentation'), None, None, None,
                lambda: webbrowser.open(
                    "https://www.ffmpeg.org/documentation.html")
                )
        imagemagickdocAction = utils.create_action(
                self, 'ImageMagick ' + self.tr('documentation'), None, None,
                None, lambda: webbrowser.open(
                    "http://www.imagemagick.org/script/convert.php")
                )
        aboutAction = utils.create_action(
                self, self.tr('About'), 'Ctrl+?', None,
                self.tr('About'), self.open_dialog_about
                )

        fileMenu = self.menuBar().addMenu(self.tr('File'))
        editMenu = self.menuBar().addMenu(self.tr('Edit'))
        presetsMenu = self.menuBar().addMenu(self.tr('Presets'))
        helpMenu = self.menuBar().addMenu(self.tr('Help'))

        utils.add_actions(
                fileMenu, [openAction, convertAction, None, quitAction])
        utils.add_actions(
                presetsMenu,
                [edit_presetsAction, importAction, exportAction, resetAction,
                 None, syncAction, removeoldAction]
                )
        utils.add_actions(editMenu, [clearallAction, None, preferencesAction])
        utils.add_actions(
                helpMenu,
                [trackerAction, wikiAction, None, ffmpegdocAction,
                imagemagickdocAction, None, aboutAction]
                )

        self.filesList.dropped.connect(self.filesList_add_dragged)
        addQPB.clicked.connect(self.filesList_add)
        delQPB.clicked.connect(self.filesList_delete)
        clearQPB.clicked.connect(self.filesList_clear)
        self.tabWidget.currentChanged.connect(
                lambda: self.tabs[0].moreQPB.setChecked(False))
        self.origQCB.toggled.connect(
                lambda: self.toQLE.setEnabled(not self.origQCB.isChecked()))
        self.toQTB.clicked.connect(self.get_output_folder)
        convertQPB.clicked.connect(convertAction.triggered)

        del_shortcut = QShortcut(self)
        del_shortcut.setKey(Qt.Key_Delete)
        del_shortcut.activated.connect(self.filesList_delete)

        self.setWindowTitle('FF Multi Converter')

        self.load_settings()
        self.check_for_dependencies()

        self.audiovideo_tab.set_default_command()
        self.image_tab.set_default_command()
        self.toQLE.setText(self.default_output)

        self.filesList_update()


    def parse_cla(self):
        """Parse command line arguments."""
        for i in QCoreApplication.arguments()[1:]:
            i = os.path.abspath(i)
            if os.path.isfile(i):
                self.fnames.append(i)
            else:
                print("ffmulticonverter: {0}: Not a file".format(i))

    def check_for_dependencies(self):
        """
        Check if each one of the program dependencies are installed and
        update self.dependenciesQL with the appropriate message.
        """
        if not utils.is_installed(self.ffmpeg_path):
            self.ffmpeg_path = utils.is_installed('ffmpeg')
            QSettings().setValue('ffmpeg_path', self.ffmpeg_path)
        self.unoconv = utils.is_installed('unoconv')
        self.imagemagick = utils.is_installed('convert')

        missing = []
        if not self.ffmpeg_path:
            missing.append('ffmpeg')
        if not self.unoconv:
            missing.append('unoconv')
        if not self.imagemagick:
            missing.append('imagemagick')

        if missing:
            missing = ', '.join(missing)
            status = self.tr('Missing dependencies:') + ' ' + missing
            self.dependenciesQL.setText(status)

    def load_settings(self):
        settings = QSettings()

        self.overwrite_existing = settings.value('overwrite_existing', type=bool)
        self.default_output = settings.value('default_output', type=str)
        self.prefix = settings.value('prefix', type=str)
        self.suffix = settings.value('suffix', type=str)
        self.ffmpeg_path = settings.value('ffmpeg_path', type=str)
        self.default_command = (settings.value('default_command', type=str) or
                config.default_ffmpeg_cmd)
        # type=list won't work for some reason
        extraformats_video = (settings.value('extraformats_video') or [])
        videocodecs = (settings.value('videocodecs') or config.video_codecs)
        audiocodecs = (settings.value('audiocodecs') or config.audio_codecs)
        self.default_command_image = (settings.value('default_command_image',
                type=str) or
                config.default_imagemagick_cmd)
        extraformats_image = (settings.value('extraformats_image') or [])
        extraformats_document = (settings.value('extraformats_document') or [])

        self.audiovideo_tab.fill_video_comboboxes(videocodecs,
                audiocodecs, extraformats_video)
        self.image_tab.fill_extension_combobox(extraformats_image)
        self.document_tab.fill_extension_combobox(extraformats_document)

    def get_current_tab(self):
        for i in self.tabs:
            if self.tabs.index(i) == self.tabWidget.currentIndex():
                return i

    def filesList_update(self):
        self.filesList.clear()
        for i in self.fnames:
            self.filesList.addItem(i)

    def filesList_add(self):
        filters  = 'All Files (*);;'
        filters += 'Audio/Video Files (*.{});;'.format(
                ' *.'.join(self.audiovideo_tab.formats))
        filters += 'Image Files (*.{});;'.format(
                ' *.'.join(self.image_tab.formats + self.image_tab.extra_img))
        filters += 'Document Files (*.{})'.format(
                ' *.'.join(self.document_tab.formats))

        fnames = QFileDialog.getOpenFileNames(self, 'FF Multi Converter - ' +
                self.tr('Choose File'), config.home, filters,
                options=QFileDialog.HideNameFilterDetails)[0]

        if fnames:
            for i in fnames:
                if not i in self.fnames:
                    self.fnames.append(i)
            self.filesList_update()

    def filesList_add_dragged(self, links):
        for path in links:
            if os.path.isfile(path) and not path in self.fnames:
                self.fnames.append(path)
        self.filesList_update()

    def filesList_delete(self):
        items = self.filesList.selectedItems()
        if items:
            for i in items:
                self.fnames.remove(i.text())
            self.filesList_update()

    def filesList_clear(self):
        self.fnames = []
        self.filesList_update()

    def clear_all(self):
        """Clears or sets to default the values of all graphical widgets."""
        self.toQLE.clear()
        self.origQCB.setChecked(False)
        self.deleteQCB.setChecked(False)
        self.filesList_clear()

        self.audiovideo_tab.clear()
        self.image_tab.clear()

    def get_output_folder(self):
        if self.toQLE.isEnabled():
            output = QFileDialog.getExistingDirectory(
                    self, 'FF Multi Converter - ' +
                    self.tr('Choose output destination'),
                    config.home)
            if output:
                self.toQLE.setText(output)

    def import_presets(self):
        presets_dlgs.ShowPresets().import_presets()

    def export_presets(self):
        presets_dlgs.ShowPresets().export_presets()

    def reset_presets(self):
        presets_dlgs.ShowPresets().reset()

    def sync_presets(self):
        presets_dlgs.ShowPresets().synchronize()

    def removeold_presets(self):
        presets_dlgs.ShowPresets().remove_old()

    def ok_to_continue(self):
        """
        Check if everything is ok to continue with conversion.

        Check if:
        - At least one file has given for conversion.
        - An output folder has given.
        - Output folder exists.

        Return False if an error arises, else True.
        """
        try:
            if not self.fnames:
                raise ValidationError(
                        self.tr('You must add at least one file to convert!'))
            elif not self.origQCB.isChecked() and not self.toQLE.text():
                raise ValidationError(
                        self.tr('You must choose an output folder!'))
            elif (not self.origQCB.isChecked() and
                  not os.path.exists(self.toQLE.text())):
                raise ValidationError(self.tr('Output folder does not exists!'))
            if not self.get_current_tab().ok_to_continue():
                return False
            return True

        except ValidationError as e:
            QMessageBox.warning(
                    self, 'FF Multi Converter - ' + self.tr('Error!'), str(e))
            return False

    def start_conversion(self):
        """
        Extract the appropriate information from GUI and call the
        Progress dialog with the suitable argumens.
        """
        if not self.ok_to_continue():
            return

        tab = self.get_current_tab()
        ext_to = '.' + tab.extQCB.currentText()

        if tab.name == 'Documents' and not self.office_listener_started:
            utils.start_office_listener()
            self.office_listener_started = True

        _list = utils.create_paths_list(
                self.fnames, ext_to, self.prefix, self.suffix,
                self.toQLE.text(), self.origQCB.isChecked(),
                self.overwrite_existing
                )

        dialog = progress.Progress(
                _list, tab, self.deleteQCB.isChecked(), self)
        dialog.show()

    def open_dialog_preferences(self):
        """Open the preferences dialog."""
        dialog = preferences_dlg.Preferences(self)
        if dialog.exec_():
            self.load_settings()

    def open_dialog_presets(self):
        """Open the presets dialog."""
        dialog = presets_dlgs.ShowPresets(self)
        dialog.exec_()

    def open_dialog_about(self):
        """Call the about dialog with the appropriate values."""
        msg = self.tr('Convert among several file types to other formats')
        msg = textwrap.fill(msg, 54).replace('\n', '<br>')
        text = '''<b> FF Multi Converter {0} </b>
                 <p>{1}
                 <p><a href="{2}">FF Multi Converter - Home Page</a>
                 <p>Copyright &copy; 2011-2016 {3}
                 <br>License: {4}
                 <p>Python {5} - Qt {6} - PyQt {7} on {8}'''\
                 .format(ffmc.__version__, msg, ffmc.__url__, ffmc.__author__,
                         ffmc.__license__, platform.python_version()[:5],
                         QT_VERSION_STR, PYQT_VERSION_STR, platform.system())
        image = ':/ffmulticonverter.png'
        authors = '{0} <{1}>\n\n'.format(ffmc.__author__, ffmc.__author_email__)
        authors += 'Contributors:\nPanagiotis Mavrogiorgos'
        translators = []
        for i in config.translators:
            translators.append('{0}\n     {1}'.format(i[0], i[1]))
        translators = '\n\n'.join(translators)

        dialog = about_dlg.AboutDialog(text, image, authors, translators, self)
        dialog.exec_()


def main():
    app = QApplication([i.encode('utf-8') for i in sys.argv])
    app.setOrganizationName(ffmc.__name__)
    app.setOrganizationDomain(ffmc.__url__)
    app.setApplicationName('FF Multi Converter')
    app.setWindowIcon(QIcon(':/ffmulticonverter.png'))

    locale = QLocale.system().name()
    qtTranslator = QTranslator()
    if qtTranslator.load('qt_' + locale, ':/'):
        app.installTranslator(qtTranslator)
    appTranslator = QTranslator()
    if appTranslator.load('ffmulticonverter_' + locale, ':/'):
        app.installTranslator(appTranslator)

    if not os.path.exists(config.log_dir):
        os.makedirs(config.log_dir)

    logging.basicConfig(
            filename=config.log_file,
            level=logging.DEBUG,
            format=config.log_format,
            datefmt=config.log_dateformat
            )

    converter = MainWindow()
    converter.show()
    app.exec_()
