=====================================================
FF Multi Converter 
=====================================================

Description
------------
FF Multi Converter is a GUI application that converts multiple file formats to different extensions ,
using and combining other programs. The application supports Audio, Video, Image and Document file formats.
It uses ffmpeg for audio/video files, unoconv for document files (which uses the OpenOffice's UNO bindings) 
and PIL library for image file convertions. It also offers recursively conversions (same type or extension).

Dependencies
-------------
This version requires:
python 2.7, PyQt4, ffmpeg, unoconv, Open/Libre office suite

In an Ubuntu system you can install the dependencies with the command:
	sudo apt-get install python-qt4 ffmpeg unoconv

Python and OpenOffice are already installed.

The program does NOT require all dependencies to run. 
E.g. you can run the application even if you don't have unoconv installed, but you will be able to do
any other convertions, except document files.

Installation
-------------
From application's directory just run:
	sudo ./setup.py install

