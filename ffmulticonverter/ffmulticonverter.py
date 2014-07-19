# Copyright (C) 2011-2014 Ilias Stamatis <stamatis.iliass@gmail.com>
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
import logging
import textwrap

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

        # main window dimensions
        self.main_width = 780
        self.main_height = 510
        self.main_fixed_height = 684
        self.default_command = config.default_ffmpeg_cmd

        self.fnames = list()  # list of file names to be converted
        self.docconv = False  # True when a documents conversion is running

        self.parse_cla()

        addButton = QPushButton(self.tr('Add'))
        delButton = QPushButton(self.tr('Delete'))
        clearButton = QPushButton(self.tr('Clear'))
        vlayout1 = utils.add_to_layout(
                'v', addButton, delButton, clearButton, None)

        self.filesList = utils.FilesList()
        self.filesList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        hlayout1 = utils.add_to_layout('h', self.filesList, vlayout1)

        output_label = QLabel(self.tr('Output folder:'))
        toLineEdit = QLineEdit()
        toLineEdit.setReadOnly(True)
        toToolButton = QToolButton()
        toToolButton.setText('...')
        hlayout2 = utils.add_to_layout(
                'h', output_label, toLineEdit, toToolButton)

        self.audiovideo_tab = AudioVideoTab(self)
        self.image_tab = ImageTab(self)
        self.document_tab = DocumentTab(self)

        self.tabs = [self.audiovideo_tab, self.image_tab, self.document_tab]
        tab_names = [self.tr('Audio/Video'), self.tr('Images'),
                     self.tr('Documents')]

        tabWidget = QTabWidget()
        for num, tab in enumerate(tab_names):
            tabWidget.addTab(self.tabs[num], tab)
        tabWidget.setCurrentIndex(0)

        origCheckBox = QCheckBox(
                self.tr('Save each file in the same\nfolder as input file'))
        deleteCheckBox = QCheckBox(self.tr('Delete original'))
        convertPushButton = QPushButton(self.tr('&Convert'))

        hlayout3 = utils.add_to_layout('h', origCheckBox, deleteCheckBox, None)
        hlayout4 = utils.add_to_layout('h', None, convertPushButton)
        final_layout = utils.add_to_layout(
                'v', hlayout1, tabWidget, hlayout2, hlayout3, hlayout4)

        dependenciesLabel = QLabel()
        self.statusBar().addPermanentWidget(dependenciesLabel, stretch=1)

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
                self.tr('Edit Presets'), self.presets
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
                None, self.tr('Preferences'), self.preferences
                )
        aboutAction = utils.create_action(
                self, self.tr('About'), 'Ctrl+?', None,
                self.tr('About'), self.about
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
        utils.add_actions(helpMenu, [aboutAction])

        self.filesList.dropped.connect(self.url_dropped)
        addButton.clicked.connect(self.add_files)
        delButton.clicked.connect(self.delete_files)
        clearButton.clicked.connect(self.clear_fileslist)
        tabWidget.currentChanged.connect(
                lambda: self.tabs[0].moreButton.setChecked(False))
        origCheckBox.clicked.connect(
                lambda: toLineEdit.setEnabled(not origCheckBox.isChecked()))
        toToolButton.clicked.connect(self.open_dir)
        convertPushButton.clicked.connect(convertAction.triggered)

        del_shortcut = QShortcut(self)
        del_shortcut.setKey(Qt.Key_Delete)
        del_shortcut.activated.connect(self.delete_files)

        # aliasing
        self.toLineEdit = toLineEdit
        self.toToolButton = toToolButton
        self.tabWidget = tabWidget
        self.origCheckBox = origCheckBox
        self.deleteCheckBox = deleteCheckBox
        self.convertPushButton = convertPushButton
        self.dependenciesLabel = dependenciesLabel

        self.resize(self.main_width, self.main_height)
        self.setWindowTitle('FF Multi Converter')

        QTimer.singleShot(0, self.check_for_dependencies)
        QTimer.singleShot(0, self.load_settings)
        QTimer.singleShot(0, self.audiovideo_tab.set_default_command)
        QTimer.singleShot(0, self.update_filesList)

    def parse_cla(self):
        """Parse command line arguments."""
        for i in QCoreApplication.argv()[1:]:
            i = os.path.abspath(i)
            if os.path.isfile(i):
                self.fnames.append(i)
            else:
                print("ffmulticonverter: {0}: Not a file".format(i))

    def load_settings(self):
        """Load settings values."""
        def get_str_value(settings, name):
            value = settings.value(name)
            if value is not None:
                return value
            return ''

        settings = QSettings()
        self.overwrite_existing = utils.str_to_bool(
                get_str_value(settings, 'overwrite_existing'))
        self.avconv_prefered = utils.str_to_bool(
                get_str_value(settings, 'avconv_prefered'))
        self.default_output = get_str_value(settings, 'default_output')
        self.prefix = get_str_value(settings, 'prefix')
        self.suffix = get_str_value(settings, 'suffix')
        defcmd = get_str_value(settings, 'default_command')
        videocodecs = get_str_value(settings, 'videocodecs')
        videocodecs = [i for i in videocodecs.split("\n")]
        audiocodecs = get_str_value(settings, 'audiocodecs')
        audiocodecs = [i for i in audiocodecs.split("\n")]

        if defcmd:
            self.default_command = defcmd

        self.toLineEdit.setText(self.default_output)
        self.audiovideo_tab.fill_codecs_comboboxes(videocodecs, audiocodecs)

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

    def url_dropped(self, links):
        """
        Append to self.fnames each file name that not already exists
        and update self.filesList.
        """
        for url in links:
            if os.path.isfile(url) and not url in self.fnames:
                self.fnames.append(url)
        self.update_filesList()

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
        self.toLineEdit.clear()
        self.origCheckBox.setChecked(False)
        self.deleteCheckBox.setChecked(False)
        self.clear_fileslist()

        self.audiovideo_tab.clear()
        self.image_tab.clear()

    def open_dir(self):
        """
        Get a directory name using a standard QtDialog and update
        self.toLineEdit with dir's name.
        """
        if self.toLineEdit.isEnabled():
            output = QFileDialog.getExistingDirectory(
                    self, 'FF Multi Converter - ' +
                    self.tr('Choose output destination'),
                    config.home)
            if output:
                self.toLineEdit.setText(output)

    def preferences(self):
        """Open the preferences dialog."""
        dialog = preferences_dlg.Preferences(self)
        if dialog.exec_():
            self.load_settings()

    def presets(self):
        """Open the presets dialog."""
        dialog = presets_dlgs.ShowPresets(self)
        dialog.exec_()

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
            elif not self.origCheckBox.isChecked() and not self.toLineEdit.text():
                raise ValidationError(
                        self.tr('You must choose an output folder!'))
            elif (not self.origCheckBox.isChecked() and
                  not os.path.exists(self.toLineEdit.text())):
                raise ValidationError(self.tr('Output folder does not exists!'))
            if not self.current_tab().ok_to_continue():
                return False
            return True

        except ValidationError as e:
            QMessageBox.warning(
                    self, 'FF Multi Converter - ' + self.tr('Error!'), str(e))
            return False

    def output_ext(self):
        """Extract the desired output file extension from GUI and return it."""
        tab = self.current_tab()
        if tab.name == 'AudioVideo':
            if self.audiovideo_tab.extLineEdit.isEnabled():
                ext_to = self.audiovideo_tab.extLineEdit.text()
            else:
                ext_to = self.audiovideo_tab.extComboBox.currentText()
        elif tab.name == 'Images':
            ext_to = tab.extComboBox.currentText()
        else:
            ext_to = tab.convertComboBox.currentText().split()[-1]

        return '.' + ext_to

    def start_conversion(self):
        """
        Extract the appropriate information from GUI and call the
        Progress dialog with the suitable argumens.
        """
        if not self.ok_to_continue():
            return

        ext_to = self.output_ext()
        _list = utils.create_paths_list(
                self.fnames, ext_to, self.prefix, self.suffix,
                self.toLineEdit.text(), self.origCheckBox.isChecked(),
                self.overwrite_existing
                )

        tab = self.current_tab()
        cmd = ''
        size = ''
        mntaspect = False
        imgcmd = ''

        if tab.name == 'AudioVideo':
            cmd = tab.commandLineEdit.text()
        elif tab.name == 'Images':
            width = tab.widthLineEdit.text()
            if width:
                height = tab.heightLineEdit.text()
                size = '{0}x{1}'.format(width, height)
                mntaspect = tab.imgaspectCheckBox.isChecked()
            imgcmd = tab.commandLineEdit.text()
        else:
            self.docconv = True

        dialog = progress.Progress(
                _list, tab.name, cmd, not self.avconv_prefered, size, mntaspect,
                imgcmd, self.deleteCheckBox.isChecked(),self
                )
        dialog.show()

    def check_for_dependencies(self):
        """
        Check if each one of the program dependencies are installed and
        update self.dependenciesLabel with the appropriate message.
        """
        self.ffmpeg = utils.is_installed('ffmpeg')
        self.avconv = utils.is_installed('avconv')
        self.unoconv = utils.is_installed('unoconv')
        self.imagemagick = utils.is_installed('convert')

        missing = []
        if not self.ffmpeg and not self.avconv:
            missing.append('ffmpeg/avconv')
        if not self.unoconv:
            missing.append('unoconv')
        if not self.imagemagick:
            missing.append('imagemagick')

        if missing:
            missing = ', '.join(missing)
            status = self.tr('Missing dependencies:') + ' ' + missing
            self.dependenciesLabel.setText(status)

    def about(self):
        """Call the about dialog with the appropriate values."""
        msg = self.tr('Convert among several file types to other extensions')
        msg = textwrap.fill(msg, 54).replace('\n', '<br>')
        text = '''<b> FF Multi Converter {0} </b>
                 <p>{1}
                 <p><a href="{2}">FF Multi Converter - Home Page</a>
                 <p>Copyright &copy; 2011-2014 {3}
                 <br>License: {4}
                 <p>Python {5} - Qt {6} - PyQt {7} on {8}'''\
                 .format(ffmc.__version__, msg, ffmc.__url__, ffmc.__author__,
                         ffmc.__license__, platform.python_version()[:5],
                         QT_VERSION_STR, PYQT_VERSION_STR, platform.system())
        image = ':/ffmulticonverter.png'
        authors = '{0} <{1}>\n\n'.format(ffmc.__author__, ffmc.__author_email__)
        authors += 'Contributors:\nPanagiotis Mavrogiorgos'
        transl_list = [['[bg] Bulgarian', 'Vasil Blagoev'],
                       ['[cs] Czech', 'Petr Simacek'],
                       ['[de_DE] German (Germany)', 'Stefan Wilhelm'],
                       ['[el] Greek', 'Ilias Stamatis'],
                       ['[es] Spanish', 'Miguel Ángel Rodríguez Muíños'],
                       ['[fr] French', 'Rémi Mercier'
                                '\n     Lebarhon'],
                       ['[hu] Hungarian', 'Farkas Norbert'],
                       ['[it] Italian', 'Fabio Boccaletti'],
                       ['[ms_MY] Malay (Malaysia)', 'abuyop'],
                       ['[pl_PL] Polish (Poland)', 'Lukasz Koszy'
                                            '\n     Piotr Surdacki'],
                       ['[pt] Portuguese', 'Sérgio Marques'],
                       ['[pt_BR] Portuguese (Brasil)', 'José Humberto A Melo'],
                       ['[ru] Russian', 'Andrew Lapshin'],
                       ['[tu] Turkish', 'Tayfun Kayha'],
                       ['[vi] Vietnamese', 'Anh Phan'],
                       ['[zh_CN] Chinese (China)', 'Dianjin Wang'],
                       ['[zh_TW] Chinese (Taiwan)', 'Taijuin Lee'],
                      ]
        translators = []
        for i in transl_list:
            translators.append('{0}\n     {1}'.format(i[0], i[1]))
        translators = '\n\n'.join(translators)

        dialog = about_dlg.AboutDialog(text, image, authors, translators, self)
        dialog.exec_()


def main():
    app = QApplication([i.encode('utf-8') for i in sys.argv])
    app.setOrganizationName(ffmc.__name__)
    app.setOrganizationDomain(ffmc.__url__)
    app.setApplicationName('FF Muli Converter')
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
            filename = config.log_file,
            level=logging.DEBUG,
            format='%(asctime)s : %(levelname)s - %(type)s\n'
                   'Command: %(command)s\n'
                   'Return code: %(returncode)s\n%(message)s\n',
            datefmt='%Y-%m-%d %H:%M:%S'
    )

    converter = MainWindow()
    converter.show()
    app.exec_()
