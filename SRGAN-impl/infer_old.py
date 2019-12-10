from argparse import ArgumentParser
from tensorflow import keras
import numpy as np
import cv2
import os
import time

parser = ArgumentParser()
parser.add_argument('--image_dir', type=str, help='Directory where images are kept.')
parser.add_argument('--output_dir', type=str, help='Directory where to output high res images.')


def main():
    args = parser.parse_args()

    # Get all image paths
    image_paths = [os.path.join(args.image_dir, x) for x in os.listdir(args.image_dir)]

    # Change model input shape to accept all size inputs
    model = keras.models.load_model('models/generator.h5')
    inputs = keras.Input((None, None, 3))
    output = model(inputs)
    model = keras.models.Model(inputs, output)

    i = 0
    start_time = []
    start_time.append(time.time())
    print(start_time[0])

    # Loop over all images
    for image_path in image_paths:
        
        if (i % 100 == 0):
            print("{}\t".format(i) )

        # Read image
        low_res = cv2.imread(image_path, 1)

        # if low_res.empty():
        #     break
        i += 1


        # Convert to RGB (opencv uses BGR as default)
        low_res = cv2.cvtColor(low_res, cv2.COLOR_BGR2RGB)

        # Rescale to 0-1.
        low_res = low_res / 255.0

        # Get super resolution image
        sr = model.predict(np.expand_dims(low_res, axis=0))[0]

        # Uncomment to save results
        # Rescale values in range 0-255
        sr = ((sr + 1) / 2.) * 255

        # Convert back to BGR for opencv
        sr = cv2.cvtColor(sr, cv2.COLOR_RGB2BGR)

        # Save the results:
        cv2.imwrite(os.path.join(args.output_dir, os.path.basename(image_path)), sr)

        start_time.append(time.time())

    time_used = time.time() - start_time[1]
    print()
    print("Time used: \t", time_used)
    print("#images: \t", i)
    print("FPS: \t\t", i/time_used)

    # for i in range(10):
    #     print(start_time[i], sep="\t")

if __name__ == '__main__':
    main()
