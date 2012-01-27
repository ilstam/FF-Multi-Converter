#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import os

#Uncomment to run tests without having ffmulticonverter installed:
#import sys
#sys.path.append('..')
from ffmulticonverter import path_builders

class BuildLists(unittest.TestCase):
    path = os.path.abspath('folder')
    output = os.path.abspath('folder_dest')
    files = ['file1.png', 'file2.png', 'file3.bmp', 'folder2/file4.png', 
         'folder2/file5.bmp', 'folder2/file6.gif', 'folder2/folder3/file8.png']        
    files_list = [os.path.abspath('folder/'+i) for i in files]
    
    prefix = 'p'
    suffix = 's'      

    def expect_conv_list_output_builder(self, files, out=output):
        list_with_dicts = []
        for i in range(len(files)):
            final = '"' + out + '/' + files[i] + '.tif' + '"'
            _dict = {}            
            _dict['"' + self.files_list[i] + '"'] = final
            list_with_dicts.append(_dict)
        return list_with_dicts

    def test_tooutput_norebuild_overwrite(self):
        """build_lists should give known result with known input"""               
        files = ['pfile1s', 'pfile2s', 'pfile3s', 'pfile4s', 'pfile5s', 
                 'pfile6s', 'pfile8s']        
        expect_conv_list = self.expect_conv_list_output_builder(files)           
        folder_result, conv_result = path_builders.build_lists(self.files_list, 
              '.tif', self.prefix, self.suffix, self.output, True, False, True)        
        self.assertListEqual(sorted(expect_conv_list), sorted(conv_result))

    def test_tooutput_norebuild_nooverwrite(self):
        """build_lists should give known result with known input"""
        files = ['~pfile1s', 'pfile2s', 'pfile3s', 'pfile4s', '~pfile5s', 
                 'pfile6s', 'pfile8s']     
        expect_conv_list = self.expect_conv_list_output_builder(files)           
        folder_result, conv_result = path_builders.build_lists(self.files_list, 
             '.tif', self.prefix, self.suffix, self.output, True, False, False)        
        self.assertListEqual(sorted(expect_conv_list), sorted(conv_result))

    def test_tooutput_rebuild_overwrite(self):
        """build_lists should give known result with known input"""           
        files = ['pfile1s', 'pfile2s', 'pfile3s', 'folder2/pfile4s', 
               'folder2/pfile5s', 'folder2/pfile6s', 'folder2/folder3/pfile8s']     
        expect_conv_list = self.expect_conv_list_output_builder(files)
        expect_fold_list = [os.path.abspath(i) for i in \
                        ('folder_dest/folder2', 'folder_dest/folder2/folder3')]
        folder_result, conv_result = path_builders.build_lists(self.files_list, 
               '.tif', self.prefix, self.suffix, self.output, True, True, True)        
        self.assertListEqual(sorted(expect_conv_list), sorted(conv_result))
        self.assertListEqual(sorted(expect_fold_list), sorted(folder_result))

    def test_tooutput_rebuild_nooverwrite(self):
        """build_lists should give known result with known input"""           
        files = ['~pfile1s', 'pfile2s', 'pfile3s', 'folder2/pfile4s', 
               'folder2/pfile5s', 'folder2/pfile6s', 'folder2/folder3/pfile8s']     
        expect_conv_list = self.expect_conv_list_output_builder(files)
        expect_fold_list = [os.path.abspath(i) for i in \
                        ('folder_dest/folder2', 'folder_dest/folder2/folder3')]
        folder_result, conv_result = path_builders.build_lists(self.files_list, 
              '.tif', self.prefix, self.suffix, self.output, True, True, False)        
        self.assertListEqual(sorted(expect_conv_list), sorted(conv_result))
        self.assertListEqual(sorted(expect_fold_list), sorted(folder_result))

    def test_notooutput_overwrite(self):
        """build_lists should give known result with known input"""           
        files = ['pfile1s', 'pfile2s', 'pfile3s', 'folder2/pfile4s', 
               'folder2/pfile5s', 'folder2/pfile6s', 'folder2/folder3/pfile8s']     
        expect_conv_list = self.expect_conv_list_output_builder(files,self.path)
        folder_result, conv_result = path_builders.build_lists(self.files_list, 
             '.tif', self.prefix, self.suffix, self.output, False, False, True)        
        self.assertListEqual(sorted(expect_conv_list), sorted(conv_result))

    def test_notooutput_nooverwrite(self):
        """build_lists should give known result with known input"""           
        files = ['pfile1s', 'pfile2s', 'pfile3s', 'folder2/pfile4s', 
              'folder2/pfile5s', 'folder2/~pfile6s', 'folder2/folder3/pfile8s']     
        expect_conv_list = self.expect_conv_list_output_builder(files,self.path)
        folder_result, conv_result = path_builders.build_lists(self.files_list, 
            '.tif', self.prefix, self.suffix, self.output, False, False, False)        
        self.assertListEqual(sorted(expect_conv_list), sorted(conv_result))
        

class BuildListsBadInput(unittest.TestCase):        
    def test_extto_without_dot(self):
        """build_lists should fail if ext_to starts without '.'"""
        self.assertRaises(path_builders.ExtToError, path_builders.build_lists, 
                                    [], 'png', '', '', '', False, False, False)
   
                                 
if __name__ == '__main__':
    unittest.main()