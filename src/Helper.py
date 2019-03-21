# N - SHDC; E - SHDC; S - SHDC; W - SHDC
# S - NESW; H - NESW; D - NESW; C - NESW; NT - NESW;

from Header import dbitMapRank, DDS_RANK, DDS_SUIT

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

	if inputMode == "3D":

		suit_counter = 0
		card_counter = 0

		temp = []

		for cards in hand_list:
			for bits in dbitMapRank:
			
				if bits & cards:
					if suit_counter == 0:
						temp.append ([1])
					else:
						temp [card_counter].append (1)
				else:
					if suit_counter == 0:
						temp.append ([0])
					else:
						temp [card_counter].append (0)
			
				card_counter +=1
				if card_counter == 13:
					card_counter = 0
					suit_counter += 1

			if suit_counter == 4:
				suit_counter = 0
				hand_ret.append (temp)
				temp = []

		hand_ret = list (reversed (hand_ret))

		for i in range (3):
			hand_ret.append (hand_ret [i])

		# hand_ret.append (hand_ret [3])

	if inputMode == "3D_Suit_Endian":

		hand_counter = 0
		suit_counter = 0

		temp = [[],[],[],[]]

		for cards in hand_list:
			for bits in dbitMapRank:
				if bits & cards:
					temp [suit_counter].append (1)
				else:
					temp [suit_counter].append (0)
			
			suit_counter += 1
			if suit_counter == 4:
				hand_counter += 1
				suit_counter = 0
				hand_ret.append (temp)
				temp = [[],[],[],[]]

	if inputMode != "Full" and inputMode != "Compact" and inputMode != "2D" and inputMode != "3D" and inputMode != "3D_Suit_Endian":
		print ("Input Mode Error.")
		return ([], -1)
	# =======================================
	if outputMode == "NT_by_N":
		res_ret = result_list [16]

	if outputMode == "None":
		res_ret == -1

	if outputMode == "Par":
		res_ret = -1

	if outputMode != "NT_by_N" and outputMode != "None" and outputMode != "Par":
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

def calcScore (level, suit, double, result, vulnerable = True):

	if level < 1 or level > 7:
		return -1
	if suit < 0 or suit > 4:
		return -1
	if double < 0 or double > 2:
		return -1
	if result < 0 or result > 13:
		return -1

	score = 0
	suit_score = 0
	if suit > 1:
		suit_score = 30
	else:
		suit_score = 20

	if result >= level + 6:
		#-- Contract Score --#
		score += level * suit_score
		if suit == 4:
			score += 10
		if double == 1:
			score *= 2
		if double == 2:
			score *= 4
		#-- Game/Part Bonus --#
		if score < 100:
			score += 50
		else:
			if vulnerable:
				score += 500
			else:
				score += 300
		#-- Overtrick Bonus --#
		if double == 0:
			overtrick_bonus = (result - level - 6) * suit_score
		else:
			overtrick_bonus = (result - level - 6) * 100 * double
			if vulnerable:
				overtrick_bonus *= 2
		score += overtrick_bonus
		#-- Insult Bonus --#
		if double == 1:
			score += 50
		if double == 2:
			score += 100
		#-- Slam Bonus --#
		if level == 6:
			if vulnerable:
				score += 750
			else:
				score += 500
		if level == 7:
			if vulnerable:
				score += 1500
			else:
				score += 1000
		return score

	penalty = 0
	undertrick = level + 6 - result

	if double == 0:
		penalty = -50 * undertrick
		if vulnerable:
			penalty *= 2
		return penalty

	if not vulnerable:
		if undertrick >= 1:
			penalty -= 100
		if undertrick >= 2:
			penalty -= 200
		if undertrick >= 3:
			penalty -= 200
		for i in range (4, undertrick + 1):
			penalty -= 300

	if vulnerable:
		if undertrick >= 1:
			penalty -= 200
		for i in range (2, undertrick + 1):
			penalty -= 300	

	penalty *= double
	return penalty	

