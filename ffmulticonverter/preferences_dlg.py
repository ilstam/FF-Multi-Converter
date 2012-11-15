#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011-2012 Ilias Stamatis <stamatis.iliass@gmail.com>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from PyQt4.QtCore import QSettings
from PyQt4.QtGui import (QDialog, QWidget, QGridLayout, QHBoxLayout,
                  QVBoxLayout, QSpacerItem, QLabel, QRadioButton, QButtonGroup,
                  QCheckBox, QLineEdit, QToolButton, QTabWidget,
                  QDialogButtonBox, QFileDialog)

import os
import pyqttools


class Preferences(QDialog):
    def __init__(self, parent=None):
        super(Preferences, self).__init__(parent)
        self.parent = parent
        self.home = os.getenv('HOME')

        saveLabel = QLabel('<html><b>' + self.tr('Save files') + '</b></html>')
        self.saveto_outRadioButton = QRadioButton(self.tr(
                                       'Save all files\nto ouput destination'))
        self.saveto_origRadioButton = QRadioButton(
                             self.tr('Save each file to\nits original folder'))
        self.group = QButtonGroup()
        self.group.addButton(self.saveto_outRadioButton)
        self.group.addButton(self.saveto_origRadioButton)
        saving_dest_layout = pyqttools.add_to_layout(QHBoxLayout(),
                 self.saveto_outRadioButton, self.saveto_origRadioButton, None)

        exist_Label = QLabel(self.tr('Existing files:'))
        self.exst_add_prefixRadioButton = QRadioButton(self.tr(
                                                             "Add '~' prefix"))
        self.exst_overwriteRadioButton = QRadioButton(self.tr('Overwrite'))
        exist_layout = pyqttools.add_to_layout(QHBoxLayout(),
               self.exst_add_prefixRadioButton, self.exst_overwriteRadioButton)

        self.rebuildCheckBox = QCheckBox(self.tr('Rebuild files structure'))
        defaultLabel = QLabel(self.tr('Default output destination:'))
        self.defaultLineEdit = QLineEdit()
        self.defaultToolButton = QToolButton()
        self.defaultToolButton.setText('...')
        deafult_fol_layout = pyqttools.add_to_layout(QHBoxLayout(),
                                  self.defaultLineEdit, self.defaultToolButton)
        name_Label = QLabel('<html><b>' + self.tr('Name files') +'</b></html>')
        prefixLabel = QLabel(self.tr('Prefix:'))
        suffixLabel = QLabel(self.tr('Suffix:'))
        self.prefixLineEdit = QLineEdit()
        self.suffixLineEdit = QLineEdit()
        grid = pyqttools.add_to_grid(QGridLayout(),
                                            [prefixLabel, self.prefixLineEdit],
                                            [suffixLabel, self.suffixLineEdit])
        prefix_layout = pyqttools.add_to_layout(QHBoxLayout(), grid, None)

        tabwidget1_layout = pyqttools.add_to_layout(QVBoxLayout(), saveLabel,
               QSpacerItem(14, 13), saving_dest_layout, self.rebuildCheckBox,
               QSpacerItem(14, 13), exist_Label, exist_layout,
               QSpacerItem(14, 13), defaultLabel, deafult_fol_layout,
               QSpacerItem(13, 13), name_Label, QSpacerItem(14, 13),
               prefix_layout)

        ffmpegLabel = QLabel('<html><b>' + self.tr('FFmpeg') +'</b></html>')
        default_commandLabel = QLabel(self.tr('Default command:'))
        self.commandLineEdit = QLineEdit()
        useLabel = QLabel(self.tr('Use:'))
        self.ffmpegRadioButton = QRadioButton(self.tr('FFmpeg'))
        self.avconvRadioButton = QRadioButton(self.tr('avconv'))

        hlayout = pyqttools.add_to_layout(QHBoxLayout(),
                                self.ffmpegRadioButton, self.avconvRadioButton)

        tabwidget2_layout = pyqttools.add_to_layout(QVBoxLayout(), ffmpegLabel,
                QSpacerItem(14, 13), useLabel, hlayout, QSpacerItem(14, 13),
                default_commandLabel, self.commandLineEdit, None)

        widget1 = QWidget()
        widget1.setLayout(tabwidget1_layout)
        widget2 = QWidget()
        widget2.setLayout(tabwidget2_layout)
        self.TabWidget = QTabWidget()
        self.TabWidget.addTab(widget1, self.tr('General'))
        self.TabWidget.addTab(widget2, self.tr('Audio/Video'))

        self.buttonBox = QDialogButtonBox(
                                   QDialogButtonBox.Ok|QDialogButtonBox.Cancel)

        final_layout = pyqttools.add_to_layout(QVBoxLayout(), self.TabWidget,
                                                          None, self.buttonBox)
        self.setLayout(final_layout)

        self.saveto_outRadioButton.clicked.connect(lambda:
                                             self.radiobutton_changed('ouput'))
        self.saveto_origRadioButton.clicked.connect(lambda:
                                          self.radiobutton_changed('original'))
        self.defaultToolButton.clicked.connect(self.open_dir)
        self.buttonBox.accepted.connect(self.save_settings)
        self.buttonBox.rejected.connect(self.reject)

        settings = QSettings()
        saveto_output = settings.value('saveto_output').toBool()
        rebuild_structure = settings.value('rebuild_structure').toBool()
        overwrite_existing = settings.value('overwrite_existing').toBool()
        default_output = settings.value('default_output').toString()
        prefix = settings.value('prefix').toString()
        suffix = settings.value('suffix').toString()
        avconv_prefered = settings.value('avconv_prefered').toBool()
        default_command = settings.value('default_command').toString()

        if saveto_output:
            self.saveto_outRadioButton.setChecked(True)
        else:
            self.saveto_origRadioButton.setChecked(True)
            self.rebuildCheckBox.setEnabled(False)
            self.defaultLineEdit.setEnabled(False)
        if rebuild_structure:
            self.rebuildCheckBox.setChecked(True)
        if overwrite_existing:
            self.exst_overwriteRadioButton.setChecked(True)
        else:
            self.exst_add_prefixRadioButton.setChecked(True)
        if default_output:
            self.defaultLineEdit.setText(default_output)
        if prefix:
            self.prefixLineEdit.setText(prefix)
        if suffix:
            self.suffixLineEdit.setText(suffix)
        if avconv_prefered:
            self.avconvRadioButton.setChecked(True)
        else:
            self.ffmpegRadioButton.setChecked(True)
        if default_command:
            self.commandLineEdit.setText(default_command)
        else:
            self.commandLineEdit.setText('-ab 320k -ar 48000 -ac 2')

        if not self.parent.ffmpeg:
            self.avconvRadioButton.setChecked(True)
            self.ffmpegRadioButton.setEnabled(False)
        if not self.parent.avconv:
            self.ffmpegRadioButton.setChecked(True)
            self.avconvRadioButton.setEnabled(False)

        self.resize(414, 457)
        self.setWindowTitle(self.tr('Preferences'))

    def radiobutton_changed(self, data):
        enable = bool(data == 'ouput')
        self.rebuildCheckBox.setEnabled(enable)
        self.defaultLineEdit.setEnabled(enable)

    def open_dir(self):
        """Uses standard QtDialog to get directory name."""
        if self.defaultLineEdit.isEnabled():
            _dir = QFileDialog.getExistingDirectory(self, 'FF Multi Converter '
                '- ' + self.tr('Choose default output destination'), self.home)
            _dir = unicode(_dir)
            if _dir:
                self.defaultLineEdit.setText(_dir)

    def save_settings(self):
        """Defines settings before accept the dialog."""
        saveto_output = self.saveto_outRadioButton.isChecked()
        rebuild_structure = self.rebuildCheckBox.isChecked() and \
                                               self.rebuildCheckBox.isEnabled()
        overwrite_existing = self.exst_overwriteRadioButton.isChecked()
        default_output = unicode(self.defaultLineEdit.text())
        prefix = unicode(self.prefixLineEdit.text())
        suffix = unicode(self.suffixLineEdit.text())
        avconv_prefered = self.avconvRadioButton.isChecked()
        default_command = unicode(self.commandLineEdit.text())

        settings = QSettings()
        settings.setValue('saveto_output', saveto_output)
        settings.setValue('rebuild_structure', rebuild_structure)
        settings.setValue('overwrite_existing', overwrite_existing)
        settings.setValue('default_output', default_output)
        settings.setValue('prefix', prefix)
        settings.setValue('suffix', suffix)
        settings.setValue('avconv_prefered', avconv_prefered)
        settings.setValue('default_command', default_command)

        self.accept()


if __name__ == '__main__':
    #test dialog
    from PyQt4.QtGui import QApplication
    import sys
    app = QApplication(sys.argv)
    dialog = Preferences()
    dialog.show()
    app.exec_()
