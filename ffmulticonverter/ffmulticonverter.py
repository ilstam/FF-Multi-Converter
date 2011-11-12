#!/usr/bin/python
# -*- coding: utf-8 -*-
# Program: FF Multi Converter
# Purpose: GUI application to convert multiple file formats 
# Requires: python 2.7, PyQt4, ffmpeg, unoconv, Open/Libre office suite
#
# Copyright (C) 2011 Ilias Stamatis <il.stam@yahoo.gr>
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

__version__ = "1.0.2"

if platform.system() != 'Linux':
    exit('ΣΦΑΛΜΑ: Η εφαρμογή τρέχει μόνο σε συστήματα Linux.')

if not (py_version > '2.7' and py_version < '3'):
    exit('ΣΦΑΛΜΑ: Το πρόγραμμα χρειάζεται την Python 2.7 για να τρέξει.')
    
try:
    import PyQt4
except ImportError:
    exit('ΣΦΑΛΜΑ: Το πρόγραμμα χρειάζεται την PyQt4 για να τρέξει.')    

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import os
import subprocess
import shlex
import functools
from PIL import Image

import path_generator
import ui_ffmulticonverter
import qrc_resources

class FFMultiConverter(QMainWindow, 
            ui_ffmulticonverter.Ui_FFMultiConverter):    
    
    def __init__(self, parent=None):
        super(FFMultiConverter, self).__init__(parent)        
        self.setupUi(self)
        
        self.ffmpeg, self.unoconv = self.check_for_dependencies()  
        
        types = ['Ήχος', 'Video', 'Εικόνα', 'Έγγραφο Κειμένου']
        [self.typeComboBox.addItem(_type) for _type in types]          
        
        self.connect(self.typeComboBox, SIGNAL('currentIndexChanged(QString)'),
                                                    self.refresh_comboboxes)
        self.connect(self.fromComboBox, SIGNAL('currentIndexChanged(QString)'),
                                                self.refresh_document_combo)
        self.connect(self.folderCheckBox, SIGNAL('clicked()'), 
                        functools.partial(self.checkboxes_clicked, 'fol'))
        self.connect(self.recursiveCheckBox, SIGNAL('clicked()'), 
                        functools.partial(self.checkboxes_clicked, 'rec')) 
        self.connect(self.openToolButton, SIGNAL('clicked()'), 
                                                        self.choose_file)
        self.connect(self.convertPushButton, SIGNAL('clicked()'), self.convert)
        self.connect(self.convertAction, SIGNAL('triggered()'), self.convert)
        self.connect(self.aboutAction, SIGNAL('triggered()'), self.about)
        self.connect(self.exitAction, SIGNAL('triggered()'), self.close)

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
        QTimer.singleShot(0, self.refresh_comboboxes)
    
    def refresh_comboboxes(self):
        """Add the appropriate values to comboboxes."""
        # disconnect the signal in order not to be emitted
        # while adding items to fromComboBox.
        self.disconnect(self.fromComboBox, 
                SIGNAL('currentIndexChanged(QString)'), 
                self.refresh_document_combo)
                
        self.fromComboBox.clear()
        self.toComboBox.clear()
        index = self.typeComboBox.currentIndex()       
                
        if index == 0:
            for ext in self.audio_formats:
                self.fromComboBox.addItem(ext)
                self.toComboBox.addItem(ext)        
        elif index == 1:
            for ext in self.video_formats:
                self.fromComboBox.addItem(ext)
                self.toComboBox.addItem(ext)
            string = '(Μόνο ήχος)'
            for ext in self.vid_to_aud_formats:                
                item = ext + '  '  + string 
                self.toComboBox.addItem(item)
        elif index == 2:
            for ext in self.image_formats:
                self.fromComboBox.addItem(ext)
                self.toComboBox.addItem(ext)
        else:                        
            # ---Different procedure here because document_formats is
            # a dictionary.
            
            # creation of a sorted list with document_formats extensions
            _list = []
            [_list.append(ext) for ext in self.document_formats]
            _list.sort()            
            [self.fromComboBox.addItem(ext) for ext in _list]                            
            
            text = str(self.fromComboBox.currentText())
            for ext in self.document_formats[text]:
                self.toComboBox.addItem(ext)                
        
        # reconnect the signal 
        self.connect(self.fromComboBox, 
                SIGNAL('currentIndexChanged(QString)'),
                self.refresh_document_combo)
                
        # execute the below method although that no checkbox clicked, 
        # because of the specificity of typeRadioButton when type
        # is document files (see the method).
        self.checkboxes_clicked()
                
    def refresh_document_combo(self):
        """Add the appropriate values to toComboBox when file type
        is document."""
        # document_formats is dict, so only some extensions corresponds
        # to some others.
        if self.typeComboBox.currentIndex() == 3:
            self.toComboBox.clear()
            text = str(self.fromComboBox.currentText())
            for ext in self.document_formats[text]:
                self.toComboBox.addItem(ext)       
                
    def checkboxes_clicked(self, data=None):
        """Manage the behavior of checkboxes and radiobuttons.
        
        Keywords arguments:
        data -- a string to show from which CheckBox the signal emitted.
        """
        # data default value is None because the method can also be called
        # from self.refresh_comboboxes()
        fol = self.folderCheckBox
        rec = self.recursiveCheckBox
        _type = self.typeRadioButton
        ext = self.extRadioButton
        
        index = self.typeComboBox.currentIndex()
        
        if data == 'fol' and rec.isChecked():
            rec.setChecked(False)
        elif data == 'rec' and fol.isChecked():
            fol.setChecked(False)
        
        enable = bool(rec.isChecked() or fol.isChecked())
        # set typeRadioButton disabled when type == document files,
        # because it is not possible to convert every file format to any 
        # other file format.
        if enable and index == 3:
            _type.setEnabled(False)
            ext.setChecked(True)
        else:
            _type.setEnabled(enable)
        ext.setEnabled(enable)        
        if not (_type.isChecked() or ext.isChecked()):
            _type.setChecked(True) 
            
    def choose_file(self):
        """Uses standard QtDialog to get files name."""
        hold_fname = self.fname
        self.fname = QFileDialog.getOpenFileName(self, 
                    "FF Multi Converter - Επιλογή αρχείου")
        self.fname = unicode(self.fname)
        if self.fname:
            self.fromLineEdit.setText(self.fname)
        else:
            self.fname = hold_fname
            
    def find_type(self):
        """Specifies the current file formats.
        
        Returns: list
        """
        index = self.typeComboBox.currentIndex()
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
        # typeComboBox == document files
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
        
    def ok_to_continue(self):
        ### also add check for dependencies
        """Check if everything is ok to continue with conversion.
        
        Checks if: 
         - Theres is no given file
         - Given file exists
         - Given file extension is same with the declared extension
         - Declared from_extension == declared to_extension
         - Missing dependencies for this file type
        
        Returns: boolean        
        """
        ext_from = str(self.fromComboBox.currentText())
        ext_to = unicode(self.toComboBox.currentText())        
        _dir, _file = os.path.split(self.fname)
        base, real_ext = os.path.splitext(_file)
        index = self.typeComboBox.currentIndex()
        # give small names to the variables in order to wide use them below
        a = real_ext[1:]
        b = ext_from
        
        class ValidationError(Exception): pass
        
        try:
            if self.fname == '':
                raise ValidationError('Δεν ορίσατε αρχείο για μετατροπή!')
            elif not os.path.exists(self.fname):
                raise ValidationError('Το αρχείο {} δεν υπάρχει!'
                                                        .format(self.fname))            
            elif not a == b and not ((a == 'dib' and b == 'bmp') or \
                (a == 'ps' and b == 'eps') or ((a == 'jpg' or a == 'jpe')\
                and b == 'jpeg') or (a == 'tiff' and b == 'tif')):
                # look if real_ext is same type with ext_from and just have
                # different extension. eg: jpg is same as jpeg
                raise ValidationError("Η επέκταση του αρχείου δεν είναι {}."\
                                                    .format(ext_from))
            elif ext_from == ext_to:
                raise ValidationError('Δεν γίνεται να μετατρέψετε την επέκταση'
                            ' του αρχείου στην ήδη υπάρχουσα!')
            elif (index == 0 or index == 1) and not self.ffmpeg:
                raise ValidationError('Το πρόγραμμα ffmpeg δεν είναι '
                    'εγκατεστημένο.\nΔεν μπορείτε να κάνετε μετατροπές video ή'
                    ' ήχου μέχρι να το εγκαταστήσετε.')
            elif index == 3 and not self.unoconv:
                raise ValidationError('Το πρόγραμμα unoconv δεν είναι '
                'εγκατεστημένο.\nΔεν μπορείτε να κάνετε μετατροπές εγγράφων '
                'κειμένου μέχρι να το εγκαταστήσετε.')                                
            return True
        except ValidationError as e:
            QMessageBox.warning(self, "FF Multi Converter - Σφάλμα!", 
                                                                unicode(e))
            return False  
            
    def convert(self):
        """Starts the convert procedure."""
        if not self.ok_to_continue():
            return
        files_to_conv = self.files_to_conv_list()
        ext_to = unicode(self.toComboBox.currentText())   
        # split from the docsting (Μόνο ήχος) if it is appropriate
        ext_to = ext_to.split(' ')[0]
        index = self.typeComboBox.currentIndex()
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
        # Add quotations to every dir's or file's name in order to avoid error
        # in special cases such as spaces or special characters.
        path = ''
        for i in from_file.split('/')[1:]:
            path += '/"' + i + '"'        
        
        _dir, _file = os.path.split(path)
        base = os.path.splitext(_file)[0]
        to_file = _dir + '/' + base + '.' + extension + '"'
        command = 'ffmpeg -y -i {} {}'.format(path, to_file)
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
        # Add quotations to every dir's or file's name in order to avoid error
        # in special cases such as spaces or special characters.        
        path = ''
        for i in from_file.split('/')[1:]:
            path += '/"' + i + '"'        
        
        command = 'unoconv --format={} {}'.format(extension, path)
        command = str(QString(command).toUtf8())
        command = shlex.split(command)
        return True if subprocess.call(command) == 0 else False                                      
            
    def about(self):
        """Shows an About dialog using qt standard dialog."""
        QMessageBox.about(self, "Περί FF Multi Converter", 
            '''<b> FF Multi Converter {0} </b>
            <p>Μετατροπή μεταξύ διάφορων τύπων αρχείων σε διαφορετικές 
            επεκτάσεις.
            <p>Copyright &copy; 2011 Ilias Stamatis  
            <br>Άδεια: GNU GPL3
            <p>Python {1} - Qt {2} - PyQt {3} on {4}'''.format(__version__, 
            platform.python_version()[:5], QT_VERSION_STR, PYQT_VERSION_STR,
            platform.system()))    
    
    def check_for_dependencies(self):
        """Checks if ffmpeg and unoconv is installed.
        
        Returns: two boolean
        """
        # subprocess.call() raises an Error if the program is not installed.
        # Not the best way to check if a package is already installed, 
        # but it works.
        try:
            subprocess.call(['ffmpeg'])
            ffmpeg = True
        except:
            ffmpeg = False
        try:
            subprocess.call(['unoconv'])
            unoconv = True
        except:
            unoconv = False  
        return ffmpeg, unoconv
            
    def missing_dependencies(self):
        """Shows a dialog to inform that some dependencies is not installed."""
        if not self.ffmpeg and not self.unoconv:
            QMessageBox.information(self, 'Ελλιπείς εξαρτήσεις', 
                'Τα πρόγραμματα ffmpeg και unoconv δεν είναι εγκατεστημένα.\n'
                'Δεν μπορείτε να κάνετε μετατροπές video/ήχου και εγγράφων '
                'κειμένου μέχρι να τα εγκαταστήσετε.')        
        elif not self.ffmpeg:
            QMessageBox.information(self, 'Ελλιπείς εξαρτήσεις', 'Το πρόγραμμα'
                ' ffmpeg δεν είναι εγκατεστημένο.\nΔεν μπορείτε να κάνετε '
                'μετατροπές video ή ήχου μέχρι να το εγκαταστήσετε.')
        elif not self.unoconv:
            QMessageBox.information(self, 'Ελλιπείς εξαρτήσεις', 'Το πρόγραμμα'
                ' unoconv δεν είναι εγκατεστημένο.\nΔεν μπορείτε να κάνετε '
                'μετατροπές εγγράφων κειμένου μέχρι να το εγκαταστήσετε.')

                
class ProgressDlg(QDialog):
    
    def __init__(self, files, ext_to, index, delete, parent=None):
        """Constructs the progress dialog.
        
        Keyword arguments:
        files -- list with files to be converted
        ext_to -- the extension to convert to
        index -- number that shows file type
        delete -- boolean that shows if files must removed after convertion
        """
        super(ProgressDlg, self).__init__(parent)
        self.setWindowTitle('FF Multi Converter - Μετατροπή')        
        self.setGeometry(300, 300, 300, 120)
        self.bar = QProgressBar()
        self.bar.setValue(0)
        self.stopButton = QPushButton('Διακοπή')
        self.label = QLabel('Μετατροπή αρχείων...')
        
        self.connect(self.stopButton, SIGNAL('clicked()'), self.reject)
        
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
        # ok and error shows the number of files that converted successfully 
        # or not
        self.ok = 0 
        self.error = 0
        
        self.timer = QBasicTimer()
        self.timer.start(100, self)         
        
    def timerEvent(self, timeout):
        """Event handler for self.timer."""
        if self.bar.value() >= 100:
            self.timer.stop()
            sum_files = self.ok + self.error
            QMessageBox.information(self, 'Αναφορά', 'Μετατράπηκαν: {}/{}'
                    .format(self.ok, sum_files))
            self.accept()
            return
        self.convert_a_file()            
        if self.bar.value() + self.step > 100:
            self.bar.setValue(100)            
        else:
            value = self.bar.value() + self.step
            self.bar.setValue(value)
                                
    def reject(self):
        """Use Qt standard dialog to ask whether procedure must stop or not."""
        self.timer.stop()
        reply = QMessageBox.question(self, 'FF Multi Converter - Διακοπή '
            'μετατροπής', 'Είστε σίγουρος ότι θέλετε να διακόψετε τη '
            'διαδικασία;', QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            QDialog.reject(self)
        if reply == QMessageBox.Cancel:
            self.timer.start(100, self)
            
    def convert_a_file(self):
        """Do the conversions of files using methods of Conversions class."""
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
    converter = FFMultiConverter()
    converter.show()
    if not converter.ffmpeg or not converter.unoconv:
        converter.missing_dependencies()
    app.exec_()    
    
if __name__ == '__main__':
    main() 
