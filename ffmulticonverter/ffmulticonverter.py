# Copyright (C) 2011-2015 Ilias Stamatis <stamatis.iliass@gmail.com>
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

from PyQt4.QtCore import (
        PYQT_VERSION_STR, QCoreApplication, QLocale, QSettings,
        Qt, QTimer, QTranslator, QT_VERSION_STR
        )
from PyQt4.QtGui import (
        QAbstractItemView, QApplication, QCheckBox, QFileDialog, QIcon,
        QKeySequence, QLabel, QLineEdit, QMainWindow, QMessageBox,
        QPushButton, QShortcut, QTabWidget, QToolButton, QWidget
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
                self.tr('Open a file'), self.add_files
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

        self.filesList.dropped.connect(self.add_files_dropped)
        addQPB.clicked.connect(self.add_files)
        delQPB.clicked.connect(self.delete_files)
        clearQPB.clicked.connect(self.clear_fileslist)
        self.tabWidget.currentChanged.connect(
                lambda: self.tabs[0].moreQPB.setChecked(False))
        self.origQCB.toggled.connect(
                lambda: self.toQLE.setEnabled(not self.origQCB.isChecked()))
        self.toQTB.clicked.connect(self.open_dir)
        convertQPB.clicked.connect(convertAction.triggered)

        del_shortcut = QShortcut(self)
        del_shortcut.setKey(Qt.Key_Delete)
        del_shortcut.activated.connect(self.delete_files)

        self.setWindowTitle('FF Multi Converter')

        QTimer.singleShot(0, self.check_for_dependencies)
        QTimer.singleShot(0, self.load_settings)
        QTimer.singleShot(0, self.audiovideo_tab.set_default_command)
        QTimer.singleShot(0, self.image_tab.set_default_command)
        QTimer.singleShot(0, self.update_filesList)

    def parse_cla(self):
        """Parse command line arguments."""
        for i in QCoreApplication.argv()[1:]:
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
        self.vidconverter = None
        if utils.is_installed('ffmpeg'):
            self.vidconverter = 'ffmpeg'
        elif utils.is_installed('avconv'):
            self.vidconverter = 'avconv'
        self.unoconv = utils.is_installed('unoconv')
        self.imagemagick = utils.is_installed('convert')

        missing = []
        if self.vidconverter is None:
            missing.append('ffmpeg/avconv')
        if not self.unoconv:
            missing.append('unoconv')
        if not self.imagemagick:
            missing.append('imagemagick')

        if missing:
            missing = ', '.join(missing)
            status = self.tr('Missing dependencies:') + ' ' + missing
            self.dependenciesQL.setText(status)

    def load_settings(self, onstart=True):
        """
        Load settings values.

        onstart -- True means that this is the first time the method called,
                   usually when program beggins
        """
        def get_str_value(settings, name):
            value = settings.value(name)
            if value is not None:
                return value
            return ''

        settings = QSettings()
        self.overwrite_existing = utils.str_to_bool(
                get_str_value(settings, 'overwrite_existing'))
        self.default_output = get_str_value(settings, 'default_output')
        self.prefix = get_str_value(settings, 'prefix')
        self.suffix = get_str_value(settings, 'suffix')
        defcmd = get_str_value(settings, 'default_command')
        extraformats_video = get_str_value(settings, 'extraformats')
        videocodecs = settings.value('videocodecs')
        audiocodecs = settings.value('audiocodecs')
        defcmd_image = get_str_value(settings, 'default_command_image')
        extraformats_image = get_str_value(settings, 'extraformats_image')

        if videocodecs is None:
            videocodecs = "\n".join(config.video_codecs)
            settings.setValue('videocodecs', videocodecs)
        if audiocodecs is None:
            audiocodecs = "\n".join(config.audio_codecs)
            settings.setValue('audiocodecs', audiocodecs)

        if defcmd:
            self.default_command = defcmd
        else:
            self.default_command = config.default_ffmpeg_cmd
        if defcmd_image:
            self.default_command_image = defcmd_image
        else:
            self.default_command_image = config.default_imagemagick_cmd

        self.audiovideo_tab.fill_video_comboboxes(
                videocodecs, audiocodecs, extraformats_video)
        self.image_tab.fill_extension_combobox(extraformats_image)

        if onstart:
            self.toQLE.setText(self.default_output)

    def current_tab(self):
        """Return the corresponding object of the selected tab."""
        for i in self.tabs:
            if self.tabs.index(i) == self.tabWidget.currentIndex():
                return i

    def update_filesList(self):
        """Clear self.filesList and add to it all items of self.fname."""
        self.filesList.clear()
        for i in self.fnames:
            self.filesList.addItem(i)

    def add_files(self):
        """
        Get file names using a standard Qt dialog.
        Append to self.fnames each file name that not already exists
        and update self.filesList.
        """
        # Create lists holding file formats extension.
        # To be passed in QFileDialog.getOpenFileNames().
        all_files = '*'
        audiovideo_files = ' '.join(
                ['*.'+i for i in self.audiovideo_tab.formats])
        img_formats = self.image_tab.formats[:]
        img_formats.extend(self.image_tab.extra_img)
        image_files = ' '.join(['*.'+i for i in img_formats])
        document_files = ' '.join(['*.'+i for i in self.document_tab.formats])
        formats = [all_files, audiovideo_files, image_files, document_files]
        strings = [self.tr('All Files'), self.tr('Audio/Video Files'),
                   self.tr('Image Files'), self.tr('Document Files')]

        filters = ''
        for string, extensions in zip(strings, formats):
            filters += string + ' ({0});;'.format(extensions)
        filters = filters[:-2] # remove last ';;'

        fnames = QFileDialog.getOpenFileNames(self, 'FF Multi Converter - ' +
                self.tr('Choose File'), config.home, filters)

        if fnames:
            for i in fnames:
                if not i in self.fnames:
                    self.fnames.append(i)
            self.update_filesList()

    def add_files_dropped(self, links):
        """
        Append to self.fnames each file name that not already exists
        and update self.filesList.
        """
        for path in links:
            if os.path.isfile(path) and not path in self.fnames:
                self.fnames.append(path)
        self.update_filesList()

    def delete_files(self):
        """
        Get selectedItems of self.filesList, remove them from self.fnames and
        update the filesList.
        """
        items = self.filesList.selectedItems()
        if items:
            for i in items:
                self.fnames.remove(i.text())
            self.update_filesList()

    def clear_fileslist(self):
        """Make self.fnames empty and update self.filesList."""
        self.fnames = []
        self.update_filesList()

    def clear_all(self):
        """Clear all values of graphical widgets."""
        self.toQLE.clear()
        self.origQCB.setChecked(False)
        self.deleteQCB.setChecked(False)
        self.clear_fileslist()

        self.audiovideo_tab.clear()
        self.image_tab.clear()

    def open_dir(self):
        """
        Get a directory name using a standard QtDialog and update
        self.toQLE with dir's name.
        """
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
            if not self.current_tab().ok_to_continue():
                return False
            return True

        except ValidationError as e:
            QMessageBox.warning(
                    self, 'FF Multi Converter - ' + self.tr('Error!'), str(e))
            return False

    def get_output_extension(self):
        """Extract the desired output file extension from GUI and return it."""
        tab = self.current_tab()
        if tab.name == 'AudioVideo':
            ext_to = self.audiovideo_tab.extQCB.currentText()
        elif tab.name == 'Images':
            ext_to = tab.extQCB.currentText()
        else:
            ext_to = tab.convertQCB.currentText().split()[-1]

        return '.' + ext_to

    def start_conversion(self):
        """
        Extract the appropriate information from GUI and call the
        Progress dialog with the suitable argumens.
        """
        if not self.ok_to_continue():
            return

        tab = self.current_tab()
        if tab.name == 'Documents' and not self.office_listener_started:
            utils.start_office_listener()
            self.office_listener_started = True

        ext_to = self.get_output_extension()
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
            self.load_settings(onstart=False)

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
                 <p>Copyright &copy; 2011-2015 {3}
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
