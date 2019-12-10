# local imports
from exceptions import *
from upscaler import AVAILABLE_DRIVERS
from upscaler import Upscaler

# built-in imports
import argparse
import contextlib
import json
import pathlib
import re
import shutil
import sys
import tempfile
import time
import traceback

# third-party imports
from avalon_framework import Avalon
import GPUtil
import psutil

def process_arguments():
    """Processes CLI arguments

    This function parses all arguments
    This allows users to customize options
    for the output video.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # video options
    file_options = parser.add_argument_group('File Options')
    file_options.add_argument('-i', '--input', type=pathlib.Path, help='source video file/directory', action='store')
    file_options.add_argument('-o', '--output', type=pathlib.Path, help='output video file/directory', action='store')

    # upscaler options
    upscaler_options = parser.add_argument_group('Upscaler Options')
    upscaler_options.add_argument('-m', '--method', help='upscaling method', action='store', default='gpu', choices=['cpu', 'gpu', 'cudnn'])
    upscaler_options.add_argument('-d', '--driver', help='upscaling driver', action='store', default='waifu2x_caffe', choices=AVAILABLE_DRIVERS)
    upscaler_options.add_argument('-y', '--model_dir', type=pathlib.Path, help='directory containing model JSON files', action='store')
    upscaler_options.add_argument('-t', '--threads', help='number of threads to use for upscaling', action='store', type=int, default=1)
    upscaler_options.add_argument('-c', '--config', type=pathlib.Path, help='video2x config file location', action='store', default=pathlib.Path(sys.argv[0]).parent.absolute() / 'video2x.json')
    upscaler_options.add_argument('-b', '--batch', help='enable batch mode (select all default values to questions)', action='store_true')

    # scaling options
    scaling_options = parser.add_argument_group('Scaling Options')
    scaling_options.add_argument('--width', help='output video width', action='store', type=int)
    scaling_options.add_argument('--height', help='output video height', action='store', type=int)
    scaling_options.add_argument('-r', '--ratio', help='scaling ratio', action='store', type=float)

    # extra options
    extra_options = parser.add_argument_group('Extra Options')
    extra_options.add_argument('-v', '--version', help='display version, lawful information and exit', action='store_true')

    # parse arguments
    return parser.parse_args()

def read_config(config_file):
    """ Reads configuration file

    Returns a dictionary read by JSON.
    """
    with open(config_file, 'r') as raw_config:
        config = json.load(raw_config)
        return config


def absolutify_paths(config):
    """ Check to see if paths to binaries are absolute

    This function checks if paths to binary files are absolute.
    If not, then absolutify the path.

    Arguments:
        config {dict} -- configuration file dictionary

    Returns:
        dict -- configuration file dictionary
    """
    current_directory = pathlib.Path(sys.argv[0]).parent.absolute()

    # check ffmpeg path
    if not re.match('^[a-z]:', config['ffmpeg']['ffmpeg_path'], re.IGNORECASE):
        config['ffmpeg']['ffmpeg_path'] = current_directory / config['ffmpeg']['ffmpeg_path']

    # check video2x cache path
    if config['video2x']['video2x_cache_directory']:
        if not re.match('^[a-z]:', config['video2x']['video2x_cache_directory'], re.IGNORECASE):
            config['video2x']['video2x_cache_directory'] = current_directory / config['video2x']['video2x_cache_directory']

    return config

# /////////////////// Execution /////////////////// #

# this is not a library
if __name__ != '__main__':
    Avalon.error('This file cannot be imported')
    raise ImportError(f'{__file__} cannot be imported')

# process CLI arguments
args = process_arguments()

# arguments sanity check
if not args.input:
    Avalon.error('You must specify input video file/directory path')
    raise ArgumentError('input video path not specified')
if not args.output:
    Avalon.error('You must specify output video file/directory path')
    raise ArgumentError('output video path not specified')
if (args.driver in ['waifu2x_converter', 'waifu2x_ncnn_vulkan', 'anime4k']) and args.width and args.height:
    Avalon.error('Selected driver accepts only scaling ratio')
    raise ArgumentError('selected driver supports only scaling ratio')
if args.driver == 'waifu2x_ncnn_vulkan' and (args.ratio > 2 or not args.ratio.is_integer()):
    Avalon.error('Scaling ratio must be 1 or 2 for waifu2x_ncnn_vulkan')
    raise ArgumentError('scaling ratio must be 1 or 2 for waifu2x_ncnn_vulkan')
if (args.width or args.height) and args.ratio:
    Avalon.error('You can only specify either scaling ratio or output width and height')
    raise ArgumentError('both scaling ration and width/height specified')
if (args.width and not args.height) or (not args.width and args.height):
    Avalon.error('You must specify both width and height')
    raise ArgumentError('only one of width or height is specified')

# read configurations from JSON
config = read_config(args.config)
config = absolutify_paths(config)
waifu2x_settings = config['anime4k']
if not pathlib.Path(waifu2x_settings['anime4k_path']).is_file():
    Avalon.error('Specified anime4k directory doesn\'t exist')
    Avalon.error('Please check the configuration file settings')
    raise FileNotFoundError(waifu2x_settings['anime4k_path'])
# read FFmpeg configuration
ffmpeg_settings = config['ffmpeg']

# load video2x settings
image_format = config['video2x']['image_format'].lower()
preserve_frames = config['video2x']['preserve_frames']

# load cache directory
if isinstance(config['video2x']['video2x_cache_directory'], str):
    video2x_cache_directory = pathlib.Path(config['video2x']['video2x_cache_directory'])
else:
    video2x_cache_directory = pathlib.Path.cwd() / 'temp'
    # video2x_cache_directory = pathlib.Path(tempfile.gettempdir()) / 'video2x'

if video2x_cache_directory.exists() and not video2x_cache_directory.is_dir():
    Avalon.error('Specified cache directory is a file/link')
    raise FileExistsError('Specified cache directory is a file/link')

elif not video2x_cache_directory.exists():
    # if destination file is a file or a symbolic link
    Avalon.warning(f'Specified cache directory {video2x_cache_directory} does not exist')

    # try creating the cache directory
    if Avalon.ask('Create directory?', default=True, batch=args.batch):
        try:
            video2x_cache_directory.mkdir(parents=True, exist_ok=True)
            Avalon.info(f'{video2x_cache_directory} created')

        # there can be a number of exceptions here
        # PermissionError, FileExistsError, etc.
        # therefore, we put a catch-them-all here
        except Exception as e:
            Avalon.error(f'Unable to create {video2x_cache_directory}')
            Avalon.error('Aborting...')
            raise e
    else:
        raise FileNotFoundError('Could not create cache directory')


# start execution
try:
    # start timer
    begin_time = time.time()

    # if input specified is a single file
    if args.input.is_file():

        # upscale single video file
        Avalon.info(f'Upscaling single video file: {args.input}')

        # check for input output format mismatch
        if args.output.is_dir():
            Avalon.error('Input and output path type mismatch')
            Avalon.error('Input is single file but output is directory')
            raise Exception('input output path type mismatch')
        if not re.search(r'.*\..*$', str(args.output)):
            Avalon.error('No suffix found in output file path')
            Avalon.error('Suffix must be specified for FFmpeg')
            raise Exception('No suffix specified')

        upscaler = Upscaler(input_video=args.input, output_video=args.output, method=args.method, waifu2x_settings=waifu2x_settings, ffmpeg_settings=ffmpeg_settings)

        # set optional options
        upscaler.waifu2x_driver = args.driver
        upscaler.scale_width = args.width
        upscaler.scale_height = args.height
        upscaler.scale_ratio = args.ratio
        upscaler.model_dir = args.model_dir
        upscaler.threads = args.threads
        upscaler.video2x_cache_directory = video2x_cache_directory
        upscaler.image_format = image_format
        upscaler.preserve_frames = preserve_frames

        # run upscaler
        upscaler.create_temp_directories()
        upscaler.run()
        upscaler.cleanup_temp_directories()

    # if input specified is a directory
    elif args.input.is_dir():
        # upscale videos in a directory
        Avalon.info(f'Upscaling videos in directory: {args.input}')

        # make output directory if it doesn't exist
        args.output.mkdir(parents=True, exist_ok=True)

        for input_video in [f for f in args.input.iterdir() if f.is_file()]:
            output_video = args.output / input_video.name
            upscaler = Upscaler(input_video=input_video, output_video=output_video, method=args.method, waifu2x_settings=waifu2x_settings, ffmpeg_settings=ffmpeg_settings)

            # set optional options
            upscaler.waifu2x_driver = args.driver
            upscaler.scale_width = args.width
            upscaler.scale_height = args.height
            upscaler.scale_ratio = args.ratio
            upscaler.model_dir = args.model_dir
            upscaler.threads = args.threads
            upscaler.video2x_cache_directory = video2x_cache_directory
            upscaler.image_format = image_format
            upscaler.preserve_frames = preserve_frames

            # run upscaler
            upscaler.create_temp_directories()
            upscaler.run()
            upscaler.cleanup_temp_directories()
    else:
        Avalon.error('Input path is neither a file nor a directory')
        raise FileNotFoundError(f'{args.input} is neither file nor directory')

    Avalon.info(f'Program completed, taking {round((time.time() - begin_time), 5)} seconds')
except Exception:
    Avalon.error('An exception has occurred')
    traceback.print_exc()
finally:
    # remove Video2X cache directory
    with contextlib.suppress(FileNotFoundError):
        if not preserve_frames:
            shutil.rmtree(video2x_cache_directory)
