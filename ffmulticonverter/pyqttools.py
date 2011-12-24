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

"""
A class with some useful methods to automate some parts of ui creation.
"""

from PyQt4.QtGui import QWidget, QLayout, QAction, QLineEdit, QSpacerItem
from PyQt4.QtCore import QSize

class Tools:
    def __init__(self):
        pass
        
    def add_to_layout(self, layout, *items):
        """Add items to QVBox and QHBox layouts easily.
        
        Keyword arguments:
        layout -- a layout (QVBox or QHBox)
        *items -- list with items to be added
        """
        for item in items:
            if isinstance(item, QWidget):
                layout.addWidget(item)
            elif isinstance(item, QLayout):
                layout.addLayout(item)
            elif isinstance(item, QSpacerItem):
                layout.addItem(item)
            elif item is None:
                layout.addStretch()
        return layout

    def add_to_grid(self, layout, *items):
        """Add items to a QGrid layout easily.
        
        Keyword arguments:
        layout -- a QGridLayout
        *items -- list with items to be added
        """
        # for know it just only adds only 1 item per cell.
        x = 0
        for _list in items:
            y = 0
            for item in _list:
                if isinstance(item, QWidget):
                    layout.addWidget(item, x, y)
                elif isinstance(item, QLayout):
                    layout.addLayout(item, x, y)
                elif isinstance(item, QSpacerItem):
                    layout.addItem(item, x, y)
                y += 1
            x += 1
        return layout

    def createAction(self, parent, text, slot, shortcut=None, tip=None):
        """Creates Actions.
        
        Keyword arguments:
        parent -- parent
        text -- action's text
        slot -- slot to connect action
        shortcut -- action's shortcut
        tip -- action's tip to display
        
        Returns: QAction
        """
        action = QAction(text, parent)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        action.triggered.connect(slot)
        return action    
        
    def addActions(self, target, actions):
        """Adds actions to menus.
        
        Keyword arguments:
        target -- Menu to add action
        actions -- list with actions to add
                   Add separator for None in list
        """
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_LineEdit(self, maxsize, validator, maxlength):
        """Creates a lineEdit
        
        Keyword arguments:
        maxsize -- maximum size
        validator -- a regular expression to be added as validator
        maxlength - maximum length
        """        
        lineEdit = QLineEdit()
        if maxsize is not None:
            lineEdit.setMaximumSize(QSize(maxsize[0], maxsize[1]))
        if validator is not None:
            lineEdit.setValidator(validator)
        if maxlength is not None:
            lineEdit.setMaxLength(maxlength)
        return lineEdit
