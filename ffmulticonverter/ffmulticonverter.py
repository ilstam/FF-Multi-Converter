#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011-2013 Ilias Stamatis <stamatis.iliass@gmail.com>
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

from __future__ import unicode_literals
from __future__ import print_function

from __init__ import __version__

from PyQt4.QtCore import (pyqtSignal, PYQT_VERSION_STR, QCoreApplication,
                          QLocale, QRegExp, QSettings, QSize, Qt, QTimer,
                          QTranslator, QT_VERSION_STR)
from PyQt4.QtGui import (QAbstractItemView, QApplication, QButtonGroup,
                         QCheckBox, QComboBox, QFileDialog, QFrame,
                         QHBoxLayout, QIcon, QKeySequence, QLabel, QLineEdit,
                         QListWidget, QMainWindow, QMessageBox, QPushButton,
                         QRadioButton, QRegExpValidator, QShortcut, QSizePolicy,
                         QSpacerItem, QTabWidget, QToolButton, QVBoxLayout,
                         QWidget)

import os
import sys
import re
import platform
import logging
import codecs

import about_dlg
import preferences_dlg
import presets_dlgs
import progress
import pyqttools
import qrc_resources

try:
    import PythonMagick
except ImportError:
    pass


# global variables
MAIN_WIDTH = 700 # main window width
MAIN_HEIGHT = 500
MAIN_FIXED_HEIGHT = 622
DEFAULT_COMMAND = '-ab 320k -ar 48000 -ac 2' # default ffmpeg command


class ValidationError(Exception):
    pass


class FilesList(QListWidget):
    dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super(FilesList, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(unicode(url.toLocalFile()))
            self.dropped.emit(links)
        else:
            event.ignore()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.home = os.getenv('HOME')
        self.fnames = list()  # list of file names to be converted
        self.docconv = False  # True when a documents conversion is running

        # parse command line arguments
        for i in QCoreApplication.argv()[1:]:
            i = codecs.utf_8_decode(os.path.abspath(i))[0]
            if os.path.isfile(i):
                self.fnames.append(i)
            else:
                print("ffmulticonverter: {0}: Not a file".format(i))

        addButton = QPushButton(self.tr('Add'))
        delButton = QPushButton(self.tr('Delete'))
        clearButton = QPushButton(self.tr('Clear'))
        vlayout1 = pyqttools.add_to_layout(QVBoxLayout(), addButton, delButton,
                                           clearButton, None)

        self.filesList = FilesList()
        self.filesList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        hlayout1 = pyqttools.add_to_layout(QHBoxLayout(), self.filesList,
                                           vlayout1)

        output_label = QLabel(self.tr('Output folder:'))
        self.toLineEdit = QLineEdit()
        self.toLineEdit.setReadOnly(True)
        self.toToolButton = QToolButton()
        self.toToolButton.setText('...')
        hlayout2 = pyqttools.add_to_layout(QHBoxLayout(), output_label,
                                           self.toLineEdit, self.toToolButton)

        self.audiovideo_tab = AudioVideoTab(self)
        self.image_tab = ImageTab(self)
        self.document_tab = DocumentTab(self)

        self.tabs = [self.audiovideo_tab, self.image_tab, self.document_tab]
        tab_names = [self.tr('Audio/Video'), self.tr('Images'),
                     self.tr('Documents')]
        self.TabWidget = QTabWidget()
        for num, tab in enumerate(tab_names):
            self.TabWidget.addTab(self.tabs[num], tab)
        self.TabWidget.setCurrentIndex(0)

        self.origCheckBox = QCheckBox(
                   self.tr('Save each file in the same\nfolder as input file'))
        self.deleteCheckBox = QCheckBox(self.tr('Delete original'))
        self.convertPushButton = QPushButton(self.tr('&Convert'))

        hlayout3 = pyqttools.add_to_layout(QHBoxLayout(), self.origCheckBox,
                                           self.deleteCheckBox, None)
        hlayout4 = pyqttools.add_to_layout(QHBoxLayout(), None,
                                          self.convertPushButton)
        final_layout = pyqttools.add_to_layout(QVBoxLayout(), hlayout1,
                                               self.TabWidget, hlayout2,
                                               hlayout3, hlayout4)

        self.statusBar = self.statusBar()
        self.dependenciesLabel = QLabel()
        self.statusBar.addPermanentWidget(self.dependenciesLabel, stretch=1)

        Widget = QWidget()
        Widget.setLayout(final_layout)
        self.setCentralWidget(Widget)

        c_act = pyqttools.create_action
        openAction = c_act(self, self.tr('Open'), QKeySequence.Open, None,
                           self.tr('Open a file'), self.add_files)
        convertAction = c_act(self, self.tr('Convert'), 'Ctrl+C', None,
                              self.tr('Convert files'), self.start_conversion)
        quitAction = c_act(self, self.tr('Quit'), 'Ctrl+Q', None,
                           self.tr('Quit'), self.close)
        edit_presetsAction = c_act(self, self.tr('Edit Presets'), 'Ctrl+P',
                                   None, self.tr('Edit Presets'), self.presets)
        importAction = c_act(self, self.tr('Import'), None, None,
                             self.tr('Import presets'), self.import_presets)
        exportAction = c_act(self, self.tr('Export'), None, None,
                             self.tr('Export presets'), self.export_presets)
        resetAction = c_act(self, self.tr('Reset'), None, None,
                            self.tr('Reset presets'), self.reset_presets)
        clearallAction = c_act(self, self.tr('Clear All'), None, None,
                               self.tr('Clear form'), self.clear_all)
        preferencesAction = c_act(self, self.tr('Preferences'), 'Alt+Ctrl+P',
                                  None, self.tr('Preferences'), self.preferences)
        aboutAction = c_act(self, self.tr('About'), 'Ctrl+?', None,
                            self.tr('About'), self.about)

        fileMenu = self.menuBar().addMenu(self.tr('File'))
        editMenu = self.menuBar().addMenu(self.tr('Edit'))
        presetsMenu = self.menuBar().addMenu(self.tr('Presets'))
        helpMenu = self.menuBar().addMenu(self.tr('Help'))
        pyqttools.add_actions(fileMenu,
                              [openAction, convertAction, None, quitAction])
        pyqttools.add_actions(presetsMenu, [edit_presetsAction, importAction,
                                            exportAction, resetAction])
        pyqttools.add_actions(editMenu,
                              [clearallAction, None, preferencesAction])
        pyqttools.add_actions(helpMenu, [aboutAction])

        self.filesList.dropped.connect(self.url_dropped)
        addButton.clicked.connect(self.add_files)
        delButton.clicked.connect(self.delete_files)
        clearButton.clicked.connect(self.clear_fileslist)
        self.TabWidget.currentChanged.connect(lambda:
                                     self.tabs[0].moreButton.setChecked(False))
        self.origCheckBox.clicked.connect(lambda:
                 self.toLineEdit.setEnabled(not self.origCheckBox.isChecked()))
        self.toToolButton.clicked.connect(self.open_dir)
        self.convertPushButton.clicked.connect(convertAction.triggered)

        del_shortcut = QShortcut(self)
        del_shortcut.setKey(Qt.Key_Delete)
        del_shortcut.activated.connect(self.delete_files)

        self.resize(MAIN_WIDTH, MAIN_HEIGHT)
        self.setWindowTitle('FF Multi Converter')

        QTimer.singleShot(0, self.check_for_dependencies)
        QTimer.singleShot(0, self.load_settings)
        QTimer.singleShot(0, self.audiovideo_tab.set_default_command)
        QTimer.singleShot(0, self.update_filesList)

    def load_settings(self):
        """Load settings values."""
        settings = QSettings()
        self.overwrite_existing = settings.value('overwrite_existing').toBool()
        self.default_output = unicode(
                                   settings.value('default_output').toString())
        self.prefix = unicode(settings.value('prefix').toString())
        self.suffix = unicode(settings.value('suffix').toString())
        self.avconv_prefered = settings.value('avconv_prefered').toBool()
        self.default_command = unicode(
                                  settings.value('default_command').toString())
        if not self.default_command:
            self.default_command = DEFAULT_COMMAND

        self.toLineEdit.setText(self.default_output)

    def current_tab(self):
        """Return the corresponding object of the selected tab."""
        for i in self.tabs:
            if self.tabs.index(i) == self.TabWidget.currentIndex():
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
                                    self.tr('Choose File'), self.home, filters)

        if fnames:
            for i in fnames:
                if not i in self.fnames:
                    self.fnames.append(unicode(i))
            self.update_filesList()

    def delete_files(self):
        """
        Get selectedItems of self.filesList, remove them from self.fnames and
        update the filesList.
        """
        items = self.filesList.selectedItems()
        if items:
            for i in items:
                self.fnames.remove(unicode(i.text()))
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
            output = QFileDialog.getExistingDirectory(self,
                'FF Multi Converter - ' + self.tr('Choose output destination'),
                self.home)
            #output = unicode(output)
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
                raise ValidationError(self.tr(
                                 'You must add at least one file to convert!'))
            elif not self.origCheckBox.isChecked() and not self.toLineEdit.text():
                raise ValidationError(self.tr(
                                      'You must choose an output folder!'))
            elif (not self.origCheckBox.isChecked() and
                  not os.path.exists(unicode(self.toLineEdit.text()))):
                raise ValidationError(self.tr('Output folder does not exists!'))
            if not self.current_tab().ok_to_continue():
                return False
            return True

        except ValidationError as e:
            QMessageBox.warning(self, 'FF Multi Converter - ' + \
                                self.tr('Error!'), unicode(e))
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
            ext_to = str(tab.convertComboBox.currentText()).split()[-1]

        return str('.' + ext_to)

    def create_paths_list(self, files_list, ext_to, prefix, suffix, output,
                          orig_dir, overwrite_existing):
        """
        Keyword arguments:
        files_list -- list with files to be converted
        ext_to     -- the extension to which each file must be converted to
        prefix     -- string that will be added as a prefix to all filenames
        suffix     -- string that will be added as a suffix to all filenames
        output     -- the output folder
        orig_dir   -- if True, each file will be saved at its original directory
                      else, files will be saved at output
        overwrite_existing -- if False, a '~' will be added as prefix to
                              filenames

        Create and return a list with dicts.
        Each dict will have only one key and one corresponding value.
        Key will be a file to be converted and it's value will be the name
        of the new converted file.

        Example list:
        [{"/foo/bar.png" : "/foo/bar.bmp"}, {"/f/bar2.png" : "/f/bar2.bmp"}]
        """
        assert ext_to.startswith('.'), 'ext_to must start with a dot (.)'

        conversion_list = []

        for _file in files_list:
            _dir, name = os.path.split(_file)
            y = prefix + os.path.splitext(name)[0] + suffix + ext_to

            if orig_dir:
                y = _dir + '/' + y
            else:
                y = output + '/' + y

            if not overwrite_existing:
                while os.path.exists(y):
                    _dir2, _name2 = os.path.split(y)
                    y = _dir2 + '/~' + _name2

            # Add quotations to paths in order to avoid error in special
            # cases such as spaces or special characters.
            _file = '"' + _file + '"'
            y = '"' + y + '"'

            _dict = {}
            _dict[_file] = y
            conversion_list.append(_dict)

        return conversion_list

    def start_conversion(self):
        """
        Extract the appropriate information from GUI and call the
        Progress dialog with the suitable argumens.
        """
        if not self.ok_to_continue():
            return

        ext_to = self.output_ext()
        _list = self.create_paths_list(self.fnames, ext_to,
                                       self.prefix, self.suffix,
                                       unicode(self.toLineEdit.text()),
                                       self.origCheckBox.isChecked(),
                                       self.overwrite_existing)

        tab = self.current_tab()
        cmd = ''
        size = str('')

        if tab.name == 'AudioVideo':
            cmd = tab.commandLineEdit.text()
        elif tab.name == 'Images':
            width = tab.widthLineEdit.text()
            if width:
                height = tab.heightLineEdit.text()
                size = str('{0}x{1}'.format(width, height))
        else:
            self.docconv = True

        dialog = progress.Progress(_list, tab.name, cmd, self.ffmpeg, size,
                                   self.deleteCheckBox.isChecked(), self)
        dialog.show()

    def is_installed(self, program):
        """Return True if program appears in user's PATH var, else False."""
        for path in os.getenv('PATH').split(os.pathsep):
            fpath = os.path.join(path, program)
            if os.path.exists(fpath) and os.access(fpath, os.X_OK):
                return True
        return False

    def check_for_dependencies(self):
        """
        Check if each one of the program dependencies are installed and
        update self.dependenciesLabel with the appropriate message.
        """
        self.ffmpeg = self.is_installed('ffmpeg')
        self.avconv = self.is_installed('avconv')
        self.unoconv = self.is_installed('unoconv')
        self.pmagick = True
        try:
            # We tried to import PythonMagick earlier.
            # If that raises an error it means that PythonMagick is not
            # available on the system.
            PythonMagick
        except NameError:
            self.pmagick = False

        missing = []
        if not self.ffmpeg and not self.avconv:
            missing.append('FFmpeg/avconv')
        if not self.unoconv:
            missing.append('unoconv')
        if not self.pmagick:
            missing.append('PythonMagick')

        # It would nice and clean for user if nothing missed.
        if missing:
            missing = ', '.join(missing)
            status = self.tr('Missing dependencies:') + ' ' + missing
            self.dependenciesLabel.setText(status)

    def about(self):
        """Call the about dialog with the appropriate values."""
        link = 'http://sites.google.com/site/ffmulticonverter/'
        msg = self.tr('Convert among several file types to other extensions')
        if len(msg) > 54:
            # break line if msg is too long to fit the window
            nmsg = ''
            for n, w in enumerate(msg.split(' ')):
                if len(nmsg) > 54:
                    break
                nmsg += w + ' '
            nmsg += '<br>' + msg[len(nmsg):]
            msg = nmsg
        text = '''<b> FF Multi Converter {0} </b>
                 <p>{1}
                 <p><a href="{2}">FF Multi Converter - Home Page</a>
                 <p>Copyright &copy; 2011-2013 Ilias Stamatis
                 <br>License: GNU GPL3
                 <p>Python {3} - Qt {4} - PyQt {5} on {6}'''\
                 .format(__version__, msg, link, platform.python_version()[:5],
                         QT_VERSION_STR, PYQT_VERSION_STR, platform.system())
        image = ':/ffmulticonverter.png'
        authors = 'Ilias Stamatis <stamatis.iliass@gmail.com>\n\n'
        authors += 'Contributors:\nPanagiotis Mavrogiorgos'
        transl_list = [['[cs] Czech', 'Petr Simacek'],
                       ['[de_DE] German (Germany)', 'Stefan Wilhelm'],
                       ['[el] Greek', 'Ilias Stamatis'],
                       ['[hu] Hungarian', 'Farkas Norbert'],
                       ['[pl_PL] Polish (Poland)', 'Lukasz Koszy'],
                       ['[pt] Portuguese', 'Sérgio Marques'],
                       ['[pt_BR] Portuguese (Brasil)', 'José Humberto A Melo'],
                       ['[ru] Russian', 'Andrew Lapshin'],
                       ['[tu] Turkish', 'Tayfun Kayha'],
                       ['[zh_CN] Chinese (China)', 'Dianjin Wang']]
        translators = ''
        for i in transl_list:
            translators += '{0}\n     {1}\n\n'.format(i[0], i[1])
        translators = translators[:-2]

        dialog = about_dlg.AboutDialog(text, image, authors, translators, self)
        dialog.exec_()


class AudioVideoTab(QWidget):
    def __init__(self, parent):
        super(AudioVideoTab, self).__init__(parent)
        self.parent = parent
        self.name = 'AudioVideo'
        self.formats = ['aac', 'ac3', 'afc', 'aiff', 'amr', 'asf', 'au',
                        'avi', 'dvd', 'flac', 'flv', 'mka',
                        'mkv', 'mmf', 'mov', 'mp3', 'mp4', 'mpg',
                        'ogg', 'ogv', 'psp', 'rm', 'spx', 'vob',
                        'wav', 'webm', 'wma', 'wmv']
        self.extra_formats = ['aifc', 'm2t', 'm4a', 'm4v', 'mp2', 'mpeg',
                              'ra', 'ts']

        nochange = self.tr('No Change')
        frequency_values = [nochange, '22050', '44100', '48000']
        bitrate_values = [nochange, '32', '96', '112', '128', '160', '192',
                          '256', '320']
        pattern = QRegExp(r'^[1-9]\d*')
        validator = QRegExpValidator(pattern, self)

        converttoLabel = QLabel(self.tr('Convert to:'))
        self.extComboBox = QComboBox()
        self.extComboBox.addItems(self.formats + [self.tr('Other')])
        self.extComboBox.setMinimumWidth(130)
        self.extLineEdit = QLineEdit()
        self.extLineEdit.setMaximumWidth(85)
        self.extLineEdit.setEnabled(False)
        hlayout1 = pyqttools.add_to_layout(QHBoxLayout(), converttoLabel,
                                           None, self.extComboBox,
                                           self.extLineEdit)
        commandLabel = QLabel(self.tr('Command:'))
        self.commandLineEdit = QLineEdit()
        self.presetButton = QPushButton(self.tr('Preset'))
        self.defaultButton = QPushButton(self.tr('Default'))
        hlayout2 = pyqttools.add_to_layout(QHBoxLayout(), commandLabel,
                                       self.commandLineEdit, self.presetButton,
                                       self.defaultButton)

        sizeLabel = QLabel(self.tr('Video Size:'))
        aspectLabel = QLabel(self.tr('Aspect:'))
        frameLabel = QLabel(self.tr('Frame Rate (fps):'))
        bitrateLabel = QLabel(self.tr('Video Bitrate (kbps):'))

        self.widthLineEdit = pyqttools.create_LineEdit((50, 16777215),
                                                       validator, 4)
        self.heightLineEdit = pyqttools.create_LineEdit((50, 16777215),
                                                        validator,4)
        label = QLabel('x')
        layout1 = pyqttools.add_to_layout(QHBoxLayout(), self.widthLineEdit,
                                          label, self.heightLineEdit)
        self.aspect1LineEdit = pyqttools.create_LineEdit((35, 16777215),
                                                         validator,2)
        self.aspect2LineEdit = pyqttools.create_LineEdit((35, 16777215),
                                                         validator,2)
        label = QLabel(':')
        layout2 = pyqttools.add_to_layout(QHBoxLayout(), self.aspect1LineEdit,
                                          label, self.aspect2LineEdit)
        self.frameLineEdit = pyqttools.create_LineEdit(None, validator, 4)
        self.bitrateLineEdit = pyqttools.create_LineEdit(None, validator, 6)

        labels = [sizeLabel, aspectLabel, frameLabel, bitrateLabel]
        widgets = [layout1, layout2, self.frameLineEdit, self.bitrateLineEdit]

        videosettings_layout = QHBoxLayout()
        for a, b in zip(labels, widgets):
            text = a.text()
            a.setText('<html><p align="center">{0}</p></html>'.format(text))
            layout = pyqttools.add_to_layout(QVBoxLayout(), a, b)
            videosettings_layout.addLayout(layout)

        freqLabel = QLabel(self.tr('Frequency (Hz):'))
        chanLabel = QLabel(self.tr('Channels:'))
        bitrateLabel = QLabel(self.tr('Audio Bitrate (kbps):'))

        self.freqComboBox = QComboBox()
        self.freqComboBox.addItems(frequency_values)
        self.chan1RadioButton = QRadioButton('1')
        self.chan1RadioButton.setMaximumSize(QSize(51, 16777215))
        self.chan2RadioButton = QRadioButton('2')
        self.chan2RadioButton.setMaximumSize(QSize(51, 16777215))
        self.group = QButtonGroup()
        self.group.addButton(self.chan1RadioButton)
        self.group.addButton(self.chan2RadioButton)
        spcr1 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        spcr2 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        chanlayout = pyqttools.add_to_layout(QHBoxLayout(), spcr1,
                                             self.chan1RadioButton,
                                             self.chan2RadioButton, spcr2)
        self.audio_bitrateComboBox = QComboBox()
        self.audio_bitrateComboBox.addItems(bitrate_values)

        labels = [freqLabel, chanLabel, bitrateLabel]
        widgets = [self.freqComboBox, chanlayout, self.audio_bitrateComboBox]

        audiosettings_layout = QHBoxLayout()
        for a, b in zip(labels, widgets):
            text = a.text()
            a.setText('<html><p align="center">{0}</p></html>'.format(text))
            layout = pyqttools.add_to_layout(QVBoxLayout(), a, b)
            audiosettings_layout.addLayout(layout)

        hidden_layout = pyqttools.add_to_layout(QVBoxLayout(),
                                                videosettings_layout,
                                                audiosettings_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.moreButton = QPushButton(QApplication.translate('Tab', 'More'))
        self.moreButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed))
        self.moreButton.setCheckable(True)
        hlayout3 = pyqttools.add_to_layout(QHBoxLayout(), line, self.moreButton)

        self.frame = QFrame()
        self.frame.setLayout(hidden_layout)
        self.frame.hide()

        final_layout = pyqttools.add_to_layout(QVBoxLayout(), hlayout1,
                                               hlayout2, hlayout3, self.frame)
        self.setLayout(final_layout)


        self.presetButton.clicked.connect(self.choose_preset)
        self.defaultButton.clicked.connect(self.set_default_command)
        self.moreButton.toggled.connect(self.frame.setVisible)
        self.moreButton.toggled.connect(self.resize_parent)
        self.extComboBox.currentIndexChanged.connect(
                lambda: self.extLineEdit.setEnabled(
                self.extComboBox.currentIndex() == len(self.formats)))
        self.widthLineEdit.textChanged.connect(
                lambda: self.command_elements_change('size'))
        self.heightLineEdit.textChanged.connect(
                lambda: self.command_elements_change('size'))
        self.aspect1LineEdit.textChanged.connect(
                lambda: self.command_elements_change('aspect'))
        self.aspect2LineEdit.textChanged.connect(
                lambda: self.command_elements_change('aspect'))
        self.frameLineEdit.textChanged.connect(
                lambda: self.command_elements_change('frames'))
        self.bitrateLineEdit.textChanged.connect(
                lambda: self.command_elements_change('video_bitrate'))
        self.freqComboBox.currentIndexChanged.connect(
                lambda: self.command_elements_change('frequency'))
        self.audio_bitrateComboBox.currentIndexChanged.connect(
                lambda: self.command_elements_change('audio_bitrate'))
        self.chan1RadioButton.clicked.connect(
                lambda: self.command_elements_change('channels1'))
        self.chan2RadioButton.clicked.connect(
                lambda: self.command_elements_change('channels2'))

    def resize_parent(self):
        """Resize MainWindow."""
        height = MAIN_FIXED_HEIGHT if self.frame.isVisible() else MAIN_HEIGHT
        self.parent.setMinimumSize(MAIN_WIDTH, height)
        self.parent.resize(MAIN_WIDTH, height)

    def clear(self):
        """Clear all values of graphical widgets."""
        lines = [self.commandLineEdit, self.widthLineEdit, self.heightLineEdit,
                 self.aspect1LineEdit, self.aspect2LineEdit, self.frameLineEdit,
                 self.bitrateLineEdit, self.extLineEdit]
        for i in lines:
            i.clear()

        self.freqComboBox.setCurrentIndex(0)
        self.audio_bitrateComboBox.setCurrentIndex(0)
        self.group.setExclusive(False)
        self.chan1RadioButton.setChecked(False)
        self.chan2RadioButton.setChecked(False)
        self.group.setExclusive(True)
        # setExclusive(False) in order to be able to uncheck checkboxes and
        # then setExclusive(True) so only one radio button can be set

    def ok_to_continue(self):
        """
        Check if everything is ok with audiovideotab to continue conversion.

        Check if:
        - Either ffmpeg or avconv are installed.
        - Desired extension is valid.
        - self.commandLineEdit is empty.

        Return True if all tests pass, else False.
        """
        if not self.parent.ffmpeg and not self.parent.avconv:
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                'Error!'), self.tr('Neither ffmpeg nor avconv are installed.'
                '\nYou will not be able to convert audio/video files until you'
                ' install one of them.'))
            return False
        if self.extLineEdit.isEnabled():
            text = str(self.extLineEdit.text()).strip()
            if len(text.split()) != 1 or text[0] == '.':
                QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                    'Error!'), self.tr('Extension must be one word and must '
                    'not start with a dot.'))
                self.extLineEdit.selectAll()
                self.extLineEdit.setFocus()
                return False
        if not self.commandLineEdit.text():
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                  'Error!'), self.tr('The command LineEdit may not be empty.'))
            self.commandLineEdit.setFocus()
            return False
        return True

    def set_default_command(self):
        """Set the default value to self.commandLineEdit."""
        self.clear()
        self.commandLineEdit.setText(self.parent.default_command)

    def choose_preset(self):
        """
        Open the presets dialog and update self.commandLineEdit,
        self.extComboBox and self.extLineEdit with the appropriate values.
        """
        dialog = presets_dlgs.ShowPresets()
        if dialog.exec_() and dialog.the_command is not None:
            self.commandLineEdit.setText(dialog.the_command)
            self.commandLineEdit.home(False)
            find = self.extComboBox.findText(dialog.the_extension)
            if find >= 0:
                self.extComboBox.setCurrentIndex(find)
            else:
                self.extComboBox.setCurrentIndex(len(self.formats))
                self.extLineEdit.setText(dialog.the_extension)

    def remove_consecutive_spaces(self, string):
        """Remove any consecutive spaces from a string and return it."""
        temp = string
        string = ''
        for i in temp.split():
            if i:
                string += i + ' '
        return string[:-1]

    def command_elements_change(self, widget):
        """Fill self.commandLineEdit with the appropriate command parameters."""
        command = str(self.commandLineEdit.text())

        if widget == 'size':
            text1 = self.widthLineEdit.text()
            text2 = self.heightLineEdit.text()

            if (text1 or text2) and not (text1 and text2):
                return
            f = re.sub(r'^.*(-s\s+\d+x\d+).*$', r'\1', command)
            if re.match(r'^.*(-s\s+\d+x\d+).*$', f):
                command = command.replace(f, '').strip()
            if text1 and text2:
                command += ' -s {0}x{1}'.format(text1, text2)

        elif widget == 'aspect':
            text1 = self.aspect1LineEdit.text()
            text2 = self.aspect2LineEdit.text()

            if (text1 or text2) and not (text1 and text2):
                return
            f = re.sub(r'^.*(-aspect\s+\d+:\d+).*$', r'\1', command)
            if re.match(r'^.*(-aspect\s+\d+:\d+).*$', f):
                command = command.replace(f, '').strip()
            if text1 and text2:
                command += ' -aspect {0}:{1}'.format(text1, text2)

        elif widget == 'frames':
            text = self.frameLineEdit.text()
            f = re.sub(r'^.*(-r\s+\d+).*$', r'\1', command)
            if re.match(r'^.*(-r\s+\d+).*$', f):
                command = command.replace(f, '').strip()
            if text:
                command += ' -r {0}'.format(text)

        elif widget == 'video_bitrate':
            text = self.bitrateLineEdit.text()
            f = re.sub(r'^.*(-b\s+\d+k).*$', r'\1', command)
            if re.match(r'^.*(-b\s+\d+k).*$', f):
                command = command.replace(f, '')
            if text:
                command += ' -b {0}k'.format(text)
            command = command.replace('-sameq', '').strip()

        elif widget == 'frequency':
            text = self.freqComboBox.currentText()
            f = re.sub(r'^.*(-ar\s+\d+).*$', r'\1', command)
            if re.match(r'^.*(-ar\s+\d+).*$', f):
                command = command.replace(f, '').strip()
            if text != 'No Change':
                command += ' -ar {0}'.format(text)

        elif widget == 'audio_bitrate':
            text = self.audio_bitrateComboBox.currentText()
            f = re.sub(r'^.*(-ab\s+\d+k).*$', r'\1', command)
            if re.match(r'^.*(-ab\s+\d+k).*$', f):
                command = command.replace(f, '').strip()
            if text != 'No Change':
                command += ' -ab {0}k'.format(text)

        elif widget in ('channels1', 'channels2'):
            text = self.chan1RadioButton.text() if widget == 'channels1' \
                                            else self.chan2RadioButton.text()
            f = re.sub(r'^.*(-ac\s+\d+).*$', r'\1', command)
            if re.match(r'^.*(-ac\s+\d+).*$', f):
                command = command.replace(f, '').strip()
            command += ' -ac {0}'.format(text)

        self.commandLineEdit.clear()
        self.commandLineEdit.setText(self.remove_consecutive_spaces(command))


class ImageTab(QWidget):
    def __init__(self, parent):
        super(ImageTab, self).__init__(parent)
        self.parent = parent
        self.name = 'Images'
        self.formats = ['bmp', 'cgm', 'dpx', 'emf', 'eps', 'fpx', 'gif',
                        'jbig', 'jng', 'jpeg', 'mrsid', 'p7', 'pdf', 'picon',
                        'png', 'ppm', 'psd', 'rad', 'tga', 'tif','webp', 'xpm']

        self.extra_img = ['bmp2', 'bmp3', 'dib', 'epdf', 'epi', 'eps2', 'eps3',
                          'epsf', 'epsi', 'icon', 'jpe', 'jpg', 'pgm', 'png24',
                          'png32', 'pnm', 'ps', 'ps2', 'ps3', 'sid', 'tiff']

        pattern = QRegExp(r'^[1-9]\d*')
        validator = QRegExpValidator(pattern, self)

        converttoLabel = QLabel(self.tr('Convert to:'))
        self.extComboBox = QComboBox()
        self.extComboBox.addItems(self.formats)

        hlayout1 = pyqttools.add_to_layout(QHBoxLayout(), converttoLabel,
                                           self.extComboBox, None)

        sizeLabel = QLabel(self.tr('Image Size:'))
        self.widthLineEdit = pyqttools.create_LineEdit((50, 16777215),
                                                       validator, 4)
        self.heightLineEdit = pyqttools.create_LineEdit((50, 16777215),
                                                        validator,4)
        label = QLabel('x')
        label.setMaximumWidth(25)
        hlayout2 = pyqttools.add_to_layout(QHBoxLayout(), sizeLabel,
                                           self.widthLineEdit, label,
                                           self.heightLineEdit, None)
        final_layout = pyqttools.add_to_layout(QVBoxLayout(),hlayout1,hlayout2)
        self.setLayout(final_layout)

    def clear(self):
        """Clear self.widthLineEdit and self.heightLineEdit."""
        self.widthLineEdit.clear()
        self.heightLineEdit.clear()

    def ok_to_continue(self):
        """
        Check if everything is ok with imagetab to continue conversion.

        Check if:
        - PythonMagick is missing.
        - Given files can be converted.
        - Either none or both size lineEdits are active at a time.

        Return True if all tests pass, else False.
        """
        width = self.widthLineEdit.text()
        height = self.heightLineEdit.text()

        if not self.parent.pmagick:
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                'Error!'), self.tr('PythonMagick is not installed.\nYou will '
                'not be able to convert image files until you install it.'))
            return False
        if (width and not height) or (not width and height):
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                     'Error!'), self.tr('The size LineEdit may not be empty.'))
            if width and not height:
                self.heightLineEdit.setFocus()
            else:
                self.widthLineEdit.setFocus()
            return False
        for i in self.parent.fnames:
            i = unicode(i)
            file_ext = os.path.splitext(i)[-1][1:]
            if not file_ext in self.formats and not file_ext in self.extra_img:
                QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                       'Error!'),
                       self.tr('%1 is of unknown image file type!').arg(i))
                return False
        return True


class DocumentTab(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(DocumentTab, self).__init__(parent)
        self.name = 'Documents'
        self.formats = {
                'doc' : ['odt', 'pdf'],
                'html' : ['odt'],
                'odp' : ['pdf', 'ppt'],
                'ods' : ['pdf'],
                'odt' : ['doc', 'html', 'pdf', 'rtf', 'sxw', 'txt','xml'],
                'ppt' : ['odp'],
                'rtf' : ['odt'],
                'sdw' : ['odt'],
                'sxw' : ['odt'],
                'txt' : ['odt'],
                'xls' : ['ods'],
                'xml' : ['doc', 'odt', 'pdf']
                }

        flist = []
        for i in self.formats:
            for y in self.formats[i]:
                flist.append(i + ' to ' + y)
        flist.sort()

        convertLabel = QLabel(self.tr('Convert:'))
        self.convertComboBox = QComboBox()
        self.convertComboBox.addItems(flist)
        final_layout = pyqttools.add_to_layout(QHBoxLayout(), convertLabel,
                                               self.convertComboBox, None)
        self.setLayout(final_layout)

    def ok_to_continue(self):
        """
        Check if everything is ok with documenttab to continue conversion.

        Checks if:
        - unoconv is missing.
        - Given file extension is same with the declared extension.

        Return True if all tests pass, else False.
        """
        decl_ext = self.convertComboBox.currentText().split(' ')[0]

        try:
            if not self.parent.unoconv:
                raise ValidationError(self.tr(
                        'Unocov is not installed.\nYou will not be able '
                        'to convert document files until you install it.'))
            for i in self.parent.fnames:
                i = unicode(i)
                file_ext = os.path.splitext(i)[-1][1:]
                if file_ext != decl_ext:
                    raise ValidationError(self.tr(
                            '%1 is not %2!').arg(i, decl_ext))
            if self.parent.docconv:
                raise ValidationError(self.tr(
                            'You can not make parallel document conversions.'))
            return True

        except ValidationError as e:
            QMessageBox.warning(self, 'FF Multi Converter - ' + \
                    self.tr('Error!'), unicode(e))
            return False


def logging_config():
    log_folder = os.path.join(os.getenv('HOME'), '.config/ffmulticonverter/logs')
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    log_file = os.path.join(log_folder, 'history.log')

    logging.basicConfig(
            filename = log_file,
            level=logging.DEBUG,
            format='%(asctime)s : %(levelname)s - %(type)s\n'
                   'Command: %(command)s\n'
                   'Return code: %(returncode)s\n%(message)s\n',
            datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    app = QApplication(sys.argv)
    app.setOrganizationName('ffmulticonverter')
    app.setOrganizationDomain('sites.google.com/site/ffmulticonverter/')
    app.setApplicationName('FF Muli Converter')
    app.setWindowIcon(QIcon(':/ffmulticonverter.png'))

    locale = QLocale.system().name()
    qtTranslator = QTranslator()
    if qtTranslator.load('qt_' + locale, ':/'):
        app.installTranslator(qtTranslator)
    appTranslator = QTranslator()
    if appTranslator.load('ffmulticonverter_' + locale, ':/'):
        app.installTranslator(appTranslator)

    logging_config()
    converter = MainWindow()
    converter.show()
    app.exec_()

if __name__ == '__main__':
    main()
