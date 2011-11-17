#!/usr/bin/python
# -*- coding: utf-8 -*-
# Program: FF Multi Converter
# Purpose: GUI application to convert multiple file formats 
#
# Copyright (C) 2011 Ilias Stamatis <stamatis.iliass@gmail.com>
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

import platform
py_version = platform.python_version()

__version__ = "1.1.0"

if platform.system() != 'Linux':
    exit('Error: The application is available for Linux platforms only.')

if not (py_version >= '2.6' and py_version < '3'):
    exit('Error: You need python 2.6 or python2.7 to run this program.')
    
try:
    import PyQt4
except ImportError:
    exit('Error: You need PyQt4 to run this program.')    

try:
    from PIL import Image
except ImportError:
    pass
    # User will be informed about this later

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import os
import subprocess
import shlex

import path_generator
import ui_ffmulticonverter
import qrc_resources

class FFMultiConverter(QMainWindow, 
            ui_ffmulticonverter.Ui_FFMultiConverter):    
    
    def __init__(self, parent=None):
        super(FFMultiConverter, self).__init__(parent)        
        self.setupUi(self)   
        
        self.audio_formats = ['aac', 'ac3', 'aiff', 'amr', 'asf', 'au', 'avi', 
                              'dvd', 'flac', 'flv', 'm4a', 'm4v', 'mmf', 'mov',
                              'mp2', 'mp3', 'mp4', 'mpeg', 'ogg', 'rm', 'vob',
                              'wav', 'webm', 'wma']
        
        self.video_formats = ['asf', 'avi', 'dvd', 'flv', 'mkv', 'mmf', 
                              'mov', 'mp4', 'mpeg', 'ogg', 'psp', 'vob', 
                              'webm', 'wma', 'wmv']
                              
        self.vid_to_aud_formats = ['aac', 'ac3', 'aiff', 'au', 'flac', 
                                   'mp2' , 'wav']                                                          
                              
        self.image_formats = ['bmp', 'eps', 'gif', 'jpeg', 'pcx', 'pdf', 'png',
                              'ppm', 'tif', 'tga']    
                              
        self.document_formats = {'doc' : ['odt', 'pdf'],
                                'html' : ['odt'],
                                'odp' : ['pdf', 'ppt'],
                                'ods' : ['pdf'],
                                'odt' : ['doc', 'html', 'pdf', 'rtf', 'sxw', 
                                         'txt', 'xml'],
                                'ppt' : ['odp'],
                                'rtf' : ['odt'],
                                'sdw' : ['odt'],
                                'sxw' : ['odt'],
                                'txt' : ['odt'],
                                'xls' : ['ods'],
                                'xml' : ['doc', 'odt', 'pdf']}              
        self.fname = ''        
                
        # connect TabWidget to checkboxes_clicked() because checboxe's behavior 
        # is different when file type == documents
        self.TabWidget.currentChanged.connect(self.checkboxes_clicked)
        # use lambda to pass extra data when signal emmited.
        self.folderCheckBox.clicked.connect(
                                        lambda: self.checkboxes_clicked('fol'))
        self.recursiveCheckBox.clicked.connect(
                                        lambda: self.checkboxes_clicked('rec'))                                        
        self.openToolButton.clicked.connect(self.choose_file)
        self.docFromComboBox.currentIndexChanged.connect(
                                                      self.refresh_docComboBox)
        self.convertPushButton.clicked.connect(self.convert)
        self.convertAction.triggered.connect(self.convert)
        self.aboutAction.triggered.connect(self.about)
        self.quitAction.triggered.connect(self.close)
        
        self.TabWidget.setCurrentIndex(0)
        [self.audFromComboBox.addItem(i) for i in self.audio_formats]
        [self.audToComboBox.addItem(i) for i in self.audio_formats]
        [self.vidFromComboBox.addItem(i) for i in self.video_formats]
        [self.vidToComboBox.addItem(i) for i in self.video_formats]
        string = self.tr(' (Audio only)')
        [self.vidToComboBox.addItem(i+string) for i in self.vid_to_aud_formats]
        [self.imgFromComboBox.addItem(i) for i in self.image_formats]
        [self.imgToComboBox.addItem(i) for i in self.image_formats]
        # create a sorted list with document_formats extensions because 
        # self.document_formats is a dict so values are not sorted
        _list = []
        [_list.append(ext) for ext in self.document_formats]
        _list.sort()         
        [self.docFromComboBox.addItem(i) for i in _list]
        # self.refresh_docComboBox() will care about docToComboBox values
        self.typeRadioButton.setChecked(True) # but disabled        
        self.dependenciesLabel = QLabel()
        self.statusBar.addPermanentWidget(self.dependenciesLabel, stretch=1)

        QTimer.singleShot(0, self.check_for_dependencies)                              
    
    def checkboxes_clicked(self, data=None):
        """Manages the behavior of checkboxes and radiobuttons.
        
        Keywords arguments:
        data -- a string to show from which CheckBox the signal emitted.
        """
        # data default value is None because the method can also be called
        # when TabWidget's tab change.
        if data == 'fol' and self.recursiveCheckBox.isChecked():
            self.recursiveCheckBox.setChecked(False)
        elif data == 'rec' and self.folderCheckBox.isChecked():
            self.folderCheckBox.setChecked(False)
        
        index = self.TabWidget.currentIndex()
        enable = bool(self.recursiveCheckBox.isChecked() 
                                            or self.folderCheckBox.isChecked())
        self.extRadioButton.setEnabled(enable)  
        if enable and index == 3:
            # set typeRadioButton disabled when type == document files,
            # because it is not possible to convert every file format to any 
            # other file format.            
            self.typeRadioButton.setEnabled(False)
            self.extRadioButton.setChecked(True)
        else:
            self.typeRadioButton.setEnabled(enable)
            
    def refresh_docComboBox(self):
        """Add the appropriate values to docToComboBox."""
        # document_formats is dict, so only some extensions corresponds
        # to some others.
        self.docToComboBox.clear()
        text = str(self.docFromComboBox.currentText())
        [self.docToComboBox.addItem(i) for i in self.document_formats[text]]            
            
    def choose_file(self):
        """Uses standard QtDialog to get files name."""
        hold_fname = self.fname
        self.fname = QFileDialog.getOpenFileName(self, 
                                   self.tr("FF Multi Converter - Choose File"))
        self.fname = unicode(self.fname)
        if self.fname:
            self.fromLineEdit.setText(self.fname)
        else:
            self.fname = hold_fname
            
    def get_extensions(self):
        """Returns the from and to extensions.
        
        Returns: string
        """
        index = self.TabWidget.currentIndex()
        if index == 0:
            ext_from = unicode(self.audFromComboBox.currentText())
            ext_to = unicode(self.audToComboBox.currentText())
        elif index == 1:
            ext_from = unicode(self.vidFromComboBox.currentText())
            ext_to = unicode(self.vidToComboBox.currentText())
            # split from the docsting (Audio Only) if it is appropriate
            ext_to = ext_to.split(' ')[0]                        
        elif index == 2:
            ext_from = unicode(self.imgFromComboBox.currentText())
            ext_to = unicode(self.imgToComboBox.currentText())
        elif index == 3:
            ext_from = unicode(self.docFromComboBox.currentText())
            ext_to = unicode(self.docToComboBox.currentText())
        return ext_from, ext_to

    def find_type(self):
        """Specifies the current file formats.
        
        Returns: list
        """
        index = self.TabWidget.currentIndex()
        if index == 0:
            type_formats = self.audio_formats            
        elif index == 1:
            type_formats = self.video_formats            
        elif index == 2:
            type_formats = self.image_formats
            # some extra extensions (same type, different extension)
            # eg: jpg == gpeg
            extra_extensions = ['dib', 'ps', 'jpg', 'jpe', 'tiff']
            [type_formats.append(i) for i in extra_extensions]
        else:
            type_formats = []            
        # self.document_formats are not needed.
        # the function is used in self.files_to_conv_list() when the 
        # typeRadioButton is enabled, but this never gonna happens when 
        # type == document files
        return type_formats      
        
    def files_to_conv_list(self):
        """Creates a list of the files that must be converted, regarding
        the checkboxes and radiobuttons values.
                
        Returns: list
        """        
        files_to_conv = []
        _dir, name = os.path.split(self.fname)
        _dir += '/*'
        base, ext = os.path.splitext(name)   
        type_formats = self.find_type()
        
        if self.folderCheckBox.isChecked():
            if self.extRadioButton.isChecked():
                path = _dir + ext
                for i in path_generator._paths_from_path_patterns([path]):
                    files_to_conv.append(i)
            elif self.typeRadioButton.isChecked():
                includes = []
                [includes.append('*.' + i) for i in type_formats]
                for i in path_generator._paths_from_path_patterns([_dir], 
                                    recursive=False, includes=includes):
                    files_to_conv.append(i)
        elif self.recursiveCheckBox.isChecked():
            if self.extRadioButton.isChecked():
                includes = ['*' + ext]
                for i in path_generator._paths_from_path_patterns([_dir],
                                                    includes=includes):
                    files_to_conv.append(i)
            elif self.typeRadioButton.isChecked():
                includes = []
                [includes.append('*.' + i) for i in type_formats]
                for i in path_generator._paths_from_path_patterns([_dir], 
                                                    includes=includes):
                    files_to_conv.append(i)                
        else:
            files_to_conv = [self.fname]
            
        # put given file first in list
        files_to_conv.remove(self.fname)
        files_to_conv.insert(0, self.fname)
        return files_to_conv
        
    def ok_to_continue(self, ext_from, ext_to):
        """Checks if everything is ok to continue with conversion.
        
        Keyword arguments:
        ext_from -- current file extension
        ext_to -- the extension for file to be converted to
        
        Checks if: 
         - Theres is no given file
         - Given file exists
         - Given file extension is same with the declared extension
         - Declared from_extension == declared to_extension
         - Missing dependencies for this file type
        
        Returns: boolean        
        """
        _file = os.path.split(self.fname)[-1]
        real_ext = os.path.splitext(_file)[-1]
        index = self.TabWidget.currentIndex()
        
        # give small names to the variables in order to wide use them below
        a = real_ext[1:]
        b = ext_from
        
        try:
            if self.fname == '':
                raise Exception(self.tr("You must choose a file to convert!"))
            elif not os.path.exists(self.fname):
                raise Exception(self.tr('The selected file does not exists!'))
            elif not a == b and not ((a == 'dib' and b == 'bmp') or \
                (a == 'ps' and b == 'eps') or ((a == 'jpg' or a == 'jpe')\
                and b == 'jpeg') or (a == 'tiff' and b == 'tif')):
                # look if real_ext is same type with ext_from and just have
                # different extension. eg: jpg is same as jpeg
                raise Exception(self.tr(
                                "File' s extensions is not %1.").arg(ext_from))
            elif ext_from == ext_to:
                raise Exception(self.tr(
                    'You can not convert the file extension to the existing!'))
            elif (index == 0 or index == 1) and not self.ffmpeg:
                raise Exception(self.tr(
                    'Program FFmpeg is not installed.\nYou will not be able '
                    'to convert video and audio files until you install it.'))
            elif index == 2 and not self.pil:
                raise Exception(self.tr(
                    'Python Imaging Library (PIL) is not installed.\nYou will '
                    'not be able to convert image files until you install it.')
                    )
            elif index == 3 and not self.unoconv:
                raise Exception(self.tr(
                    'Program unocov is not installed.\nYou will not be able '
                    'to convert document files until you install it.'))
            return True
        except Exception as e:
            QMessageBox.warning(self, self.tr("FF Multi Converter - Error!"), 
                                                                    unicode(e))
            return False  
            
    def convert(self):
        """Starts the convert procedure."""
        ext_from, ext_to = self.get_extensions()
        if not self.ok_to_continue(ext_from, ext_to):
            return
        files_to_conv = self.files_to_conv_list()
        index = self.TabWidget.currentIndex()
        delete = self.deleteCheckBox.isChecked()
        
        dialog = ProgressDlg(files_to_conv, ext_to, index, delete)
        dialog.exec_()  
        
    def convert_video_or_audio(self, from_file, extension):
        """Converts the file format of a video or audio via ffmpeg.
        
        Keyword arguments:
        from_file -- the file to be converted
        extension -- the extension of the new file
        
        Returns: boolean
        """
        # Add quotations to path in order to avoid error in special cases 
        # such as spaces or special characters.
        from_file = '"' + from_file + '"'        
        _dir, _file = os.path.split(from_file)
        base = os.path.splitext(_file)[0]
        to_file = _dir + '/' + base + '.' + extension + '"'
        command = 'ffmpeg -y -i {} {}'.format(from_file, to_file)
        command = str(QString(command).toUtf8())
        command = shlex.split(command)
        return True if subprocess.call(command) == 0 else False
        
    def convert_image(self, from_file, extension):
        """Converts the file format of an image.
        
        Keyword arguments:
        from_file -- the file to be converted
        extension -- the extension of the new file        
        
        Returns: boolean
        """
        _dir, _file = os.path.split(from_file)
        base = os.path.splitext(_file)[0]
        to_file = _dir + '/' + base + '.' + extension
        try:
            Image.open(from_file).save(to_file)
            return True
        except:
            return False
        
    def convert_document_file(self, from_file, extension):
        """Converts the file format of a document file.
        
        Keyword arguments:
        from_file -- the file to be converted
        extension -- the extension of the new file
        
        Returns: boolean        
        """        
        # Add quotations to path in order to avoid error in special cases 
        # such as spaces or special characters.        
        from_file = '"' + from_file + '"'                
        command = 'unoconv --format={} {}'.format(extension, from_file)
        command = str(QString(command).toUtf8())
        command = shlex.split(command)
        return True if subprocess.call(command) == 0 else False                                      
            
    def about(self):
        """Shows an About dialog using qt standard dialog."""
        link  = 'https://github.com/Ilias95/FF-Multi-Converter/wiki/'
        link += 'FF-Multi-Converter'
        QMessageBox.about(self, self.tr("About FF Multi Converter"), self.tr( 
            '''<b> FF Multi Converter %1 </b>
            <p>Convert among several file types to other extensions
            <p><a href="%2">FF Multi Converter</a>
            <p>Copyright &copy; 2011 Ilias Stamatis  
            <br>License: GNU GPL3
            <p>Python %3 - Qt %4 - PyQt %5 on %6''').arg(__version__).arg(link)
            .arg(platform.python_version()[:5]).arg(QT_VERSION_STR)
            .arg(PYQT_VERSION_STR).arg(platform.system()))
    
    def check_for_dependencies(self):
        """Checks if ffmpeg, unoconv and PIL are installed and set 
        dependenciesLabel status."""
        # subprocess.call() raises an Error if the program is not installed.
        # Not the best way to check if a package is already installed, 
        # but it works.
        missing = []
        try:
            subprocess.call(['ffmpeg'])
            self.ffmpeg = True
        except:
            self.ffmpeg = False
            missing.append('FFmpeg')
        try:
            subprocess.call(['unoconv'])
            self.unoconv = True
        except:
            self.unoconv = False  
            missing.append('Unoconv')
        try:
            import PIL
            self.pil = True
        except ImportError:
            self.pil = False
            missing.append('PIL')
        missing = ", ".join(missing) if missing else self.tr('None')
        status = self.tr('Missing dependencies: ') + missing
        self.dependenciesLabel.setText(status)
                
class ProgressDlg(QDialog):
    
    def __init__(self, files, ext_to, index, delete, parent=None):
        """Constructs the progress dialog.
        
        Keyword arguments:
        files -- list with files to be converted
        ext_to -- the extension to convert to
        index -- number that shows file type
        delete -- boolean that shows if files must removed after conversion
        """
        super(ProgressDlg, self).__init__(parent)
        self.setWindowTitle(self.tr('FF Multi Converter - Conversion'))   
        self.setGeometry(300, 300, 300, 120)
        self.bar = QProgressBar()
        self.bar.setValue(0)
        self.stopButton = QPushButton(self.tr('Stop'))
        self.label = QLabel(self.tr('Converting files...'))
        
        self.stopButton.clicked.connect(self.reject)
        
        hlayout = QHBoxLayout()
        hlayout.addStretch()
        hlayout.addWidget(self.label)
        hlayout.addStretch()
        hlayout2 = QHBoxLayout()
        hlayout2.addStretch()      
        hlayout2.addWidget(self.stopButton)
        vlayout = QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addWidget(self.bar)
        vlayout.addLayout(hlayout2)
        self.setLayout(vlayout)

        self.files = files
        self.ext_to = ext_to
        self.index = index
        self.delete = delete
        self.step = 100 / len(files)
        self.ok = 0 
        self.error = 0
        
        self.timer = QBasicTimer()
        self.timer.start(100, self)         
        
    def timerEvent(self, timeout):
        """Event handler for self.timer."""
        if self.bar.value() >= 100:
            self.timer.stop()
            sum_files = self.ok + self.error
            QMessageBox.information(self, 
                self.tr('Report'), 
                self.tr('Converted: %1/%2').arg(self.ok).arg(sum_files))
            self.accept()
            return
        self.convert_a_file()            
        if self.bar.value() + self.step > 100:
            self.bar.setValue(100)            
        else:
            value = self.bar.value() + self.step
            self.bar.setValue(value)
                                
    def reject(self):
        """Uses standard dialog to ask whether procedure must stop or not."""
        self.timer.stop()
        reply = QMessageBox.question(self, 
            self.tr('FF Multi Converter - Interrupt Conversion'), 
            self.tr('Are you sure that you want to interrupt the procedure?'), 
            QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            QDialog.reject(self)
        if reply == QMessageBox.Cancel:
            self.timer.start(100, self)
            
    def convert_a_file(self):
        """Does the conversions of files"""
        if not self.files:
            return
        if self.index == 0 or self.index == 1:
            if converter.convert_video_or_audio(self.files[0], self.ext_to):
                self.ok += 1
                if self.delete:
                    os.remove(self.files[0])
            else:
                self.error += 1
        elif self.index == 2:
            if converter.convert_image(self.files[0], self.ext_to):
                self.ok += 1
                if self.delete:
                    os.remove(self.files[0])                
            else:
                self.error += 1                
        else:
            if converter.convert_document_file(self.files[0], self.ext_to):
                self.ok += 1
                if self.delete:
                    os.remove(self.files[0])                
            else:
                self.error += 1  
        self.files.pop(0)                
                    
def main():
    global converter
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/ffmulticonverter.png'))
    
    # search if there is locale translation avalaible and set the Translators
    locale = QLocale.system().name()
    qtTranslator = QTranslator()
    if qtTranslator.load("qt_" + locale, ":/"):
        app.installTranslator(qtTranslator)
    appTranslator = QTranslator()
    if appTranslator.load("ffmulticonverter_" + locale, ":/"):
        app.installTranslator(appTranslator)    
        
    converter = FFMultiConverter()
    converter.show()
    app.exec_()    
    
if __name__ == '__main__':
    main() 
