# N - SHDC; E - SHDC; S - SHDC; W - SHDC
# S - NESW; H - NESW; D - NESW; C - NESW; NT - NESW;

from Header import dbitMapRank, DDS_RANK

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

	if inputMode == "Compact":
		for i in range (52):
			hand_ret.append (-1)

		player = 0
		suit = 0
		rank = 0

		for cards in hand_list:
			for bits in dbitMapRank:
				if bits & cards:
					if player == 0:
						hand_ret [suit * DDS_RANK + rank] = 1
					if player == 1:
						hand_ret [suit * DDS_RANK + rank] = -1
					if player == 2:
						hand_ret [suit * DDS_RANK + rank] = 0.5
					if player == 3:
						hand_ret [suit * DDS_RANK + rank] = -0.5

				rank += 1
			rank = 0
			suit += 1
			if suit >= 4:
				suit = 0
				player += 1

	if inputMode == "2D":

		counter = 0
		temp = []
		for cards in hand_list:
			for bits in dbitMapRank:
				if bits & cards:
					temp.append ([1])
				else:
					temp.append ([0])
			
			counter +=1

			if counter == 4:
				counter = 0
				hand_ret.append (temp)
				temp = []

		hand_ret = list (reversed (hand_ret))

		for i in range (3):
			hand_ret.append (hand_ret [i])

		# hand_ret.append (hand_ret [3])

	if inputMode != "Full" and inputMode != "Compact" and inputMode != "2D":
		print ("Input Mode Error.")
		return ([], -1)
	# =======================================
	if outputMode == "NT_by_N":
		res_ret = result_list [16]

	if outputMode != "NT_by_N":
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
import numpy as np

def mse (Y_pred, Y):

	Y_pred = Y_pred.reshape (Y_pred.shape [0],)

	s = 0
	c = 0

	for (y, y_pred) in zip (Y_pred, Y):
		c += 1
		t = y - y_pred
		s += t * t

	return s/c

def accuracy (Y_pred, Y, margin = 0):

	if type (Y_pred) != type (Y):
		print ("Different data type in Accuracy Test!!!!")
		return -1

	if margin < 0:
		print ("Margin cannot be zero!")
		return -1

	Y_pred = Y_pred.reshape (Y_pred.shape [0],)

	s = 0
	c = 0

	for (y, y_pred) in zip (Y_pred, Y):
		c += 1
		if margin == 0:
			if y_pred == y:
				s += 1
		else:
			if abs (y_pred - y) <= margin:
				s += 1

	return s/c