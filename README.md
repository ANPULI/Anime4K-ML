# Anime4K-ML

This is the course project of _2019 Fall CSCI-SHU 360 Machine Learning_. This project proposes an improved Anime real-time up-scaling method using a Generative Adversarial Network for super resolution, based on [Anime4K](https://github.com/bloc97/Anime4K "Anime4K"): an open-source, high-quality real-time anime upscaling algorithm.

- [Anime4K-ML](#anime4k-ml)
  - [:vertical_traffic_light: Quick Start: Traning and Testing](#verticaltrafficlight-quick-start-traning-and-testing)
  - [:vertical_traffic_light: Quick Start: Video Upscaling](#verticaltrafficlight-quick-start-video-upscaling)
    - [:nut_and_bolt: Prerequisites](#nutandbolt-prerequisites)
    - [:hammer_and_wrench: Installation &amp; Setup](#hammerandwrench-installation-amp-setup)
      - [:warning: Change Configuration](#warning-change-configuration)
    - [:tv: Sample Video](#tv-sample-video)
    - [:rocket: Run Upscaling](#rocket-run-upscaling)
  - [:vertical_traffic_light: Quick Start: Web Demo](#verticaltrafficlight-quick-start-web-demo)
    - [:nut_and_bolt: Prerequisites](#nutandbolt-prerequisites-1)
    - [:hammer_and_wrench: Deployment](#hammerandwrench-deployment)
    - [:tv: Usage](#tv-usage)
  - [:bulb: Credits](#bulb-credits)

## :vertical_traffic_light: Quick Start: Traning and Testing



## :vertical_traffic_light: Quick Start: Video Upscaling

### :nut_and_bolt: Prerequisites

- **Windows System**
- **Python 3** [Download](https://www.python.org/downloads/windows/)
- **FFmpeg Windows Build** [Download](https://ffmpeg.org/download.html)

### :hammer_and_wrench: Installation & Setup

First, clone the ANIME4K-ML repository to your local directory.

```shell
git clone https://github.com/ANPULI/Anime4K-ML.git
cd ANIME4K-ML/SRGAN-video
```

Then, install the python dependencies using the following command before proceding.

```shell
pip install -r requirements.txt
```

#### :warning: Change Configuration

After installing FFmpeg, please change the `ffmpeg_path` in `video2x.json` to the absolution path of your local installation.

### :tv: Sample Video

If you do not have a video to start with, you can use the sample video provided in the sub-directory.

![sample_contrast](https://user-images.githubusercontent.com/26131764/70491203-9aa8de00-1b3b-11ea-8f18-4975a04b6258.png)

- [Sample Video Original (240p)](SRGAN-video/sample_input.mp4)
- [Sample Video Upscaled (960p)](SRGAN-video/sample_output.mp4)

Clip is from anime "さくら荘のペットな彼女". Copyright belongs to "株式会社アニプレックス (Aniplex Inc.)". Will delete immediately if use of clip is in violation of copyright.

### :rocket: Run Upscaling

Enlarge the video to 960p ($4\times$) using the CPU.

```shell
python main.py -i sample_input.mp4 -o sample_input_upscaled.mp4 -m cpu -r 4
```


## :vertical_traffic_light: Quick Start: Web Demo

### :nut_and_bolt: Prerequisites

None. This project uses [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer), an extension on [VS Code](https://code.visualstudio.com/) to simply build a local server, but there is no specified requirements. In the following sections, all commands will be based on this setting.

### :hammer_and_wrench: Deployment

First, clone the ANIME4K-ML repository to your local directory.

```shell
git clone https://github.com/ANPULI/Anime4K-ML.git
code web
```

Open `index-demo.html`. Press `Ctrl+Shift+P` and then select `Live Server: Open with Live Server`. Or simply use the shortcut `Alt+L Alt+O` to deploy the website.

### :tv: Usage

The path is already set. Simple click `load with URI`, and you can take a look at the difference between the original video and upscaled one.

This is a screenshot of the demo page. The upper is the upscaled video and the lower one is the original video. You can clearly notice that the upscaled video has smoother lines across the face and hair.

![demo](https://user-images.githubusercontent.com/26131764/70494161-30953680-1b45-11ea-9625-2d83755874b3.png)


For usage on other videos/images, you may deploy `index.html` and click `choose file`. You can play with the Scale, Bold, and Blur to see tilt the result.

## :bulb: Credits

The implementation of this project cannot be done without the insights derived from [Fast-SRGAN](https://github.com/HasnainRaz/Fast-SRGAN "Fast-SRGAN") and [Video2X](https://github.com/k4yt3x/video2x "Video2X"). This project also relies on [FFmpeg](https://ffmpeg.org/) and [Anime4K](https://github.com/bloc97/Anime4K).