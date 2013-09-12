#!/usr/bin/env python3

import sys
from PyQt4.QtGui import QApplication

#from ffmulticonverter import qrc_resources
from ffmulticonverter.about_dlg import AboutDialog
from ffmulticonverter.presets_dlgs import ShowPresets
from ffmulticonverter.preferences_dlg import Preferences
from ffmulticonverter.progress import Progress


def test_AboutDialog():
    return AboutDialog('About Dialog', ':/ffmulticonverter.png', 'Authors',
                       'Translators')

def test_ShowPresetsDialog():
    return ShowPresets()

def test_PreferencesDialog():
    return Preferences(test=True)

def test_ProgressDialog():
    return Progress([], '', '', False, '', False, False, None, test=True)


def main():
    app = QApplication(sys.argv)
    # uncomment the dialog you wish to test
    dialog = test_AboutDialog()
    #dialog = test_ShowPresetsDialog()
    #dialog = test_PreferencesDialog()
    #dialog = test_ProgressDialog()
    dialog.show()
    app.exec_()


if __name__ == '__main__':
    main()
