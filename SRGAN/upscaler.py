#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: Video2X Upscaler
Author: K4YT3X
Date Created: December 10, 2018
Last Modified: August 21, 2019

Dev: SAT3LL

Licensed under the GNU General Public License Version 3 (GNU GPL v3),
    available at: https://www.gnu.org/licenses/gpl-3.0.txt

(C) 2018-2019 K4YT3X
"""

# local imports
# from anime4k import Anime4k
from exceptions import *
from ffmpeg import Ffmpeg
from image_cleaner import ImageCleaner
from srgan import SRGAN

# built-in imports
from fractions import Fraction
import contextlib
import copy
import pathlib
import re
import shutil
import tempfile
import threading
import time
import traceback

# third-party imports
from avalon_framework import Avalon
from tqdm import tqdm

AVAILABLE_DRIVERS = ['waifu2x_caffe', 'waifu2x_converter', 'waifu2x_ncnn_vulkan', 'anime4k']


class Upscaler:
    """ An instance of this class is a upscaler that will
    upscale all images in the given directory.

    Raises:
        Exception -- all exceptions
        ArgumentError -- if argument is not valid
    """

    def __init__(self, input_video, output_video, method, waifu2x_settings, ffmpeg_settings):
        # mandatory arguments
        self.input_video = input_video
        self.output_video = output_video
        self.method = method
        self.waifu2x_settings = waifu2x_settings
        self.ffmpeg_settings = ffmpeg_settings

        # optional arguments
        self.waifu2x_driver = 'waifu2x_caffe'
        self.scale_width = None
        self.scale_height = None
        self.scale_ratio = None
        self.model_dir = None
        self.threads = 5
        self.video2x_cache_directory = pathlib.Path(tempfile.gettempdir()) / 'video2x'
        self.image_format = 'png'
        self.preserve_frames = True

    def create_temp_directories(self):
        """create temporary directory
        """
        self.extracted_frames = pathlib.Path(tempfile.mkdtemp(dir=self.video2x_cache_directory))
        Avalon.debug_info(f'Extracted frames are being saved to: {self.extracted_frames}')
        self.upscaled_frames = pathlib.Path(tempfile.mkdtemp(dir=self.video2x_cache_directory))
        Avalon.debug_info(f'Upscaled frames are being saved to: {self.upscaled_frames}')

    # def cleanup_temp_directories(self):
    #     """delete temp directories when done
    #     """
    #     if not self.preserve_frames:
    #         for directory in [self.extracted_frames, self.upscaled_frames]:
    #             try:
    #                 # avalon framework cannot be used if python is shutting down
    #                 # therefore, plain print is used
    #                 print(f'Cleaning up cache directory: {directory}')
    #                 shutil.rmtree(directory)
    #             except (OSError, FileNotFoundError):
    #                 print(f'Unable to delete: {directory}')
    #                 traceback.print_exc()

    def _check_arguments(self):
        # check if arguments are valid / all necessary argument
        # values are specified
        if not self.input_video:
            raise ArgumentError('You need to specify the video to process')
        elif (not self.scale_width or not self.scale_height) and not self.scale_ratio:
            raise ArgumentError('You must specify output video width and height or upscale factor')
        elif not self.output_video:
            raise ArgumentError('You need to specify the output video name')
        elif not self.method:
            raise ArgumentError('You need to specify the enlarging processing unit')

    def _progress_bar(self, extracted_frames_directories):
        """ This method prints a progress bar

        This method prints a progress bar by keeping track
        of the amount of frames in the input directory
        and the output directory. This is originally
        suggested by @ArmandBernard.
        """

        # get number of extracted frames
        self.total_frames = 0
        for directory in extracted_frames_directories:
            self.total_frames += len([f for f in directory.iterdir() if str(f)[-4:] == f'.{self.image_format}'])

        with tqdm(total=self.total_frames, ascii=True, desc='Upscaling Progress') as progress_bar:

            # tqdm update method adds the value to the progress
            # bar instead of setting the value. Therefore, a delta
            # needs to be calculated.
            previous_cycle_frames = 0
            while not self.progress_bar_exit_signal:

                with contextlib.suppress(FileNotFoundError):
                    self.total_frames_upscaled = len([f for f in self.upscaled_frames.iterdir() if str(f)[-4:] == f'.{self.image_format}'])
                    delta = self.total_frames_upscaled - previous_cycle_frames
                    previous_cycle_frames = self.total_frames_upscaled

                    # if upscaling is finished
                    if self.total_frames_upscaled >= self.total_frames:
                        return

                    # adds the delta into the progress bar
                    progress_bar.update(delta)

                time.sleep(1)

    def run(self):
        """Main controller for Video2X

        This function controls the flow of video conversion
        and handles all necessary functions.
        """

        # parse arguments for waifu2x
        # check argument sanity
        self._check_arguments()

        # convert paths to absolute paths
        self.input_video = self.input_video.absolute()
        self.output_video = self.output_video.absolute()

        # initialize objects for ffmpeg and waifu2x-caffe
        fm = Ffmpeg(self.ffmpeg_settings, self.image_format)

        # extract frames from video
        fm.extract_frames(self.input_video, self.extracted_frames)

        Avalon.info('Reading video information')
        video_info = fm.get_video_info(self.input_video)
        # analyze original video with ffprobe and retrieve framerate
        # width, height = info['streams'][0]['width'], info['streams'][0]['height']

        # find index of video stream
        video_stream_index = None
        for stream in video_info['streams']:
            if stream['codec_type'] == 'video':
                video_stream_index = stream['index']
                break

        # exit if no video stream found
        if video_stream_index is None:
            Avalon.error('Aborting: No video stream found')
            raise StreamNotFoundError('no video stream found')

        # get average frame rate of video stream
        framerate = float(Fraction(video_info['streams'][video_stream_index]['avg_frame_rate']))
        fm.pixel_format = video_info['streams'][video_stream_index]['pix_fmt']

        # get a dict of all pixel formats and corresponding bit depth
        pixel_formats = fm.get_pixel_formats()

        try:
            self.bit_depth = pixel_formats[fm.pixel_format]
        except KeyError:
            Avalon.error(f'Unsupported pixel format: {fm.pixel_format}')
            raise UnsupportedPixelError(f'unsupported pixel format {fm.pixel_format}')

        Avalon.info(f'Framerate: {framerate}')

        # width/height will be coded width/height x upscale factor
        if self.scale_ratio:
            original_width = video_info['streams'][video_stream_index]['width']
            original_height = video_info['streams'][video_stream_index]['height']
            self.scale_width = int(self.scale_ratio * original_width)
            self.scale_height = int(self.scale_ratio * original_height)


        # upscale images one by one using waifu2x
        Avalon.info('Starting to upscale extracted images')
        # self._upscale_frames()
        sr = SRGAN()
        sr.upscale(self.extracted_frames, self.upscaled_frames)
        Avalon.info('Upscaling completed')

        # frames to Video
        Avalon.info('Converting extracted frames into video')

        # use user defined output size
        fm.convert_video(framerate, f'{self.scale_width}x{self.scale_height}', self.upscaled_frames)
        Avalon.info('Conversion completed')

        # migrate audio tracks and subtitles
        Avalon.info('Migrating audio tracks and subtitles to upscaled video')
        fm.migrate_audio_tracks_subtitles(self.input_video, self.output_video, self.upscaled_frames)

def main():
    upscaler = Upscaler(input_video=args.input, output_video=args.output, method=args.method, waifu2x_settings=waifu2x_settings, ffmpeg_settings=ffmpeg_settings)