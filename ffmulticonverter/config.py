import os
import sys
import logging

home = os.getenv("HOME")
config_dir = os.path.join(home, '.config/ffmulticonverter/')

log_dir = os.path.join(config_dir, 'logs/')
log_file = os.path.join(log_dir, 'history.log')

presets_file_name = 'presets.xml'
presets_file = os.path.join(config_dir, presets_file_name)
# prefix for old presets when synchronizing
presets_old = '__OLD'

default_ffmpeg_cmd = '-ab 320k -ar 48000 -ac 2'


def logging_config(log_file):
    logging.basicConfig(
            filename = log_file,
            level=logging.DEBUG,
            format='%(asctime)s : %(levelname)s - %(type)s\n'
                   'Command: %(command)s\n'
                   'Return code: %(returncode)s\n%(message)s\n',
            datefmt='%Y-%m-%d %H:%M:%S'
    )

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
