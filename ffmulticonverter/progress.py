#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011-2013 Ilias Stamatis <stamatis.iliass@gmail.com>
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

from PyQt4.QtCore import QTimer, pyqtSignal
from PyQt4.QtGui import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                  QFrame, QLabel, QPushButton, QProgressBar, QMessageBox,
                  QTextEdit, QCommandLinkButton, QTextCursor, QSizePolicy)

import os
import signal
import threading

import pyqttools


class Progress(QDialog):
    file_converted_signal = pyqtSignal()
    refr_bars_signal = pyqtSignal(int)
    update_text_edit_signal = pyqtSignal(str)

    def __init__(self, parent, files, delete, test=False):
        """Constructs the progress dialog.

        Keyword arguments:
        files -- list with files to be converted
        delete -- boolean that shows if files must removed after conversion
        """
        super(Progress, self).__init__(parent)
        self.parent = parent
        if not test:
            self.tab = self.parent.current_tab()

        self.files = files
        self.delete = delete
        if not test:
            self.step = int(100 / len(files))
        self.ok = 0
        self.error = 0
        self.running = True

        self.nowLabel = QLabel(self.tr('In progress: '))
        totalLabel = QLabel(self.tr('Total:'))
        self.nowBar = QProgressBar()
        self.nowBar.setValue(0)
        self.totalBar = QProgressBar()
        self.totalBar.setValue(0)
        self.cancelButton = QPushButton(self.tr('Cancel'))

        detailsButton = QCommandLinkButton(self.tr('Details'))
        detailsButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed))
        detailsButton.setCheckable(True)
        detailsButton.setMaximumWidth(113)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.frame = QFrame()
        frame_layout = pyqttools.add_to_layout(QHBoxLayout(), self.textEdit)
        self.frame.setLayout(frame_layout)
        self.frame.hide()

        hlayout = pyqttools.add_to_layout(QHBoxLayout(), None, self.nowLabel,
                                                                          None)
        hlayout2 = pyqttools.add_to_layout(QHBoxLayout(), None, totalLabel,
                                                                          None)
        hlayout3 = pyqttools.add_to_layout(QHBoxLayout(), detailsButton, line)
        hlayout4 = pyqttools.add_to_layout(QHBoxLayout(), self.frame)
        hlayout5 = pyqttools.add_to_layout(QHBoxLayout(), None,
                                                             self.cancelButton)
        vlayout = pyqttools.add_to_layout(QVBoxLayout(), hlayout, self.nowBar,
                  hlayout2, self.totalBar, None, hlayout3, hlayout4, hlayout5)
        self.setLayout(vlayout)

        detailsButton.toggled.connect(self.resize_dialog)
        detailsButton.toggled.connect(self.frame.setVisible)
        self.cancelButton.clicked.connect(self.reject)
        self.file_converted_signal.connect(self.file_converted)
        self.refr_bars_signal.connect(self.refresh_progress_bars)
        self.update_text_edit_signal.connect(self.update_text_edit)

        self.resize(484, 200)
        self.setWindowTitle('FF Multi Converter - ' + self.tr('Conversion'))

        if not test:
            QTimer.singleShot(0, self.manage_conversions)

    def resize_dialog(self):
        """Resizes Dialog"""
        height = 200 if self.frame.isVisible() else 366
        self.setMinimumSize(484, height)
        self.resize(484, height)

    def update_text_edit(self, text):
        """Update text of self.textEdit"""
        current = self.textEdit.toPlainText()
        self.textEdit.setText(current+text)
        self.textEdit.moveCursor(QTextCursor.End)

    def manage_conversions(self):
        """Checks whether all files have been converted.
        If not, it will allow convert_a_file() to convert the next file.
        """
        if not self.running:
            return
        if not self.files:
            self.totalBar.setValue(100)
        if self.totalBar.value() >= 100:
            sum_files = self.ok + self.error
            QMessageBox.information(self, self.tr('Report'),
                       self.tr('Converted: %1/%2').arg(self.ok).arg(sum_files))
        else:
            self.convert_a_file()

    def file_converted(self):
        """Sets progress bars values"""
        self.totalBar.setValue(self.max_value)
        self.nowBar.setValue(100)
        QApplication.processEvents()
        self.files.pop(0)
        self.manage_conversions()

    def reject(self):
        """Uses standard dialog to ask whether procedure must stop or not."""
        if not self.files:
            QDialog.accept(self)
            return
        if self.tab.name == 'AudioVideo':
            self.tab.process.send_signal(signal.SIGSTOP) #pause
        else:
            self.running = False
        reply = QMessageBox.question(self,
            'FF Multi Converter - ' + self.tr('Cancel Conversion'),
            self.tr('Are you sure you want to cancel conversion?'),
            QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            QDialog.reject(self)
            if self.tab.name == 'AudioVideo':
                self.tab.process.kill() #kill
            self.thread.join()
        if reply == QMessageBox.Cancel:
            if self.tab.name == 'AudioVideo':
                self.tab.process.send_signal(signal.SIGCONT) #continue
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
        self.nowLabel.setText(self.tr('In progress:') + ' ' + text)
        self.nowBar.setValue(0)

        self.min_value = self.totalBar.value()
        self.max_value = self.min_value + self.step

        def convert():
            if self.tab.name == 'AudioVideo':
                parameters = (self, from_file, to_file,
                           self.tab.commandLineEdit.text(), self.parent.ffmpeg)
            else:
                parameters = (self, from_file, to_file)

            if self.tab.convert(*parameters):
                self.ok += 1
                if self.delete:
                    try:
                        os.remove(from_file[1:-1])
                    except OSError:
                        pass
            else:
                self.error += 1

            self.file_converted_signal.emit()

        self.thread = threading.Thread(target=convert)
        self.thread.start()

    def refresh_progress_bars(self, now_percent):
        """Refresh the values of self.nowBar and self.totalBar"""
        total_percent = int(((now_percent * self.step) / 100) + self.min_value)

        if now_percent > self.nowBar.value() and not (now_percent > 100):
            self.nowBar.setValue(now_percent)
        if total_percent > self.totalBar.value() and not \
                                              (total_percent > self.max_value):
            self.totalBar.setValue(total_percent)


if __name__ == '__main__':
    #test dialog
    import sys
    app = QApplication(sys.argv)
    dialog = Progress(None, [], False, test=True)
    dialog.show()
    app.exec_()
