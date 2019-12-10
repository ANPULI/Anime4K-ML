from tensorflow import keras
import numpy as np
import cv2
import os

class SRGAN:
    def __init__(self):
        self.settings = 0
    
    def upscale(self, input_directory, output_directory):

        # Get all image paths
        image_paths = [os.path.join(input_directory, x) for x in os.listdir(input_directory)]

        # Change model input shape to accept all size inputs
        model = keras.models.load_model('../models/generator.h5')
        inputs = keras.Input((None, None, 3))
        output = model(inputs)
        model = keras.models.Model(inputs, output)

        # Loop over all images
        for image_path in image_paths:
            
            # Read image
            low_res = cv2.imread(image_path, 1)

            # Convert to RGB (opencv uses BGR as default)
            low_res = cv2.cvtColor(low_res, cv2.COLOR_BGR2RGB)

            # Rescale to 0-1.
            low_res = low_res / 255.0

            # Get super resolution image
            sr = model.predict(np.expand_dims(low_res, axis=0))[0]

            # Rescale values in range 0-255
            sr = ((sr + 1) / 2.) * 255

            # Convert back to BGR for opencv
            sr = cv2.cvtColor(sr, cv2.COLOR_RGB2BGR)

            # Save the results:
            cv2.imwrite(os.path.join(output_directory, os.path.basename(image_path)), sr)
