#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011-2012 Ilias Stamatis <stamatis.iliass@gmail.com>
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

from __future__ import unicode_literals

import os
import re
import glob

class PathError(Exception): pass
class IncludesError(Exception): pass
class ExtToError(Exception): pass

def _should_include(path, includes):
    """Returns True if the given path should be included."""
    ext = os.path.splitext(path)[-1]
    if not includes:
        return True
    else:
        return True if ext in includes else False

def create_paths_list(path_pattern, recursive=True, includes=[]):
    """Creates a list of paths from a path pattern.

    Keyword arguments:
    path_pattern -- an str path using the '*' glob pattern
    recursive    -- if True, include files recursively
                    if False, include only files in the same folder
    includes     -- list of file patterns to include in recursive searches

    Returns: list
    """
    if not path_pattern.endswith('*'):
        raise PathError('path must end with an asterisk (*)')
    if not all(i.startswith('.') for i in includes):
        raise IncludesError('all includes must start with a dot (.)')

    paths_list = []
    paths = glob.glob(path_pattern)
    for path in paths:
        if not os.path.islink(path) and os.path.isdir(path) and recursive:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in sorted(filenames):
                    f = os.path.join(dirpath, filename)
                    if _should_include(f, includes):
                        paths_list.append(f)

        elif _should_include(path, includes):
            paths_list.append(path)

    return paths_list

def build_lists(files_list, ext_to, prefix, suffix, output,
                        saveto_output, rebuild_structure, overwrite_existing):
    """Creates two lists:

    1.conversion_list -- list with dicts to show where each file must be saved
    Example: [{/foo/bar.png : "/foo/bar.png"}, {/f/bar2.png : "/foo2/bar.png"}]

    2.create_folders_list -- a list with folders that must be created

    Keyword arguments:
    files_list -- list with files to be converted
    ext_to     -- the extension to which each file must be converted to
    prefix     -- string that will be added as a prefix to all filenames
    suffix     -- string that will be added as a suffix to all filenames
    output     -- the output folder
    saveto_output -- if True, files will be saved at ouput
                     if False, each file will be saved at its original folder
    rebuild_structure  -- if True, file's structure will be rebuild
    overwrite_existing -- if False, a '~' will be added as prefix to filenames

    Returns: two lists
    """
    if not ext_to.startswith('.'):
        raise ExtToError('ext_to must start with a dot (.)')

    rel_path_files_list = []
    folders = []
    create_folders_list = []
    conversion_list = []

    parent_file = files_list[0]
    parent_dir, parent_name = os.path.split(parent_file)
    parent_base, parent_ext = os.path.split(parent_name)
    parent_dir += '/'

    for _file in files_list:
        _dir, name = os.path.split(_file)
        base, ext = os.path.splitext(name)
        _dir += '/'
        y = _dir + prefix + base + suffix + ext_to

        if saveto_output:
            folder = output + '/'
            if rebuild_structure:
                y = re.sub('^'+parent_dir, '', y)
                y = folder + y
                rel_path_files_list.append(y)
                for z in rel_path_files_list:
                    folder_to_create = os.path.split(z)[0]
                    folders.append(folder_to_create)

                # remove list from duplicates
                for fol in folders:
                    if not fol in create_folders_list:
                        create_folders_list.append(fol)
                create_folders_list.sort()
                # remove first folder because it already exists.
                create_folders_list.pop(0)
            else:
                y = re.sub('^'+_dir, '', y)
                y = folder + y

        if os.path.exists(y) and not overwrite_existing:
            _dir2, _name2 = os.path.split(y)
            y = _dir2 + '/~' + _name2
        # Add quotations to path in order to avoid error in special
        # cases such as spaces or special characters.
        _file = '"' + _file + '"'
        y = '"' + y + '"'

        _dict = {}
        _dict[_file] = y
        conversion_list.append(_dict)

    return create_folders_list, conversion_list
