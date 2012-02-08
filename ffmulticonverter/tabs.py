#!/usr/bin/python
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
from PyQt4.QtGui import (QApplication, QWidget, QFrame, QGridLayout,
                  QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QSpacerItem,
                  QLineEdit, QComboBox, QButtonGroup, QRadioButton,
                  QPushButton, QMessageBox, QRegExpValidator)

import os
import subprocess
import shlex
import shutil
import re
import time

import data
import pyqttools

try:
    import PythonMagick
except ImportError:
    pass

class ValidationError(Exception): pass
class HeightLineError(ValidationError): pass
class WidthLineError(ValidationError): pass
class AspectLineError(ValidationError): pass

class Tab(QWidget):
    """Standard ui and methods for each tab."""
    def __init__(self, parent):
        super(Tab, self).__init__(parent)
        self.parent = parent

        label1 = QLabel(QApplication.translate('Tab', 'Convert from:'))
        label2 = QLabel(QApplication.translate('Tab', 'Convert to:'))
        self.fromComboBox = QComboBox()
        self.toComboBox = QComboBox()
        grid = pyqttools.add_to_grid(QGridLayout(),
                        [label1, self.fromComboBox], [label2, self.toComboBox])
        self.layout = pyqttools.add_to_layout(QVBoxLayout(), grid)
        self.setLayout(self.layout)

        self.update_comboboxes()

    def update_comboboxes(self):
        """Add items to comboboxes."""
        self.fromComboBox.addItems(self.formats)
        self.toComboBox.addItems(self.formats)

    def resize_parent(self):
        """Resizes MainWindow"""
        if self.frame.isVisible():
            self.parent.resize(685, 453)
        else:
            self.parent.setMinimumSize(685, 378)
            self.parent.resize(685, 378)

    def create_hidden_layout(self, layout):
        """Creates hidden widget

        Creates a QFrame and a QPushButton.
        Clicking the button for the first time the frame will be displayed and 
        by clicking it again the fraim will be hidden.        
        """
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.moreButton = QPushButton(QApplication.translate('Tab', 'More'))
        moreSizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.moreButton.setSizePolicy(moreSizePolicy)
        self.moreButton.setCheckable(True)
        hlayout = pyqttools.add_to_layout(QHBoxLayout(), line, self.moreButton)  
        
        self.frame = QFrame()
        self.frame.setLayout(layout)
        self.frame.hide()
        pyqttools.add_to_layout(self.layout, hlayout, self.frame)

        self.moreButton.toggled.connect(self.frame.setVisible)
        self.moreButton.toggled.connect(self.resize_parent)        

    def create_LineEdit(self, maxsize, validator, maxlength):
        """Creates a lineEdit

        Keyword arguments:
        maxsize -- maximum size
        validator -- a QValidator
        maxlength - maximum length

        Returns: QLineEdit
        """
        lineEdit = QLineEdit()
        if maxsize is not None:
            lineEdit.setMaximumSize(QSize(maxsize[0], maxsize[1]))
        if validator is not None:
            lineEdit.setValidator(validator)
        if maxlength is not None:
            lineEdit.setMaxLength(maxlength)
        return lineEdit

    def change_to_current_index(self, fname):
        ext = os.path.splitext(fname)[-1][1:]
        try:
            i = self.formats.index(ext)
        except AttributeError:
            #in DocumentTab
            for index, _format in enumerate(sorted(self.formats)):
                if _format == ext:
                    i = index
        except ValueError:
            index = self.parent.TabWidget.currentIndex()
            if index == 2:
                if ext in self.extra_img_formats_list:
                    for x in self.extra_img_formats_dict:
                        for y in self.extra_img_formats_dict[x]:
                            if y == ext:
                                i = self.formats.index(x)
                                break
        try:
            self.fromComboBox.setCurrentIndex(i)
        except NameError:
            pass

    def clear(self):
        pass

    def ok_to_continue(self):
        return True


class AudioTab(Tab):
    """The responsible tab for audio conversions."""
    def __init__(self, parent):
        self.formats = data.audio_formats
        super(AudioTab, self).__init__(parent)

        nochange = self.tr('No Change')
        self.frequency_values = [nochange, '22050', '44100', '48000']
        self.bitrate_values = [nochange, '32', '96', '112', '128', '160',
                                                           '192', '256', '320']

        freqLabel = QLabel(self.tr('Frequency (Hz):'))
        chanLabel = QLabel(self.tr('Channels:'))
        bitrateLabel = QLabel(self.tr('Bitrate (kbps):'))

        self.freqComboBox = QComboBox()
        self.freqComboBox.addItems(self.frequency_values)
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
        self.bitrateComboBox = QComboBox()
        self.bitrateComboBox.addItems(self.bitrate_values)

        labels = [freqLabel, chanLabel, bitrateLabel]
        widgets = [self.freqComboBox, chanlayout, self.bitrateComboBox]

        final_layout = QHBoxLayout()
        for a, b in zip(labels, widgets):
            text = a.text()
            a.setText('<html><p align="center">{0}</p></html>'.format(text))
            layout = pyqttools.add_to_layout(QVBoxLayout(), a, b)
            final_layout.addLayout(layout)

        self.create_hidden_layout(final_layout)

    def clear(self):
        """Clear values."""
        self.freqComboBox.setCurrentIndex(0)
        self.bitrateComboBox.setCurrentIndex(0)
        self.group.setExclusive(False)
        self.chan1RadioButton.setChecked(False)
        self.chan2RadioButton.setChecked(False)
        self.group.setExclusive(True)
        # setExclusive(False) in order to be able to uncheck checkboxes and
        # then setExclusive(True) so only one radio button can be set

    def get_data(self):
        """Collects audio tab data.

        Returns: tuple
        """
        if self.freqComboBox.currentIndex() == 0:
            frequency = ''
        else:
            frequency = ' -ar {0} '.format(self.freqComboBox.currentText())

        if self.chan1RadioButton.isChecked():
            channels = ' -ac 1 '
        elif self.chan2RadioButton.isChecked():
            channels = ' -ac 2 '
        else:
            channels = ''

        if self.bitrateComboBox.currentIndex() == 0:
            bitrate = ''
        else:
            bitrate = ' -ab {0}k '.format(self.bitrateComboBox.currentText())

        return frequency, channels, bitrate

    def start_conversion(self, parent, from_file, to_file):
        """Starts the conversion procedure.

        Returns: boolean
        """
        frequency, channels, bitrate = self.get_data()
        self.convert_audio(from_file, to_file, frequency, channels, bitrate)
        return self.convert_prcs.poll() == 0

    def convert_audio(self, from_file, to_file, frequency='', channels='',
                                                                   bitrate=''):
        """Converts the file format of an audio via ffmpeg.

        Keyword arguments:
        from_file -- the file to be converted
        to_file -- new file's location
        """
        assert isinstance(from_file, unicode) and isinstance(to_file, unicode)
        assert from_file.startswith('"') and from_file.endswith('"')
        assert to_file.startswith('"') and to_file.endswith('"')

        command = 'ffmpeg -y -i {0}{1}{2}{3} {4}'.format(
                              from_file, frequency, channels, bitrate, to_file)
        command = str(QString(command).toUtf8())
        command = shlex.split(command)
        self.convert_prcs = subprocess.Popen(command)
        self.convert_prcs.wait()


class VideoTab(Tab):
    """The responsible tab for video conversions."""
    def __init__(self, parent=None):
        self.formats = data.video_formats
        self.vid_to_aud = data.vid_to_aud
        super(VideoTab, self).__init__(parent)

        pattern = QRegExp(r'^[1-9]\d*')
        validator = QRegExpValidator(pattern, self)

        sizeLabel = QLabel(self.tr('Video Size:'))
        aspectLabel = QLabel(self.tr('Aspect:'))
        frameLabel = QLabel(self.tr('Frame Rate (fps):'))
        bitrateLabel = QLabel(self.tr('Bitrate (kbps):'))

        self.widthLineEdit = self.create_LineEdit((50, 16777215), validator, 4)
        self.heightLineEdit = self.create_LineEdit((50, 16777215), validator,4)
        label = QLabel('x')
        layout1 = pyqttools.add_to_layout(QHBoxLayout(), self.widthLineEdit,
                                                    label, self.heightLineEdit)
        self.aspect1LineEdit = self.create_LineEdit((35, 16777215),validator,2)
        self.aspect2LineEdit = self.create_LineEdit((35, 16777215),validator,2)
        label = QLabel(':')
        layout2 = pyqttools.add_to_layout(QHBoxLayout(), self.aspect1LineEdit,
                                                   label, self.aspect2LineEdit)
        self.frameLineEdit = self.create_LineEdit(None, validator, 4)
        self.bitrateLineEdit = self.create_LineEdit(None, validator, 6)

        labels = [sizeLabel, aspectLabel, frameLabel, bitrateLabel]
        widgets = [layout1, layout2, self.frameLineEdit, self.bitrateLineEdit]

        final_layout = QHBoxLayout()
        for a, b in zip(labels, widgets):
            text = a.text()
            a.setText('<html><p align="center">{0}</p></html>'.format(text))
            layout = pyqttools.add_to_layout(QVBoxLayout(), a, b)
            final_layout.addLayout(layout)

        self.create_hidden_layout(final_layout)

    def update_comboboxes(self):
        """Add items to comboboxes."""
        string = ' ' + self.tr('(Audio only)')
        self.fromComboBox.addItems(self.formats)
        self.toComboBox.addItems(self.formats)
        self.toComboBox.addItems([(i+string) for i in self.vid_to_aud])

    def clear(self):
        """Clear values."""
        lineEdits = [self.widthLineEdit, self.heightLineEdit,
                    self.aspect1LineEdit, self.aspect2LineEdit,
                    self.frameLineEdit, self.bitrateLineEdit]
        for i in lineEdits:
            i.clear()

    def ok_to_continue(self):
        """Checks if everything is ok with videotab to continue with conversion

        Checks if:
         - One lineEdit is active and its pair is empty.
         - One of the size lineEdits has a value less than 50.

        Returns: boolean
        """
        width = self.widthLineEdit.text()
        height = self.heightLineEdit.text()
        aspect1 = self.aspect1LineEdit.text()
        aspect2 = self.aspect2LineEdit.text()
        try:
            if width and not height:
                raise HeightLineError(self.tr(
                                        'The size LineEdit may not be empty.'))
            elif not width and height:
                raise WidthLineError(self.tr(
                                        'The size LineEdit may not be empty.'))
            if width:
                if int(width) < 50:
                    raise WidthLineError(self.tr(
                                     'The size LineEdit must be at least 50.'))
            if height:
                if int(height) < 50:
                    raise HeightLineError(self.tr(
                                     'The size LineEdit must be at least 50.'))
            if (aspect1 and not aspect2) or (not aspect1 and aspect2):
                raise AspectLineError(self.tr(
                                      'The aspect LineEdit may not be empty.'))
            return True
        except WidthLineError as e:
            QMessageBox.warning(self, 'FF Multi Converter - ' + \
                                                 self.tr('Error!'), unicode(e))
            self.widthLineEdit.selectAll()
            self.widthLineEdit.setFocus()
            return False
        except HeightLineError as e:
            QMessageBox.warning(self, 'FF Multi Converter - ' + \
                                                 self.tr('Error!'), unicode(e))
            self.heightLineEdit.selectAll()
            self.heightLineEdit.setFocus()
            return False
        except AspectLineError as e:
            QMessageBox.warning(self, 'FF Multi Converter - ' + \
                                                 self.tr('Error!'), unicode(e))
            self.aspect2LineEdit.setFocus() if aspect1 and not aspect2 \
                                           else self.aspect1LineEdit.setFocus()
            return False

    def get_data(self):
        """Collects video tab data.

        Returns: tuple
        """
        if not self.widthLineEdit.text():
            size = ''
        else:
            width = self.widthLineEdit.text()
            height = self.heightLineEdit.text()
            size = ' -s {0}x{1} '.format(width, height)

        if not self.aspect1LineEdit.text():
            aspect = ''
        else:
            aspect1 = self.aspect1LineEdit.text()
            aspect2 = self.aspect2LineEdit.text()
            aspect = ' -aspect {0}:{1} '.format(aspect1, aspect2)

        if not self.frameLineEdit.text():
            framerate = ''
        else:
            framerate = ' -r {0} '.format(self.frameLineEdit.text())

        if not self.bitrateLineEdit.text():
            bitrate = ' -sameq '
        else:
            bitrate = ' -b {0}k '.format(self.bitrateLineEdit.text())

        return size, aspect, framerate, bitrate

    def count_newfile_frames(self, _file):
        """Counts the number of frames of the new file.

        if new-file fps are greater than old-file fps then returns old_file fps

        Returns: integer
        """

        for i in range(2):
            # do it twice because get_frames() fails some times at first time
            old_file_frames = self.get_frames(_file)
        old_file_duration = self.get_duration(_file)
        if old_file_frames == 0 or old_file_duration == 0:
            return 0

        old_file_fps = old_file_frames / old_file_duration
        text = self.frameLineEdit.text()
        new_file_fps = int(text) if text else 0
        if not new_file_fps or new_file_fps >= old_file_fps:
            new_file_frames = old_file_frames
        else:
            new_file_frames = new_file_fps * old_file_duration

        return new_file_frames

    def get_duration(self, _file):
        """Returns the number of seconds of a video.

        Returns: integer
        """
        cmd = 'ffmpeg -i {0} 2>&1'.format(_file)
        cmd = str(QString(cmd).toUtf8())
        exec_cmd = subprocess.Popen(shlex.split(cmd), stderr=subprocess.PIPE)
        output = unicode(QString(exec_cmd.stderr.read()))
        for i in output.split('\n'):
            if 'Duration:' in i:
                duration = re.sub( r'^\s*Duration:\s*([0-9:]+).*$', r'\1', i)
        try:
            hours, mins, secs = duration.split(':')
            hours = int(hours)
            mins = int(mins)
            secs = int(secs)
            secs += (hours * 3600) + (mins * 60)
            return secs
        except (NameError, ValueError, Exception):
            return 0

    def get_frames(self, _file):
        """Returns the number of frames of a video.

        Returns: integer
        """
        cmd = 'ffmpeg -i {0} -vcodec copy -f rawvideo -y /dev/null'.format(
                                                                         _file)
        cmd = str(QString(cmd).toUtf8())
        exec_cmd = subprocess.Popen(shlex.split(cmd), stderr=subprocess.PIPE)
        try:
            output = unicode(QString(exec_cmd.stderr.read()))
        except IOError:
            #[Errno 4] Interrupted system call
            return 0
        for i in output.split('\n'):
            if 'frame=' in i:
                frames = re.sub( r'^frame=\s*([0-9]+)\s.*$', r'\1', i)

        try:
            frames = int(frames)
        except (NameError, ValueError):
            frames = 0
        return frames

    def start_conversion(self, parent, from_file, to_file):
        """Starts the conversion procedure.

        Returns: boolean
        """
        total_frames = self.count_newfile_frames(from_file)
        size, aspect, framerate, bitrate = self.get_data()
        self.convert_video(from_file, to_file, size, aspect, framerate,bitrate)
        if total_frames == 0:
            self.convert_prcs.wait()
        else:
            while self.convert_prcs.poll() is None:
                time.sleep(1) #deter python loop as quickly as possible
                frames = self.get_frames(to_file)
                parent.refr_bars_signal.emit(frames, total_frames)

        return self.convert_prcs.poll() == 0

    def convert_video(self, from_file, to_file, size='', aspect='',
                                 framerate='', bitrate=' -sameq ', test=False):
        """Converts the file format of a video via ffmpeg.

        Keyword arguments:
        from_file -- the file to be converted
        to_file   -- the new file
        test      -- Boolean, this is for testing purposes
        """
        assert isinstance(from_file, unicode) and isinstance(to_file, unicode)
        assert from_file.startswith('"') and from_file.endswith('"')
        assert to_file.startswith('"') and to_file.endswith('"')

        convert_cmd = 'ffmpeg -y -i {0}{1}{2}{3}{4} {5}'.format(
                          from_file, size, aspect, framerate, bitrate, to_file)
        convert_cmd = str(QString(convert_cmd).toUtf8())
        self.convert_prcs = subprocess.Popen(shlex.split(convert_cmd))


class ImageTab(Tab):
    """The responsible tab for image conversions."""
    def __init__(self, parent):
        self.formats = data.image_formats
        self.extra_img_formats_dict = data.extra_img_formats_dict
        self.extra_img_formats_list = []
        for i in self.extra_img_formats_dict.values():
            self.extra_img_formats_list.extend(i)
        super(ImageTab, self).__init__(parent)

        pattern = QRegExp(r'^[1-9]\d*')
        validator = QRegExpValidator(pattern, self)

        resizeLabel = QLabel(self.tr('Image Size:'))
        resizeLabel.setText('<html><p align="center">{0}</p></html>'.format(
                                                           resizeLabel.text()))
        self.widthLineEdit = self.create_LineEdit((50, 16777215), validator, 4)
        self.heightLineEdit = self.create_LineEdit((50, 16777215), validator,4)
        label = QLabel('x')
        layout1 = pyqttools.add_to_layout(QHBoxLayout(), self.widthLineEdit,
                                                    label, self.heightLineEdit)
        spcr1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spcr2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        vlayout = pyqttools.add_to_layout(QVBoxLayout(), resizeLabel, layout1)
        final_layout = pyqttools.add_to_layout(QHBoxLayout(), vlayout, spcr1, 
                                                                         spcr2)

        self.create_hidden_layout(final_layout)

    def clear(self):
        """Clear values."""
        lineEdits = [self.widthLineEdit, self.heightLineEdit]
        for i in lineEdits:
            i.clear()

    def ok_to_continue(self):
        """Checks if everything is ok with audiotab to continue with conversion

        Checks if:
         - One lineEdit is active and its pair is empty.

        Returns: boolean
        """
        width = self.widthLineEdit.text()
        height = self.heightLineEdit.text()
        try:
            if width and not height:
                raise HeightLineError(self.tr(
                                        'The size LineEdit may not be empty.'))
            elif not width and height:
                raise WidthLineError(self.tr(
                                        'The size LineEdit may not be empty.'))
            return True
        except WidthLineError as e:
            QMessageBox.warning(self, 'FF Multi Converter - ' + \
                                                 self.tr('Error!'), unicode(e))
            self.widthLineEdit.setFocus()
            return False
        except HeightLineError as e:
            QMessageBox.warning(self, 'FF Multi Converter - ' + \
                                                 self.tr('Error!'), unicode(e))
            self.heightLineEdit.setFocus()
            return False

    def get_data(self):
        """Collects image tab data.

        Returns: QString
        """
        if not self.widthLineEdit.text():
            size = ''
        else:
            width = self.widthLineEdit.text()
            height = self.heightLineEdit.text()
            size = '{0}x{1}'.format(width, height)

        return size

    def start_conversion(self, parent, from_file, to_file):
        """Starts the conversion procedure.

        Returns: boolean
        """
        size = str(self.get_data())
        return self.convert_image(from_file, to_file, size)

    def convert_image(self, from_file, to_file, size):
        """Converts the file format of an image.

        Keyword arguments:
        from_file -- the file to be converted
        to_file -- the new file

        Returns: boolean
        """
        assert isinstance(from_file, unicode) and isinstance(to_file, unicode)
        assert from_file.startswith('"') and from_file.endswith('"')
        assert to_file.startswith('"') and to_file.endswith('"')

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


class DocumentTab(Tab):
    """The responsible tab for document conversions."""
    def __init__(self, parent):
        self.formats = data.document_formats
        super(DocumentTab, self).__init__(parent)

        self.fromComboBox.currentIndexChanged.connect(self.refresh_toComboBox)
        self.refresh_toComboBox()

    def update_comboboxes(self):
        """Add items to comboboxes."""
        # create a sorted list with document_formats extensions because
        # self.formats is a dict so values are not sorted
        _list = []
        for ext in self.formats:
            _list.append(ext)
        _list.sort()
        self.fromComboBox.addItems(_list)

    def refresh_toComboBox(self):
        """Add the appropriate values to toComboBox."""
        self.toComboBox.clear()
        text = str(self.fromComboBox.currentText())
        self.toComboBox.addItems([i for i in self.formats[text]])

    def start_conversion(self, parent, from_file, to_file):
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

    def convert_document(self, _file, extension):
        """Converts the file format of a document file.

        Keyword arguments:
        _file -- the file to be converted
        extension -- the extension to convert to

        Returns: boolean
        """
        assert isinstance(_file, unicode)
        assert _file.startswith('"') and _file.endswith('"')
        assert not extension.startswith('.')

        command = 'unoconv --format={0} {1}'.format(extension, _file)
        command = str(QString(command).toUtf8())
        command = shlex.split(command)
        return subprocess.call(command) == 0
