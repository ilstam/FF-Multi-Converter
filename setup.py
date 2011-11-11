#!/usr/bin/python
# -*- coding: utf-8 -*-
# FF Multi Converter's setup.py

from distutils.core import setup

setup(
    name = "ffmulticonverter",
    packages = ["ffmulticonverter"],
    scripts = ["ffmulticonverter/ffmulticonverter"],
    data_files = [("/usr/share/app-install/icons/", 
                              ["ffmulticonverter/icons/ffmulticonverter.png"]),
                  ("/usr/share/applications/", 
                     ["ffmulticonverter/desktop/FF-Multi-Converter.desktop"])],
    version = "1.0",
    description = "GUI File Format Converter",
    author = "Ilias Stamatis",
    author_email = "il.stam@yahoo.gr",
    license = "GNU GPL3",
    platforms = 'Linux',
    requires = ['python2', 'PyQt4', 'ffmpeg', 'unoconv'], 
    url = "http://pypi.python.org/pypi/ffmulticonverter",
    keywords = ["convert", "file format", "extension"],
    classifiers = [
        "Programming Language :: Python", 
        "License :: OSI Approved :: GNU General Public License (GPL)", 
        "Operating System :: POSIX :: Linux", 
        "Development Status :: 3 - Alpha", 
        "Environment :: X11 Applications :: Qt", 
        "Natural Language :: Greek", 
        "Intended Audience :: End Users/Desktop", 
        "Topic :: Multimedia :: Sound/Audio :: Conversion", 
        "Topic :: Utilities"],    
    long_description = """
File Format Multi Converter
---------------------------

GUI application that converts audio, video, image and document file formats to 
other extensions using ffmpeg, unoconv, and PIL library.

Features
 - Converts files in the same folder (same type or extension)
 - Recursively convert files (same type or extension)
 - Delete original files
 
Requires: python 2.7, PyQt4, ffmpeg, unoconv, Open/Libre office suite
"""
)
