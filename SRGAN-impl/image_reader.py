import h5py
import numpy as np
import matplotlib.pyplot as plt

def batch_train(train_batch_size=456):
    
    
    hdf5_path = './images1.hdf5'
    dataset = h5py.File(hdf5_path, "r")
    
    
    train_batch_imgs=[]
    for i in range(train_batch_size):
        img=(dataset['train_img'])[i]
        img=img/1.
        train_batch_imgs.append(img)    
    train_batch_imgs=np.array(train_batch_imgs)
    
    dataset.close()
    
    return train_batch_imgs