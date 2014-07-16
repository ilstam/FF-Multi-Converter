# Copyright (C) 2011-2014 Ilias Stamatis <stamatis.iliass@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
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

import os
import re
import xml.etree.ElementTree as etree

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import (
        QDialog, QDialogButtonBox, QFileDialog, QLabel, QLineEdit, QListWidget,
        QMessageBox, QPushButton, QShortcut, QSizePolicy, QSpacerItem
        )

from ffmulticonverter import utils
from ffmulticonverter import config


class ShowPresets(QDialog):
    def __init__(self, parent=None):
        super(ShowPresets, self).__init__(parent)

        self.original_presets_file = config.find_presets_file(
                config.presets_file_name)
        self.current_presets_file = config.presets_file

        presListWidget = QListWidget()
        labelLabel = QLabel(self.tr('Preset label'))
        labelLineEdit = QLineEdit()
        labelLineEdit.setReadOnly(True)
        commandLabel = QLabel(self.tr('Preset command line parameters'))
        commandLineEdit = QLineEdit()
        commandLineEdit.setReadOnly(True)
        extLabel = QLabel(self.tr('Output file extension'))
        extLineEdit = QLineEdit()
        extLineEdit.setReadOnly(True)
        addButton = QPushButton(self.tr('Add'))
        deleteButton = QPushButton(self.tr('Delete'))
        delete_allButton = QPushButton(self.tr('Delete all'))
        editButton = QPushButton(self.tr('Edit'))
        searchLabel = QLabel(self.tr('Search'))
        searchLineEdit = QLineEdit()
        okButton = QPushButton(self.tr('OK'))
        okButton.setDefault(True)

        spc1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spc2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spc3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        grid = utils.add_to_grid(
                [delete_allButton, addButton, spc1],
                [deleteButton, editButton, spc2]
                )

        hlayout = utils.add_to_layout(
                'h', searchLabel, searchLineEdit, None, okButton)

        final_layout = utils.add_to_layout(
                'v', presListWidget, labelLabel, labelLineEdit, commandLabel,
                commandLineEdit, extLabel, extLineEdit, grid, spc3, hlayout
                )

        self.setLayout(final_layout)

        okButton.clicked.connect(self.accept)
        presListWidget.currentRowChanged.connect(self.show_preset)
        addButton.clicked.connect(self.add_preset)
        deleteButton.clicked.connect(self.delete_preset)
        delete_allButton.clicked.connect(self.delete_all_presets)
        editButton.clicked.connect(self.edit_preset)
        searchLineEdit.textEdited.connect(self.search)

        del_shortcut = QShortcut(self)
        del_shortcut.setKey(Qt.Key_Delete)
        del_shortcut.activated.connect(self.delete_preset)

        #aliasing
        self.presListWidget = presListWidget
        self.labelLineEdit = labelLineEdit
        self.commandLineEdit = commandLineEdit
        self.extLineEdit = extLineEdit
        self.deleteButton = deleteButton
        self.delete_allButton = delete_allButton
        self.editButton = editButton
        self.searchLineEdit = searchLineEdit

        self.resize(430, 480)
        self.setWindowTitle(self.tr('Edit Presets'))

        QTimer.singleShot(0, self.load_xml)
        QTimer.singleShot(0, self.fill_presListWidget)

    def load_xml(self):
        """Load xml tree and set xml root."""
        try:
            self.tree = etree.parse(self.current_presets_file)
        except (etree.ParseError, FileNotFoundError):
            try:
                self.tree = etree.parse(self.original_presets_file)
            except FileNotFoundError:
                # when program is not installed
                try:
                    self.tree = etree.parse('share/' + config.presets_file_name)
                except FileNotFoundError:
                    # when running from test_dialogs.py
                    self.tree = etree.parse(
                            '../share/' + config.presets_file_name)
            if not os.path.exists(config.config_dir):
                os.makedirs(config.config_dir)
        self.root = self.tree.getroot()

    def set_buttons_clear_lineEdits(self):
        """Enable or disable button's and clear lineEdits."""
        enable = bool(self.presListWidget)
        self.editButton.setEnabled(enable)
        self.deleteButton.setEnabled(enable)
        self.delete_allButton.setEnabled(enable)
        if not enable:
            self.labelLineEdit.clear()
            self.commandLineEdit.clear()
            self.extLineEdit.clear()

    def fill_presListWidget(self):
        """Clear self.presListWidget and to it presets' tags."""
        self.presListWidget.clear()
        for i in sorted([y.tag for y in self.root]):
            elem = self.root.find(i)
            self.presListWidget.addItem(utils.XmlListItem(i, elem))

        self.presListWidget.setCurrentRow(0)
        self.set_buttons_clear_lineEdits()
        self.searchLineEdit.clear()

    def show_preset(self):
        """Fill LineEdits with current xml element's values."""
        try:
            xml_elem = self.presListWidget.currentItem().xml_element
        except AttributeError:
            return

        self.labelLineEdit.setText(xml_elem[0].text)
        self.commandLineEdit.setText(xml_elem[1].text)
        self.commandLineEdit.home(False)
        self.extLineEdit.setText(xml_elem[2].text)

    def add_preset(self):
        """Open AddorEditPreset() dialog and add a preset xml root."""
        dialog = AddorEditPreset(None, False, self)
        if dialog.exec_():
            element = etree.Element(dialog.name_text)
            label = etree.Element('label')
            label.text = dialog.label_text
            command = etree.Element('params')
            command.text = dialog.command_text
            ext = etree.Element('extension')
            ext.text = dialog.ext_text
            category = etree.Element('category')
            category.text = 'Scattered'

            for num, elem in enumerate([label, command, ext, category]):
                element.insert(num, elem)
            index = sorted(
                    [i.tag for i in self.root] + [dialog.name_text]
                    ).index(dialog.name_text)
            self.root.insert(index, element)
            self.save_tree()
            self.fill_presListWidget()

    def delete_preset(self):
        """
        Ask user wether he wants to delete the selected preset.
        If so, delete the preset from xml root.
        """
        try:
            xml_elem = self.presListWidget.currentItem().xml_element
        except AttributeError:
            return

        reply = QMessageBox.question(self, 'FF Multi Converter - ' + self.tr(
            'Delete Preset'), self.tr('Are you sure that you want to delete '
            'the {0} preset?'.format(xml_elem.tag)),
            QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            self.root.remove(xml_elem)
            self.save_tree()
            self.fill_presListWidget()

    def delete_all_presets(self):
        """
        Ask user if he wants to delete all presets.
        If so, clear xml root.
        """
        reply = QMessageBox.question(self, 'FF Multi Converter - ' + self.tr(
            'Delete Preset'), self.tr('Are you sure that you want to delete '
            'all presets?'), QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            self.root.clear()
            self.save_tree()
            self.fill_presListWidget()

    def edit_preset(self):
        """Call the AddorEditPreset() dialog and update xml element's values."""
        elem = self.presListWidget.currentItem().xml_element
        dialog = AddorEditPreset(elem, True)

        if dialog.exec_():
            elem.tag = dialog.name_text
            elem[0].text = dialog.label_text
            elem[1].text = dialog.command_text
            elem[2].text = dialog.ext_text
            self.save_tree()
            self.fill_presListWidget()

    def search(self):
        """
        Search for keywords in presets data.

        Show a preset only if its tag, label or extension matches any of
        search string's tokens.
        """
        txt = self.searchLineEdit.text().strip().lower()
        if not txt:
            self.fill_presListWidget()
            return

        self.presListWidget.clear()
        for i in txt.split(' '):
            for p in sorted([y.tag for y in self.root]):
                elem = self.root.find(p)
                if (i.strip() and (
                        i in elem.tag.lower()
                        or i in elem[0].text.lower()
                        or i in elem[2].text.lower())):
                    self.presListWidget.addItem(utils.XmlListItem(p, elem))

        self.presListWidget.setCurrentRow(0)
        self.set_buttons_clear_lineEdits()

    def save_tree(self):
        """Save xml tree."""
        with open(self.current_presets_file, 'wb') as _file:
            try:
                etree.ElementTree(self.root).write(_file)
            except:
                pass

    def import_presets(self):
        """Import an xml tree."""
        title = 'FF Multi Converter - Import'
        reply = QMessageBox.question(self, title, self.tr('All current '
                'presets will be deleted.\nAre you sure that you want to '
                'continue?'), QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            fname = QFileDialog.getOpenFileName(self, title)
            if fname:
                msg = self.tr('Succesful import!')
                try:
                    self.tree = etree.parse(fname)
                except:
                    msg = self.tr('Import failed!')
                else:
                    self.root = self.tree.getroot()
                    self.save_tree()
                QMessageBox.information(self, title, msg)

    def export_presets(self):
        """Export the xml tree."""
        fname = QFileDialog.getSaveFileName(
                self, 'FF Multi Converter - ' + self.tr('Export presets'),
                '.xml')
        if fname:
            self.load_xml()
            with open(fname, 'wb') as _file:
                try:
                    etree.ElementTree(self.root).write(_file)
                except:
                    pass

    def reset(self):
        """Import the default xml tree."""
        reply = QMessageBox.question(self, 'FF Multi Converter - ' + self.tr(
            'Delete Preset'), self.tr('Are you sure that you want to restore '
            'the default presets?'), QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            if os.path.exists(self.current_presets_file):
                os.remove(self.current_presets_file)

    def synchronize(self):
        """
        Synchronize current presets with default presets.

        For each preset in default presets:
        - if not contained in current presets, add it to current presets
        - if has the same name with some preset in current presets but
          different attributes, then add this preset to current presets and
          add an '__OLD' suffix to matching preset's name
        """
        reply = QMessageBox.question(
                self, 'FF Multi Converter - ' +
                self.tr('Presets Synchronization'),
                self.tr('Current presets and default presets will be merged. '
                'Are you sure that you want to continue?'),
                QMessageBox.Yes|QMessageBox.Cancel
                )
        if not reply == QMessageBox.Yes:
            return

        def_tree = etree.parse(self.original_presets_file)
        def_root = def_tree.getroot()
        self.load_xml()

        for i in def_root:
            for n, y in enumerate(self.root):
                if i.tag == y.tag:
                    if not (i[0].text == y[0].text
                            and i[1].text == y[1].text
                            and i[2].text == y[2].text):
                        # copy element and change its name
                        elem = etree.Element(y.tag)
                        label = etree.Element('label')
                        label.text = i[0].text
                        command = etree.Element('params')
                        command.text = i[1].text
                        ext = etree.Element('extension')
                        ext.text = i[2].text
                        elem.insert(0, label)
                        elem.insert(1, command)
                        elem.insert(2, ext)

                        y.tag = y.tag + config.presets_old
                        self.root.insert(n+1, elem)
                    break
            else:
                # preset not found
                index = sorted([x.tag for x in self.root] +
                               [i.tag]).index(i.tag)
                self.root.insert(index, i)
        self.save_tree()

    def remove_old(self):
        """Remove those xml elements which their tags has an __OLD suffix."""
        reply = QMessageBox.question(self, 'FF Multi Converter - ' + self.tr(
            'Remove old presets'), self.tr('All presets with an __OLD suffix '
            'will be deleted. Are you sure that you want to continue?'),
            QMessageBox.Yes|QMessageBox.Cancel)
        if not reply == QMessageBox.Yes:
            return

        self.load_xml()
        for i in self.root:
            if i.tag.endswith(config.presets_old):
                self.root.remove(i)
        self.save_tree()

    def accept(self):
        """
        Save current xml element's values in order to be used from
        main program and close (accept) dialog.
        """
        self.the_command = None
        if self.presListWidget:
            self.the_command = self.presListWidget.currentItem()\
                    .xml_element[1].text
            self.the_extension = self.presListWidget.currentItem()\
                    .xml_element[2].text
        QDialog.accept(self)


class AddorEditPreset(QDialog):
    def __init__(self, xml_element, edit=False, parent=None):
        super(AddorEditPreset, self).__init__(parent)

        nameLabel = QLabel(self.tr('Preset name (one word, A-z, 0-9)'))
        nameLineEdit = QLineEdit()
        labelLabel = QLabel(self.tr('Preset label'))
        labelLineEdit = QLineEdit()
        commandLabel = QLabel(self.tr('Preset command line parameters'))
        commandLineEdit = QLineEdit()
        extLabel = QLabel(self.tr('Output file extension'))
        extLineEdit = QLineEdit()
        buttonBox = QDialogButtonBox(
                QDialogButtonBox.Ok|QDialogButtonBox.Cancel)

        final_layout = utils.add_to_layout(
                'v', nameLabel, nameLineEdit, labelLabel, labelLineEdit,
                commandLabel, commandLineEdit, extLabel, extLineEdit, buttonBox
                )

        self.setLayout(final_layout)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.resize(410, 280)

        if edit:
            nameLineEdit.setText(xml_element.tag)
            labelLineEdit.setText(xml_element[0].text)
            commandLineEdit.setText(xml_element[1].text)
            commandLineEdit.home(False)
            extLineEdit.setText(xml_element[2].text)

            title = self.tr('Edit {0}'.format(xml_element.tag))
        else:
            title = self.tr('Add preset')

        #aliasing
        self.nameLineEdit = nameLineEdit
        self.labelLineEdit = labelLineEdit
        self.commandLineEdit = commandLineEdit
        self.extLineEdit = extLineEdit
        self.buttonBox = buttonBox

        self.resize(410, 280)
        self.setWindowTitle(title)

    def validation(self):
        """
        Extract data from GUI and check if everything is ok to continue.

        Check if:
        - Any lineEdit is empty.
        - Preset name and extension meet the qualifications.

        Return True if all tests pass, else False.
        """
        self.name_text = self.nameLineEdit.text().strip()
        self.label_text = self.labelLineEdit.text().strip()
        self.command_text = self.commandLineEdit.text().strip()
        self.ext_text = self.extLineEdit.text().strip()

        if not self.name_text:
            QMessageBox.warning(
                    self, 'Edit Preset - ' + self.tr('Error!'),
                    self.tr("Preset name can't be left blank.")
                    )
            self.nameLineEdit.setFocus()
            return False
        if not re.match('^[A-Za-z0-9_]*$', self.name_text):
            QMessageBox.warning(
                    self, 'Edit Preset - ' + self.tr('Error!'),
                    self.tr(
                    'Preset name must be one word and contain only letters '
                    'and digits.')
                    )
            self.nameLineEdit.selectAll()
            self.nameLineEdit.setFocus()
            return False
        if not self.label_text:
            QMessageBox.warning(
                    self, 'Edit Preset - ' + self.tr('Error!'),
                    self.tr("Preset label can't be left blank.")
                    )
            self.labelLineEdit.setFocus()
            return False
        if not self.command_text:
            QMessageBox.warning(
                    self, 'Edit Preset - ' + self.tr('Error!'),
                    self.tr("Command label can't be left blank.")
                    )
            self.commandLineEdit.setFocus()
            return False
        if not self.ext_text:
            QMessageBox.warning(
                    self, 'Edit Preset - ' + self.tr('Error!'),
                    self.tr("Extension label can't be left blank.")
                    )
            self.extLineEdit.setFocus()
            return False
        if len(self.ext_text.split()) != 1 or self.ext_text[0] == '.':
            QMessageBox.warning(
                    self, 'Edit Preset - ' + self.tr('Error!'),
                    self.tr(
                    'Extension must be one word and must not start with a  dot.')
                    )
            self.extLineEdit.selectAll()
            self.extLineEdit.setFocus()
            return False
        return True

    def accept(self):
        if self.validation():
            QDialog.accept(self)
