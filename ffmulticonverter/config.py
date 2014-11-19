import os
import sys
import logging


#-----general data

home = os.getenv("HOME")
config_dir = os.path.join(home, '.config/ffmulticonverter/')

default_ffmpeg_cmd = '-ab 320k -ar 48000 -ac 2'

#-----log data

log_dir = os.path.join(config_dir, 'logs/')
log_file = os.path.join(log_dir, 'history.log')

def logging_config(log_file):
    logging.basicConfig(
            filename = log_file,
            level=logging.DEBUG,
            format='%(asctime)s : %(levelname)s - %(type)s\n'
                   'Command: %(command)s\n'
                   'Return code: %(returncode)s\n%(message)s\n',
            datefmt='%Y-%m-%d %H:%M:%S'
    )

#-----presets data

presets_file_name = 'presets.xml'
presets_file = os.path.join(config_dir, presets_file_name)
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

video_rotation_options = [
        'None',
        '90 clockwise',
        '90 clockwise + vertical flip',
        '90 counter clockwise',
        '90 counter clockwise + vertical flip',
        '180',
        'horizontal flip',
        'vertical flip'
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

document_formats = {
        'doc' : ['odt', 'pdf'],
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


#-----misc
translators = [
        ['[bg] Bulgarian', 'Vasil Blagoev'],
        ['[cs] Czech', 'Petr Simacek'],
        ['[de_DE] German (Germany)', 'Stefan Wilhelm'],
        ['[el] Greek', 'Ilias Stamatis'],
        ['[es] Spanish', 'Miguel Ángel Rodríguez Muíños'],
        ['[fr] French', 'Rémi Mercier'
                 '\n     Lebarhon'],
        ['[gl] Galician', 'Miguel Anxo Bouzada'],
        ['[gl_ES] Galician (Spain)', 'Miguel Anxo Bouzada'],
        ['[hu] Hungarian', 'Farkas Norbert'],
        ['[it] Italian', 'Fabio Boccaletti'],
        ['[ms_MY] Malay (Malaysia)', 'abuyop'],
        ['[pl_PL] Polish (Poland)', 'Lukasz Koszy'
                             '\n     Piotr Surdacki'],
        ['[pt] Portuguese', 'Sérgio Marques'],
        ['[pt_BR] Portuguese (Brasil)', 'José Humberto A Melo'],
        ['[ro_RO] Romanian (Romania)', 'Angelescu Constantin'],
        ['[ru] Russian', 'Andrew Lapshin'],
        ['[tu] Turkish', 'Tayfun Kayha'],
        ['[vi] Vietnamese', 'Anh Phan'],
        ['[zh_CN] Chinese (China)', 'Dianjin Wang'],
        ['[zh_TW] Chinese (Taiwan)', 'Taijuin Lee']
        ]

def find_presets_file(name):
    """
    The default presets.xml could be stored in different locations during
    the installation depending on different Linux distributions.
    Search for this file on each possible directory to which user
    specific data files could be stored.

    Return the path of the file if found, else an empty string.
    """
    possible_dirs = os.environ.get(
            "XDG_DATA_DIRS", "/usr/local/share/:/usr/share/"
            ).split(":")
    # for virtualenv installations
    posdir = os.path.realpath(
            os.path.join(os.path.dirname(sys.argv[0]), '..', 'share'))
    if not posdir in possible_dirs:
        possible_dirs.append(posdir)

    for _dir in possible_dirs:
        _file = os.path.join(_dir, 'ffmulticonverter/' + name)
        if os.path.exists(_file):
            return _file
    return ''
