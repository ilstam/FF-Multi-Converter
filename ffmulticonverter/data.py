#!/usr/bin/python
# -*- coding: utf-8 -*-

from __init__ import __version__

#Supported formats

audio_formats = ['aac', 'ac3', 'afc', 'aifc', 'aiff', 'amr', 'asf', 'au',
                 'avi', 'dvd', 'flac', 'flv', 'm4a', 'm4v', 'mka', 'mmf',
                 'mov', 'mp2', 'mp3', 'mp4', 'mpeg', 'ogg', 'ra', 'rm', 'spx',
                 'vob', 'wav', 'webm', 'wma']

video_formats = ['asf', 'avi', 'dvd', 'flv', 'm1v', 'm2t', 'm2v', 'mkv', 'mov',
                 'mp4', 'mpeg', 'mpg', 'ogg', 'ogv', 'psp', 'rm', 'ts', 'vob',
                 'webm', 'wma', 'wmv']

vid_to_aud = ['aac', 'ac3', 'aiff', 'au', 'flac', 'mp2' , 'wav']

image_formats = ['aai', 'bmp', 'cgm', 'dcm', 'dpx', 'emf', 'eps', 'fpx', 'gif',
                 'jbig', 'jng', 'jpeg', 'mrsid', 'p7', 'pdf', 'picon', 'png',
                 'ppm', 'psd', 'rad', 'tga', 'tif', 'webp', 'wpg', 'xpm']

extra_img_formats_dict = { 'bmp' : ['bmp2', 'bmp3', 'dib'],
                           'eps' : ['ps', 'ps2', 'ps3', 'eps2',
                           'eps3', 'epi', 'epsi', 'epsf'],
                           'jpeg' : ['jpg', 'jpe'],
                           'mrsid' : ['sid'],
                           'pdf' : ['epdf'],
                           'picon' : ['icon'],
                           'png' : ['png24', 'png32'],
                           'ppm' : ['pnm', 'pgm'],
                           'tif' : ['tiff']
                          }

document_formats = { 'doc' : ['odt', 'pdf'],
                     'html' : ['odt'],
                     'odp' : ['pdf', 'ppt'],
                     'ods' : ['pdf'],
                     'odt' : ['doc', 'html', 'pdf', 'rtf', 'sxw', 'txt','xml'],
                     'ppt' : ['odp'],
                     'rtf' : ['odt'],
                     'sdw' : ['odt'],
                     'sxw' : ['odt'],
                     'txt' : ['odt'],
                     'xls' : ['ods'],
                     'xml' : ['doc', 'odt', 'pdf']
                    }
