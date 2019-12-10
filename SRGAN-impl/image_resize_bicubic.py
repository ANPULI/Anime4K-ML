#!/usr/bin/python
from PIL import Image
import os, sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--res', type=str, help='resized res')
parser.add_argument('--input_dir', type=str, help='Directory where to input low res images.')
parser.add_argument('--output_dir', type=str, help='Directory where to output high res images.')

# path = "./images/2019"
# output_path = "./images/2019_resized"
args = parser.parse_args()
path = args.input_dir
output_path = args.output_dir
res = int(args.res)

print("res: \t", res)
print("input path: \t", path)
print("output path: \t", output_path)

dirs = os.listdir( path )
print(dirs)

def resize():
    i = 0
    for item in dirs:
        if (i%100 == 0):
            print(i)
        i+=1
        if os.path.isfile(path+item):
            im = Image.open(path+item)
            f, e = os.path.splitext(path+item)
            orig_width, orig_height = im.size
            im_height = res
            im_width = int(orig_width * res / orig_height)
            if (im_height < orig_height):
                imResize = im.resize((im_width,im_height), Image.ANTIALIAS)
            else:
                imResize = im.resize((im_width,im_height), Image.BICUBIC)
            # print(output_path + item + ' resized.png')
            # break
            print(output_path + item.split('.')[0] + '_bicubic_resized_' + str(res) + '.png')
            imResize.save(output_path + item.split('.')[0] + '_bicubic_resized_' + str(res) + '.png', 'png', quality=90)

resize()