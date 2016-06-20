# Copyright (C) 2011-2016 Ilias Stamatis <stamatis.iliass@gmail.com>
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

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
        QDialog, QLabel, QPlainTextEdit, QPushButton, QTabWidget
        )

from ffmulticonverter import utils


class AboutDialog(QDialog):
    def __init__(self, text, image, authors, translators, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.parent = parent
        self.authors = authors
        self.translators = translators

        imageQL = QLabel()
        imageQL.setMaximumSize(QSize(63, 61))
        imageQL.setPixmap(QPixmap(image))
        imageQL.setScaledContents(True)
        textQL = QLabel()
        textQL.setText(text)
        textQL.setOpenExternalLinks(True)
        creditsQPB = QPushButton(self.tr('C&redits'))
        closeQPB = QPushButton(self.tr('&Close'))

        vlayout1 = utils.add_to_layout('v', imageQL, None)
        hlayout1 = utils.add_to_layout('h', vlayout1, textQL)
        hlayout2 = utils.add_to_layout('h', creditsQPB, None, closeQPB)
        fin_layout = utils.add_to_layout('v', hlayout1, hlayout2)

        self.setLayout(fin_layout)

        closeQPB.clicked.connect(self.close)
        creditsQPB.clicked.connect(self.show_credits)

        self.resize(455, 200)
        self.setWindowTitle(self.tr('About FF Multi Converter'))

    def show_credits(self):
        """Call CreditsDialog."""
        dialog = CreditsDialog(self.authors, self.translators, self)
        dialog.exec_()


class CreditsDialog(QDialog):
    def __init__(self, authors, translators, parent=None):
        super(CreditsDialog, self).__init__(parent)
        self.parent = parent

        authorsLabel = QPlainTextEdit(authors)
        authorsLabel.setReadOnly(True)
        translatorsLabel = QPlainTextEdit(translators)
        translatorsLabel.setReadOnly(True)
        TabWidget = QTabWidget()
        TabWidget.addTab(authorsLabel, self.tr('Written by'))
        TabWidget.addTab(translatorsLabel, self.tr('Translated by'))
        closeQPB = QPushButton(self.tr('&Close'))

        hlayout = utils.add_to_layout('h', None, closeQPB)
        vlayout = utils.add_to_layout('v', TabWidget, hlayout)

        self.setLayout(vlayout)
        closeQPB.clicked.connect(self.close)

        self.setMinimumSize(QSize(335, 370))
        self.setMaximumSize(QSize(335, 370))
        self.setWindowTitle(self.tr('Credits'))
