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

from PyQt4.QtCore import QSettings, QTimer
from PyQt4.QtGui import (
        QDialog, QDialogButtonBox, QFileDialog, QLabel, QLineEdit,
        QRadioButton, QSpacerItem, QTabWidget, QToolButton, QWidget,
        QPlainTextEdit, QPushButton
        )

from ffmulticonverter import utils
from ffmulticonverter import config


class Preferences(QDialog):
    def __init__(self, parent=None, test = False):
        super(Preferences, self).__init__(parent)
        self.parent = parent
        self.test = test

        self.default_videocodecs = [
                'mpeg4', 'msmpeg4', 'mpeg2video', 'h263', 'libx264', 'libxvid',
                'flv', 'libvpx', 'wmv2'
                ]

        self.default_audiocodecs = [
                'libmp3lame', 'libvorbis', 'ac3', 'aac', 'libfaac',
                'libvo_aacenc', 'wmav2', 'mp2', 'copy'
                ]

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
                prefix_layout, None
                )

        ffmpegLabel = QLabel('<html><b>' + self.tr('FFmpeg') +'</b></html>')
        default_commandLabel = QLabel(self.tr('Default command:'))
        commandLineEdit = QLineEdit()
        useLabel = QLabel(self.tr('Use:'))
        ffmpegRadioButton = QRadioButton(self.tr('FFmpeg'))
        avconvRadioButton = QRadioButton(self.tr('avconv'))

        hlayout = utils.add_to_layout('h', ffmpegRadioButton,avconvRadioButton)

        vidcodecsLabel = QLabel(
                '<html><b>' + self.tr('Video codecs') +'</b></html>')
        vidcodecsTextEdit = QPlainTextEdit()
        audcodecsLabel = QLabel(
                '<html><b>' + self.tr('Audio codecs') +'</b></html>')
        audcodecsTextEdit = QPlainTextEdit()

        gridlayout = utils.add_to_grid([vidcodecsLabel, audcodecsLabel], [vidcodecsTextEdit, audcodecsTextEdit])

        defvidcodecsButton = QPushButton(self.tr("Default video codecs"))
        defaudcodecsButton = QPushButton(self.tr("Default audio codecs"))

        hlayout2 = utils.add_to_layout(
                'h', None, defvidcodecsButton, defaudcodecsButton)

        tabwidget2_layout = utils.add_to_layout(
                'v', ffmpegLabel, QSpacerItem(14, 13), useLabel,
                hlayout, QSpacerItem(14, 13), default_commandLabel,
                commandLineEdit, QSpacerItem(20, 20), gridlayout, hlayout2,
                None
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
        defvidcodecsButton.clicked.connect(self.set_default_videocodecs)
        defaudcodecsButton.clicked.connect(self.set_default_audiocodecs)

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
        self.vidcodecsTextEdit = vidcodecsTextEdit
        self.audcodecsTextEdit = audcodecsTextEdit

        self.resize(400, 480)
        self.setWindowTitle(self.tr('Preferences'))

        QTimer.singleShot(0, self.load_settings)

    def load_settings(self):
        """Load settings and update graphical widgets with loaded values."""
        settings = QSettings()
        overwrite_existing = utils.str_to_bool(
                settings.value('overwrite_existing'))
        default_output = settings.value('default_output')
        prefix = settings.value('prefix')
        suffix = settings.value('suffix')
        avconv_prefered = utils.str_to_bool(settings.value('avconv_prefered'))
        default_command = settings.value('default_command')
        videocodecs = settings.value('videocodecs')
        audiocodecs = settings.value('audiocodecs')

        # QSettings.value() returns str() in python3, not QVariant() as in p2
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
            self.commandLineEdit.setText(config.default_ffmpeg_cmd)

        if not self.test and not self.parent.ffmpeg:
            self.avconvRadioButton.setChecked(True)
            self.ffmpegRadioButton.setEnabled(False)
        if not self.test and not self.parent.avconv:
            self.ffmpegRadioButton.setChecked(True)
            self.avconvRadioButton.setEnabled(False)

        if not videocodecs:
            self.set_default_videocodecs()
        else:
            self.vidcodecsTextEdit.setPlainText(videocodecs)
        if not audiocodecs:
            self.set_default_audiocodecs
        else:
            self.audcodecsTextEdit.setPlainText(audiocodecs)

    def set_default_videocodecs(self):
        self.vidcodecsTextEdit.setPlainText("\n".join(self.default_videocodecs))

    def set_default_audiocodecs(self):
        self.audcodecsTextEdit.setPlainText("\n".join(self.default_audiocodecs))

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
        # remove empty codecs
        videocodecs = []
        for i in self.vidcodecsTextEdit.toPlainText().split("\n"):
            i = i.strip()
            if i:
                videocodecs.append(i)
        videocodecs = "\n".join(videocodecs)

        audiocodecs = []
        for i in self.audcodecsTextEdit.toPlainText().split("\n"):
            i = i.strip()
            if i:
                audiocodecs.append(i)
        audiocodecs = "\n".join(audiocodecs)

        settings = QSettings()
        settings.setValue(
                'overwrite_existing', self.exst_overwriteRadioButton.isChecked())
        settings.setValue(
                'default_output', self.defaultLineEdit.text())
        settings.setValue(
                'prefix', self.prefixLineEdit.text())
        settings.setValue(
                'suffix', self.suffixLineEdit.text())
        settings.setValue(
                'avconv_prefered', self.avconvRadioButton.isChecked())
        settings.setValue(
                'default_command', self.commandLineEdit.text())
        settings.setValue(
                'videocodecs', videocodecs)
        settings.setValue(
                'audiocodecs', audiocodecs)

        self.accept()
