#!/usr/bin/python
# -*- coding: utf-8 -*-
# FF Multi Converter's setup.py

import ffmulticonverter
from distutils.core import setup

data_files = [('share/applications/', ['data/FF-Multi-Converter.desktop']),
              ('share/icons/', ['data/ffmulticonverter.png']),
              ('share/man/man1', ['doc/ffmulticonverter.1'])]

setup(
    name = 'ffmulticonverter',
    packages = ['ffmulticonverter', 'ffmulticonverter/qrc_resources'],
    scripts = ['ffmulticonverter/ffmulticonverter'],
    data_files = data_files,
    version = ffmulticonverter.__version__,
    description = 'GUI File Format Converter',
    author = 'Ilias Stamatis',
    author_email = 'stamatis.iliass@gmail.com',
    license = 'GNU GPL3',
    platforms = 'Linux',
    url = 'https://sites.google.com/site/ffmulticonverter/',
    download_url = 'https://github.com/Ilias95/FF-Multi-Converter/downloads',
    keywords = ['convert', 'file format', 'extension', 'audio', 'video',
                                                         'images', 'document'],
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Natural Language :: English',
        'Natural Language :: Greek',
        'Natural Language :: Turkish',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Video :: Conversion',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
        'Topic :: Utilities'],
    long_description = """
FF Multi Converter
-------------------

Graphical application which enables you to convert audio, video, image and
document files between all popular formats using ffmpeg, unoconv, and PythonMagick.

Features:
 - Conversions for several file formats.
 - Very easy to use interface.
 - Access to common conversion options.
 - Options for saving and naming files.
 - Recursive conversions.

Requires: python2, PyQt4, ffmpeg, PythonMagick, unoconv
"""
)
