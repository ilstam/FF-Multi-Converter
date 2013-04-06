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

from PyQt4.QtCore import pyqtSignal, QString, QTimer
from PyQt4.QtGui import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                  QFrame, QLabel, QPushButton, QProgressBar, QMessageBox,
                  QTextEdit, QCommandLinkButton, QTextCursor, QSizePolicy)

import os
import re
import signal
import threading
import shutil
import subprocess
import shlex
import logging

import pyqttools

try:
    import PythonMagick
except ImportError:
    pass


class Progress(QDialog):
    file_converted_signal = pyqtSignal()
    refr_bars_signal = pyqtSignal(int)
    update_text_edit_signal = pyqtSignal(str)

    def __init__(self, files, _type, cmd, ffmpeg, size, delete,
                 parent=None, test=False):
        """
        Keyword arguments:
        files  -- list with dicts containing file names
        _type  -- 'AudioVideo', 'Images' or 'Documents' depending files type
        cmd    -- ffmpeg command, for audio/video conversions
        ffmpeg -- if True ffmpeg will be used, else avconv
                  for audio/video conversions
        size   -- new image size string of type 'widthxheight' eg. '300x300'
                  for image conversions
        delete -- boolean that shows if files must removed after conversion

        files:
        Each dict have only one key and one corresponding value.
        Key is a file to be converted and it's value is the name of the new
        file that will be converted.

        Example list:
        [{"/foo/bar.png" : "/foo/bar.bmp"}, {"/f/bar2.png" : "/f/bar2.bmp"}]
        """
        super(Progress, self).__init__(parent)
        self.parent = parent
        self._type = _type
        self.cmd = cmd
        self.ffmpeg = ffmpeg
        self.size = size

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
                                          hlayout2, self.totalBar, None,
                                          hlayout3, hlayout4, hlayout5)
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
        """Resize dialog."""
        height = 200 if self.frame.isVisible() else 366
        self.setMinimumSize(484, height)
        self.resize(484, height)

    def update_text_edit(self, txt):
        """Append txt to the end of current self.textEdit's text."""
        current = self.textEdit.toPlainText()
        self.textEdit.setText(current+txt)
        self.textEdit.moveCursor(QTextCursor.End)

    def refresh_progress_bars(self, now_percent):
        """Refresh the values of self.nowBar and self.totalBar."""
        total_percent = int(((now_percent * self.step) / 100) + self.min_value)

        if now_percent > self.nowBar.value() and not (now_percent > 100):
            self.nowBar.setValue(now_percent)
        if (total_percent > self.totalBar.value() and
        not (total_percent > self.max_value)):
            self.totalBar.setValue(total_percent)

    def manage_conversions(self):
        """
        Check whether all files have been converted.
        If not, it will allow convert_a_file() to convert the next file.
        """
        if not self.running:
            return
        if not self.files:
            self.totalBar.setValue(100)
        if self.totalBar.value() >= 100:
            sum_files = self.ok + self.error
            dialog = Report(
                       self.tr('Converted: %1/%2').arg(self.ok).arg(sum_files),
                       self)
            dialog.show()
            if self._type == 'Documents':
                self.parent.docconv = False  # doc conversion end
        else:
            self.convert_a_file()

    def file_converted(self):
        """
        Update progress bars values, remove converted file from self.files
        and call manage_conversions() to continue the process.
        """
        self.totalBar.setValue(self.max_value)
        self.nowBar.setValue(100)
        QApplication.processEvents()
        self.files.pop(0)
        self.manage_conversions()

    def reject(self):
        """
        Use standard dialog to ask whether procedure must stop or not.
        Use the SIGSTOP to stop the conversion process while waiting for user
        to respond and SIGCONT or kill depending on user's answer.
        """
        if not self.files:
            QDialog.accept(self)
            return
        if self._type == 'AudioVideo':
            self.process.send_signal(signal.SIGSTOP)
        self.running = False
        reply = QMessageBox.question(self,
            'FF Multi Converter - ' + self.tr('Cancel Conversion'),
            self.tr('Are you sure you want to cancel conversion?'),
            QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            if self._type == 'AudioVideo':
                self.process.kill()
            if self._type == 'Documents':
                self.parent.docconv = False
            self.running = False
            self.thread.join()
            QDialog.reject(self)
        if reply == QMessageBox.Cancel:
            self.running = True
            if self._type == 'AudioVideo':
                self.process.send_signal(signal.SIGCONT)
            else:
                self.manage_conversions()

    def convert_a_file(self):
        """
        Update self.nowLabel's text with current file's name, set self.nowBar
        value to zero and start the conversion procedure in a second thread
        using threading module.
        """
        if not self.files:
            return
        from_file = self.files[0].keys()[0]
        to_file = self.files[0].values()[0]

        if len(from_file) > 40:
            # split file name if it is too long in order to display it properly
            text = '.../' + from_file.split('/')[-1]
        else:
            text = from_file

        self.nowLabel.setText(self.tr('In progress:') + ' ' + text)
        self.nowBar.setValue(0)

        self.min_value = self.totalBar.value()
        self.max_value = self.min_value + self.step

        if not os.path.exists(from_file[1:-1]):
            self.error += 1
            self.file_converted_signal.emit()
            return

        def convert():
            if self._type == 'AudioVideo':
                conv_func = self.convert_video
                params = (from_file, to_file, self.cmd, self.ffmpeg)
            elif self._type == 'Images':
                conv_func = self.convert_image
                params = (from_file, to_file, self.size)
            else:
                conv_func = self.convert_doc
                params = (from_file, to_file)

            if conv_func(*params):
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

    def duration_in_seconds(self, duration):
        """
        Return the number of seconds of duration, an integer.
        Duration is a strinf of type hh:mm:ss.ts
        """
        duration = duration.split('.')[0]
        hours, mins, secs = duration.split(':')
        seconds = int(secs)
        seconds += (int(hours) * 3600) + (int(mins) * 60)
        return seconds

    def convert_video(self, from_file, to_file, command, ffmpeg):
        """
        Create the ffmpeg command and execute it in a new process using the
        subprocess module. While the process is alive, parse ffmpeg output,
        estimate conversion progress using video's duration.
        With the result, emit the corresponding signal in order progressbars
        to be updated. Also emit regularly the corresponding signal in order
        an textEdit to be updated with ffmpeg's output. Finally, save log
        information.

        Return True if conversion succeed, else False.
        """
        assert isinstance(from_file, unicode) and isinstance(to_file, unicode)
        assert from_file.startswith('"') and from_file.endswith('"')
        assert to_file.startswith('"') and to_file.endswith('"')

        converter = 'ffmpeg' if ffmpeg else 'avconv'
        convert_cmd = '{0} -y -i {1} {2} {3}'.format(converter, from_file,
                                                     command, to_file)
        convert_cmd = str(QString(convert_cmd).toUtf8())
        self.update_text_edit_signal.emit(unicode(convert_cmd, 'utf-8')+'\n')

        self.process = subprocess.Popen(shlex.split(convert_cmd),
                                        stderr=subprocess.STDOUT,
                                        stdout=subprocess.PIPE)

        final_output = myline = str('')
        while True:
            out = str(QString(self.process.stdout.read(1)).toUtf8())
            if out == str('') and self.process.poll() is not None:
                break

            myline += out
            if out in (str('\r'), str('\n')):
                m = re.search("Duration: ([0-9:.]+), start: [0-9.]+", myline)
                if m:
                    total = self.duration_in_seconds(m.group(1))
                n = re.search("time=([0-9:]+)", myline)
                # time can be of format 'time=hh:mm:ss.ts' or 'time=ss.ts'
                # depending on ffmpeg version
                if n:
                    time = n.group(1)
                    if ':' in time:
                        time = self.duration_in_seconds(time)
                    now_sec = int(float(time))
                    try:
                        self.refr_bars_signal.emit(100 * now_sec / total)
                    except ZeroDivisionError:
                        pass
                self.update_text_edit_signal.emit(myline)
                final_output += myline
                myline = str('')
        self.update_text_edit_signal.emit('\n\n')

        return_code = self.process.poll()

        log_data = {'command' : unicode(convert_cmd, 'utf-8'),
                    'returncode' : return_code, 'type' : 'VIDEO'}
        log_lvl = logging.info if return_code == 0 else logging.error
        log_lvl(unicode(final_output, 'utf-8'), extra=log_data)

        return return_code == 0

    def convert_image(self, from_file, to_file, size):
        """
        Convert an image with the desired size using PythonMagick.
        Create conversion info ("command") and emit the corresponding signal
        in order an textEdit to be updated with that info.
        Finally, save log information.

        Return True if conversion succeed, else False.
        """
        assert isinstance(from_file, unicode) and isinstance(to_file, unicode)
        assert from_file.startswith('"') and from_file.endswith('"')
        assert to_file.startswith('"') and to_file.endswith('"')

        from_file = str(QString(from_file).toUtf8())[1:-1]
        to_file = str(QString(to_file).toUtf8())[1:-1]

        command = 'from {0} to {1}'.format(unicode(from_file, 'utf-8'),
                                           unicode(to_file, 'utf-8'))
        if size:
            command += ' -s ' + size
        self.update_text_edit_signal.emit(command+'\n')
        final_output = ''

        try:
            if os.path.exists(to_file):
                os.remove(to_file)
            img = PythonMagick.Image(from_file)
            if size:
                img.transform(size)
            img.write(to_file)
            converted = True
        except (RuntimeError, OSError, Exception) as e:
            final_output = str(e)
            self.update_text_edit_signal.emit(final_output)
            converted = False
        self.update_text_edit_signal.emit('\n\n')

        log_data = {'command' : command, 'returncode' : int(not converted),
                    'type' : 'IMAGE'}
        log_lvl = logging.info if converted == 1 else logging.error
        log_lvl(final_output, extra=log_data)

        return converted

    def convert_doc(self, from_file, to_file):
        """
        Create the unoconv command and execute it using the subprocess module.

        Unoconv doesn't accept output file's name so we have to:
          1. make a copy of the original file with output file's name
          2. convert the copy
          3. rename the converted file to match the desired output file's name

        Also emit the corresponding signal in order an textEdit to be updated
        with unoconv's output. Finally, save log information.

        Return True if conversion succeed, else False.
        """
        assert isinstance(from_file, unicode) and isinstance(to_file, unicode)

        from_file = from_file[1:-1]
        to_file = to_file[1:-1]
        from_base, from_ext = os.path.splitext(from_file)
        to_base, to_ext = os.path.splitext(to_file)

        dummy_file = to_base + from_ext
        dummy_base, dummy_ext = os.path.splitext(dummy_file)
        while os.path.exists(dummy_file):
            # do not overwrite existing files
            dummy_file = dummy_base + '~' + dummy_ext
            dummy_base = os.path.splitext(dummy_file)[0]

        converted_file = dummy_base + to_ext
        shutil.copy(from_file, dummy_file)

        cmd = 'unoconv --format={0} {1}'.format(to_ext[1:], '"'+dummy_file+'"')
        cmd = str(QString(cmd).toUtf8())
        self.update_text_edit_signal.emit(unicode(cmd, 'utf-8')+'\n')
        child = subprocess.Popen(shlex.split(cmd),
                                 stderr=subprocess.STDOUT,
                                 stdout=subprocess.PIPE)
        child.wait()

        os.remove(dummy_file)
        try:
            shutil.move(converted_file, to_file)
        except IOError:
            # unoconv conversion failed and converted_file does not exist
            pass

        final_output = unicode(child.stdout.read(), 'utf-8')
        self.update_text_edit_signal.emit(final_output+'\n\n')

        return_code = child.poll()

        log_data = {'command' : unicode(cmd, 'utf-8'),
                    'returncode' : return_code, 'type' : 'DOCUMENT'}
        log_lvl = logging.info if return_code == 0 else logging.error
        log_lvl(final_output, extra=log_data)

        return return_code == 0

class Report(QDialog):
    def __init__(self, text, parent=None):
        super(Report, self).__init__(parent)
        label = QLabel(text)
        button = QPushButton('OK')

        hlayout = pyqttools.add_to_layout(QHBoxLayout(), None, label, None)
        hlayout2 = pyqttools.add_to_layout(QHBoxLayout(), None, button)
        final_layout = pyqttools.add_to_layout(QVBoxLayout(), hlayout, hlayout2)
        self.setLayout(final_layout)

        button.clicked.connect(self.close)

        self.resize(170, 100)
        self.setWindowTitle('Report')


if __name__ == '__main__':
    #test dialog
    import sys
    app = QApplication(sys.argv)
    dialog = Progress([], '', '', False, '', False, test=True)
    #dialog = Report('Converted 1/1')
    dialog.show()
    app.exec_()
