# N - SHDC; E - SHDC; S - SHDC; W - SHDC
# S - NESW; H - NESW; D - NESW; C - NESW; NT - NESW;

import os
from Helper import getData

Trainingfilename = "../data/HandRecords/Small HandRecords/HandRecord_100_0"
Networkfilename = "../data/Networks/NT_by_N/Network"

_dataSize = 2000		#	Training + Validation Data Size
_inputMode = "Full"
_outputMode = "NT_by_N"

(hand, res) = getData (filename = Trainingfilename, dataSize = _dataSize, inputMode = _inputMode, outputMode = _outputMode)

# --------------------------------       Training        -------------------------------------------

import numpy as np

X = np.asarray (hand)
Y = np.asarray (res)

print ("X_shape", X.shape)
print ("Y_shape", Y.shape)

from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=1)

# ----- setting random seed ----- #
seed = 6
np.random.seed (seed)

# ----- hyperparameter ----- #
epoch_ = 10
lr_ = 0.001
momentum_ = 0.9
decay_ = lr_/epoch_
batch_size_ = 5

# ----- Training ----- #

from keras import backend as K
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import SGD
from sklearn.metrics import mean_squared_error
from keras.constraints import maxnorm

model = Sequential ()
model.add (Dense (512, activation = 'relu', W_constraint = maxnorm(2), input_shape = (208, )))
# model.add (Dropout(0.3))
model.add (Dense (512, activation = 'relu', W_constraint = maxnorm(2)))
# model.add (Dropout(0.3))
model.add (Dense (512, activation = 'relu', W_constraint = maxnorm(2)))
# model.add (Dropout(0.3))
model.add (Dense (512, activation = 'relu', W_constraint = maxnorm(2)))
# model.add (Dropout(0.3))
model.add (Dense (64))
model.add (Dense (1))
sgd = SGD(lr=lr_, momentum=momentum_, decay=decay_, nesterov=False)
model.compile(loss='mse', optimizer=sgd)

from keras.callbacks import EarlyStopping

early_stopping = EarlyStopping (monitor = "val_loss", patience = 5, min_delta = 0)
model.fit(X, Y, epochs = epoch_, batch_size=batch_size_, verbose = True, validation_split = 0.1, callbacks = [early_stopping])

from Helpler import unclash

Networkfilename = unclash (Networkfilename, ".h5")
print (Networkfilename)
model.save (Networkfilename)

K.clear_session ()
