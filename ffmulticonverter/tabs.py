#!/usr/bin/env python
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
from __future__ import division

from PyQt4.QtCore import QString, QRegExp, QSize
from PyQt4.QtGui import (QApplication, QWidget, QFrame, QVBoxLayout,
                  QHBoxLayout, QSizePolicy, QLabel, QSpacerItem, QLineEdit,
                  QComboBox, QButtonGroup, QRadioButton, QPushButton,
                  QMessageBox, QRegExpValidator)

import os
import re
import shutil
import shlex
import subprocess

import pyqttools
import presets_dlgs

try:
    import PythonMagick
except ImportError:
    pass


class ValidationError(Exception): pass

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
                                      None, self.extComboBox, self.extLineEdit)
        commandLabel = QLabel(self.tr('Command:'))
        self.commandLineEdit = QLineEdit()
        self.presetButton = QPushButton(self.tr('Preset'))
        self.defaultButton = QPushButton(self.tr('Default'))
        hlayout2 = pyqttools.add_to_layout(QHBoxLayout(), commandLabel,
                   self.commandLineEdit, self.presetButton, self.defaultButton)

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
                           self.chan1RadioButton, self.chan2RadioButton, spcr2)
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
                              videosettings_layout, audiosettings_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.moreButton = QPushButton(QApplication.translate('Tab', 'More'))
        moreSizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.moreButton.setSizePolicy(moreSizePolicy)
        self.moreButton.setCheckable(True)
        hlayout3 = pyqttools.add_to_layout(QHBoxLayout(), line,self.moreButton)

        self.frame = QFrame()
        self.frame.setLayout(hidden_layout)
        self.frame.hide()

        final_layout = pyqttools.add_to_layout(QVBoxLayout(), hlayout1,
                                                hlayout2, hlayout3, self.frame)
        self.setLayout(final_layout)


        self.extComboBox.currentIndexChanged.connect(self.set_line_enable)
        self.presetButton.clicked.connect(self.choose_preset)
        self.defaultButton.clicked.connect(self.set_default_command)
        self.moreButton.toggled.connect(self.frame.setVisible)
        self.moreButton.toggled.connect(self.resize_parent)
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
        """Resizes MainWindow"""
        height = 520 if self.frame.isVisible() else 378
        self.parent.setMinimumSize(660, height)
        self.parent.resize(660, height)

    def set_line_enable(self):
        """Enable or disable self.extLineEdit."""
        self.extLineEdit.setEnabled(
                          self.extComboBox.currentIndex() == len(self.formats))

    def clear(self):
        """Clear values."""
        lineEdits = [self.commandLineEdit, self.widthLineEdit,
            self.heightLineEdit, self.aspect1LineEdit, self.aspect2LineEdit,
            self.frameLineEdit, self.bitrateLineEdit, self.extLineEdit]
        for i in lineEdits:
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
        """Checks if commanLineEdit is empty in order to continue to conversion

        Returns: boolean
        """
        if not self.parent.ffmpeg and not self.parent.avconv:
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                'Error!'), self.tr('Neither ffmpeg nor avconv are installed.'
                '\nYou will not be able to convert document files until you '
                'install one of them.'))
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
        """Sets the default value to self.commandLineEdit"""
        self.clear()
        self.commandLineEdit.setText(self.parent.default_command)

    def choose_preset(self):
        """Opens the presets dialog and set the appropriate value to
           commandLineEdit.
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
        """Removes any consecutive spaces from a string.

        Returns: String
        """
        temp = string
        string = ''
        for i in temp.split():
            if i:
                string += i + ' '
        return string[:-1]

    def command_elements_change(self, widget):
        """Fill commandLineEdit with the appropriate command parameters."""
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

    def duration_in_seconds(self, duration):
        """Gets a time of type: hh:mm:ss.ts and return the number of seconds.

        Return: integer
        """
        duration = duration.split('.')[0]
        hours, mins, secs = duration.split(':')
        seconds = int(secs)
        seconds += (int(hours) * 3600) + (int(mins) * 60)
        return seconds

    def convert(self, parent, from_file, to_file, command, ffmpeg):
        """Converts an audio/video file.

        Returns: boolean
        """
        assert isinstance(from_file, unicode) and isinstance(to_file, unicode)
        assert from_file.startswith('"') and from_file.endswith('"')
        assert to_file.startswith('"') and to_file.endswith('"')

        converter = 'ffmpeg' if ffmpeg else 'avconv'
        convert_cmd = '{0} -y -i {1} {2} {3}'.format(converter, from_file,
                                                              command, to_file)
        convert_cmd = str(QString(convert_cmd).toUtf8())

        self.process = subprocess.Popen(convert_cmd, shell=True,
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        myline = ''
        while True:
            out = self.process.stderr.read(1)
            if out == '' and self.process.poll() != None:
                break

            myline += out
            if out in ('\r','\n'):
                m = re.search("Duration: ([0-9:.]+), start: [0-9.]+", myline)
                if m:
                    total = self.duration_in_seconds(m.group(1))
                n = re.search("time=([0-9.]+)", myline)
                if n:
                    now_sec = int(float(n.group(1)))
                    parent.refr_bars_signal.emit(100 * now_sec / total)
                myline = ''

        return self.process.poll() == 0


class ImageTab(QWidget):
    def __init__(self, parent):
        super(ImageTab, self).__init__(parent)
        self.parent = parent
        self.name = 'Images'
        self.formats = ['aai', 'bmp', 'cgm', 'dcm', 'dpx', 'emf', 'eps', 'fpx',
                        'gif', 'jbig', 'jng', 'jpeg', 'mrsid', 'p7', 'pdf',
                        'picon', 'png', 'ppm', 'psd', 'rad', 'tga', 'tif',
                        'webp', 'wpg', 'xpm']

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
                          self.widthLineEdit, label, self.heightLineEdit, None)
        final_layout = pyqttools.add_to_layout(QVBoxLayout(),hlayout1,hlayout2)
        self.setLayout(final_layout)

    def clear(self):
        """Clear lineEdits"""
        self.widthLineEdit.clear()
        self.heightLineEdit.clear()

    def ok_to_continue(self):
        """Checks if everything is ok with imagetab to continue conversion

        Checks if:
        - There are missing dependencies
        - Given file can be converted
        - One lineEdit is active and its pair is empty

        Returns: boolean
        """
        file_ext = os.path.splitext(self.parent.fname)[-1][1:]
        width = self.widthLineEdit.text()
        height = self.heightLineEdit.text()

        if not self.parent.pmagick:
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                'Error!'), self.tr('PythonMagick is not installed.\nYou will '
                'not be able to convert image files until you install it.'))
            return False
        if not file_ext in self.formats and not file_ext in self.extra_img:
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                'Error!'), self.tr('Could not convert this file type!'))
            return False
        if (width and not height) or (not width and height):
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                'Error!'), self.tr('The size LineEdit may not be empty.'))
            self.heightLineEdit.setFocus() if width and not height else \
                                                  self.widthLineEdit.setFocus()
            return False
        return True

    def convert(self, from_file, to_file):
        """Converts an image.

        Returns: boolean
        """
        assert isinstance(from_file, unicode) and isinstance(to_file, unicode)
        assert from_file.startswith('"') and from_file.endswith('"')
        assert to_file.startswith('"') and to_file.endswith('"')

        if not self.widthLineEdit.text():
            size = ''
        else:
            width = self.widthLineEdit.text()
            height = self.heightLineEdit.text()
            size = str('{0}x{1}'.format(width, height))

        from_file = str(QString(from_file).toUtf8())[1:-1]
        to_file = str(QString(to_file).toUtf8())[1:-1]
        try:
            if os.path.exists(to_file):
                os.remove(to_file)
            img = PythonMagick.Image(from_file)
            if size:
                img.transform(size)
            img.write(to_file)
            return True
        except (RuntimeError, OSError, Exception):
            return False


class DocumentTab(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(DocumentTab, self).__init__(parent)
        self.name = 'Documents'
        self.formats = { 'doc' : ['odt', 'pdf'],
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
        """Checks if everything is ok with documenttab to continue conversion

        Checks if:
        - There are missing dependencies
        - Given file extension is same with the declared extension

        Returns: boolean
        """
        file_ext = os.path.splitext(self.parent.fname)[-1][1:]
        decl_ext = self.convertComboBox.currentText().split(' ')[0]

        try:
            if not self.parent.unoconv:
                raise ValidationError(self.tr(
                       'Unocov is not installed.\nYou will not be able '
                       'to convert document files until you install it.'))
            if file_ext != decl_ext:
                raise ValidationError(self.tr(
                                    'Given file is not {0}!'.format(decl_ext)))
            return True

        except ValidationError as e:
            QMessageBox.warning(self, 'FF Multi Converter - ' + \
                                                 self.tr('Error!'), unicode(e))
            return False

    def convert(self, from_file, to_file):
        """Starts the conversion procedure.

        Returns: boolean
        """
        from_file = from_file[1:-1]
        to_file = to_file[1:-1]
        _file, extension = os.path.splitext(to_file)
        moved_file = _file + os.path.splitext(from_file)[-1]
        if os.path.exists(moved_file):
            moved_file = _file + '~~' + os.path.splitext(from_file)[-1]
        shutil.copy(from_file, moved_file)

        converted = self.convert_document('"'+moved_file+'"', extension[1:])
        os.remove(moved_file)
        final_file = os.path.splitext(moved_file)[0] + extension
        shutil.move(final_file, to_file)

        return converted

    def convert(self, from_file, to_file):
        """Converts a document.

        Returns: boolean
        """
        assert isinstance(from_file, unicode) and isinstance(to_file, unicode)

        from_file = from_file[1:-1]
        to_file = to_file[1:-1]
        _file, extension = os.path.splitext(to_file)
        moved_file = _file + os.path.splitext(from_file)[-1]
        if os.path.exists(moved_file):
            moved_file = _file + '~~' + os.path.splitext(from_file)[-1]
        shutil.copy(from_file, moved_file)

        command = 'unoconv --format={0} {1}'.format(
                                            extension[1:], '"'+moved_file+'"')
        command = str(QString(command).toUtf8())
        child = subprocess.call(shlex.split(command))

        os.remove(moved_file)
        final_file = os.path.splitext(moved_file)[0] + extension
        shutil.move(final_file, to_file)

        return child == 0
