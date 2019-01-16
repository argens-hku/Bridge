# Author: Argens Ng
# Description: This program tests neural networks in batch and clears screen to output in a neat manner

result = []
# currentDirectory = os.path.dirname(os.path.abspath(__file__))
# import os

_handRecordsDirectory = "../data/HandRecords"
_testingFilename = _handRecordsDirectory + "/Shared/HandRecord_20000_0"
# _testingFilename = _handRecordsDirectory + "/Small/HandRecord_100_0"

_networkDirectory = "../data/Networks/NT_by_N"
_networkFilename = _networkDirectory + "/Network_3.h5"
# _networkFilename = _networkDirectory + "/NT_by_N/Network_0.h5"

# Description: Clears the standard output screen

def clearScreen ():
	print ("\033c")

from Helper import getData, mse, accuracy
import numpy as np

_dataSize = -1		#	Training + Validation Data Size
_inputMode = "Compact"
_outputMode = "NT_by_N"


def testing (hand, res, networkFilename, testingFilename):


	X = np.asarray (hand)
	Y = np.asarray (res)
	# Y = np.asarray (list_move)


	from keras.models import load_model

	model = load_model (networkFilename)
	Y_pred = model.predict(X, verbose=True)

	# clearScreen ()
	print ("")
	# print ("X_shape", X.shape)
	# print ("Y_shape", Y.shape)

	(size, ) = Y.shape
	mean_squared_error = mse (Y_pred, Y)

	Y_pred_int = np.around (Y_pred).astype (int)
	acc = accuracy (Y_pred_int, Y)
	acc_1 = accuracy (Y_pred_int, Y, 1)
	acc_2 = accuracy (Y_pred_int, Y, 2)

	print ("")
	print (networkFilename)
	print (testingFilename)
	print (mean_squared_error, acc, acc_1, acc_2)
	print ("")

	from keras import backend as K
	K.clear_session ()

(hand, res) = getData (filename = _testingFilename, dataSize = _dataSize, inputMode = _inputMode, outputMode = _outputMode)
testing (hand, res, _networkFilename, _testingFilename)

_testingFilename2 = _handRecordsDirectory + "/Shared/HandRecord_25000_0"
(hand, res) = getData (filename = _testingFilename2, dataSize = _dataSize, inputMode = _inputMode, outputMode = _outputMode)
testing (hand, res, _networkFilename, _testingFilename2)