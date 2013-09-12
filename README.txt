FF Multi Converter
====================

FF Multi Converter is a simple graphical application which enables you to
convert audio, video, image and document files between all popular formats,
using and combining other programs. It uses ffmpeg for audio/video files,
unoconv for document files and PythonMagick library for image file conversions.

Project homepage: https://sites.google.com/site/ffmulticonverter/
Download page: https://sourceforge.net/projects/ffmulticonv/files/

Dependencies
-------------
python3
pyqt4

Optional dependencies
----------------------
ffmpeg
pythonmagick
unoconv

The program does NOT require the optional dependencies to run.
E.g. you can run the application even if you don't have PythonMagick installed,
but you will be able to convert any other types except image files.

Installation
-------------
From application's directory run as root:
    ./setup.py install
