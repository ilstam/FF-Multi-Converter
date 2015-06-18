# Copyright (C) 2011-2015 Ilias Stamatis <stamatis.iliass@gmail.com>
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
        QMessageBox
        )

from ffmulticonverter import utils
from ffmulticonverter import config


class ImageTab(QWidget):
    def __init__(self, parent):
        super(ImageTab, self).__init__(parent)
        self.parent = parent
        self.name = 'Images'

        self.formats = config.image_formats
        self.extra_img = config.image_extra_formats

        validator = QRegExpValidator(QRegExp(r'^[1-9]\d*'), self)

        converttoQL = QLabel(self.tr('Convert to:'))
        self.extQCB = QComboBox()
        self.extQCB.addItems(self.formats)
        commandQL = QLabel(self.tr('Extra options:'))
        self.commandQLE = QLineEdit()

        hlayout2 = utils.add_to_layout(
                'h', converttoQL, self.extQCB, commandQL, self.commandQLE)

        sizeQL = QLabel(
                '<html><p align="center">' + self.tr('Image Size:') +
                '</p></html>')
        self.widthQLE = utils.create_LineEdit((50, 16777215), validator, 4)
        self.heightQLE = utils.create_LineEdit((50, 16777215), validator, 4)
        label = QLabel('<html><p align="center">x</p></html>')
        label.setMaximumWidth(25)

        hlayout1 = utils.add_to_layout('h', self.widthQLE, label,self.heightQLE)
        sizelayout = utils.add_to_layout('v', sizeQL, hlayout1)

        self.imgaspectQChB = QCheckBox(self.tr("Maintain aspect ratio"))
        self.autocropQChB = QCheckBox(self.tr("Auto-crop"))

        vlayout = utils.add_to_layout('v', self.imgaspectQChB,self.autocropQChB)

        rotateQL = QLabel(
                "<html><div align='center'>" + self.tr("Rotate") +
                ":</div><br>(" + self.tr("degrees - clockwise") + ")</html>")
        self.rotateQLE = utils.create_LineEdit((100, 16777215), validator, 3)
        self.vflipQChB = QCheckBox(self.tr('Vertical flip'))
        self.hflipQChB = QCheckBox(self.tr('Horizontal flip'))

        vlayout2 = utils.add_to_layout('v', self.vflipQChB, self.hflipQChB)
        hlayout3 = utils.add_to_layout(
                'h', sizelayout, vlayout, rotateQL, self.rotateQLE,
                vlayout2, None)

        final_layout = utils.add_to_layout('v', hlayout2, hlayout3)
        self.setLayout(final_layout)

    def clear(self):
        """Clear self.widthQLE and self.heightQLE."""
        self.widthQLE.clear()
        self.heightQLE.clear()
        self.commandQLE.clear()
        self.rotateQLE.clear()
        self.imgaspectQChB.setChecked(False)
        self.autocropQChB.setChecked(False)
        self.vflipQChB.setChecked(False)
        self.hflipQChB.setChecked(False)

    def fill_extension_combobox(self, extraformats):
        extraformats = [i for i in extraformats.split("\n")] if extraformats else []
        self.extQCB.clear()
        self.extQCB.addItems(sorted(self.formats + extraformats))

    def ok_to_continue(self):
        """
        Check if everything is ok with imagetab to continue conversion.

        Check if:
        - ImageMagick is missing.
        - Either none or both size lineEdits are active at a time.

        Return True if all tests pass, else False.
        """
        width = self.widthQLE.text()
        height = self.heightQLE.text()

        if not self.parent.imagemagick:
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                'Error!'), self.tr('ImageMagick is not installed.\nYou will '
                'not be able to convert image files until you install it.'))
            return False
        if (width and not height) or (not width and height):
            QMessageBox.warning(self, 'FF Multi Converter - ' + self.tr(
                     'Error!'), self.tr('The size LineEdit may not be empty.'))
            if width and not height:
                self.heightQLE.setFocus()
            else:
                self.widthQLE.setFocus()
            return False
        return True

    def set_default_command(self):
        """Set the default value to self.commandQLE."""
        self.clear()
        self.commandQLE.setText(self.parent.default_command_image)
