#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011-2013 Ilias Stamatis <stamatis.iliass@gmail.com>
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
Useful functions to automate some parts of ui creation.
"""

from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import (QAction, QLayout, QLineEdit, QMenu, QSpacerItem,
                         QWidget)


def add_to_layout(layout, *items):
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
        else:
            raise TypeError("Argument of wrong type!")
    return layout

def add_to_grid(layout, *items):
    """Add items to a QGrid layout easily.

    Keyword arguments:
    layout -- a QGridLayout
    *items -- list with lists of items to be added.
              items in the same list will be added to the same line of grid.
    """
    # for now it adds only 1 item per cell.
    for x, _list in enumerate(items):
        for y, item in enumerate(_list):
            if isinstance(item, QWidget):
                layout.addWidget(item, x, y)
            elif isinstance(item, QLayout):
                layout.addLayout(item, x, y)
            elif isinstance(item, QSpacerItem):
                layout.addItem(item, x, y)
            elif item is None:
                pass
            else:
                raise TypeError("Argument of wrong type!")
    return layout

def create_action(parent, text, shortcut=None, icon=None, tip=None,
                  triggered=None, toggled=None, context=Qt.WindowShortcut):
    """Create a QAction with the given attributes."""
    action = QAction(text, parent)
    if triggered is not None:
        action.triggered.connect(triggered)
    if toggled is not None:
        action.toggled.connect(toggled)
        action.setCheckable(True)
    if icon is not None:
        action.setIcon( icon )
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    action.setShortcutContext(context)
    return action

def add_actions(target, actions, insert_before=None):
    """Add actions to menu.

    Keyword arguments:
    target -- menu to add action
    actions -- list with actions to add
    """
    previous_action = None
    target_actions = list(target.actions())
    if target_actions:
        previous_action = target_actions[-1]
        if previous_action.isSeparator():
            previous_action = None
    for action in actions:
        if (action is None) and (previous_action is not None):
            if insert_before is None:
                target.addSeparator()
            else:
                target.insertSeparator(insert_before)
        elif isinstance(action, QMenu):
            if insert_before is None:
                target.addMenu(action)
            else:
                target.insertMenu(insert_before, action)
        elif isinstance(action, QAction):
            if insert_before is None:
                target.addAction(action)
            else:
                target.insertAction(insert_before, action)
        previous_action = action

def create_LineEdit(maxsize, validator, maxlength):
    """Create a lineEdit with the given attributes.

    Keyword arguments:
    maxsize -- maximum size
    validator -- a QValidator
    maxlength - maximum length

    Returns: QLineEdit
    """
    lineEdit = QLineEdit()
    if maxsize is not None:
        lineEdit.setMaximumSize(QSize(maxsize[0], maxsize[1]))
    if validator is not None:
        lineEdit.setValidator(validator)
    if maxlength is not None:
        lineEdit.setMaxLength(maxlength)
    return lineEdit
