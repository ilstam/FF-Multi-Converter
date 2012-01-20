=====================================================
FF Multi Converter 1.3.0 Beta
=====================================================

Description
------------
FF Multi Converter is a simple graphical application that enables you to convert audio, video, image and document files
between all popular formats, using and combining other programs. It uses ffmpeg for audio/video files, unoconv for document files (which uses the OpenOffice's UNO bindings) and PythonMagick library for image file conversions. 
It offers extra options such as to configure Frequency, Channels, Bitrate on audio conversions, Size, Aspect, Frame Rate, Bitrate on video conversions and Size on images. Recursive conversions are also available.

The goal of FF Multi Converter is to gather all multimedia types in one application and provide conversions for them easily through a user friendly interface. Extra options will be gradually added.


Dependencies
-------------
python (>= 2.6) & (< 3.0) 
PyQt4

Optional dependencies
----------------------
ffmpeg
PythonMagick
unoconv
Open/Libre office

The program does NOT require the optional dependencies to run. 
E.g. you can run the application even if you don't have PythonMagick installed, but you will be able to convert
any other types except image files.

Installation
-------------
You don't have to compile the program.
From application's directory run as root:
	./setup.py install

