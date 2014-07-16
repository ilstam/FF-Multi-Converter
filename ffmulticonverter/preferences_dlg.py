# Copyright (C) 2011-2014 Ilias Stamatis <stamatis.iliass@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
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

from PyQt4.QtCore import QSettings
from PyQt4.QtGui import (
        QDialog, QDialogButtonBox, QFileDialog, QLabel, QLineEdit,
        QRadioButton, QSpacerItem, QTabWidget, QToolButton, QWidget
        )

from ffmulticonverter import utils
from ffmulticonverter import config


class Preferences(QDialog):
    def __init__(self, parent=None, test = False):
        super(Preferences, self).__init__(parent)
        self.parent = parent

        saveLabel = QLabel('<html><b>' + self.tr('Save files') + '</b></html>')
        exist_Label = QLabel(self.tr('Existing files:'))
        exst_add_prefixRadioButton = QRadioButton(self.tr("Add '~' prefix"))
        exst_overwriteRadioButton = QRadioButton(self.tr('Overwrite'))
        exist_layout = utils.add_to_layout(
                'h', exst_add_prefixRadioButton, exst_overwriteRadioButton)

        defaultLabel = QLabel(self.tr('Default output destination:'))
        defaultLineEdit = QLineEdit()
        defaultToolButton = QToolButton()
        defaultToolButton.setText('...')
        deafult_fol_layout = utils.add_to_layout(
                'h', defaultLineEdit, defaultToolButton)
        name_Label = QLabel('<html><b>' + self.tr('Name files') +'</b></html>')
        prefixLabel = QLabel(self.tr('Prefix:'))
        suffixLabel = QLabel(self.tr('Suffix:'))
        prefixLineEdit = QLineEdit()
        suffixLineEdit = QLineEdit()
        grid = utils.add_to_grid(
                [prefixLabel, prefixLineEdit], [suffixLabel, suffixLineEdit])
        prefix_layout = utils.add_to_layout('h', grid, None)

        tabwidget1_layout = utils.add_to_layout(
                'v', saveLabel,
                QSpacerItem(14, 13), exist_Label, exist_layout,
                QSpacerItem(14, 13), defaultLabel, deafult_fol_layout,
                QSpacerItem(13, 13), name_Label, QSpacerItem(14, 13),
                prefix_layout
                )

        ffmpegLabel = QLabel('<html><b>' + self.tr('FFmpeg') +'</b></html>')
        default_commandLabel = QLabel(self.tr('Default command:'))
        commandLineEdit = QLineEdit()
        useLabel = QLabel(self.tr('Use:'))
        ffmpegRadioButton = QRadioButton(self.tr('FFmpeg'))
        avconvRadioButton = QRadioButton(self.tr('avconv'))

        hlayout = utils.add_to_layout('h', ffmpegRadioButton, avconvRadioButton)

        tabwidget2_layout = utils.add_to_layout(
                'v', ffmpegLabel, QSpacerItem(14, 13), useLabel,
                hlayout, QSpacerItem(14, 13), default_commandLabel,
                commandLineEdit, None
                )

        widget1 = QWidget()
        widget1.setLayout(tabwidget1_layout)
        widget2 = QWidget()
        widget2.setLayout(tabwidget2_layout)
        tabWidget = QTabWidget()
        tabWidget.addTab(widget1, self.tr('General'))
        tabWidget.addTab(widget2, self.tr('Audio/Video'))

        buttonBox = QDialogButtonBox(
                QDialogButtonBox.Ok|QDialogButtonBox.Cancel)

        final_layout = utils.add_to_layout('v', tabWidget, None, buttonBox)
        self.setLayout(final_layout)

        defaultToolButton.clicked.connect(self.open_dir)
        buttonBox.accepted.connect(self.save_settings)
        buttonBox.rejected.connect(self.reject)

        settings = QSettings()
        overwrite_existing = utils.str_to_bool(
                settings.value('overwrite_existing'))
        default_output = settings.value('default_output')
        prefix = settings.value('prefix')
        suffix = settings.value('suffix')
        avconv_prefered = utils.str_to_bool(settings.value('avconv_prefered'))
        default_command = settings.value('default_command')

        # QSettings.value() returns str() in python3, not QVariant() as in p2
        if overwrite_existing:
            exst_overwriteRadioButton.setChecked(True)
        else:
            exst_add_prefixRadioButton.setChecked(True)
        if default_output:
            defaultLineEdit.setText(default_output)
        if prefix:
            prefixLineEdit.setText(prefix)
        if suffix:
            suffixLineEdit.setText(suffix)
        if avconv_prefered:
            avconvRadioButton.setChecked(True)
        else:
            ffmpegRadioButton.setChecked(True)
        if default_command:
            commandLineEdit.setText(default_command)
        else:
            commandLineEdit.setText(config.default_ffmpeg_cmd)

        if not test and not self.parent.ffmpeg:
            avconvRadioButton.setChecked(True)
            ffmpegRadioButton.setEnabled(False)
        if not test and not self.parent.avconv:
            ffmpegRadioButton.setChecked(True)
            avconvRadioButton.setEnabled(False)

        #aliasing
        self.exst_add_prefixRadioButton = exst_add_prefixRadioButton
        self.exst_overwriteRadioButton = exst_overwriteRadioButton
        self.defaultLineEdit = defaultLineEdit
        self.defaultToolButton = defaultToolButton
        self.prefixLineEdit = prefixLineEdit
        self.suffixLineEdit = suffixLineEdit
        self.commandLineEdit = commandLineEdit
        self.ffmpegRadioButton = ffmpegRadioButton
        self.avconvRadioButton = avconvRadioButton
        self.buttonBox = buttonBox

        self.resize(400, 390)
        self.setWindowTitle(self.tr('Preferences'))

    def open_dir(self):
        """Get a directory name using a standard Qt dialog and update
        self.defaultLineEdit with dir's name."""
        if self.defaultLineEdit.isEnabled():
            _dir = QFileDialog.getExistingDirectory(
                    self, 'FF Multi Converter - ' +
                    self.tr('Choose default output destination'), config.home
                    )
            if _dir:
                self.defaultLineEdit.setText(_dir)

    def save_settings(self):
        """Set settings values, extracting the appropriate information from
        the graphical widgets."""
        overwrite_existing = self.exst_overwriteRadioButton.isChecked()
        default_output = self.defaultLineEdit.text()
        prefix = self.prefixLineEdit.text()
        suffix = self.suffixLineEdit.text()
        avconv_prefered = self.avconvRadioButton.isChecked()
        default_command = self.commandLineEdit.text()

        settings = QSettings()
        settings.setValue('overwrite_existing', overwrite_existing)
        settings.setValue('default_output', default_output)
        settings.setValue('prefix', prefix)
        settings.setValue('suffix', suffix)
        settings.setValue('avconv_prefered', avconv_prefered)
        settings.setValue('default_command', default_command)

        self.accept()
