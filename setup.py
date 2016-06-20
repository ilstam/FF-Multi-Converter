#!/usr/bin/env python3

import ffmulticonverter
from distutils.core import setup


data_files = [('share/applications/', ['share/ffmulticonverter.desktop']),
              ('share/pixmaps/', ['share/ffmulticonverter.png']),
              ('share/ffmulticonverter', ['share/presets.xml']),
              ('share/man/man1', ['man/ffmulticonverter.1.gz'])]

setup(
    name = ffmulticonverter.__name__,
    packages = [ffmulticonverter.__name__],
    scripts = ['bin/ffmulticonverter'],
    data_files = data_files,
    version = ffmulticonverter.__version__,
    description = ffmulticonverter.__description__,
    author = ffmulticonverter.__author__,
    author_email = ffmulticonverter.__author_email__,
    license = ffmulticonverter.__license__,
    platforms = ffmulticonverter.__platforms__,
    url = ffmulticonverter.__url__,
    download_url = ffmulticonverter.__download_url__,
    keywords = ['convert', 'file format', 'extension', 'audio', 'video',
                'images', 'documents', 'ffmpeg', 'imagemagick', 'unoconv'],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Natural Language :: English',
        'Natural Language :: Bulgarian',
        'Natural Language :: Catalan',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Czech',
        'Natural Language :: French',
        'Natural Language :: Italian',
        'Natural Language :: Galician',
        'Natural Language :: German',
        'Natural Language :: Greek',
        'Natural Language :: Hungarian',
        'Natural Language :: Malay',
        'Natural Language :: Polish',
        'Natural Language :: Portuguese',
        'Natural Language :: Portuguese (Brazilian)',
        'Natural Language :: Romanian',
        'Natural Language :: Russian',
        'Natural Language :: Spanish',
        'Natural Language :: Turkish',
        'Natural Language :: Vietnamese',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Video :: Conversion',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
        'Topic :: Utilities'],
    long_description = """
FF Multi Converter
-------------------

Graphical application which enables you to convert audio, video, image and
document files between all popular formats using ffmpeg, unoconv, and ImageMagick.

Features:
 - Conversions for several file formats.
 - Very easy to use interface.
 - Access to common conversion options.
 - Audio/video ffmpeg-presets management.
 - Options for saving and naming files.
 - Multilingual - over 20 languages.

Requires: python3, pyqt5
Optionally requires: ffmpeg, imagemagick, unoconv
"""
)
