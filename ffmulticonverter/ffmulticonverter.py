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
import re
import platform
import logging
import textwrap

from PyQt4.QtCore import (
        PYQT_VERSION_STR, QCoreApplication, QLocale, QRegExp, QSettings, QSize,
        Qt, QTimer, QTranslator, QT_VERSION_STR
        )
from PyQt4.QtGui import (
        QAbstractItemView, QApplication, QButtonGroup, QCheckBox, QComboBox,
        QFileDialog, QFrame, QHBoxLayout, QIcon, QKeySequence, QLabel,
        QLineEdit, QMainWindow, QMessageBox, QPushButton, QRadioButton,
        QRegExpValidator, QShortcut, QSizePolicy, QSpacerItem, QTabWidget,
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


class ValidationError(Exception):
    pass


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # main window dimensions
        self.main_width = 760
        self.main_height = 510
        self.main_fixed_height = 640
        self.default_command = config.default_ffmpeg_cmd

        self.fnames = list()  # list of file names to be converted
        self.docconv = False  # True when a documents conversion is running

        # parse command line arguments
        for i in QCoreApplication.argv()[1:]:
            i = os.path.abspath(i)
            if os.path.isfile(i):
                self.fnames.append(i)
            else:
                print("ffmulticonverter: {0}: Not a file".format(i))

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
        if defcmd:
            self.default_command = defcmd

        self.toLineEdit.setText(self.default_output)

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


class AudioVideoTab(QWidget):
    def __init__(self, parent):
        super(AudioVideoTab, self).__init__(parent)
        self.parent = parent
        self.name = 'AudioVideo'
        self.formats = [
                '3gp', 'aac', 'ac3', 'afc', 'aiff', 'amr', 'asf', 'au', 'avi',
                'dvd', 'flac', 'flv', 'mka', 'mkv', 'mmf', 'mov', 'mp3', 'mp4',
                'mpg', 'ogg', 'ogv', 'psp', 'rm', 'spx', 'vob', 'wav', 'webm',
                'wma', 'wmv'
                ]
        self.extra_formats = [
                'aifc', 'm2t', 'm4a', 'm4v', 'mp2', 'mpeg', 'ra', 'ts'
                ]

        videocodecs = [
                'mpeg4', 'msmpeg4', 'mpeg2video', 'h263', 'libx264', 'libxvid',
                'flv', 'libvpx', 'wmv2'
                ]
        audiocodecs = [
                'libmp3lame', 'libvorbis', 'ac3', 'aac', 'libfaac',
                'libvo_aacenc', 'wmav2', 'mp2', 'copy'
                ]

        nochange = self.tr('No Change')
        other = self.tr('Other')
        frequency_values = [nochange, '22050', '44100', '48000']
        bitrate_values = [
                nochange, '32', '96', '112', '128', '160', '192', '256', '320'
                ]
        validator = QRegExpValidator(QRegExp(r'^[1-9]\d*'), self)

        converttoLabel = QLabel(self.tr('Convert to:'))
        extComboBox = QComboBox()
        extComboBox.addItems(self.formats + [other])
        extComboBox.setMinimumWidth(130)
        extLineEdit = QLineEdit()
        extLineEdit.setMaximumWidth(85)
        extLineEdit.setEnabled(False)
        vidcodecLabel = QLabel('Video codec:')
        vidcodecComboBox = QComboBox()
        vidcodecComboBox.addItems(videocodecs + [other])
        vidcodecLineEdit = QLineEdit()
        vidcodecLineEdit.setEnabled(False)

        hlayout1 = utils.add_to_layout(
                'h', converttoLabel, extComboBox, extLineEdit,
                vidcodecLabel, vidcodecComboBox, vidcodecLineEdit)

        commandLabel = QLabel(self.tr('Command:'))
        commandLineEdit = QLineEdit()
        presetButton = QPushButton(self.tr('Preset'))
        defaultButton = QPushButton(self.tr('Default'))
        hlayout2 = utils.add_to_layout(
                'h', commandLabel, commandLineEdit, presetButton, defaultButton)

        sizeLabel = QLabel(self.tr('Video Size:'))
        aspectLabel = QLabel(self.tr('Aspect:'))
        frameLabel = QLabel(self.tr('Frame Rate (fps):'))
        bitrateLabel = QLabel(self.tr('Video Bitrate (kbps):'))

        widthLineEdit = utils.create_LineEdit((70, 16777215), validator, 4)
        heightLineEdit = utils.create_LineEdit((70, 16777215), validator, 4)
        label = QLabel('<html><p align="center">x</p></html>')
        layout1 = utils.add_to_layout('h', widthLineEdit, label, heightLineEdit)
        aspect1LineEdit = utils.create_LineEdit((50, 16777215), validator, 2)
        aspect2LineEdit = utils.create_LineEdit((50, 16777215), validator, 2)
        label = QLabel('<html><p align="center">:</p></html>')
        layout2 = utils.add_to_layout(
                'h', aspect1LineEdit, label, aspect2LineEdit)
        frameLineEdit = utils.create_LineEdit((120, 16777215), validator, 4)
        bitrateLineEdit = utils.create_LineEdit((130, 16777215), validator, 6)

        labels = [sizeLabel, aspectLabel, frameLabel, bitrateLabel]
        widgets = [layout1, layout2, frameLineEdit, bitrateLineEdit]

        vidaspectCheckBox = QCheckBox(self.tr("Preserve\naspect ratio"))

        videosettings_layout = QHBoxLayout()
        for a, b in zip(labels, widgets):
            a.setText('<html><p align="center">{0}</p></html>'.format(a.text()))
            layout = utils.add_to_layout('v', a, b)
            videosettings_layout.addLayout(layout)
            if a == aspectLabel:
                # add vidaspectCB in layout after aspectLabel
                videosettings_layout.addWidget(vidaspectCheckBox)

        freqLabel = QLabel(self.tr('Frequency (Hz):'))
        chanLabel = QLabel(self.tr('Audio Channels:'))
        bitrateLabel = QLabel(self.tr('Audio Bitrate (kbps):'))
        threadsLabel = QLabel('Threads:')
        audcodecLabel = QLabel('Audio codec:')

        freqComboBox = QComboBox()
        freqComboBox.addItems(frequency_values)
        chan1RadioButton = QRadioButton('1')
        chan1RadioButton.setMaximumSize(QSize(51, 16777215))
        chan2RadioButton = QRadioButton('2')
        chan2RadioButton.setMaximumSize(QSize(51, 16777215))
        self.group = QButtonGroup()
        self.group.addButton(chan1RadioButton)
        self.group.addButton(chan2RadioButton)
        spcr1 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        spcr2 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        chanlayout = utils.add_to_layout(
                'h', spcr1, chan1RadioButton, chan2RadioButton, spcr2)
        audio_bitrateComboBox = QComboBox()
        audio_bitrateComboBox.addItems(bitrate_values)
        validator = QRegExpValidator(QRegExp(r'^[0-9]'), self)
        threadsLineEdit = utils.create_LineEdit((50, 16777215), validator, None)

        audcodecComboBox = QComboBox()
        audcodecComboBox.addItems(audiocodecs + [other])
        audcodecLineEdit = QLineEdit()
        audcodecLineEdit.setEnabled(False)

        audcodhlayout = utils.add_to_layout(
                'h', audcodecComboBox, audcodecLineEdit);

        labels = [freqLabel, chanLabel, bitrateLabel, audcodecLabel,
                  threadsLabel]
        widgets = [freqComboBox, chanlayout, audio_bitrateComboBox,
                   audcodhlayout, threadsLineEdit]

        audiosettings_layout = QHBoxLayout()
        for a, b in zip(labels, widgets):
            a.setText('<html><p align="center">{0}</p></html>'.format(a.text()))
            layout = utils.add_to_layout('v', a, b)
            audiosettings_layout.addLayout(layout)

        hidden_layout = utils.add_to_layout(
                'v', videosettings_layout, audiosettings_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        moreButton = QPushButton(QApplication.translate('Tab', 'More'))
        moreButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed))
        moreButton.setCheckable(True)
        hlayout3 = utils.add_to_layout('h', line, moreButton)

        self.frame = QFrame()
        self.frame.setLayout(hidden_layout)
        self.frame.hide()
        #for development
        #self.frame.setVisible(True)

        final_layout = utils.add_to_layout(
                'v', hlayout1, hlayout2, hlayout3, self.frame)
        self.setLayout(final_layout)

        presetButton.clicked.connect(self.choose_preset)
        defaultButton.clicked.connect(self.set_default_command)
        moreButton.toggled.connect(self.frame.setVisible)
        moreButton.toggled.connect(self.resize_parent)
        # enable labels when user choose 'other' which is always the last choice
        extComboBox.currentIndexChanged.connect(
                lambda: extLineEdit.setEnabled(
                        extComboBox.currentIndex() == len(self.formats))
                )
        vidcodecComboBox.currentIndexChanged.connect(
                lambda: vidcodecLineEdit.setEnabled(
                        vidcodecComboBox.currentIndex() == len(videocodecs))
                )
        audcodecComboBox.currentIndexChanged.connect(
                lambda: audcodecLineEdit.setEnabled(
                        audcodecComboBox.currentIndex() == len(audiocodecs))
                )
        vidaspectCheckBox.toggled.connect(
                lambda: aspect1LineEdit.setEnabled(
                        not vidaspectCheckBox.isChecked())
                )
        vidaspectCheckBox.toggled.connect(
                lambda: aspect2LineEdit.setEnabled(
                        not vidaspectCheckBox.isChecked())
                )
        widthLineEdit.textChanged.connect(
                lambda: self.command_elements_change('size'))
        heightLineEdit.textChanged.connect(
                lambda: self.command_elements_change('size'))
        aspect1LineEdit.textChanged.connect(
                lambda: self.command_elements_change('aspect'))
        aspect2LineEdit.textChanged.connect(
                lambda: self.command_elements_change('aspect'))
        frameLineEdit.textChanged.connect(
                lambda: self.command_elements_change('frames'))
        bitrateLineEdit.textChanged.connect(
                lambda: self.command_elements_change('video_bitrate'))
        freqComboBox.currentIndexChanged.connect(
                lambda: self.command_elements_change('frequency'))
        audio_bitrateComboBox.currentIndexChanged.connect(
                lambda: self.command_elements_change('audio_bitrate'))
        chan1RadioButton.clicked.connect(
                lambda: self.command_elements_change('channels1'))
        chan2RadioButton.clicked.connect(
                lambda: self.command_elements_change('channels2'))

        #aliasing
        self.extComboBox = extComboBox
        self.extLineEdit = extLineEdit
        self.vidcodecComboBox = vidcodecComboBox
        self.vidcodecLineEdit = vidcodecLineEdit
        self.commandLineEdit = commandLineEdit
        self.presetButton = presetButton
        self.defaultButton = defaultButton
        self.widthLineEdit = widthLineEdit
        self.heightLineEdit = heightLineEdit
        self.aspect1LineEdit = aspect1LineEdit
        self.aspect2LineEdit = aspect2LineEdit
        self.frameLineEdit = frameLineEdit
        self.bitrateLineEdit = bitrateLineEdit
        self.vidaspectCheckBox = vidaspectCheckBox
        self.freqComboBox = freqComboBox
        self.chan1RadioButton = chan1RadioButton
        self.chan2RadioButton = chan2RadioButton
        self.audio_bitrateComboBox = audio_bitrateComboBox
        self.threadsLineEdit = threadsLineEdit
        self.audcodecComboBox = audcodecComboBox
        self.audcodecLineEdit = audcodecLineEdit
        self.moreButton = moreButton

    def resize_parent(self):
        """Resize MainWindow."""
        if self.frame.isVisible():
            height = self.parent.main_fixed_height
        else:
            height = self.parent.main_height
        self.parent.setMinimumSize(self.parent.main_width, height)
        self.parent.resize(self.parent.main_width, height)

    def clear(self):
        """Clear all values of graphical widgets."""
        lines = [
                self.commandLineEdit, self.widthLineEdit, self.heightLineEdit,
                self.aspect1LineEdit, self.aspect2LineEdit, self.frameLineEdit,
                self.bitrateLineEdit, self.extLineEdit, self.threadsLineEdit,
                self.audcodecLineEdit, self.vidcodecLineEdit
                ]
        for i in lines:
            i.clear()

        self.freqComboBox.setCurrentIndex(0)
        self.audio_bitrateComboBox.setCurrentIndex(0)
        self.vidaspectCheckBox.setChecked(False)
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

        Return True if all tests pass, else False.
        """
        if not self.parent.ffmpeg and not self.parent.avconv:
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                'Error!'), self.tr('Neither ffmpeg nor avconv are installed.'
                '\nYou will not be able to convert audio/video files until you'
                ' install one of them.'))
            return False
        if self.extLineEdit.isEnabled():
            text = self.extLineEdit.text().strip()
            if len(text.split()) != 1 or text[0] == '.':
                QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                    'Error!'), self.tr('Extension must be one word and must '
                    'not start with a dot.'))
                self.extLineEdit.selectAll()
                self.extLineEdit.setFocus()
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

    def command_elements_change(self, widget):
        """Fill self.commandLineEdit with the appropriate command parameters."""
        command = self.commandLineEdit.text()

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
            if widget == 'channels1':
                text = self.chan1RadioButton.text()
            else:
                text = self.chan2RadioButton.text()

            f = re.sub(r'^.*(-ac\s+\d+).*$', r'\1', command)
            if re.match(r'^.*(-ac\s+\d+).*$', f):
                command = command.replace(f, '').strip()
            command += ' -ac {0}'.format(text)

        self.commandLineEdit.clear()
        self.commandLineEdit.setText(utils.remove_consecutive_spaces(command))


class ImageTab(QWidget):
    def __init__(self, parent):
        super(ImageTab, self).__init__(parent)
        self.parent = parent
        self.name = 'Images'
        self.formats = [
                'bmp', 'cgm', 'dpx', 'emf', 'eps', 'fpx', 'gif', 'jbig', 'jng',
                'jpeg', 'mrsid', 'p7', 'pdf', 'picon', 'png', 'ppm', 'psd',
                'rad', 'tga', 'tif','webp', 'xpm'
                ]

        self.extra_img = [
                'bmp2', 'bmp3', 'dib', 'epdf', 'epi', 'eps2', 'eps3', 'epsf',
                'epsi', 'icon', 'jpe', 'jpg', 'pgm', 'png24', 'png32', 'pnm',
                'ps', 'ps2', 'ps3', 'sid', 'tiff'
                ]

        validator = QRegExpValidator(QRegExp(r'^[1-9]\d*'), self)

        converttoLabel = QLabel(self.tr('Convert to:'))
        extComboBox = QComboBox()
        extComboBox.addItems(self.formats)

        sizeLabel = QLabel(
                '<html><p align="center">' + self.tr('Image Size:') +
                '</p></html>')
        widthLineEdit = utils.create_LineEdit((50, 16777215), validator, 4)
        heightLineEdit = utils.create_LineEdit((50, 16777215), validator, 4)
        label = QLabel('<html><p align="center">x</p></html>')
        label.setMaximumWidth(25)
        imgaspectCheckBox = QCheckBox(self.tr("Maintain aspect ratio"))
        hlayout1 = utils.add_to_layout('h', widthLineEdit,label,heightLineEdit)
        vlayout = utils.add_to_layout('v', sizeLabel, hlayout1)
        hlayout2 = utils.add_to_layout('h', vlayout, imgaspectCheckBox, None)
        hlayout3 = utils.add_to_layout(
                'h', converttoLabel, extComboBox, hlayout2, None)

        commandLabel = QLabel(self.tr('Extra options:'))
        commandLineEdit = QLineEdit()
        hlayout4 = utils.add_to_layout(
                'h', commandLabel, commandLineEdit, QSpacerItem(180, 40))

        final_layout = utils.add_to_layout('v', hlayout3, hlayout4)
        self.setLayout(final_layout)

        #aliasing
        self.extComboBox = extComboBox
        self.widthLineEdit = widthLineEdit
        self.heightLineEdit = heightLineEdit
        self.imgaspectCheckBox = imgaspectCheckBox
        self.commandLineEdit = commandLineEdit

    def clear(self):
        """Clear self.widthLineEdit and self.heightLineEdit."""
        self.widthLineEdit.clear()
        self.heightLineEdit.clear()
        self.commandLineEdit.clear()

    def ok_to_continue(self):
        """
        Check if everything is ok with imagetab to continue conversion.

        Check if:
        - ImageMagick is missing.
        - Either none or both size lineEdits are active at a time.

        Return True if all tests pass, else False.
        """
        width = self.widthLineEdit.text()
        height = self.heightLineEdit.text()

        if not self.parent.imagemagick:
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                'Error!'), self.tr('ImageMagick is not installed.\nYou will '
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
        final_layout = utils.add_to_layout(
                'h', convertLabel, self.convertComboBox, None)
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
                raise ValidationError(
                        self.tr(
                        'Unocov is not installed.\nYou will not be able '
                        'to convert document files until you install it.')
                        )
            for i in self.parent.fnames:
                file_ext = os.path.splitext(i)[-1][1:]
                if file_ext != decl_ext:
                    raise ValidationError(
                            self.trUtf8('{0} is not {1}!'.format(i, decl_ext)))
            if self.parent.docconv:
                raise ValidationError(
                        self.tr(
                        'You can not make parallel document conversions.')
                        )
            return True

        except ValidationError as e:
            QMessageBox.warning(self, 'FF Multi Converter - ' + \
                    self.tr('Error!'), str(e))
            return False

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
