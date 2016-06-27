import os


#-----general data

home = os.getenv("HOME")
config_dir = os.path.join(home, '.config/ffmulticonverter/')

default_ffmpeg_cmd = ''
default_imagemagick_cmd = ''

#-----log data

log_dir = os.path.join(config_dir, 'logs/')
log_file = os.path.join(log_dir, 'history.log')
log_format  = '%(asctime)s : %(levelname)s - %(type)s\n' +\
              'Command: %(command)s\n' +\
              'Return code: %(returncode)s\n%(message)s\n'
log_dateformat = '%Y-%m-%d %H:%M:%S'

#-----presets data

presets_file_name = 'presets.xml'
presets_file = os.path.join(config_dir, presets_file_name)
presets_lookup_dirs = ["/usr/local/share/", "/usr/share/"]
presets_lookup_virtenv = 'share'
# prefix for old presets when synchronizing
presets_old = '__OLD'

#-----audiovideo data

video_codecs = [
        'copy', 'flv', 'h263', 'libvpx', 'libx264', 'libxvid', 'mpeg2video',
        'mpeg4', 'msmpeg4', 'wmv2'
        ]

audio_codecs = [
        'aac', 'ac3', 'copy', 'libfaac', 'libmp3lame', 'libvo_aacenc',
        'libvorbis', 'mp2', 'wmav2'
        ]

video_formats = [
        '3g2', '3gp', 'aac', 'ac3', 'avi', 'dv', 'flac', 'flv', 'm4a', 'm4v',
        'mka', 'mkv', 'mov', 'mp3', 'mp4', 'mpg', 'ogg', 'vob', 'wav', 'webm',
        'wma', 'wmv'
        ]

video_frequency_values = [
        '22050', '44100', '48000'
        ]

video_bitrate_values = [
        '32', '96', '112', '128', '160', '192', '256', '320'
        ]

#-----image data

image_formats = [
        'bmp', 'cgm', 'dpx', 'emf', 'eps', 'fpx', 'gif', 'jbig', 'jng', 'jpeg',
        'mrsid', 'p7', 'pdf', 'picon', 'png', 'ppm', 'psd', 'rad', 'tga',
        'tif','webp', 'xpm'
        ]

image_extra_formats = [
        'bmp2', 'bmp3', 'dib', 'epdf', 'epi', 'eps2', 'eps3', 'epsf', 'epsi',
        'icon', 'jpe', 'jpg', 'pgm', 'png24', 'png32', 'pnm', 'ps', 'ps2',
        'ps3', 'sid', 'tiff'
        ]

#-----document data

document_formats = [
        'bib', 'csv', 'dif', 'doc', 'docx', 'html', 'ltx', 'odp', 'ods', 'odt',
        'pdf', 'ppt', 'pptx', 'rtf', 'sdc', 'sdw', 'txt', 'xls', 'xlsx', 'xml'
        ]


#-----misc
translators = [
        ['[bg] Bulgarian', 'Vasil Blagoev'],
        ['[ca] Catalan', 'David Sabadell i Ximenes'
                  '\n     Toni Estévez'],
        ['[cs] Czech', 'Petr Simacek'],
        ['[de_DE] German (Germany)', 'Stefan Wilhelm'],
        ['[el] Greek', 'Ilias Stamatis'],
        ['[es] Spanish', 'Miguel Ángel Rodríguez Muíños'
                  '\n     Toni Estévez'],
        ['[fr] French', 'Rémi Mercier'
                 '\n     Lebarhon'],
        ['[gl] Galician', 'Miguel Anxo Bouzada'],
        ['[gl_ES] Galician (Spain)', 'Miguel Anxo Bouzada'],
        ['[hu] Hungarian', 'Farkas Norbert'],
        ['[it] Italian', 'Fabio Boccaletti'],
        ['[ms_MY] Malay (Malaysia)', 'abuyop'],
        ['[pl_PL] Polish (Poland)', 'Lukasz Koszy'
                             '\n     Piotr Surdacki'],
        ['[pt] Portuguese', 'Sérgio Marques'
                     '\n     Paulo Braz'
                     '\n     Nuno Duarte'],
        ['[pt_BR] Portuguese (Brasil)', 'José Humberto A Melo'],
        ['[ro_RO] Romanian (Romania)', 'Angelescu Constantin'],
        ['[ru] Russian', 'Andrew Lapshin'],
        ['[tu] Turkish', 'Tayfun Kayha'],
        ['[vi] Vietnamese', 'Anh Phan'],
        ['[zh_CN] Chinese (China)', 'Dianjin Wang'
                             '\n     Ziyun Lin'],
        ['[zh_TW] Chinese (Taiwan)', 'Taijuin Lee'
                              '\n     Jeff Huang'],
        ]
