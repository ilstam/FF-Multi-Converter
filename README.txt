FF Multi Converter
====================

FF Multi Converter is a simple graphical application which enables you to
convert audio, video, image and document files between all popular formats,
by using and combining other applications. It uses ffmpeg for audio/video files,
unoconv for document files and ImageMagick library for image file conversions.

Project homepage: https://sites.google.com/site/ffmulticonverter/

Dependencies
-------------
python3
pyqt4

Optional dependencies
----------------------
ffmpeg or libav
imagemagick
unoconv

The program does NOT require the optional dependencies to run.
E.g. you can run the application even if you don't have ImageMagick installed,
but you will be able to convert any other types except image files.

Installation
-------------
From application's directory run as root:
    python3 setup.py install

Uninstall
----------
Run the following as root to delete all project files from your system:
    sh uninstall.sh

Note:
If you've used a package manager to install the application you should use it
again to remove it, instead of running the above script.
