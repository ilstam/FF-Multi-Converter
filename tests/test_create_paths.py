#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import os

#Uncomment to run tests without having ffmulticonverter installed:
#import sys
#sys.path.append('..')
from ffmulticonverter import path_builders

class CreatePathsLists(unittest.TestCase):
    path = os.path.abspath('folder') + '/'
    many_includes = ['.png', '.bmp', '.gif', '.tif']

    def expect_builder(self, files):
        return [self.path + i for i in files]

    def test_recursive_with_one_include(self):
        """create_paths_list should give known result with known input"""
        expect = self.expect_builder(['file1.png', 'file2.png', 
                             'folder2/file4.png', 'folder2/folder3/file8.png'])
        result = path_builders.create_paths_list(self.path+'*', True, ['.png'])
        self.assertListEqual(sorted(expect), sorted(result))

    def test_recursive_with_many_includes(self):
        """create_paths_list should give known result with known input"""
        expect = self.expect_builder(['file1.png', 'file2.png', 'file3.bmp',
                'folder2/file4.png', 'folder2/file5.bmp', 'folder2/file6.gif',
                           'folder2/pfile6s.tif', 'folder2/folder3/file8.png'])
        result = path_builders.create_paths_list(self.path+'*', True,
                                                            self.many_includes)
        self.assertListEqual(sorted(expect), sorted(result))

    def test_norecursive_with_one_include(self):
        """create_paths_list should give known result with known input"""
        expect = self.expect_builder(['file1.png', 'file2.png'])
        result = path_builders.create_paths_list(self.path+'*', False,['.png'])
        self.assertListEqual(sorted(expect), sorted(result))

    def test_norecursive_with_many_includes(self):
        """create_paths_list should give known result with known input"""
        expect = self.expect_builder(['file1.png', 'file2.png', 'file3.bmp'])
        result = path_builders.create_paths_list(self.path+'*', False,
                                                            self.many_includes)
        self.assertListEqual(sorted(expect), sorted(result))


class CreatePathsListsBadInput(unittest.TestCase):
    def test_path_without_asterisk(self):
        """create_paths_list should fail without '*' at the end of path"""
        self.assertRaises(path_builders.PathError,
                     path_builders.create_paths_list, 'path/', False, ['.png'])

    def test_includes_without_dot(self):
        """create_paths_list should fail if any include starts without '.'"""
        self.assertRaises(path_builders.IncludesError, path_builders.\
                   create_paths_list, 'path/*', False, ['.png', '.bmp', 'gif'])


if __name__ == '__main__':
    unittest.main()
