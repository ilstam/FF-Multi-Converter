#!/usr/bin/python
# -*- coding: utf-8 -*-
# Program: FF Multi Converter
# Purpose: GUI application to convert multiple file formats
#
# Copyright (C) 2011-2012 Ilias Stamatis <stamatis.iliass@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# the Free Software Foundation, either version 3 of the License, or
# it under the terms of the GNU General Public License as published by
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
from data import __version__

from PyQt4.QtCore import (Qt, QSettings, QTimer,
                  QLocale, QTranslator, QT_VERSION_STR,PYQT_VERSION_STR)
from PyQt4.QtGui import (QApplication, QMainWindow, QWidget, QGridLayout,
                  QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QToolButton,
                  QCheckBox, QRadioButton, QPushButton, QTabWidget, QIcon,
                  QAction, QMenu, QKeySequence, QFileDialog, QMessageBox)

import sys
import os
import glob
import re
import platform

import tabs
import progress
import pyqttools
import preferences_dlg
import qrc_resources

try:
    import PythonMagick
except ImportError:
    pass

class ValidationError(Exception): pass

class MainWindow(QMainWindow):
    """Main Windows' ui and methods"""
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.home = os.getenv('HOME')
        self.fname = ''
        self.output = ''

        select_label = QLabel(self.tr('Select file:'))
        output_label = QLabel(self.tr('Output destination:'))
        self.fromLineEdit = QLineEdit()
        self.fromLineEdit.setReadOnly(True)
        self.toLineEdit = QLineEdit()
        self.toLineEdit.setReadOnly(True)
        self.fromToolButton = QToolButton()
        self.fromToolButton.setText('...')
        self.toToolButton = QToolButton()
        self.toToolButton.setText('...')
        grid1 = pyqttools.add_to_grid(QGridLayout(),
                        [select_label, self.fromLineEdit, self.fromToolButton],
                        [output_label, self.toLineEdit, self.toToolButton])

        self.audio_tab = tabs.AudioTab(self)
        self.video_tab = tabs.VideoTab(self)
        self.image_tab = tabs.ImageTab(self)
        self.document_tab = tabs.DocumentTab(self)

        self.tabs = [self.audio_tab, self.video_tab, self.image_tab,
                     self.document_tab]
        tab_names = [self.tr('Audio'), self.tr('Videos'), self.tr('Images'),
                     self.tr('Documents')]
        self.TabWidget  = QTabWidget()
        for num, tab in enumerate(tab_names):
            self.TabWidget.addTab(self.tabs[num], tab)
        self.TabWidget.setCurrentIndex(0)

        self.folderCheckBox = QCheckBox(self.tr(
                                          'Convert all files\nin this folder'))
        self.recursiveCheckBox = QCheckBox(self.tr(
                                                 'Convert files\nrecursively'))
        self.deleteCheckBox = QCheckBox(self.tr('Delete original'))
        layout1 = pyqttools.add_to_layout(QHBoxLayout(),self.folderCheckBox,
                             self.recursiveCheckBox, self.deleteCheckBox, None)

        self.typeRadioButton = QRadioButton(self.tr('Same type'))
        self.typeRadioButton.setEnabled(False)
        self.typeRadioButton.setChecked(True)
        self.extRadioButton = QRadioButton(self.tr('Same extension'))
        self.extRadioButton.setEnabled(False)
        layout2 = pyqttools.add_to_layout(QHBoxLayout(), self.typeRadioButton,
                                                     self.extRadioButton, None)
        layout3 = pyqttools.add_to_layout(QVBoxLayout(), layout1, layout2)

        self.convertPushButton = QPushButton(self.tr('&Convert'))
        layout4 = pyqttools.add_to_layout(QHBoxLayout(), None,
                                                        self.convertPushButton)
        final_layout = pyqttools.add_to_layout(QVBoxLayout(), grid1,
                                        self.TabWidget, layout3, None, layout4)

        self.statusBar = self.statusBar()
        self.dependenciesLabel = QLabel()
        self.statusBar.addPermanentWidget(self.dependenciesLabel, stretch=1)

        Widget = QWidget()
        Widget.setLayout(final_layout)
        self.setCentralWidget(Widget)

        openAction = self.create_action(self.tr('Open'), QKeySequence.Open,
                                  None, self.tr('Open a file'), self.open_file)
        convertAction = self.create_action(self.tr('Convert'), 'Ctrl+C', None,
                               self.tr('Convert files'), self.start_conversion)
        quitAction = self.create_action(self.tr('Quit'), 'Ctrl+Q', None,
                                                   self.tr('Quit'), self.close)
        clearAction = self.create_action(self.tr('Clear'), None, None,
                                             self.tr('Clear form'), self.clear)
        preferencesAction = self.create_action(self.tr('Preferences'),
                  'Alt+Ctrl+P', None, self.tr('Preferences'), self.preferences)
        aboutAction = self.create_action(self.tr('About'), 'Ctrl+?', None,
                                                  self.tr('About'), self.about)

        fileMenu = self.menuBar().addMenu(self.tr('File'))
        editMenu = self.menuBar().addMenu(self.tr('Edit'))
        helpMenu = self.menuBar().addMenu(self.tr('Help'))
        self.add_actions(fileMenu, [openAction, convertAction, None,
                                                                   quitAction])
        self.add_actions(editMenu, [clearAction, None, preferencesAction])
        self.add_actions(helpMenu, [aboutAction])

        self.TabWidget.currentChanged.connect(self.checkboxes_clicked)
        self.TabWidget.currentChanged.connect(self.resize_window)
        self.folderCheckBox.clicked.connect(lambda:
                                             self.checkboxes_clicked('folder'))
        self.recursiveCheckBox.clicked.connect(lambda:
                                          self.checkboxes_clicked('recursive'))
        self.fromToolButton.clicked.connect(self.open_file)
        self.toToolButton.clicked.connect(self.open_dir)
        self.convertPushButton.clicked.connect(convertAction.triggered)

        self.resize(685, 378)
        self.setWindowTitle('FF Multi Converter')

        QTimer.singleShot(0, self.check_for_dependencies)
        QTimer.singleShot(0, self.set_settings)

    def create_action(self, text, shortcut=None, icon=None, tip=None,
                      triggered=None, toggled=None, context=Qt.WindowShortcut):
        """Creates a QAction"""
        action = QAction(text, self)
        if triggered is not None:
            action.triggered.connect(triggered)
        if toggled is not None:
            action.toggled.connect(toggled)
            action.setCheckable(True)
        if icon is not None:
            action.setIcon( icon )
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        action.setShortcutContext(context)
        return action

    def add_actions(self, target, actions, insert_before=None):
        """Adds actions to menus.

        Keyword arguments:
        target -- menu to add action
        actions -- list with actions to add
        """
        previous_action = None
        target_actions = list(target.actions())
        if target_actions:
            previous_action = target_actions[-1]
            if previous_action.isSeparator():
                previous_action = None
        for action in actions:
            if (action is None) and (previous_action is not None):
                if insert_before is None:
                    target.addSeparator()
                else:
                    target.insertSeparator(insert_before)
            elif isinstance(action, QMenu):
                if insert_before is None:
                    target.addMenu(action)
                else:
                    target.insertMenu(insert_before, action)
            elif isinstance(action, QAction):
                if insert_before is None:
                    target.addAction(action)
                else:
                    target.insertAction(insert_before, action)
            previous_action = action

    def set_settings(self):
        """Sets program settings"""
        settings = QSettings()
        self.saveto_output = settings.value('saveto_output').toBool()
        self.rebuild_structure = settings.value('rebuild_structure').toBool()
        self.default_output = unicode(
                                   settings.value('default_output').toString())
        self.prefix = unicode(settings.value('prefix').toString())
        self.suffix = unicode(settings.value('suffix').toString())

        if self.saveto_output:
            if self.toLineEdit.text() == self.tr('Each file to its original '
                                     'folder') or self.toLineEdit.text() == '':
                self.output = self.default_output
                self.toLineEdit.setText(self.output)
            self.toLineEdit.setEnabled(True)
        else:
            self.toLineEdit.setEnabled(False)
            self.toLineEdit.setText(self.tr(
                                           'Each file to its original folder'))
            self.output = None

    def current_tab(self):
        """Returns current tab."""
        for i in self.tabs:
            if self.tabs.index(i) == self.TabWidget.currentIndex():
                return i

    def resize_window(self):
        """It hides widgets and resizes the window."""
        for i in self.tabs[:3]:
            i.moreButton.setChecked(False)

    def checkboxes_clicked(self, data=None):
        """Manages the behavior of checkboxes and radiobuttons.

        Keywords arguments:
        data -- a string to show from which CheckBox the signal emitted.
        """
        # data default value is None because the method can also be called
        # when TabWidget's tab change.
        if data == 'folder' and self.recursiveCheckBox.isChecked():
            self.recursiveCheckBox.setChecked(False)
        elif data == 'recursive' and self.folderCheckBox.isChecked():
            self.folderCheckBox.setChecked(False)

        index = self.TabWidget.currentIndex()
        enable = bool(self.recursiveCheckBox.isChecked()
                                            or self.folderCheckBox.isChecked())
        self.extRadioButton.setEnabled(enable)
        if enable and index == 3:
            # set typeRadioButton disabled when type == document files,
            # because it is not possible to convert every file format to any
            # other file format.
            self.typeRadioButton.setEnabled(False)
            self.extRadioButton.setChecked(True)
        else:
            self.typeRadioButton.setEnabled(enable)

    def preferences(self):
        """Opens the preferences dialog."""
        dialog = preferences_dlg.Preferences()
        if dialog.exec_():
            self.set_settings()

    def clear(self):
        """Clears the form.

        Clears line edits and unchecks checkboxes and radio buttons.
        """

        self.fromLineEdit.clear()
        self.fname = ''
        if self.output is not None:
            self.toLineEdit.clear()
            self.output = ''
        boxes = [self.folderCheckBox, self.recursiveCheckBox,
                                                           self.deleteCheckBox]
        for box in boxes:
            box.setChecked(False)
        self.checkboxes_clicked()
        for i in self.tabs:
            i.clear()

    def open_file(self):
        """Uses standard QtDialog to get file name."""
        all_files = '*'
        audio_files = ' '.join(['*.'+i for i in self.audio_tab.formats])
        video_files = ' '.join(['*.'+i for i in self.video_tab.formats])
        img_formats = self.image_tab.formats[:]
        img_formats.extend(self.image_tab.extra_img_formats_list)
        image_files = ' '.join(['*.'+i for i in img_formats])
        document_files = ' '.join(['*.'+i for i in self.document_tab.formats])
        formats = [all_files, audio_files, video_files, image_files,
                                                                document_files]
        strings = [self.tr('All Files'), self.tr('Audio Files'),
                   self.tr('Video Files'), self.tr('Image Files'),
                   self.tr('Document Files')]

        filters = ''
        for string, extensions in zip(strings, formats):
            filters += string + ' ({0});;'.format(extensions)
        filters = filters[:-2] # remove last ';;'

        fname = QFileDialog.getOpenFileName(self, 'FF Multi Converter - ' + \
                                    self.tr('Choose File'), self.home, filters)
        fname = unicode(fname)
        if fname:
            self.fname = fname
            self.fromLineEdit.setText(self.fname)
            tab = self.current_tab()
            tab.change_to_current_index(self.fname)

    def open_dir(self):
        """Uses standard QtDialog to get directory name."""
        if self.toLineEdit.isEnabled():
            output = QFileDialog.getExistingDirectory(self, 'FF Multi '
              'Converter - ' + self.tr('Choose output destination'), self.home)
            output = unicode(output)
            if output:
                self.output = output
                self.toLineEdit.setText(self.output)
        else:
            return QMessageBox.warning(self, 'FF Multi Converter - ' + \
                    self.tr('Save Location!'), self.tr(
                   'You have chosen to save every file to its original folder.'
                   '\nYou can change this from preferences.'))

    def get_extensions(self):
        """Returns the from and to extensions.

        Returns: 2 strings
        """
        tab = self.current_tab()
        ext_from = unicode(tab.fromComboBox.currentText())
        ext_to = unicode(tab.toComboBox.currentText())
        # split from the docsting (Audio Only) if it is appropriate
        ext_to = ext_to.split(' ')[0]
        return ext_from, ext_to

    def current_formats(self):
        """Returns the file formats of current tab.

        Returns: list
        """
        index = self.TabWidget.currentIndex()
        tab = self.current_tab()
        if index == 3:
            type_formats = tab.formats.keys()
        else:
            type_formats = tab.formats[:]
            if index == 2:
                type_formats.extend(self.image_tab.extra_img_formats_list)
        return type_formats

    def create_paths_list(self, path_pattern, recursive=True, includes=[]):
        """Creates a list of paths from a path pattern.

        Keyword arguments:
        path_pattern -- a path using the '*' glob pattern
        recursive    -- boolean that indicates if paths should be recursively
                        yielded under given dirs
        includes     -- is a list of file patterns to include in recursive
                        searches

        Returns: list
        """
        def _should_include(path, includes):
            """Returns True if the given path should be included."""
            ext = os.path.splitext(path)[-1]
            if not includes:
                return True
            else:
                return True if ext in includes else False

        paths_list = []
        paths = glob.glob(path_pattern)
        for path in paths:
            if not os.path.islink(path) and os.path.isdir(path) and recursive:
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in sorted(filenames):
                        f = os.path.join(dirpath, filename)
                        if _should_include(f, includes):
                            paths_list.append(f)

            elif _should_include(path, includes):
                paths_list.append(path)

        return paths_list

    def files_to_conv_list(self):
        """Generates paths of files to convert.

        Creates:
        1.files_to_conv -- list with files that must be converted
        The list will contain only the _file if conversion is no recursive

        Returns: list
        """
        _dir, file_name = os.path.split(self.fname)
        base, ext = os.path.splitext(file_name)
        _dir += '/*'
        formats = self.current_formats()

        if not (self.folderCheckBox.isChecked() or \
                                           self.recursiveCheckBox.isChecked()):
            files_to_conv = [self.fname]

        else:
            recursive = True if self.recursiveCheckBox.isChecked() else False
            includes = [ext] if self.extRadioButton.isChecked() else \
                                                     ['.' + i for i in formats]
            files_to_conv = self.create_paths_list(_dir, recursive=recursive,
                                                             includes=includes)

        # put given file first in list
        files_to_conv.remove(self.fname)
        files_to_conv.insert(0, self.fname)

        return files_to_conv

    def build_lists(self, ext_to, files_list):
        """Creates two lists:

        1.conversion_list -- list with dicts to show where each file must be
                             saved.
        Example:
        [{/foo/bar.png : "/foo/bar.png"}, {/f/bar2.png : "/foo2/bar.png"}]
        2.create_folders_list -- a list with folders that must be created

        Keyword arguments:
        ext_to       -- the extension to which each file must be converted to
        files_list   -- list with files to be converted

        Returns: two lists
        """
        rel_path_files_list = []
        folders = []
        create_folders_list = []
        conversion_list = []

        parent_file = files_list[0]
        parent_dir, parent_name = os.path.split(parent_file)
        parent_base, parent_ext = os.path.split(parent_name)
        parent_dir += '/'

        for _file in files_list:
            _dir, name = os.path.split(_file)
            base, ext = os.path.splitext(name)
            _dir += '/'
            y = _dir + self.prefix + base + self.suffix + '.' + ext_to

            if self.saveto_output:
                folder = self.output + '/'
                if self.rebuild_structure:
                    y = re.sub('^'+parent_dir, '', y)
                    y = folder + y
                    rel_path_files_list.append(y)
                    for z in rel_path_files_list:
                        folder_to_create = os.path.split(z)[0]
                        folders.append(folder_to_create)

                    # remove list from duplicates
                    for fol in folders:
                        if not fol in create_folders_list:
                            create_folders_list.append(fol)
                    create_folders_list.sort()
                    # remove first folder because it already exists.
                    create_folders_list.pop(0)
                else:
                    y = re.sub('^'+_dir, '', y)
                    y = folder + y

            if os.path.exists(y):
                _dir2, _name2 = os.path.split(y)
                y = _dir2 + '/~' + _name2
            # Add quotations to path in order to avoid error in special cases
            # such as spaces or special characters.
            _file = '"' + _file + '"'
            y = '"' + y + '"'

            _dict = {}
            _dict[_file] = y
            conversion_list.append(_dict)

        return create_folders_list, conversion_list

    def ok_to_continue(self, ext_from, ext_to):
        """Checks if everything is ok to continue with conversion.

        Checks if:
         - Theres is no given file
         - Given file exists
         - Given output destination exists
         - Given file extension is same with the declared extension
         - Missing dependencies for this file type

        Keyword arguments:
        ext_from -- current file extension
        ext_to -- the extension for file to be converted to

        Returns: boolean
        """
        _file = os.path.split(self.fname)[-1]
        real_ext = os.path.splitext(_file)[-1][1:]
        index = self.TabWidget.currentIndex()
        tab = self.current_tab()

        extension_error = False
        if not real_ext == ext_from:
            extra = self.image_tab.extra_img_formats_dict
            if ext_from in extra:
                # look if real_ext is same type with ext_from and just have
                # different extension. eg: jpg is same as jpeg
                if not any(i == real_ext for i in extra[ext_from]):
                    extension_error = True

        try:
            if self.fname == '':
                raise ValidationError(self.tr(
                                         'You must choose a file to convert!'))
            elif not os.path.exists(self.fname):
                raise ValidationError(self.tr(
                                         'The selected file does not exists!'))
            elif self.output is not None and self.output == '':
                raise ValidationError(self.tr(
                                          'You must choose an output folder!'))
            elif self.output is not None and not os.path.exists(self.output):
                raise ValidationError(self.tr(
                                             'Output folder does not exists!'))
            elif not real_ext == ext_from and extension_error:
                raise ValidationError(self.tr(
                                "File' s extensions is not %1.").arg(ext_from))
            elif (index == 0 or index == 1) and not self.ffmpeg:
                raise ValidationError(self.tr(
                    'Program FFmpeg is not installed.\nYou will not be able '
                    'to convert video and audio files until you install it.'))
            elif index == 2 and not self.pmagick:
                raise ValidationError(self.tr(
                    'PythonMagick is not installed.\nYou will not be able to '
                    'convert image files until you install it.'))
            elif index == 3 and not (self.openoffice or self.libreoffice):
                raise ValidationError(self.tr(
                    'Open/Libre office suite is not installed.\nYou will not '
                    'be able to convert document files until you install it.'))
            elif index == 3 and not self.unoconv:
                raise ValidationError(self.tr(
                    'Program unocov is not installed.\nYou will not be able '
                    'to convert document files until you install it.'))
            if not tab.ok_to_continue():
                return False
            return True

        except ValidationError as e:
            QMessageBox.warning(self, 'FF Multi Converter - ' + \
                                                 self.tr('Error!'), unicode(e))
            return False

    def start_conversion(self):
        """Initialises the Progress dialog."""
        ext_from, ext_to = self.get_extensions()
        if not self.ok_to_continue(ext_from, ext_to):
            return

        delete = self.deleteCheckBox.isChecked()
        files_to_conv = self.files_to_conv_list()
        create_folders_list, conversion_list = self.build_lists(ext_to,
                                                                 files_to_conv)
        if create_folders_list:
            for i in create_folders_list:
                try:
                    os.mkdir(i)
                except OSError:
                    pass

        dialog = progress.Progress(self, conversion_list, delete)
        dialog.exec_()

    def about(self):
        """Shows an About dialog using qt standard dialog."""
        link = 'https://sites.google.com/site/ffmulticonverter/'
        msg = self.tr('Convert among several file types to other extensions')
        QMessageBox.about(self, self.tr('About') + ' FF Multi Converter',
            '''<b> FF Multi Converter {0} </b>
            <p>{1}
            <p><a href="{2}">FF Multi Converter - Home Page</a>
            <p>Copyright &copy; 2011-2012 Ilias Stamatis
            <br>License: GNU GPL3
            <p>Python {3} - Qt {4} - PyQt {5} on {6}'''
            .format(__version__, msg, link, platform.python_version()[:5],
            QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

    def is_installed(self, program):
        """Checks if program is installed."""
        for path in os.getenv('PATH').split(os.pathsep):
            fpath = os.path.join(path, program)
            if os.path.exists(fpath) and os.access(fpath, os.X_OK):
                return True
        return False

    def check_for_dependencies(self):
        """Checks if dependencies are installed and set dependenciesLabel
        status."""
        missing = []
        if self.is_installed('ffmpeg'):
            self.ffmpeg = True
        else:
            self.ffmpeg = False
            missing.append('FFmpeg')
        if self.is_installed('unoconv'):
            self.unoconv = True
        else:
            self.unoconv = False
            missing.append('unoconv')
        if self.is_installed('openoffice.org'):
            self.openoffice = True
        else:
            self.openoffice = False
        if self.is_installed('libreoffice'):
            self.libreoffice = True
        else:
            self.libreoffice = False
        if not self.openoffice and not self.libreoffice:
            missing.append('Open/Libre Office')
        try:
            PythonMagick # PythonMagick has imported earlier
            self.pmagick = True
        except NameError:
            self.pmagick = False
            missing.append('PythonMagick')

        missing = ', '.join(missing) if missing else self.tr('None')
        status = self.tr('Missing dependencies: ') + missing
        self.dependenciesLabel.setText(status)


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

    converter = MainWindow()
    converter.show()
    app.exec_()

if __name__ == '__main__':
    main()
