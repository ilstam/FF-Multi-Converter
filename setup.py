#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ffmulticonverter
from distutils.core import setup

data_files = [('share/applications/', ['data/ffmulticonverter.desktop']),
              ('share/icons/', ['data/ffmulticonverter.png']),
              ('share/man/man1', ['doc/ffmulticonverter.1']),
              ('/usr/share/ffmulticonverter', ['data/presets.xml'])]

setup(
    name = 'ffmulticonverter',
    packages = ['ffmulticonverter'],
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
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Natural Language :: English',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: German',
        'Natural Language :: Greek',
        'Natural Language :: Hungarian',
        'Natural Language :: Polish',
        'Natural Language :: Portuguese',
        'Natural Language :: Russian',
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
 - Audio/video ffmpeg-presets management.
 - Options for saving and naming files.
 - Recursive conversions.

Requires: python2, PyQt4, ffmpeg, PythonMagick, unoconv
"""
)
