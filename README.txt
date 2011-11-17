=====================================================
FF Multi Converter 1.1.0 
=====================================================

Description
------------
FF Multi Converter is a GUI application that converts multiple file formats to different extensions ,
using and combining other programs. The application supports Audio, Video, Image and Document file formats.
It uses ffmpeg for audio/video files, unoconv for document files (which uses the OpenOffice's UNO bindings) 
and PIL library for image file convertions. It also offers recursively conversions (same type or extension).


Requirements and Dependencies
------------------------------
To run this program you need:
python 2.7, PyQt4

Dependencies:
Python Imaging Library (PIL), ffmpeg, unoconv, Open/Libre office suite

The program does NOT require all dependencies to run. 
E.g. you can run the application even if you don't have PIL installed, but you will be able to convert
any other types except image files.

In an Ubuntu system you can install all requirements and dependencies with the command:
	sudo apt-get install python-qt4 ffmpeg unoconv

Python, PIL and OpenOffice are already installed.


Installation
-------------
You don't have to compile the program.
From application's directory just run:
	sudo ./setup.py install

