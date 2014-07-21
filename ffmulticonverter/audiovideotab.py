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

import re

from PyQt4.QtCore import QRegExp, QSize
from PyQt4.QtGui import (
        QApplication, QWidget, QComboBox, QLineEdit, QLabel, QRegExpValidator,
        QPushButton, QCheckBox, QRadioButton, QHBoxLayout, QSpacerItem,
        QSizePolicy, QFrame, QButtonGroup, QMessageBox, QToolButton
        )

from ffmulticonverter import utils
from ffmulticonverter import presets_dlgs


class AudioVideoTab(QWidget):
    def __init__(self, parent):
        super(AudioVideoTab, self).__init__(parent)
        self.parent = parent
        self.name = 'AudioVideo'

        self.formats = [
                '3gp', 'aac', 'ac3', 'afc', 'aiff', 'amr', 'asf', 'au', 'avi',
                'dvd', 'flac', 'flv', 'mka', 'mkv', 'mmf', 'mov', 'mp2', 'mp3',
                'mp4', 'mpeg', 'ogg', 'ogv', 'psp', 'rm', 'spx', 'vob', 'wav',
                'webm', 'wma', 'wmv'
                ]

        rotation_options = [
                'None',
                '90 clockwise',
                '90 clockwise + vertical flip',
                '90 counter clockwise',
                '90 counter clockwise + vertical flip',
                '180',
                'horizontal flip',
                'vertical flip'
                ]

        self.defaultStr = self.tr('Default')
        frequency_values = [self.defaultStr, '22050', '44100', '48000']
        bitrate_values = [
                self.defaultStr,
                '32', '96', '112', '128', '160', '192', '256', '320'
                ]
        validator = QRegExpValidator(QRegExp(r'^[1-9]\d*'), self)

        converttoQL = QLabel(self.tr('Convert to:'))
        self.extQCB = QComboBox()
        self.extQCB.setMinimumWidth(130)
        vidcodecQL = QLabel('Video codec:')
        self.vidcodecQCB = QComboBox()
        audcodecQL = QLabel('Audio codec:')
        self.audcodecQCB = QComboBox()

        hlayout1 = utils.add_to_layout(
                'h', converttoQL, self.extQCB, QSpacerItem(150, 20),
                vidcodecQL, self.vidcodecQCB, audcodecQL, self.audcodecQCB)

        commandQL = QLabel(self.tr('Command:'))
        self.commandQLE = QLineEdit()
        self.presetQPB = QPushButton(self.tr('Preset'))
        self.defaultQPB = QPushButton(self.defaultStr)
        hlayout2 = utils.add_to_layout(
                'h', commandQL, self.commandQLE, self.presetQPB,
                self.defaultQPB)

        sizeQL = QLabel(self.tr('Video Size:'))
        aspectQL = QLabel(self.tr('Aspect:'))
        frameQL = QLabel(self.tr('Frame Rate (fps):'))
        bitrateQL = QLabel(self.tr('Video Bitrate (kbps):'))

        self.widthQLE = utils.create_LineEdit((70, 16777215), validator, 4)
        self.heightQLE = utils.create_LineEdit((70, 16777215), validator, 4)
        label = QLabel('<html><p align="center">x</p></html>')
        layout1 = utils.add_to_layout('h', self.widthQLE, label,self.heightQLE)
        self.aspect1QLE = utils.create_LineEdit((50, 16777215), validator, 2)
        self.aspect2QLE = utils.create_LineEdit((50, 16777215), validator, 2)
        label = QLabel('<html><p align="center">:</p></html>')
        layout2 = utils.add_to_layout(
                'h', self.aspect1QLE, label, self.aspect2QLE)
        self.frameQLE = utils.create_LineEdit((120, 16777215), validator, 4)
        self.bitrateQLE = utils.create_LineEdit((130, 16777215), validator, 6)

        labels = [sizeQL, aspectQL, frameQL, bitrateQL]
        widgets = [layout1, layout2, self.frameQLE, self.bitrateQLE]

        self.preserveaspectQChB = QCheckBox(self.tr("Preserve aspect ratio"))
        self.preservesizeQChB = QCheckBox(self.tr("Preserve video size"))

        preserve_layout = utils.add_to_layout(
                'v', self.preserveaspectQChB, self.preservesizeQChB)

        videosettings_layout = QHBoxLayout()
        for a, b in zip(labels, widgets):
            a.setText('<html><p align="center">{0}</p></html>'.format(a.text()))
            layout = utils.add_to_layout('v', a, b)
            videosettings_layout.addLayout(layout)
            if a == aspectQL:
                # add vidaspectCB in layout after aspectQL
                videosettings_layout.addLayout(preserve_layout)

        freqQL = QLabel(self.tr('Frequency (Hz):'))
        chanQL = QLabel(self.tr('Audio Channels:'))
        bitrateQL = QLabel(self.tr('Audio Bitrate (kbps):'))
        threadsQL = QLabel('Threads:')

        self.freqQCB = QComboBox()
        self.freqQCB.addItems(frequency_values)
        self.chan1QRB = QRadioButton('1')
        self.chan1QRB.setMaximumSize(QSize(51, 16777215))
        self.chan2QRB = QRadioButton('2')
        self.chan2QRB.setMaximumSize(QSize(51, 16777215))
        self.group = QButtonGroup()
        self.group.addButton(self.chan1QRB)
        self.group.addButton(self.chan2QRB)
        spcr1 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        spcr2 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        chanlayout = utils.add_to_layout(
                'h', spcr1, self.chan1QRB, self.chan2QRB, spcr2)
        self.audbitrateQCB = QComboBox()
        self.audbitrateQCB.addItems(bitrate_values)
        validator = QRegExpValidator(QRegExp(r'^[0-9]'), self)
        self.threadsQLE = utils.create_LineEdit((50, 16777215), validator, None)

        labels = [freqQL, bitrateQL, chanQL, threadsQL]
        widgets = [self.freqQCB, self.audbitrateQCB, chanlayout,self.threadsQLE]

        audiosettings_layout = QHBoxLayout()
        for a, b in zip(labels, widgets):
            a.setText('<html><p align="center">{0}</p></html>'.format(a.text()))
            layout = utils.add_to_layout('v', a, b)
            audiosettings_layout.addLayout(layout)

        time_format = " (hh:mm:ss):"
        beginQL = QLabel(self.tr("Split file. Begin time") + time_format)
        self.beginQLE = QLineEdit()
        durationQL = QLabel(self.tr("Duration") + time_format)
        self.duratioinQLE = QLineEdit()

        hlayout4 = utils.add_to_layout(
                'h',  beginQL, self.beginQLE, durationQL, self.duratioinQLE)

        embedQL = QLabel(self.tr("Embed subtitle:"))
        self.embedQLE = QLineEdit()
        self.embedQLE.setReadOnly(True)
        embedToolButton = QToolButton()
        embedToolButton.setText("...")

        rotateQL = QLabel(self.tr("Rotation:"))
        self.rotateQCB = QComboBox()
        self.rotateQCB.addItems(rotation_options)

        hlayout5 = utils.add_to_layout(
                'h', rotateQL, self.rotateQCB, embedQL, self.embedQLE,
                embedToolButton)

        hidden_layout = utils.add_to_layout(
                'v', videosettings_layout, audiosettings_layout,
                hlayout4, hlayout5)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.moreQPB = QPushButton(QApplication.translate('Tab', 'More'))
        self.moreQPB.setSizePolicy(QSizePolicy(QSizePolicy.Fixed))
        self.moreQPB.setCheckable(True)
        hlayout3 = utils.add_to_layout('h', line, self.moreQPB)

        self.frame = QFrame()
        self.frame.setLayout(hidden_layout)
        self.frame.hide()
        #for development
        #self.frame.setVisible(True)

        final_layout = utils.add_to_layout(
                'v', hlayout1, hlayout2, hlayout3, self.frame)
        self.setLayout(final_layout)

        self.presetQPB.clicked.connect(self.choose_preset)
        self.defaultQPB.clicked.connect(self.set_default_command)
        self.moreQPB.toggled.connect(self.frame.setVisible)
        self.moreQPB.toggled.connect(self.resize_parent)
        self.widthQLE.textChanged.connect(self.command_update_size)
        self.heightQLE.textChanged.connect(self.command_update_size)
        self.aspect1QLE.textChanged.connect(self.command_update_aspect)
        self.aspect2QLE.textChanged.connect(self.command_update_aspect)
        self.frameQLE.textChanged.connect(self.command_update_frames)
        self.bitrateQLE.textChanged.connect(self.command_update_vidbitrate)
        self.threadsQLE.textChanged.connect(self.command_update_threads)
        self.freqQCB.currentIndexChanged.connect(self.command_update_frequency)
        self.audbitrateQCB.currentIndexChanged.connect(
                self.command_update_audbitrate)
        self.chan1QRB.clicked.connect(
                lambda: self.command_update_channels('1'))
        self.chan2QRB.clicked.connect(
                lambda: self.command_update_channels('2'))
        self.preserveaspectQChB.toggled.connect(
                lambda: (
                        self.aspect1QLE.setEnabled(
                                not self.preserveaspectQChB.isChecked()),
                        self.aspect2QLE.setEnabled(
                                not self.preserveaspectQChB.isChecked())
                        )
                )
        self.preservesizeQChB.toggled.connect(
                lambda: (
                        self.widthQLE.setEnabled(
                                not self.preservesizeQChB.isChecked()),
                        self.heightQLE.setEnabled(
                                not self.preservesizeQChB.isChecked())
                        )
                )

    def fill_video_comboboxes(self, videocodecs, audiocodecs, extraformats):
        if videocodecs:
            videocodecs = [i for i in videocodecs.split("\n")]
        else:
            videocodecs = []
        if audiocodecs:
            audiocodecs = [i for i in audiocodecs.split("\n")]
        else:
            audiocodecs = []
        if extraformats:
            extraformats = [i for i in extraformats.split("\n")]
        else:
            extraformats = []

        self.vidcodecQCB.clear()
        self.audcodecQCB.clear()
        self.extQCB.clear()
        self.vidcodecQCB.addItems([self.defaultStr] + videocodecs)
        self.audcodecQCB.addItems([self.defaultStr] + audiocodecs)
        self.extQCB.addItems(sorted(self.formats + extraformats))

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
                self.commandQLE, self.widthQLE, self.heightQLE,
                self.aspect1QLE, self.aspect2QLE, self.frameQLE,
                self.bitrateQLE, self.threadsQLE, self.beginQLE,
                self.embedQLE, self.duratioinQLE
                ]
        for i in lines:
            i.clear()

        self.vidcodecQCB.setCurrentIndex(0)
        self.audcodecQCB.setCurrentIndex(0)
        self.freqQCB.setCurrentIndex(0)
        self.audbitrateQCB.setCurrentIndex(0)
        self.rotateQCB.setCurrentIndex(0)
        self.preserveaspectQChB.setChecked(False)
        self.preservesizeQChB.setChecked(False)
        self.group.setExclusive(False)
        self.chan1QRB.setChecked(False)
        self.chan2QRB.setChecked(False)
        self.group.setExclusive(True)
        # setExclusive(False) in order to be able to uncheck checkboxes and
        # then setExclusive(True) so only one radio button can be set

    def ok_to_continue(self):
        """
        Check if everything is ok with audiovideotab to continue conversion.

        Check if:
        - Either ffmpeg or avconv are installed.

        Return True if all tests pass, else False.
        """
        if not self.parent.ffmpeg and not self.parent.avconv:
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                'Error!'), self.tr('Neither ffmpeg nor avconv are installed.'
                '\nYou will not be able to convert audio/video files until you'
                ' install one of them.'))
            return False
        return True

    def set_default_command(self):
        """Set the default value to self.commandQLE."""
        self.clear()
        self.commandQLE.setText(self.parent.default_command)

    def choose_preset(self):
        """
        Open the presets dialog and update self.commandQLE,
        and self.extQCB and with the appropriate values.
        """
        dialog = presets_dlgs.ShowPresets()
        if dialog.exec_() and dialog.the_command is not None:
            self.commandQLE.setText(dialog.the_command)
            self.commandQLE.home(False)
            find = self.extQCB.findText(dialog.the_extension)
            if find >= 0:
                self.extQCB.setCurrentIndex(find)

    def command_update_size(self):
        command = self.commandQLE.text()
        text1 = self.widthQLE.text()
        text2 = self.heightQLE.text()

        if (text1 or text2) and not (text1 and text2):
            return

        regex = r'(\s+|^)-s\s+\d+x\d+(\s+|$)'
        s = ' -s {0}x{1} '.format(text1, text2) if text1 and text2 else ' '
        if re.search(regex, command):
            command = re.sub(regex, s, command)
        else:
            command += s
        command = re.sub(' +', ' ', command).strip()

        self.commandQLE.clear()
        self.commandQLE.setText(command)

    def command_update_aspect(self):
        command = self.commandQLE.text()
        text1 = self.aspect1QLE.text()
        text2 = self.aspect2QLE.text()

        if (text1 or text2) and not (text1 and text2):
            return

        regex = r'(\s+|^)-aspect\s+\d+:\d+(\s+|$)'
        s = ' -aspect {0}:{1} '.format(text1, text2) if text1 and text2 else ' '
        if re.search(regex, command):
            command = re.sub(regex, s, command)
        else:
            command += s
        command = re.sub(' +', ' ', command).strip()

        self.commandQLE.clear()
        self.commandQLE.setText(command)

    def command_update_frames(self):
        command = self.commandQLE.text()
        text = self.frameQLE.text()

        regex = r'(\s+|^)-r\s+\d+(\s+|$)'
        s = ' -r {0} '.format(text) if text else ' '
        if re.search(regex, command):
            command = re.sub(regex, s, command)
        else:
            command += s
        command = re.sub(' +', ' ', command).strip()

        self.commandQLE.clear()
        self.commandQLE.setText(command)

    def command_update_vidbitrate(self):
        command = self.commandQLE.text()
        text = self.bitrateQLE.text()

        regex = r'(\s+|^)-b\s+\d+k(\s+|$)'
        s = ' -b {0}k '.format(text) if text else ' '
        if re.search(regex, command):
            command = re.sub(regex, s, command)
        else:
            command += s
        command = re.sub('-sameq', '', command)
        command = re.sub(' +', ' ', command).strip()

        self.commandQLE.clear()
        self.commandQLE.setText(command)

    def command_update_frequency(self):
        command = self.commandQLE.text()
        text = self.freqQCB.currentText()

        regex = r'(\s+|^)-ar\s+\d+(\s+|$)'
        s = ' -ar {0} '.format(text) if self.freqQCB.currentIndex() != 0 else ' '
        if re.search(regex, command):
            command = re.sub(regex, s, command)
        else:
            command += s
        command = re.sub(' +', ' ', command).strip()

        self.commandQLE.clear()
        self.commandQLE.setText(command)

    def command_update_audbitrate(self):
        command = self.commandQLE.text()
        text = self.audbitrateQCB.currentText()

        regex = r'(\s+|^)-ab\s+\d+k(\s+|$)'
        if self.audbitrateQCB.currentIndex() != 0:
            s = ' -ab {0}k '.format(text)
        else:
            s = ' '

        if re.search(regex, command):
            command = re.sub(regex, s, command)
        else:
            command += s
        command = re.sub(' +', ' ', command).strip()

        self.commandQLE.clear()
        self.commandQLE.setText(command)

    def command_update_channels(self, channel):
        command = self.commandQLE.text()

        regex = r'(\s+|^)-ac\s+\d+(\s+|$)'
        s = ' -ac {0} '.format(channel)
        if re.search(regex, command):
            command = re.sub(regex, s, command)
        else:
            command += s
        command = re.sub(' +', ' ', command).strip()

        self.commandQLE.clear()
        self.commandQLE.setText(command)

    def command_update_threads(self):
        command = self.commandQLE.text()
        text = self.threadsQLE.text()

        regex = r'(\s+|^)-threads\s+\d+(\s+|$)'
        s = ' -threads {0} '.format(text) if text else ' '
        if re.search(regex, command):
            command = re.sub(regex, s, command)
        else:
            command += s
        command = re.sub(' +', ' ', command).strip()

        self.commandQLE.clear()
        self.commandQLE.setText(command)
