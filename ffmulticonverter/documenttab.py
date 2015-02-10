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

import os

from PyQt4.QtGui import QWidget, QLabel, QComboBox, QMessageBox

from ffmulticonverter import utils
from ffmulticonverter import config


class ValidationError(Exception):
    pass


class DocumentTab(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(DocumentTab, self).__init__(parent)
        self.name = 'Documents'
        self.formats = config.document_formats

        flist = []
        for i in self.formats:
            for y in self.formats[i]:
                flist.append(i + ' to ' + y)
        flist.sort()

        convertQL = QLabel(self.tr('Convert:'))
        self.convertQCB = QComboBox()
        self.convertQCB.addItems(flist)
        final_layout = utils.add_to_layout(
                'h', convertQL, self.convertQCB, None)
        self.setLayout(final_layout)

    def ok_to_continue(self):
        """
        Check if everything is ok with documenttab to continue conversion.

        Checks if:
        - unoconv is missing.
        - Given file extension is same with the declared extension.

        Return True if all tests pass, else False.
        """
        decl_ext = self.convertQCB.currentText().split(' ')[0]

        try:
            if not self.parent.unoconv:
                raise ValidationError(
                        self.tr(
                        'Unocov is not installed.\nYou will not be able '
                        'to convert document files until you install it.')
                        )
            for i in self.parent.fnames:
                file_ext = os.path.splitext(i)[-1][1:]
                if file_ext != decl_ext:
                    raise ValidationError(
                            self.trUtf8('{0} is not {1}!'.format(i, decl_ext)))
            return True

        except ValidationError as e:
            QMessageBox.warning(self, 'FF Multi Converter - ' + \
                    self.tr('Error!'), str(e))
            return False
