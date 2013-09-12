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

from PyQt4.QtCore import QSize
from PyQt4.QtGui import (QDialog, QHBoxLayout, QLabel, QPixmap, QPlainTextEdit,
                         QPushButton, QTabWidget, QVBoxLayout)

from ffmulticonverter import utils


class AboutDialog(QDialog):
    def __init__(self, text, image, authors, translators, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.parent = parent
        self.authors = authors
        self.translators = translators

        imageLabel = QLabel()
        imageLabel.setMaximumSize(QSize(63, 61))
        imageLabel.setPixmap(QPixmap(image))
        imageLabel.setScaledContents(True)
        textLabel = QLabel()
        textLabel.setText(text)
        textLabel.setOpenExternalLinks(True)
        creditsButton = QPushButton(self.tr('C&redits'))
        closeButton = QPushButton(self.tr('&Close'))

        vlayout1 = utils.add_to_layout(QVBoxLayout(), imageLabel, None)
        hlayout1 = utils.add_to_layout(QHBoxLayout(), vlayout1, textLabel)
        hlayout2 = utils.add_to_layout(QHBoxLayout(), creditsButton, None,
                                       closeButton)
        fin_layout = utils.add_to_layout(QVBoxLayout(), hlayout1, hlayout2)

        self.setLayout(fin_layout)

        closeButton.clicked.connect(self.close)
        creditsButton.clicked.connect(self.show_credits)

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
        closeButton = QPushButton(self.tr('&Close'))

        hlayout = utils.add_to_layout(QHBoxLayout(), None, closeButton)
        vlayout = utils.add_to_layout(QVBoxLayout(), TabWidget, hlayout)

        self.setLayout(vlayout)
        closeButton.clicked.connect(self.close)

        self.setMinimumSize(QSize(335, 370))
        self.setMaximumSize(QSize(335, 370))
        self.setWindowTitle(self.tr('Credits'))

if __name__ == '__main__':
    #test dialog
    from PyQt4.QtGui import QApplication
    import qrc_resources
    import sys
    app = QApplication(sys.argv)
    dialog = AboutDialog('About Dialog', ':/ffmulticonverter.png',
                         'Authors', 'Translators')
    dialog.show()
    app.exec_()
