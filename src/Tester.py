# Author: Argens Ng
# Description: This program tests neural networks in batch and clears screen to output in a neat manner

result = []
# currentDirectory = os.path.dirname(os.path.abspath(__file__))
# import os

_handRecordsDirectory = "../data/HandRecords"
_testingFilename = _handRecordsDirectory + "/Shared/HandRecord_25000_0"
# _testingFilename = _handRecordsDirectory + "/Small/HandRecord_100_0"

_networkDirectory = "../data/Networks/NT_by_N"
_networkFilename = _networkDirectory + "/Network_1.h5"
# _networkFilename = _networkDirectory + "/NT_by_N/Network_0.h5"

# Description: Clears the standard output screen

def clearScreen ():
	print ("\033c")

from Helper import getData, mse

_dataSize = 25000		#	Training + Validation Data Size
_inputMode = "Full"
_outputMode = "NT_by_N"

(hand, res) = getData (filename = _testingFilename, dataSize = _dataSize, inputMode = _inputMode, outputMode = _outputMode)

import numpy as np

X = np.asarray (hand)
Y = np.asarray (res)
# Y = np.asarray (list_move)


from keras.models import load_model

model = load_model (_networkFilename)
Y_pred = model.predict(X, verbose=True)

clearScreen ()
print ("")
print ("X_shape", X.shape)
print ("Y_shape", Y.shape)

(size, ) = Y.shape
mse = mse (Y_pred, Y)
print ((_networkFilename, mse))

from keras import backend as K
K.clear_session ()