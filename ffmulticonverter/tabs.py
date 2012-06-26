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
from PyQt4.QtGui import (QApplication, QWidget, QFrame, QVBoxLayout,
                  QHBoxLayout, QSizePolicy, QLabel, QSpacerItem, QLineEdit,
                  QComboBox, QButtonGroup, QRadioButton, QPushButton,
                  QMessageBox, QRegExpValidator)

import os
#import subprocess
#import shlex
#import shutil
#import re
#import time

import pyqttools
import presets_dlgs

#try:
#    import PythonMagick
#except ImportError:
#    pass

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
        self.default_command = '-sameq -ab 320k -ar 48000 -ac 2'


        nochange = self.tr('No Change')
        frequency_values = [nochange, '22050', '44100', '48000']
        bitrate_values = [nochange, '32', '96', '112', '128', '160', '192',
                                                              '256', '320']
        pattern = QRegExp(r'^[1-9]\d*')
        validator = QRegExpValidator(pattern, self)


        converttoLabel = QLabel(self.tr('Convert to:'))
        self.extComboBox = QComboBox()
        self.extComboBox.addItems(self.formats)
        hlayout1 = pyqttools.add_to_layout(QHBoxLayout(), converttoLabel,
                                                           self.extComboBox)
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
        self.bitrateComboBox = QComboBox()
        self.bitrateComboBox.addItems(bitrate_values)

        labels = [freqLabel, chanLabel, bitrateLabel]
        widgets = [self.freqComboBox, chanlayout, self.bitrateComboBox]

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


        self.presetButton.clicked.connect(self.choose_preset)        
        self.defaultButton.clicked.connect(self.set_default_command)
        self.moreButton.toggled.connect(self.frame.setVisible)
        self.moreButton.toggled.connect(self.resize_parent)

        self.set_default_command()

    def resize_parent(self):
        """Resizes MainWindow"""
        height = 520 if self.frame.isVisible() else 378
        self.parent.setMinimumSize(660, height)
        self.parent.resize(660, height)

    def clear(self):
        """Clear values."""
        lineEdits = [self.commandLineEdit, self.widthLineEdit,
            self.heightLineEdit, self.aspect1LineEdit, self.aspect2LineEdit,
            self.frameLineEdit, self.bitrateLineEdit]
        for i in lineEdits:
            i.clear()

        self.freqComboBox.setCurrentIndex(0)
        self.bitrateComboBox.setCurrentIndex(0)
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
        if not self.commandLineEdit.text():
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                'Error!'), self.tr('The command LineEdit may not be empty.'))
            self.commandLineEdit.setFocus()
            return False
        return True

    def set_default_command(self):
        self.clear()
        self.commandLineEdit.setText(self.default_command)
        
    def choose_preset(self):
        dialog = presets_dlgs.ShowPresets()
        if dialog.exec_() and dialog.the_command is not None:
                self.commandLineEdit.setText(dialog.the_command)
                self.commandLineEdit.home(False)        


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
