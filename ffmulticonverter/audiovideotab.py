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

        rotation_options = [
                'None',
                '90 clockwise',
                '90 clockwise + vertical flip',
                '90 counter clockwise',
                '90 counter + vertical flip',
                '180',
                'horizontal flip',
                'vertical flip'
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

        preserveaspectCheckBox = QCheckBox(self.tr("Preserve aspect ratio"))
        preservesizeCheckBox = QCheckBox(self.tr("Preserve video size"))

        preserve_layout = utils.add_to_layout(
                'v', preserveaspectCheckBox, preservesizeCheckBox)

        videosettings_layout = QHBoxLayout()
        for a, b in zip(labels, widgets):
            a.setText('<html><p align="center">{0}</p></html>'.format(a.text()))
            layout = utils.add_to_layout('v', a, b)
            videosettings_layout.addLayout(layout)
            if a == aspectLabel:
                # add vidaspectCB in layout after aspectLabel
                videosettings_layout.addLayout(preserve_layout)

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

        time_format = " (hh:mm:ss):"
        beginLabel = QLabel(self.tr("Split file. Begin time") + time_format)
        beginLineEdit = QLineEdit()
        durationLabel = QLabel(self.tr("Duration") + time_format)
        durationLineEdit = QLineEdit()

        hlayout4 = utils.add_to_layout(
                'h',  beginLabel, beginLineEdit, durationLabel,
                durationLineEdit)

        embedLabel = QLabel(self.tr("Embed subtitle:"))
        embedLineEdit = QLineEdit()
        embedLineEdit.setReadOnly(True)
        embedToolButton = QToolButton()
        embedToolButton.setText("...")

        rotateLabel = QLabel(self.tr("Rotation:"))
        rotateComboBox = QComboBox()
        rotateComboBox.addItems(rotation_options)

        hlayout5 = utils.add_to_layout(
                'h', rotateLabel, rotateComboBox, embedLabel, embedLineEdit,
                embedToolButton)

        hidden_layout = utils.add_to_layout(
                'v', videosettings_layout, audiosettings_layout,
                hlayout4, hlayout5)

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
        preserveaspectCheckBox.toggled.connect(
                lambda: aspect1LineEdit.setEnabled(
                        not preserveaspectCheckBox.isChecked())
                )
        preserveaspectCheckBox.toggled.connect(
                lambda: aspect2LineEdit.setEnabled(
                        not preserveaspectCheckBox.isChecked())
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
        self.preserveaspectCheckBox = preserveaspectCheckBox
        self.preservesizeCheckBox = preservesizeCheckBox
        self.freqComboBox = freqComboBox
        self.chan1RadioButton = chan1RadioButton
        self.chan2RadioButton = chan2RadioButton
        self.audio_bitrateComboBox = audio_bitrateComboBox
        self.threadsLineEdit = threadsLineEdit
        self.audcodecComboBox = audcodecComboBox
        self.audcodecLineEdit = audcodecLineEdit
        self.moreButton = moreButton
        self.beginLineEdit = beginLineEdit
        self.durationLineEdit = durationLineEdit
        self.embedLineEdit = embedLineEdit
        self.rotateComboBox = rotateComboBox

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
                self.audcodecLineEdit, self.beginLineEdit, self.embedLineEdit,
                self.vidcodecLineEdit, self.durationLineEdit
                ]
        for i in lines:
            i.clear()

        self.freqComboBox.setCurrentIndex(0)
        self.audio_bitrateComboBox.setCurrentIndex(0)
        self.rotateComboBox.setCurrentIndex(0)
        self.preserveaspectCheckBox.setChecked(False)
        self.preservesizeCheckBox.setChecked(False)
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
