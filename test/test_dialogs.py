#!/usr/bin/env python3

import sys
from PyQt5.QtWidgets import QApplication

sys.path.append('..')
# from ffmulticonverter import qrc_resources
from ffmulticonverter.about_dlg import AboutDialog
from ffmulticonverter.presets_dlgs import ShowPresets
from ffmulticonverter.preferences_dlg import Preferences
from ffmulticonverter.progress import Progress


def main():
    app = QApplication(sys.argv)

    dlg_about = AboutDialog('About Dialog', ':/ffmulticonverter.png', 'Authors', 'Translators')
    dlg_showpresets = ShowPresets()
    dlg_preferences = Preferences(test=True)
    dlg_progress = Progress([], None, False, None, test=True)

    # uncomment the dialog you wish to test
    # dlg_about.show()
    # dlg_showpresets.show()
    dlg_preferences.show()
    # dlg_progress.show()

    app.exec_()

if __name__ == '__main__':
    main()
