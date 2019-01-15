from Header import dbitMapRank

def decodeGameRecord (line, inputMode, outputMode):
	temp_arr = line.split ("|")
	hand_list = list (map (int, temp_arr [0].split (",")))
	result_list = list (map (int, temp_arr [1].split (",")))
	hand_ret = []
	res_ret = -1
	# =======================================
	if inputMode == "Full":
		for cards in hand_list:
			for bits in dbitMapRank:
				if bits & cards:
					hand_ret.append (1)
				else:
					hand_ret.append (0)
	else:
		print ("Input Mode Error.")
		return ([], -1)
	# =======================================
	if outputMode == "NT_by_N":
		res_ret = result_list [16]
	else:
		print ("Output Mode Error.")
		return ([], -1)
	return (hand_ret, res_ret)


def getData (filename, dataSize, inputMode, outputMode):

	hand = []
	res = []

	dealFile = open (filename, "r")

	counter = 0
	for line in dealFile:
		
		(one_hand, one_res) = decodeGameRecord (line, inputMode = inputMode, outputMode = outputMode)
		if one_hand == [] or one_res == -1:
			print ("Unsuccessful Decode.")
			return ([], [])

		hand.append (one_hand)
		res.append (one_res)

		counter += 1
		if counter == dataSize:
			break

	return (hand, res)

import os.path
from pathlib import Path

def unclash (name, extension):
	
	counter = 0
	filepath = Path (name + "_" + str(counter) + extension)

	while filepath.is_file():
		counter += 1
		filepath = Path (name + "_" + str (counter) + extension)

	return (name + "_" + str (counter) + extension)


#-------------------------------------------

# Description: Helps calculate the mean squared error between testing set and prediction
# Input:
#	[(*, )FLOAT] Y_pred: a list of floats indidcating the prediction of the network
#	[(*, )INT] Y: a list of integers indicating the winner of the game in the end (1 if it is the current player, -1 if it is not, 0 if it is a draw)
# Output:
#	[FLOAT] the mean squared error

# from keras.objectives import mean_squared_error
import numpy

def mse (Y_pred, Y):

	Y_pred = Y_pred.reshape (Y_pred.shape [0],)

	s = 0
	c = 0

	for (y, y_pred) in zip (Y_pred, Y):
		c += 1
		t = y - y_pred
		s += t * t

	return s/c