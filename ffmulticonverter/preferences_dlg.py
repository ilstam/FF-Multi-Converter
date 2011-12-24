#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Ilias Stamatis <stamatis.iliass@gmail.com>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from PyQt4.QtGui import (QApplication, QDialog, QWidget, QGridLayout, 
                  QHBoxLayout, QVBoxLayout, QSpacerItem, QLabel, QRadioButton, 
                  QCheckBox, QLineEdit, QToolButton, QTabWidget, 
                  QDialogButtonBox, QFileDialog)                  
import sys
import os   
import pyqttools

pyqttools = pyqttools.Tools()               

class Preferences(QDialog):
    
    def __init__(self, settings, parent=None):
        super(Preferences, self).__init__(parent)
        self.home = os.getenv('HOME')
        
        saveLabel = QLabel(self.tr('<html><b>Save files</b></html>'))
        self.saveto_outRadioButton = QRadioButton(self.tr(
                                       'Save all files\nto ouput destination'))
        self.saveto_origRadioButton = QRadioButton(
                             self.tr('Save each file to\nits original folder'))
        layout1 = pyqttools.add_to_layout(QHBoxLayout(), 
                 self.saveto_outRadioButton, self.saveto_origRadioButton, None)
                 
        self.rebuildCheckBox = QCheckBox(self.tr('Rebuild files structure'))
        defaultLabel = QLabel(self.tr('Default output destination'))
        self.defaultLineEdit = QLineEdit()
        self.defaultToolButton = QToolButton()
        self.defaultToolButton.setText('...')
        layout2 = pyqttools.add_to_layout(QHBoxLayout(), self.defaultLineEdit, 
                                                        self.defaultToolButton)
        name_Label = QLabel(self.tr('<html><b>Name files</b></html>'))
        prefixLabel = QLabel(self.tr('Prefix'))
        suffixLabel = QLabel(self.tr('Suffix'))
        self.prefixLineEdit = QLineEdit()
        self.suffixLineEdit = QLineEdit()
        grid = pyqttools.add_to_grid(QGridLayout(), 
                                            [prefixLabel, self.prefixLineEdit], 
                                            [suffixLabel, self.suffixLineEdit])
        layout3 = pyqttools.add_to_layout(QHBoxLayout(), grid, None)
        
        tabwidget_layout = pyqttools.add_to_layout(QVBoxLayout(), saveLabel, 
               QSpacerItem(14, 13), layout1, self.rebuildCheckBox, 
               QSpacerItem(14, 13), defaultLabel, layout2, QSpacerItem(13, 13),
               name_Label, QSpacerItem(14, 13), layout3)       

        widget = QWidget()
        widget.setLayout(tabwidget_layout)                       
        self.TabWidget  = QTabWidget()
        self.TabWidget.addTab(widget, self.tr('General'))
        
        self.buttonBox = QDialogButtonBox(
                                   QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)
        
        final_layout = pyqttools.add_to_layout(QVBoxLayout(), self.TabWidget,
                                                          None, self.buttonBox) 
        self.setLayout(final_layout)
        
        self.saveto_outRadioButton.clicked.connect(lambda: 
                                             self.radiobutton_changed('ouput'))
        self.saveto_origRadioButton.clicked.connect(lambda: 
                                          self.radiobutton_changed('original'))
        self.defaultToolButton.clicked.connect(self.open_dir)
        self.buttonBox.accepted.connect(self.set_settings_list)
        self.buttonBox.rejected.connect(self.reject)
        
        saveto_output = settings[0]
        rebuild_structure = settings[1]
        default_ouput = settings[2]
        prefix = settings[3]
        suffix = settings[4]
        
        if saveto_output:
            self.saveto_outRadioButton.setChecked(True)
        else:
            self.saveto_origRadioButton.setChecked(True)
            self.rebuildCheckBox.setEnabled(False)
            self.defaultLineEdit.setEnabled(False)
        if rebuild_structure:
            self.rebuildCheckBox.setChecked(True)
        if default_ouput:
            self.defaultLineEdit.setText(default_ouput)
        if prefix:
            self.prefixLineEdit.setText(prefix)
        if suffix:
            self.suffixLineEdit.setText(suffix)                          
        
        self.resize(414, 457)
        self.setWindowTitle(self.tr('Preferences'))                      
            
    def radiobutton_changed(self, data):        
        enable = True if data == 'ouput' else False
        self.rebuildCheckBox.setEnabled(enable)
        self.defaultLineEdit.setEnabled(enable)
        
    def open_dir(self):
        if self.defaultLineEdit.isEnabled():
            """Uses standard QtDialog to get directory name."""
            _dir = QFileDialog.getExistingDirectory(self, self.tr(
                         "FF Multi Converter - Choose default output destination"), 
                        self.home)
            _dir = unicode(_dir)
            if _dir:
                self.defaultLineEdit.setText(_dir)
            
    def set_settings_list(self):
        """Defines settings before accept the dialog."""
        saveto_output = True if self.saveto_outRadioButton.isChecked() \
            else False 
        rebuild_structure = self.rebuildCheckBox.isChecked() and \
            self.rebuildCheckBox.isEnabled()
        default_ouput = unicode(self.defaultLineEdit.text())
        prefix = unicode(self.prefixLineEdit.text())
        suffix = unicode(self.suffixLineEdit.text())
        self.settings = [saveto_output, rebuild_structure, default_ouput,
                         prefix, suffix]
        self.accept()                    
        
if __name__ == '__main__':
    #test dialog
    app = QApplication(sys.argv)
    _list = [True, True, '/home/ilias/kati1', 'prin', 'meta']
    dialog = Preferences(_list)
    dialog.show()
    app.exec_()
