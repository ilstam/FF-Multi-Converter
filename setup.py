#!/usr/bin/env python3

import ffmulticonverter
from distutils.core import setup


data_files = [('share/applications/', ['share/ffmulticonverter.desktop']),
              ('share/pixmaps/', ['share/ffmulticonverter.png']),
              ('share/ffmulticonverter', ['share/presets.xml']),
              ('share/man/man1', ['man/ffmulticonverter.1.gz'])]

setup(
    name = 'ffmulticonverter',
    packages = ['ffmulticonverter'],
    scripts = ['bin/ffmulticonverter'],
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
                'images', 'documents'],
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Natural Language :: English',
        'Natural Language :: Bulgarian',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Czech',
        'Natural Language :: French',
        'Natural Language :: Italian',
        'Natural Language :: German',
        'Natural Language :: Greek',
        'Natural Language :: Hungarian',
        'Natural Language :: Malay',
        'Natural Language :: Polish',
        'Natural Language :: Portuguese',
        'Natural Language :: Portuguese (Brazilian)',
        'Natural Language :: Russian',
        'Natural Language :: Spanish',
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

Requires: python2, pyqt4, ffmpeg, pythonmagick, unoconv
"""
)
