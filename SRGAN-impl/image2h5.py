from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--image_dir', type=str, default='./image_input/', help='Directory where images are kept.')
parser.add_argument('--image_format', type=str, default='png', help='Directory where to output high res images.')
args = parser.parse_args()

print("first part")
########################## first part: prepare data ###########################
import glob

hdf5_path = './images.hdf5'  # file path for the created .hdf5 file

# images_path = './images_input/*.png' # the original data path
images_path = args.image_dir + '*.' + args.image_format

# get all the image paths 
addrs = glob.glob(images_path)

                               
# Divide the data into 80% for train and 20% for test
train_addrs = addrs[:]
print(len(train_addrs))

print("second part")
##################### second part: create the h5py object #####################
import numpy as np
import h5py

train_shape = (len(train_addrs), 426, 240, 3)

# open a hdf5 file and create earrays 
f = h5py.File(hdf5_path, mode='w')

# PIL.Image: the pixels range is 0-255,dtype is uint.
# matplotlib: the pixels range is 0-1,dtype is float.
f.create_dataset("train_img", train_shape, np.uint8)


print("third part")
######################## third part: write the images #########################
import cv2

# loop over train paths
for i in range(len(train_addrs)):
  
    if i % 10 == 0 and i > 1:
        print ('Train data: {}/{}'.format(i, len(train_addrs)) )

    addr = train_addrs[i]
    img = cv2.imread(addr)
    img = cv2.resize(img, (240, 426), interpolation=cv2.INTER_CUBIC)# resize to (128,128)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    f["train_img"][i, ...] = img[None] 


f.close()