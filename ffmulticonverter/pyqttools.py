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
Some useful functions to automate some parts of ui creation.
"""

from PyQt4.QtGui import QWidget, QLayout, QSpacerItem

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
              items in the same list will be added to the same line
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
