import matplotlib.pyplot as plt
import numpy as np
import tensorflow.keras
# import keras

img_rows = 28
img_cols = 28
channels = 1
img_shape = (img_rows, img_cols, channels)
z_dim = 100

def build_generator(z_dim):
    model = Sequential()

    model.add(Dense(256*7*7, input_dim=z_dim))
    model.