# Anime4K-ML

This is the course project of _2019 Fall CSCI-SHU 360 Machine Learning_. This project proposes an improved Anime real-time up-scaling method using a Generative Adversarial Network for super resolution, based on [Anime4K](https://github.com/bloc97/Anime4K "Anime4K"): an open-source, high-quality real-time anime upscaling algorithm. The implementation of this project cannot be done without the insights derived from [Fast-SRGAN](https://github.com/HasnainRaz/Fast-SRGAN "Fast-SRGAN") and [Video2X](https://github.com/k4yt3x/video2x "Video2X").

## Quick Start

### Prerequisites

- **Windows System**
- **Python 3** [Download](https://www.python.org/downloads/windows/)
- **FFmpeg Windows Build** [Download](https://ffmpeg.org/download.html)

### Install Dependencies

First, clone the ANIME4K-ML repository to your local directory.

```
https://github.com/ANPULI/Anime4K-ML.git
cd ANIME4K-ML/SRGAN-video
```

Then, install the python dependencies using the following command before proceding.

```
pip install -r requirements.txt
```

### Sample Video

If you do not have a video to start with, you can use the sample video provided in the sub-directory.

![sample_contrast](https://user-images.githubusercontent.com/26131764/70491203-9aa8de00-1b3b-11ea-8f18-4975a04b6258.png)

- [Sample Video Original (240p)](SRGAN-video/sample_input.mp4)
- [Sample Video Upscaled (960p)](SRGAN-video/sample_output.mp4)

Clip is from anime "さくら荘のペットな彼女". Copyright belongs to "株式会社アニプレックス (Aniplex Inc.)". Will delete immediately if use of clip is in violation of copyright.