#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011-2012 Ilias Stamatis <stamatis.iliass@gmail.com>
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
from __init__ import __version__

from PyQt4.QtCore import (QSettings, QTimer, QLocale, QTranslator,
                  QT_VERSION_STR, PYQT_VERSION_STR)
from PyQt4.QtGui import (QApplication, QMainWindow, QWidget, QGridLayout,
                  QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QToolButton,
                  QCheckBox, QRadioButton, QPushButton, QTabWidget, QIcon,
                  QKeySequence, QFileDialog, QMessageBox)

import os
import sys
import re
import glob
import platform

import tabs
import progress
import pyqttools
import preferences_dlg
import presets_dlgs
import qrc_resources

try:
    import PythonMagick
except ImportError:
    pass


class ValidationError(Exception): pass

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.home = os.getenv('HOME')
        self.fname = ''
        self.output = ''

        select_label = QLabel(self.tr('Select file:'))
        output_label = QLabel(self.tr('Output folder:'))
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

        self.audiovideo_tab = tabs.AudioVideoTab(self)
        self.image_tab = tabs.ImageTab(self)
        self.document_tab = tabs.DocumentTab(self)

        self.tabs = [self.audiovideo_tab, self.image_tab, self.document_tab]
        tab_names = [self.tr('Audio/Video'), self.tr('Images'),
                                                          self.tr('Documents')]
        self.TabWidget = QTabWidget()
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

        c_act = pyqttools.create_action
        openAction = c_act(self, self.tr('Open'), QKeySequence.Open, None,
                                        self.tr('Open a file'), self.open_file)
        convertAction = c_act(self, self.tr('Convert'), 'Ctrl+C', None,
                               self.tr('Convert files'), self.start_conversion)
        quitAction = c_act(self, self.tr('Quit'), 'Ctrl+Q', None, self.tr(
                                                           'Quit'), self.close)
        edit_presetsAction = c_act(self, self.tr('Edit Presets'), 'Ctrl+P',
                                   None, self.tr('Edit Presets'), self.presets)
        importAction = c_act(self, self.tr('Import'), None, None,
                                self.tr('Import presets'), self.import_presets)
        exportAction = c_act(self, self.tr('Export'), None, None,
                                self.tr('Export presets'), self.export_presets)
        resetAction = c_act(self, self.tr('Reset'), None, None,
                                  self.tr('Reset presets'), self.reset_presets)
        clearAction = c_act(self, self.tr('Clear'), None, None,
                                             self.tr('Clear form'), self.clear)
        preferencesAction = c_act(self, self.tr('Preferences'), 'Alt+Ctrl+P',
                                None, self.tr('Preferences'), self.preferences)
        aboutAction = c_act(self, self.tr('About'), 'Ctrl+?', None,
                                                  self.tr('About'), self.about)

        fileMenu = self.menuBar().addMenu(self.tr('File'))
        editMenu = self.menuBar().addMenu(self.tr('Edit'))
        presetsMenu = self.menuBar().addMenu(self.tr('Presets'))
        helpMenu = self.menuBar().addMenu(self.tr('Help'))
        pyqttools.add_actions(fileMenu, [openAction, convertAction, None,
                                                                   quitAction])
        pyqttools.add_actions(presetsMenu, [edit_presetsAction, importAction,
                                                    exportAction, resetAction])
        pyqttools.add_actions(editMenu, [clearAction, None, preferencesAction])
        pyqttools.add_actions(helpMenu, [aboutAction])


        self.TabWidget.currentChanged.connect(self.resize_window)
        self.TabWidget.currentChanged.connect(self.checkboxes_clicked)
        self.fromToolButton.clicked.connect(self.open_file)
        self.toToolButton.clicked.connect(self.open_dir)
        self.convertPushButton.clicked.connect(convertAction.triggered)
        self.folderCheckBox.clicked.connect(
                                     lambda: self.checkboxes_clicked('folder'))
        self.recursiveCheckBox.clicked.connect(
                                  lambda: self.checkboxes_clicked('recursive'))


        self.resize(660, 378)
        self.setWindowTitle('FF Multi Converter')

        QTimer.singleShot(0, self.check_for_dependencies)
        QTimer.singleShot(0, self.set_settings)
        QTimer.singleShot(0, self.audiovideo_tab.set_default_command)

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

        enable = self.recursiveCheckBox.isChecked() or \
                                                self.folderCheckBox.isChecked()
        self.extRadioButton.setEnabled(enable)
        if enable and self.current_tab().name == 'Documents':
            # set typeRadioButton disabled when type == document files,
            # because it is not possible to convert every file format to any
            # other file format.
            self.typeRadioButton.setEnabled(False)
            self.extRadioButton.setChecked(True)
        else:
            self.typeRadioButton.setEnabled(enable)

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

        self.audiovideo_tab.clear()
        self.image_tab.clear()

    def resize_window(self):
        """Hides widgets of AudioVideo tab and resizes the window."""
        self.tabs[0].moreButton.setChecked(False)

    def current_tab(self):
        """Returns current tab."""
        for i in self.tabs:
            if self.tabs.index(i) == self.TabWidget.currentIndex():
                return i

    def set_settings(self):
        """Sets program settings"""        
        settings = QSettings()
        self.saveto_output = settings.value('saveto_output').toBool()
        self.rebuild_structure = settings.value('rebuild_structure').toBool()
        self.overwrite_existing = settings.value('overwrite_existing').toBool()
        self.default_output = unicode(
                                   settings.value('default_output').toString())
        self.prefix = unicode(settings.value('prefix').toString())
        self.suffix = unicode(settings.value('suffix').toString())
        self.avconv_prefered = settings.value('avconv_prefered').toBool()
        self.default_command = unicode(
                                  settings.value('default_command').toString())
        if not self.default_command:
            self.default_command = '-ab 320k -ar 48000 -ac 2'

        if self.saveto_output:
            if self.output is None or self.toLineEdit.text() == '':
                self.output = self.default_output
                self.toLineEdit.setText(self.output)
            self.toLineEdit.setEnabled(True)
        else:
            self.toLineEdit.setEnabled(False)
            self.toLineEdit.setText(self.tr(
                                           'Each file to its original folder'))
            self.output = None

    def open_file(self):
        """Uses standard QtDialog to get file name."""
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

        fname = QFileDialog.getOpenFileName(self, 'FF Multi Converter - ' + \
                                    self.tr('Choose File'), self.home, filters)
        fname = unicode(fname)
        if fname:
            self.fname = fname
            self.fromLineEdit.setText(self.fname)

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

    def preferences(self):
        """Opens the preferences dialog."""
        dialog = preferences_dlg.Preferences(self)
        if dialog.exec_():
            self.set_settings()

    def presets(self):
        """Opens the presets dialog."""
        dialog = presets_dlgs.ShowPresets()
        dialog.exec_()

    def import_presets(self):
        presets_dlgs.ShowPresets().import_presets()

    def export_presets(self):
        presets_dlgs.ShowPresets().export_presets()

    def reset_presets(self):
        presets_dlgs.ShowPresets().reset()

    def ok_to_continue(self):
        """Checks if everything is ok to continue with conversion.

        Checks if:
        - Theres is no given file or no given output destination
        - Given file exists and output destination exists

        Returns: boolean
        """
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
            if not self.current_tab().ok_to_continue():
                return False
            return True

        except ValidationError as e:
            QMessageBox.warning(self, 'FF Multi Converter - ' + \
                                                 self.tr('Error!'), unicode(e))
            return False

    def get_extension(self):
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

    def current_formats(self):
        """Returns the file formats of current tab.

        Returns: list
        """
        tab = self.current_tab()
        if tab.name == 'Documents':
            type_formats = tab.formats.keys()
        elif tab.name == 'Images':
            type_formats = tab.formats[:] + tab.extra_img
        else:
            type_formats = tab.formats[:] + tab.extra_formats
            if tab.extLineEdit.isEnabled():
                type_formats.append(str(tab.extLineEdit.text()))
        return ['.' + i for i in type_formats]

    def should_include(self, path, includes):
        """Returns True if the given path should be included."""
        ext = os.path.splitext(path)[-1]
        if not includes:
            return True
        else:
            return ext in includes

    def create_paths_list(self, path_pattern, recursive=True, includes=[]):
        """Creates a list of paths from a path pattern.

        Keyword arguments:
        path_pattern -- an str path using the '*' glob pattern
        recursive    -- if True, include files recursively
                        if False, include only files in the same folder
        includes     -- list of file patterns to include in recursive searches

        Returns: list
        """
        assert path_pattern.endswith('*'), 'path must end with an asterisk (*)'
        assert all(i.startswith('.') for i in includes), \
                                       'all includes must start with a dot (.)'

        paths_list = []
        paths = glob.glob(path_pattern)
        for path in paths:
            if not os.path.islink(path) and os.path.isdir(path) and recursive:
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in sorted(filenames):
                        f = os.path.join(dirpath, filename)
                        if self.should_include(f, includes):
                            paths_list.append(f)

            elif self.should_include(path, includes):
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
            recursive = self.recursiveCheckBox.isChecked()
            includes = [ext] if self.extRadioButton.isChecked() else formats
            files_to_conv = self.create_paths_list(_dir, recursive,
                                                             includes=includes)

            # put given file first in list
            files_to_conv.remove(self.fname)
            files_to_conv.insert(0, self.fname)

        return files_to_conv

    def build_lists(self, files_list, ext_to, prefix, suffix, output,
                         saveto_output, rebuild_structure, overwrite_existing):
        """Creates two lists:

        1.conversion_list -- list with dicts to show where each file must be
                             saved
        Example:
        [{/foo/bar.png : "/foo/bar.png"}, {/f/bar2.png : "/foo2/bar.png"}]

        2.create_folders_list -- a list with folders that must be created

        Keyword arguments:
        files_list -- list with files to be converted
        ext_to     -- the extension to which each file must be converted to
        prefix     -- string that will be added as a prefix to all filenames
        suffix     -- string that will be added as a suffix to all filenames
        output     -- the output folder
        saveto_output -- if True, files will be saved at ouput
                       if False, each file will be saved at its original folder
        rebuild_structure  -- if True, file's structure will be rebuild
        overwrite_existing -- if False, a '~' will be added as prefix to
                              filenames

        Returns: two lists
        """
        assert ext_to.startswith('.'), 'ext_to must start with a dot (.)'

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
            y = _dir + prefix + base + suffix + ext_to

            if saveto_output:
                folder = output + '/'
                if rebuild_structure:
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

            if os.path.exists(y) and not overwrite_existing:
                _dir2, _name2 = os.path.split(y)
                y = _dir2 + '/~' + _name2
            # Add quotations to path in order to avoid error in special
            # cases such as spaces or special characters.
            _file = '"' + _file + '"'
            y = '"' + y + '"'

            _dict = {}
            _dict[_file] = y
            conversion_list.append(_dict)

        return conversion_list, create_folders_list

    def start_conversion(self):
        """Initialises the Progress dialog."""
        if not self.ok_to_continue():
            return

        ext_to = self.get_extension()
        files_to_conv = self.files_to_conv_list()
        conversion_list, create_folders_list = self.build_lists(
           files_to_conv, ext_to, self.prefix, self.suffix, self.output,
           self.saveto_output, self.rebuild_structure, self.overwrite_existing)

        if create_folders_list:
            for i in create_folders_list:
                try:
                    os.mkdir(i)
                except OSError:
                    pass

        delete = self.deleteCheckBox.isChecked()
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
        self.ffmpeg = self.is_installed('ffmpeg')
        self.avconv = self.is_installed('avconv')
        if not self.ffmpeg and not self.avconv:
            missing.append('FFmpeg/avconv')
        if self.is_installed('unoconv'):
            self.unoconv = True
        else:
            self.unoconv = False
            missing.append('unoconv')
        try:
            PythonMagick # PythonMagick has imported earlier
            self.pmagick = True
        except NameError:
            self.pmagick = False
            missing.append('PythonMagick')

        missing = ', '.join(missing) if missing else self.tr('None')
        status = self.tr('Missing dependencies:') + ' ' + missing
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
