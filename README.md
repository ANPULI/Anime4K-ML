# Anime4K-ML

This is the course project of _2019 Fall CSCI-SHU 360 Machine Learning_. This project proposes an improved Anime real-time up-scaling method using a Generative Adversarial Network for super resolution, based on [Anime4K](https://github.com/bloc97/Anime4K "Anime4K"): an open-source, high-quality real-time anime upscaling algorithm.

## TLDR

1. Open [this page](https://anpuli.github.io/Anime4K-ML/web/index-demo.html "demo") to see the live demo. Allow serveral seconds for loading the videos.
2. Jump to [this section](#vertical_traffic_light-quick-start-video-upscaling) to upscale your own videos.
3. Refer to [this section](#vertical_traffic_light-quick-start-traning-and-testing) to train your own model.

## Table of Contents

- [Anime4K-ML](#anime4k-ml)
  - [TLDR](#tldr)
  - [Table of Contents](#table-of-contents)
  - [:vertical_traffic_light: Quick Start: Traning and Testing](#vertical_traffic_light-quick-start-traning-and-testing)
    - [:nut_and_bolt: Prerequisites](#nut_and_bolt-prerequisites)
    - [:hammer_and_wrench: Installation &amp; Setup](#hammer_and_wrench-installation-amp-setup)
    - [:rocket: Use Pre-trained Model](#rocket-use-pre-trained-model)
      - [:ideograph_advantage: Sample Outputs](#ideograph_advantage-sample-outputs)
    - [:triangular_flag_on_post: Speed Benchmark](#triangular_flag_on_post-speed-benchmark)
    - [:mag: Similarity Measures](#mag-similarity-measures)
      - [:ideograph_advantage: Do it on your own?](#ideograph_advantage-do-it-on-your-own)
    - [:pick: Train Your Own Model](#pick-train-your-own-model)
      - [:wrench: Convert images to h5 file (buggy, don't use)](#wrench-convert-images-to-h5-file-buggy-dont-use)
      - [:wrench: Do upscaling on hdf5 image file](#wrench-do-upscaling-on-hdf5-image-file)
  - [:vertical_traffic_light: Quick Start: Video Upscaling](#vertical_traffic_light-quick-start-video-upscaling)
    - [:nut_and_bolt: Prerequisites](#nut_and_bolt-prerequisites-1)
    - [:hammer_and_wrench: Installation &amp; Setup](#hammer_and_wrench-installation-amp-setup-1)
      - [:warning: Change Configuration](#warning-change-configuration)
    - [:tv: Sample Video](#tv-sample-video)
    - [:rocket: Run Upscaling](#rocket-run-upscaling)
  - [:vertical_traffic_light: Quick Start: Web Demo](#vertical_traffic_light-quick-start-web-demo)
    - [:nut_and_bolt: Prerequisites](#nut_and_bolt-prerequisites-2)
    - [:hammer_and_wrench: Deployment](#hammer_and_wrench-deployment)
    - [:tv: Usage](#tv-usage)
  - [:bulb: Credits](#bulb-credits)

## :vertical_traffic_light: Quick Start: Traning and Testing

### :nut_and_bolt: Prerequisites

- **Windows System**
- **Python 3** [Download](https://www.python.org/downloads/windows/)

### :hammer_and_wrench: Installation & Setup

First, clone the ANIME4K-ML repository to your local directory.

```shell
git clone https://github.com/ANPULI/Anime4K-ML.git
cd ANIME4K-ML/SRGAN-impl
```

Then, install the python dependencies using the following command before proceding.

```shell
pip install -r requirements.txt
```

### :rocket: Use Pre-trained Model

You can spare the efforts of training by directly using one of the following pre-installed model:

- `models/generator.h5`, trained on [DIV2K](https://data.vision.ee.ethz.ch/cvl/DIV2K/) dataset.
- `models/generator_ANIME.h5`, trained on an [anime face dataset](https://github.com/Mckinsey666/Anime-Face-Dataset)

It is recommended to use the first model, though it was based on anime. The second dataset sufferes severely from the low resolution of the dataset, therefore it performs not well in terms of visual perception.

To use the DIV2K model, run the following in the terminal:

```shell
python infer_old.py --image_dir 'path/to/input/directory' --output_dir 'path/to/output/directory'
```

To use the anime model, run this:

```shell
python infer_anime.py --image_dir 'path/to/input/directory' --output_dir 'path/to/output/directory'
```

#### :ideograph_advantage: Sample Outputs

Here is the performance with contrast on other methods, all using 240p → 960p (4x) upscaling:

![sample outputs](https://user-images.githubusercontent.com/26131764/70522470-23476e80-1b7c-11ea-8c11-35ca91246d8d.png)

### :triangular_flag_on_post: Speed Benchmark

The trained model is applied on two datasets, one is from DIV2K (800 images) and the other is from a 19 second anime clip (426 images) used in the demo. The average rendering speed result is shown below table, using the GPU provided in [Google Colab](https://colab.research.google.com/):

| Input Image Size | Output Image Size | Time (s) | FPS |
|:----------------:|:-----------------:|:--------:|:---:|
|      128×128     |      512×512      |   0.022  |  46 |
|      256×256     |     1024×1024     |   0.045  |  22 |
|      384×384     |     1536×1536     |   0.083  |  12 |

The problem this project aims to resolve is to upscale low resolution anime videos to high resolution ones (240p → 1080p). The typical FPS of anime videos is 24. Since the program is run on Google Colab, where the GPU is not dedicated to one user and the ﬁle system works extremely bad in terms of read/write speed. In a local system, the running speed will be much higher and satisfy the requirements.

### :mag: Similarity Measures

All experiments are performed with a scale factor of 4× between the low and high resolution images, corresponding to a 16× reduction in image pixels. The images Set5 and Set14 and the corresponding result metrics are attributed to the supplementary materials of [Huang et al](https://github.com/jbhuang0604/SelfExSR) and [Twitter's work on SRGAN](https://arxiv.org/abs/1609.04802). The highest results, except for ground truth, are formatted bold. It is apparent that SR-GAN is the best among the proposed methods. The comparison with other deep learning methods is not included because they are not at the same level of computing time - SRGAN works substantially faster. The result metric is shown below. The index MOS is given in SRGAN's paper that quantifies visual perception.

| Set5&14 | nearest | bicubic |    SRGAN   |  Original  |
|:-------:|:-------:|:-------:|:----------:|:----------:|
|   PSNR  |  26.26  |  28.43  |  **29.40** |      ∞     |
|   SSIM  |  0.7552 |  0.8211 | **0.8472** |      1     |
|   MOS   |   1.28  |   1.97  |  **3.58**  |    4.32    |

Testing is also done on some anime images. The result goes as follows:

|      | nearest | bicubic |    SRGAN   |  Original  |
|:----:|:-------:|:-------:|:----------:|:----------:|
| PSNR |  29.79  |  31.67  |  **32.88** |      ∞     |
| SSIM |  0.9479 |  0.9585 | **0.9593** |      1     |

#### :ideograph_advantage: Do it on your own?

If you would like to test the similarity measures by yourself, there is an esay program [sewar](https://github.com/andrewekhalel/sewar) that provides the function. To get upscaled images using bicubic and nearest neighbors algorithms, you can use these the two python files:

- `SRGAN-impl/image_resize_bicubic.py`
- `SRGAN-impl/image_resize_nn.py`

The usage of it is 

```shell
mkdir 'path/to/output/image'
python image_resize_nn.py --res 'resolution' --input_dir 'path/to/input/image' --output_dir 'path/to/output/image'
```

### :pick: Train Your Own Model

To train the model, you need to have a local image dataset. However, you do not need to manually split the dataset into high-/low-resolution parts, the program will automatically do it for you. Then, simply execute the following command to start training:

```shell
python main.py --image_dir 'path/to/image/directory' --hr_size 384 --lr 1e-4 --save_iter 200 --epochs 10 --batch_size 14
```

The training status will get updated every 200 iteration. To monitor the training process, you can open [tensorboard](https://www.tensorflow.org/tensorboard) and point it to the `log` directory that will be created upon training.

#### :wrench: Convert images to h5 file (buggy, don't use)

If you are also using Google Colab as your training tool, and using Google Drive as the file system, you may have already spotted the following problems:

- It takes a considerable time to read/write.
- Some small files seem to exist when you visit them, but create `file_not_exist error` when accessed from programs.

If yes, you may want to convert the images to a single file to boost the read/write speed and preserve file completeness.

The `SRGAN-impl/image2h5.py` provides a solution by compressing multiple images into a [HDF5](https://support.hdfgroup.org/HDF5/whatishdf5.html) file. To use the file, first install the [h5py](https://pypi.org/project/h5py/) dependencies by executing the following command:

```shell
pip install h5py
```

Then, make sure your files are in the sub-directory `SRGAN-impl/image_input/` and of `PNG` formart, and run the following command:

```shell
python image2h5.py
```

Otherwise, you can also specifies the parameter by using:

```shell
python image2h5.py --image_dir 'path/to/your/image/input' --image_format 'your_image_format'
```

This will produce a hdf5 file called `images.hdf5` that stores the information of all your images.

#### :wrench: Do upscaling on hdf5 image file

After you have your hdf5 file, you can train the model based on it by runing:

```shell
python infer_h5.py --output_dir 'path/to/output/image'
```

This will generate upscaled images in your desired output directory.

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

Enlarge the video to 960p (4x) using the CPU.

```shell
python main.py -i sample_input.mp4 -o sample_input_upscaled.mp4 -m cpu -r 4
```

## :vertical_traffic_light: Quick Start: Web Demo

The demo is available [here](https://anpuli.github.io/Anime4K-ML/web/index-demo.html "demo"). Please allow serveral seconds for the videos to be loaded if you open the website for the first time. If it doesn't play automatically, just simply click the `Pause/Play video` button to start playing the video because [Google disabled autoplay with sound](https://developers.google.com/web/updates/2017/09/autoplay-policy-changes). You can spare the effort of deploying it locally, but feel free to preceed if you would like to make some own changes.

This is a screenshot of the demo page. The upper is the upscaled video and the lower one is the original video. You can clearly notice that the upscaled video has smoother lines across the face and hair.

![demo](https://user-images.githubusercontent.com/26131764/70494161-30953680-1b45-11ea-9625-2d83755874b3.png)

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

For usage on other videos/images, you may deploy `index.html` and click `choose file`. You can play with the Scale, Bold, and Blur to see altered results.

## :bulb: Credits

The implementation of this project cannot be done without the insights derived from [Fast-SRGAN](https://github.com/HasnainRaz/Fast-SRGAN "Fast-SRGAN") and [Video2X](https://github.com/k4yt3x/video2x "Video2X"). This project also relies on [FFmpeg](https://ffmpeg.org/) and [Anime4K](https://github.com/bloc97/Anime4K).