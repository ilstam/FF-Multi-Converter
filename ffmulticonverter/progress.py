#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011-2012 Ilias Stamatis <stamatis.iliass@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# the Free Software Foundation, either version 3 of the License, or
# it under the terms of the GNU General Public License as published by
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

from PyQt4.QtCore import QString, pyqtSignal
from PyQt4.QtGui import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                  QLabel, QCheckBox, QPushButton, QProgressBar, QMessageBox)

import os
import subprocess
import threading
import shlex

import ffmulticonverter
import pyqttools

class Progress(QDialog):
    """Shows conversion progress in a dialog."""
    # There are two bars in the dialog.
    # One that shows the progress of each file and one for total progress.
    #
    # Audio, image and document conversions don't need much time to be
    # completed so the first bar just shows 0% at the beggining and 100% when
    # conversion done for every file.
    #
    # Video conversions may take some time so the first bar takes values.
    # To find the percentage of progress it counts the frames of output file
    # at regular intervals and compares it to the number of final file
    # expected frames.

    file_converted_signal = pyqtSignal()
    refr_bars_signal = pyqtSignal(int, int)

    def __init__(self, parent, files, delete):
        """Constructs the progress dialog.

        Keyword arguments:
        files -- list with files to be converted
        delete -- boolean that shows if files must removed after conversion
        """
        super(Progress, self).__init__(parent)
        self.parent = parent

        self.files = files
        self.delete = delete
        self.step = 100 / len(files)
        self.ok = 0
        self.error = 0
        self.running = True

        self._type = ''
        ext_to = os.path.splitext(self.files[0].values()[0][1:-1])[-1][1:]
        if ext_to in parent.video_tab.formats:
            if not any(ext_to == i for i in parent.video_tab.vid_to_aud):
                self._type = 'video'

        self.nowLabel = QLabel(self.tr('In progress: '))
        totalLabel = QLabel(self.tr('Total:'))
        self.nowBar = QProgressBar()
        self.nowBar.setValue(0)
        self.totalBar = QProgressBar()
        self.totalBar.setValue(0)
        self.shutdownCheckBox = QCheckBox(self.tr('Shutdown after conversion'))
        self.cancelButton = QPushButton(self.tr('Cancel'))

        hlayout = pyqttools.add_to_layout(QHBoxLayout(), None, self.nowLabel,
                                                                          None)
        hlayout2 = pyqttools.add_to_layout(QHBoxLayout(), None, totalLabel,
                                                                          None)
        hlayout3 = pyqttools.add_to_layout(QHBoxLayout(),
                                                   self.shutdownCheckBox, None)
        hlayout4 = pyqttools.add_to_layout(QHBoxLayout(), None,
                                                             self.cancelButton)
        vlayout = pyqttools.add_to_layout(QVBoxLayout(), hlayout,
                self.nowBar, hlayout2, self.totalBar, None, hlayout3, hlayout4)
        self.setLayout(vlayout)

        self.cancelButton.clicked.connect(self.reject)
        self.file_converted_signal.connect(self.file_converted)
        self.refr_bars_signal.connect(self.refresh_progress_bars)

        self.resize(435, 190)
        self.setWindowTitle('FF Multi Converter - ' + self.tr('Conversion'))

        self.manage_conversions()

    def file_converted(self):
        """Sets progress bars values"""
        self.totalBar.setValue(self.max_value)
        self.nowBar.setValue(100)
        QApplication.processEvents()
        self.files.pop(0)
        self.manage_conversions()

    def manage_conversions(self):
        """Checks whether all files have been converted.
        If not, it will allow convert_a_file() to convert the next file.
        """
        if not self.running:
            return
        if not self.files:
            self.totalBar.setValue(100)
        if self.totalBar.value() >= 100:
            if self.shutdownCheckBox.isChecked():
                cmd = str(QString('shutdown -h now').toUtf8())
                subprocess.call(shlex.split(cmd))
            sum_files = self.ok + self.error
            QMessageBox.information(self, self.tr('Report'),
                       self.tr('Converted: %1/%2').arg(self.ok).arg(sum_files))
            self.accept()
            return
        else:
            self.convert_a_file()

    def reject(self):
        """Uses standard dialog to ask whether procedure must stop or not."""
        if self._type == 'video':
            self.parent.video_tab.manage_convert_prcs('pause')
        else:
            self.running = False
        reply = QMessageBox.question(self,
            'FF Multi Converter - ' + self.tr('Cancel Conversion'),
            self.tr('Are you sure you want to cancel conversion?'),
            QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            QDialog.reject(self)
            if self._type == 'video':
                self.parent.video_tab.manage_convert_prcs('kill')
            else:
                return
        if reply == QMessageBox.Cancel:
            if self._type == 'video':
                self.parent.video_tab.manage_convert_prcs('continue')
            else:
                self.running = True
                self.manage_conversions()

    def convert_a_file(self):
        """Starts the conversion procedure in a second thread."""
        if not self.files:
            return
        from_file = self.files[0].keys()[0]
        to_file = self.files[0].values()[0]

        text = '.../' + from_file.split('/')[-1] if len(from_file) > 40 \
                                                 else from_file
        self.nowLabel.setText(self.tr('In progress: ') + text)
        self.nowBar.setValue(0)

        self.min_value = self.totalBar.value()
        self.max_value = self.min_value + self.step

        def convert():
            tab = self.parent.current_tab()
            if tab.convert(self, from_file, to_file):
                self.ok += 1
                if self.delete:
                    try:
                        os.remove(from_file[1:-1])
                    except OSError:
                        pass
            else:
                self.error += 1
            self.file_converted_signal.emit()

        threading.Thread(target=convert).start()

    def refresh_progress_bars(self, frames, total_frames):
        """Counts the progress rates and sets the progress bars.

        Progress is calculated from the percentage of frames of the new file
        compared to frames of the original file.

        Keyword arguments:
        frames -- number of frames of new created file
        total_frames -- number of total frames of the original file
        """
        assert total_frames > 0
        now_percent = int((frames * 100) / total_frames)
        total_percent = int(((now_percent * self.step) / 100) + self.min_value)

        if now_percent > self.nowBar.value() and not (now_percent > 100):
            self.nowBar.setValue(now_percent)
        if total_percent > self.totalBar.value() and not \
                                              (total_percent > self.max_value):
            self.totalBar.setValue(total_percent)
