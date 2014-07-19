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

from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import (
        QWidget, QRegExpValidator, QLabel, QComboBox, QCheckBox, QLineEdit,
        QSpacerItem, QMessageBox
        )

from ffmulticonverter import utils


class ImageTab(QWidget):
    def __init__(self, parent):
        super(ImageTab, self).__init__(parent)
        self.parent = parent
        self.name = 'Images'
        self.formats = [
                'bmp', 'cgm', 'dpx', 'emf', 'eps', 'fpx', 'gif', 'jbig', 'jng',
                'jpeg', 'mrsid', 'p7', 'pdf', 'picon', 'png', 'ppm', 'psd',
                'rad', 'tga', 'tif','webp', 'xpm'
                ]

        self.extra_img = [
                'bmp2', 'bmp3', 'dib', 'epdf', 'epi', 'eps2', 'eps3', 'epsf',
                'epsi', 'icon', 'jpe', 'jpg', 'pgm', 'png24', 'png32', 'pnm',
                'ps', 'ps2', 'ps3', 'sid', 'tiff'
                ]

        validator = QRegExpValidator(QRegExp(r'^[1-9]\d*'), self)

        converttoLabel = QLabel(self.tr('Convert to:'))
        extComboBox = QComboBox()
        extComboBox.addItems(self.formats)
        commandLabel = QLabel(self.tr('Extra options:'))
        commandLineEdit = QLineEdit()

        hlayout2 = utils.add_to_layout(
                'h', converttoLabel, extComboBox, commandLabel, commandLineEdit)

        sizeLabel = QLabel(
                '<html><p align="center">' + self.tr('Image Size:') +
                '</p></html>')
        widthLineEdit = utils.create_LineEdit((50, 16777215), validator, 4)
        heightLineEdit = utils.create_LineEdit((50, 16777215), validator, 4)
        label = QLabel('<html><p align="center">x</p></html>')
        label.setMaximumWidth(25)

        hlayout1 = utils.add_to_layout('h', widthLineEdit,label,heightLineEdit)
        sizelayout = utils.add_to_layout('v', sizeLabel, hlayout1)

        imgaspectCheckBox = QCheckBox(self.tr("Maintain aspect ratio"))
        autocropCheckBox = QCheckBox(self.tr("Auto-crop"))

        vlayout = utils.add_to_layout('v', imgaspectCheckBox, autocropCheckBox)

        rotateLabel = QLabel(
                "<html><div align='center'>" + self.tr("Rotate") +
                ":</div><br>(" + self.tr("degrees - clockwise") + ")</html>")
        rotateLineEdit = utils.create_LineEdit((100, 16777215), validator, 3)
        vflipCheckBox = QCheckBox("Vertical flip")
        hflipCheckBox = QCheckBox("Horizontal flip")

        vlayout2 = utils.add_to_layout('v', vflipCheckBox, hflipCheckBox)
        hlayout3 = utils.add_to_layout(
                'h', sizelayout, vlayout, rotateLabel, rotateLineEdit,
                vlayout2, None)

        final_layout = utils.add_to_layout('v', hlayout2, hlayout3)
        self.setLayout(final_layout)

        #aliasing
        self.extComboBox = extComboBox
        self.widthLineEdit = widthLineEdit
        self.heightLineEdit = heightLineEdit
        self.imgaspectCheckBox = imgaspectCheckBox
        self.commandLineEdit = commandLineEdit
        self.autocropCheckBox = autocropCheckBox
        self.rotateLineEdit = rotateLineEdit
        self.vflipCheckBox = vflipCheckBox
        self.hflipCheckBox = hflipCheckBox

    def clear(self):
        """Clear self.widthLineEdit and self.heightLineEdit."""
        self.widthLineEdit.clear()
        self.heightLineEdit.clear()
        self.commandLineEdit.clear()
        self.rotateLineEdit.clear()
        self.imgaspectCheckBox.setChecked(False)
        self.autocropCheckBox.setChecked(False)
        self.vflipCheckBox.setChecked(False)
        self.hflipCheckBox.setChecked(False)

    def ok_to_continue(self):
        """
        Check if everything is ok with imagetab to continue conversion.

        Check if:
        - ImageMagick is missing.
        - Either none or both size lineEdits are active at a time.

        Return True if all tests pass, else False.
        """
        width = self.widthLineEdit.text()
        height = self.heightLineEdit.text()

        if not self.parent.imagemagick:
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                'Error!'), self.tr('ImageMagick is not installed.\nYou will '
                'not be able to convert image files until you install it.'))
            return False
        if (width and not height) or (not width and height):
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                     'Error!'), self.tr('The size LineEdit may not be empty.'))
            if width and not height:
                self.heightLineEdit.setFocus()
            else:
                self.widthLineEdit.setFocus()
            return False
        return True
