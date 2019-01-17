# N - SHDC; E - SHDC; S - SHDC; W - SHDC
# S - NESW; H - NESW; D - NESW; C - NESW; NT - NESW;

import os
from Helper import getData

_trainingFilename = "../data/HandRecords/Large/HandRecord_700000_0"
# Trainingfilename = "../data/HandRecords/Small HandRecords/HandRecord_100_0"
_networkFilename = "../data/Networks/NT_by_N/Network"
_historyFilename = "../data/Networks/NT_by_N/History/Result"

_dataSize = -1		#	Training + Validation Data Size
_inputMode = "2D"
_outputMode = "NT_by_N"

(hand, res) = getData (filename = _trainingFilename, dataSize = _dataSize, inputMode = _inputMode, outputMode = _outputMode)

# --------------------------------       Training        -------------------------------------------

import numpy as np

X = np.asarray (hand)
Y = np.asarray (res)

print ("X_shape", X.shape)
print ("Y_shape", Y.shape)

# from sklearn.model_selection import train_test_split
# X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=1)

# ----- Imports ----- #

from keras import backend as K
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten, GaussianNoise
from keras.layers import Convolution2D
from keras.optimizers import SGD
from sklearn.metrics import mean_squared_error
from keras.constraints import maxnorm
from keras.callbacks import EarlyStopping
from keras import regularizers

# -------------------------------- Start of Architecture -------------------------------------------

# ----- setting random seed ----- #

seed = 6
np.random.seed (seed)

# ----- hyperparameter ----- #

_epoch = 250
_lr = 0.001
_momentum = 0.9
_decay = _lr/_epoch
_batch_size = 50
_loss = "mse"

# ----- Training ----- #

model = Sequential ()
model.add (Convolution2D (32, (3, 3), input_shape = (7, 52, 1), border_mode = "valid", activation = "relu", kernel_constraint = maxnorm (3)))
# model.add (Dropout(0.2))
model.add (Convolution2D (32, (3, 3), border_mode = "valid", activation = "relu", kernel_constraint = maxnorm (3)))
# model.add (Dropout(0.2))
model.add (Convolution2D (32, (3, 3), border_mode = "valid", activation = "relu", kernel_constraint = maxnorm (3)))
# model.add (Dropout(0.2))
model.add (Flatten())
# model.add (Dropout(0.3))
# model.add (Dense (512, activation = 'relu', kernel_regularizer = regularizers.l1_l2 (l1=0.02, l2=0.05)))
model.add (Dense (64, activation = 'relu', kernel_constraint = maxnorm (3)))
model.add (Dropout(0.4))
# model.add (GaussianNoise (0.5))
# model.add (Dense (64, activation = 'relu', kernel_constraint = maxnorm (3)))
# model.add (Dropout(0.4))
# model.add (GaussianNoise (0.5))
# model.add (Dropout(0.3))

# model.add (Dense (256, activation = 'relu', kernel_regularizer = regularizers.l1_l2 (l1=0.02, l2=0.05)))
# model.add (Dropout(0.3))
# model.add (Dense (256, activation = 'relu', kernel_regularizer = regularizers.l1_l2 (l1=0.02, l2=0.05)))
# model.add (Dropout(0.3))
# model.add (Dense (256, activation = 'relu', kernel_regularizer = regularizers.l1_l2 (l1=0.02, l2=0.05)))
# model.add (Dropout(0.3))
# model.add (Dense (256, activation = 'relu', kernel_regularizer = regularizers.l1_l2 (l1=0.02, l2=0.05)))
# model.add (Dropout(0.3))
# model.add (Dense (256, activation = 'relu', kernel_regularizer = regularizers.l1_l2 (l1=0.02, l2=0.05)))
# model.add (Dropout(0.3))

model.add (Dense (16))
model.add (Dense (1))
sgd = SGD(lr=_lr, momentum=_momentum, decay=_decay, nesterov=False)
model.compile(loss=_loss, optimizer=sgd)


early_stopping = EarlyStopping (monitor = "val_loss", patience = 5, min_delta = 0)
history = model.fit(X, Y, epochs = _epoch, batch_size=_batch_size, verbose = True, validation_split = 0.1, callbacks = [early_stopping])
# history = model.fit(X, Y, epochs = _epoch, batch_size=_batch_size, verbose = True, validation_split = 0.1)

# -------------------------------- End of Architecture -------------------------------------------

from Helper import unclash
import matplotlib.pyplot as plt
import json

networkfn = unclash (_networkFilename, ".h5")
print (networkfn)
model.save (networkfn)

resFn = unclash (_historyFilename, ".txt")
print (resFn)
resFile = open (resFn, 'w')
resFile.write (json.dumps (history.history))
resFile.close ()

# Plot training & validation accuracy values
# plt.plot(history.history['acc'])
# plt.plot(history.history['val_acc'])
# plt.title('Model accuracy')
# plt.ylabel('Accuracy')
# plt.xlabel('Epoch')
# plt.legend(['Train', 'Test'], loc='upper left')
# plt.show()

# Plot training & validation loss values
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

K.clear_session ()
