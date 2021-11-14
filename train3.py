#!/usr/bin/env python
#model like in https://www.youtube.com/watch?v=tcpmucSLKo8

import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras import optimizers
from tensorflow.keras import backend as K
import sklearn
from utils import Sample

# Global variable
OUT_SHAPE = 1
INPUT_SHAPE = (Sample.IMG_H, Sample.IMG_W, Sample.IMG_D)


def customized_loss(y_true, y_pred, loss='euclidean'):
    # Simply a mean squared error that penalizes large joystick summed values
    if loss == 'L2':
        L2_norm_cost = 0.001
        val = K.mean(K.square((y_pred - y_true)), axis=-1) \
                    + K.sum(K.square(y_pred), axis=-1)/2 * L2_norm_cost
    # euclidean distance loss
    elif loss == 'euclidean':
        val = K.sqrt(K.sum(K.square(y_pred-y_true), axis=-1))
    return val


def create_model_1(keep_prob = 0.8):
    model = Sequential()

    # NVIDIA's model
    model.add(Conv2D(24, kernel_size=(5, 5), strides=(2, 2), activation='relu', input_shape= INPUT_SHAPE))
    model.add(Conv2D(36, kernel_size=(5, 5), strides=(2, 2), activation='relu'))
    model.add(Conv2D(48, kernel_size=(5, 5), strides=(2, 2), activation='relu'))
    model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
    model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
    model.add(Flatten())
    model.add(Dense(1164, activation='relu'))
    drop_out = 1 - keep_prob
    model.add(Dropout(drop_out))
    model.add(Dense(100, activation='relu'))
    model.add(Dropout(drop_out))
    model.add(Dense(50, activation='relu'))
    model.add(Dropout(drop_out))
    model.add(Dense(10, activation='relu'))
    model.add(Dropout(drop_out))
    
    model.add(Dense(OUT_SHAPE, activation='softsign'))
    model.summary()

    return model

def create_model_2(keep_prob = 1.0):
    model = Sequential()

    # NVIDIA's model
    model.add(Conv2D(24, kernel_size=(5, 5), strides=(2, 2), activation='elu', input_shape= INPUT_SHAPE))
    model.add(Conv2D(36, kernel_size=(5, 5), strides=(2, 2), activation='elu'))
    model.add(Conv2D(48, kernel_size=(5, 5), strides=(2, 2), activation='elu'))
    model.add(Conv2D(64, kernel_size=(3, 3), activation='elu'))
    model.add(Conv2D(64, kernel_size=(3, 3), activation='elu'))
    model.add(Flatten())
    drop_out = 1 - keep_prob
    model.add(Dropout(drop_out))
    model.add(Dense(100, activation='elu'))
    model.add(Dropout(drop_out))
    model.add(Dense(50, activation='elu'))
    model.add(Dropout(drop_out))
    model.add(Dense(10, activation='elu'))
    model.add(Dropout(drop_out))
    model.add(Dense(OUT_SHAPE))
    model.summary()

    return model

import sys
import os
if __name__ == '__main__':

    # Load Training Data
    x_train = np.load(os.path.join(sys.argv[2], "X.npy"))
    y_train = np.load(os.path.join(sys.argv[2], "y.npy"))

    x_train, y_train = sklearn.utils.shuffle(x_train, y_train)
    # print(y_train)

    print(x_train.shape[0], 'train samples')


    # Training loop variables
    epochs = 120
    batch_size = 70
    print("1")
    if(sys.argv[1] == "1"):
        model = create_model_1(0.8)
    elif(sys.argv[1] == "2"):
        model = create_model_2(0.8)

    print("2")
    #learning_rate=0.0001
    model.compile(loss='mse', optimizer=optimizers.Adam(learning_rate=0.0001))
    print("3")
    model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, shuffle=True, validation_split=0.2)
    print("4")
    model.save_weights('model_weights.h5')
