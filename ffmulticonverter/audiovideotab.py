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

import re

from PyQt4.QtCore import QRegExp, QSize, QTimer
from PyQt4.QtGui import (
        QApplication, QWidget, QComboBox, QLineEdit, QLabel, QRegExpValidator,
        QPushButton, QCheckBox, QRadioButton, QHBoxLayout, QSpacerItem,
        QSizePolicy, QFrame, QButtonGroup, QMessageBox, QToolButton,
        QFileDialog
        )

from ffmulticonverter import utils
from ffmulticonverter import presets_dlgs
from ffmulticonverter import config


class AudioVideoTab(QWidget):
    def __init__(self, parent):
        super(AudioVideoTab, self).__init__(parent)
        self.parent = parent
        self.name = 'AudioVideo'

        self.defaultStr = self.tr('Default')
        self.DisableStream = self.tr('Disable')

        self.formats = config.video_formats
        frequency_values = [self.defaultStr] + config.video_frequency_values
        bitrate_values = [self.defaultStr] + config.video_bitrate_values

        rotation_options = [
                self.tr('None'),
                '90 ' + self.tr('clockwise'),
                '90 ' + self.tr('clockwise') + ' + ' + self.tr('vertical flip'),
                '90 ' + self.tr('counter clockwise'),
                '90 ' + self.tr('counter clockwise') +
                ' + ' + self.tr('vertical flip'),
                '180',
                self.tr('horizontal flip'),
                self.tr('vertical flip')
                ]

        digits_validator = QRegExpValidator(QRegExp(r'[1-9]\d*'), self)
        digits_validator_wzero = QRegExpValidator(QRegExp(r'\d*'), self)
        digits_validator_minus = QRegExpValidator(QRegExp(r'(-1|[1-9]\d*)'), self)
        time_validator = QRegExpValidator(
                QRegExp(r'\d{1,2}:\d{1,2}:\d{1,2}\.\d+'), self)

        converttoQL = QLabel(self.tr('Convert to:'))
        self.extQCB = QComboBox()
        self.extQCB.setMinimumWidth(100)
        vidcodecQL = QLabel('Video codec:')
        self.vidcodecQCB = QComboBox()
        self.vidcodecQCB.setMinimumWidth(110)
        audcodecQL = QLabel('Audio codec:')
        self.audcodecQCB = QComboBox()
        self.audcodecQCB.setMinimumWidth(110)

        hlayout1 = utils.add_to_layout(
                'h', converttoQL, self.extQCB, QSpacerItem(180, 20),
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

        self.widthQLE = utils.create_LineEdit(
                (70, 16777215), digits_validator_minus, 4)
        self.heightQLE = utils.create_LineEdit(
                (70, 16777215), digits_validator_minus, 4)
        label = QLabel('<html><p align="center">x</p></html>')
        layout1 = utils.add_to_layout('h', self.widthQLE, label,self.heightQLE)
        self.aspect1QLE = utils.create_LineEdit(
                (50, 16777215), digits_validator, 2)
        self.aspect2QLE = utils.create_LineEdit(
                (50, 16777215), digits_validator, 2)
        label = QLabel('<html><p align="center">:</p></html>')
        layout2 = utils.add_to_layout(
                'h', self.aspect1QLE, label, self.aspect2QLE)
        self.frameQLE = utils.create_LineEdit(
                (120, 16777215), digits_validator, 4)
        self.bitrateQLE = utils.create_LineEdit(
                (130, 16777215), digits_validator, 6)

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
        threadsQL = QLabel(self.tr('Threads:'))

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
        self.threadsQLE = utils.create_LineEdit(
                (50, 16777215), digits_validator_wzero, 1)

        labels = [freqQL, bitrateQL, chanQL, threadsQL]
        widgets = [self.freqQCB, self.audbitrateQCB, chanlayout,self.threadsQLE]

        audiosettings_layout = QHBoxLayout()
        for a, b in zip(labels, widgets):
            a.setText('<html><p align="center">{0}</p></html>'.format(a.text()))
            layout = utils.add_to_layout('v', a, b)
            audiosettings_layout.addLayout(layout)

        time_format = " (hh:mm:ss):"
        beginQL = QLabel(self.tr("Split file. Begin time") + time_format)
        self.beginQLE = utils.create_LineEdit(None, time_validator, None)
        durationQL = QLabel(self.tr("Duration") + time_format)
        self.durationQLE = utils.create_LineEdit(None, time_validator, None)

        hlayout4 = utils.add_to_layout(
                'h',  beginQL, self.beginQLE, durationQL, self.durationQLE)

        embedQL = QLabel(self.tr("Embed subtitle:"))
        self.embedQLE = QLineEdit()
        self.embedQTB = QToolButton()
        self.embedQTB.setText("...")

        rotateQL = QLabel(self.tr("Rotate:"))
        self.rotateQCB = QComboBox()
        self.rotateQCB.addItems(rotation_options)

        hlayout5 = utils.add_to_layout(
                'h', rotateQL, self.rotateQCB, embedQL, self.embedQLE,
                self.embedQTB)

        hidden_layout = utils.add_to_layout(
                'v', videosettings_layout, audiosettings_layout,
                hlayout4, hlayout5)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.moreQPB = QPushButton(QApplication.translate('Tab', 'More'))
        self.moreQPB.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.moreQPB.setCheckable(True)
        hlayout3 = utils.add_to_layout('h', line, self.moreQPB)

        self.frame = QFrame()
        self.frame.setLayout(hidden_layout)
        self.frame.hide()

        final_layout = utils.add_to_layout(
                'v', hlayout1, hlayout2, hlayout3, self.frame)
        self.setLayout(final_layout)

        self.presetQPB.clicked.connect(self.choose_preset)
        self.defaultQPB.clicked.connect(self.set_default_command)
        self.embedQTB.clicked.connect(self.open_subtitle_file)
        self.moreQPB.toggled.connect(self.frame.setVisible)
        self.moreQPB.toggled.connect(
                lambda: QTimer.singleShot(100, self.resize_parent))
        self.widthQLE.textChanged.connect(self.command_update_size)
        self.heightQLE.textChanged.connect(self.command_update_size)
        self.aspect1QLE.textChanged.connect(self.command_update_aspect)
        self.aspect2QLE.textChanged.connect(self.command_update_aspect)
        self.frameQLE.textChanged.connect(self.command_update_frames)
        self.bitrateQLE.textChanged.connect(self.command_update_vidbitrate)
        self.threadsQLE.textChanged.connect(self.command_update_threads)
        self.beginQLE.textChanged.connect(self.command_update_begin_time)
        self.durationQLE.textChanged.connect(self.command_update_duration)
        self.embedQLE.textChanged.connect(self.command_update_subtitles)
        self.vidcodecQCB.currentIndexChanged.connect(self.command_update_vcodec)
        self.audcodecQCB.currentIndexChanged.connect(self.command_update_acodec)
        self.freqQCB.currentIndexChanged.connect(self.command_update_frequency)
        self.rotateQCB.currentIndexChanged.connect(self.command_update_rotation)
        self.audbitrateQCB.currentIndexChanged.connect(
                self.command_update_audbitrate)
        self.chan1QRB.clicked.connect(
                lambda: self.command_update_channels('1'))
        self.chan2QRB.clicked.connect(
                lambda: self.command_update_channels('2'))
        self.preserveaspectQChB.toggled.connect(
                self.command_update_preserve_aspect)
        self.preservesizeQChB.toggled.connect(
                self.command_update_preserve_size)

    def resize_parent(self):
        """Give MainWindow its default size."""
        self.parent.setMinimumSize(self.parent.sizeHint())
        self.parent.resize(self.parent.sizeHint())

    def clear(self):
        """Clear all values of graphical widgets."""
        lines = [
                self.commandQLE, self.widthQLE, self.heightQLE,
                self.aspect1QLE, self.aspect2QLE, self.frameQLE,
                self.bitrateQLE, self.threadsQLE, self.beginQLE,
                self.embedQLE, self.durationQLE
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

    def fill_video_comboboxes(self, vcodecs, acodecs, extraformats):
        vcodecs = [i for i in vcodecs.split("\n")] if vcodecs else []
        acodecs = [i for i in acodecs.split("\n")] if acodecs else []
        extraformats = [i for i in extraformats.split("\n")] if extraformats else []

        self.vidcodecQCB.currentIndexChanged.disconnect()
        self.audcodecQCB.currentIndexChanged.disconnect()

        self.vidcodecQCB.clear()
        self.audcodecQCB.clear()
        self.extQCB.clear()
        self.vidcodecQCB.addItems([self.defaultStr, self.DisableStream] + vcodecs)
        self.audcodecQCB.addItems([self.defaultStr, self.DisableStream] + acodecs)
        self.extQCB.addItems(sorted(self.formats + extraformats))

        self.vidcodecQCB.currentIndexChanged.connect(self.command_update_vcodec)
        self.audcodecQCB.currentIndexChanged.connect(self.command_update_acodec)

    def ok_to_continue(self):
        """
        Check if everything is ok with audiovideotab to continue conversion.

        Check if:
        - Either ffmpeg or avconv are installed.

        Return True if all tests pass, else False.
        """
        if self.parent.vidconverter is None:
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                'Error!'), self.tr('Neither ffmpeg nor libav are installed.'
                '\nYou will not be able to convert audio/video files until you'
                ' install one of them.'))
            return False
        return True

    def open_subtitle_file(self):
        """
        Get the filename using standard QtDialog and update embedQLE's text.
        """
        fname = QFileDialog.getOpenFileName(self, 'FF Multi Converter - ' +
                self.tr('Choose File'), config.home, 'Subtitles (*.srt *.sub *.ssa *.ass)')
        if fname:
            self.embedQLE.setText(fname)

    def set_default_command(self):
        """Set the default value to self.commandQLE."""
        self.clear()
        self.commandQLE.setText(self.parent.default_command)

    def choose_preset(self):
        """
        Open the presets dialog and update self.commandQLE,
        and self.extQCB and with the appropriate values.
        """
        dialog = presets_dlgs.ShowPresets(choose=True)
        if dialog.exec_() and dialog.the_command is not None:
            self.clear()
            self.commandQLE.setText(dialog.the_command)
            self.commandQLE.home(False)
            find = self.extQCB.findText(dialog.the_extension)
            if find >= 0:
                self.extQCB.setCurrentIndex(find)

    def command_update_size(self):
        command = self.commandQLE.text()
        text1 = self.widthQLE.text()
        text2 = self.heightQLE.text()

        if not (text1 == '-1' or text2 == '-1'):
            self.preserveaspectQChB.setChecked(False)

        if (text1 or text2) and not (text1 and text2) or (text1 == '-' or
                text2 == '-'):
            return

        regex = r'(\s+|^)-s(:v){0,1}\s+\d+x\d+(\s+|$)'
        if re.search(regex, command):
            command = re.sub(regex, '', command)

        regex = r'(,*\s*){0,1}(scale=-?\d+:-?\d+)(\s*,*\s*){0,1}'
        _filter = "scale={0}:{1}".format(text1, text2) if text1 and text2 else ''

        self.commandQLE.setText(utils.update_cmdline_text(
                command, _filter, regex, bool(text1 and text2), 0, 2))

    def command_update_preserve_size(self):
        checked = self.preservesizeQChB.isChecked()

        self.widthQLE.setEnabled(not checked)
        self.heightQLE.setEnabled(not checked)

        if checked:
            self.widthQLE.clear()
            self.heightQLE.clear()
            # command_update_size() is triggered here

        command = self.commandQLE.text()
        regex = r'(\s+|^)-s\s+\d+x\d+(\s+|$)'
        command = re.sub(' +', ' ', re.sub(regex, ' ', command)).strip()
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
        self.commandQLE.setText(command)

    def command_update_preserve_aspect(self):
        command = self.commandQLE.text()
        checked = self.preserveaspectQChB.isChecked()

        self.aspect1QLE.setEnabled(not checked)
        self.aspect2QLE.setEnabled(not checked)

        if checked:
            self.aspect1QLE.clear()
            self.aspect2QLE.clear()
            # self.command_update_aspect() is triggered here

            regex = r'(,*\s*){0,1}(scale=(-?\d+):(-?\d+))(\s*,*\s*){0,1}'
            search = re.search(regex, command)
            if search:
                width = search.groups()[2]
                height = search.groups()[3]
                if not (width == '-1' or height == '-1'):
                    s = "scale=-1:{0}".format(height)
                    command = re.sub(regex, r'\1{0}\5'.format(s), command)
                    self.widthQLE.setText('-1')
                    self.heightQLE.setText(height)

        regex = r'(\s+|^)-aspect\s+\d+:\d+(\s+|$)'
        command = re.sub(' +', ' ', re.sub(regex, ' ', command)).strip()
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
        self.commandQLE.setText(command)

    def command_update_vidbitrate(self):
        command = self.commandQLE.text()
        text = self.bitrateQLE.text()

        regex = r'(\s+|^)-b(:v){0,1}\s+\d+[kKmM](\s+|$)'
        s = ' -b:v {0}k '.format(text) if text else ' '

        if re.search(regex, command):
            command = re.sub(regex, s, command)
        else:
            command += s

        command = re.sub('-sameq', '', command)
        command = re.sub(' +', ' ', command).strip()

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
        self.commandQLE.setText(command)

    def command_update_audbitrate(self):
        command = self.commandQLE.text()
        text = self.audbitrateQCB.currentText()

        regex = r'(\s+|^)-(ab|b:a)\s+\d+[kKmM](\s+|$)'
        if self.audbitrateQCB.currentIndex() != 0:
            s = ' -b:a {0}k '.format(text)
        else:
            s = ' '

        if re.search(regex, command):
            command = re.sub(regex, s, command)
        else:
            command += s

        command = re.sub(' +', ' ', command).strip()
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
        self.commandQLE.setText(command)

    def command_update_begin_time(self):
        command = self.commandQLE.text()
        text = self.beginQLE.text()

        regex = r'(\s+|^)-ss\s+\S+(\s+|$)'
        s = ' -ss {0} '.format(text) if text else ' '

        if re.search(regex, command):
            command = re.sub(regex, s, command)
        else:
            command += s

        command = re.sub(' +', ' ', command).strip()
        self.commandQLE.setText(command)

    def command_update_duration(self):
        command = self.commandQLE.text()
        text = self.durationQLE.text()

        regex = r'(\s+|^)-t\s+\S+(\s+|$)'
        s = ' -t {0} '.format(text) if text else ' '

        if re.search(regex, command):
            command = re.sub(regex, s, command)
        else:
            command += s

        command = re.sub(' +', ' ', command).strip()
        self.commandQLE.setText(command)

    def command_update_vcodec(self):
        command = self.commandQLE.text()
        text = self.vidcodecQCB.currentText()

        regex = r'(\s+|^)-(vcodec|c:v)\s+\S+(\s+|$)'
        regex_vn = r'(\s+|^)-vn(\s+|$)'
        if self.vidcodecQCB.currentIndex() == 1:
            s = ' -vn '.format(text)
        elif self.vidcodecQCB.currentIndex() == 0:
            s = ' '
        else:
            s = ' -vcodec {0} '.format(text)

        if re.search(regex, command):
            command = re.sub(regex, s, command)
        elif re.search(regex_vn, command):
            command = re.sub(regex_vn, s, command)
        else:
            command += s

        command = re.sub(' +', ' ', command).strip()
        self.commandQLE.setText(command)

    def command_update_acodec(self):
        command = self.commandQLE.text()
        text = self.audcodecQCB.currentText()

        regex = r'(\s+|^)-(acodec|c:a)\s+\S+(\s+|$)'
        regex_an = r'(\s+|^)-an(\s+|$)'
        if self.audcodecQCB.currentIndex() == 1:
            s = ' -an '.format(text)
        elif self.audcodecQCB.currentIndex() == 0:
            s = ' '
        else:
            s = ' -acodec {0} '.format(text)

        if re.search(regex, command):
            command = re.sub(regex, s, command)
        elif re.search(regex_an, command):
            command = re.sub(regex_an, s, command)
        else:
            command += s

        command = re.sub(' +', ' ', command).strip()
        self.commandQLE.setText(command)

    def command_update_subtitles(self):
        command = self.commandQLE.text()
        regex = r'(,*\s*){0,1}(subtitles=\'.*\')(\s*,*\s*){0,1}'

        text = self.embedQLE.text()
        _filter = "subtitles='{0}'".format(text) if text else ''

        self.commandQLE.setText(utils.update_cmdline_text(
                command, _filter, regex, bool(text), 0, 2))

    def command_update_rotation(self):
        command = self.commandQLE.text()
        regex = r'(,*\s*){0,1}(transpose=\d(,\s*transpose=\d)*|vflip|hflip)(\s*,*\s*){0,1}'

        rotate = self.rotateQCB.currentIndex()
        if rotate == 0:   # none
            _filter = ''
        elif rotate == 1: # 90 clockwise
            _filter = 'transpose=1'
        elif rotate == 2: # 90 clockwise + vertical flip
            _filter = 'transpose=3'
        elif rotate == 3: # 90 counter clockwise
            _filter = 'transpose=2'
        elif rotate == 4: # 90 counter clockwise + vertical flip
            _filter = 'transpose=0'
        elif rotate == 5: # 180
            _filter = 'transpose=2,transpose=2'
        elif rotate == 6: # horizontal flip
            _filter = 'hflip'
        elif rotate == 7: # vertical flip
            _filter = 'vflip'

        self.commandQLE.setText(utils.update_cmdline_text(
                command, _filter, regex, bool(rotate != 0), 0, 3))
