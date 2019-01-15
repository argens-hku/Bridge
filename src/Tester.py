# Author: Argens Ng
# Description: This program tests neural networks in batch and clears screen to output in a neat manner

result = []
# currentDirectory = os.path.dirname(os.path.abspath(__file__))
import os

HandRecordsDirectory = "../data/HandRecords"
HandRecordsFilename = HandRecordsDirectory + "/Large HandRecords/HandRecord_25000_0"

NetworkDirectory = "../data/Networks"
NetworkFilename = NetworkDirectory + "HandRecord_0"

# Description: Clears the standard output screen

def clearScreen ():
	print ("\033c")

from othello import State

# Description: Converts a condensed state (Byte/Train_) format into inputs for neural network with varying features
# Input:
#	[STR] line: a line in any of the training sets
#	[STR] option: a string indicating feature option namely:
#			border (or unprovided): border padding only
#			corner_and_border: border padding highlighting corner while punishing the squares nearby
#			moves and cb: corner_and_border and an additional layer with matrix of moves available highlighted with 1s
# Output:
#	[(5,8,8) INT] OR [(4,8,8) INT] a 5-8-8 or 4-8-8 integer matrix which stores selected feature. Feature option of "moves and cb" returns a 5,8,8 matrix

def convertToNN (line, option = "border"):
	board = []
	white = []
	black = []
	empty = []
	border = []
	moves = []
	for i in range (size):
		row_white = []
		row_black = []
		row_empty = []
		row_border = []
		row_total = []
		for j in range (size):
			if i == 0 or j == 0 or i == size-1 or j == size-1:
				row_border.append (1)
			else:
				row_border.append (0)
			piece = int (line [i*8+j])
			if piece == 0:
				row_empty.append (1)
				row_black.append (0)
				row_white.append (0)
				row_total.append (0)
			else:
				if piece == 1:
					row_empty.append (0)
					row_black.append (1)
					row_white.append (0)
					row_total.append (1)
				else:
					row_empty.append (0)
					row_black.append (0)
					row_white.append (1)
					row_total.append (-1)

		empty.append (row_empty)
		white.append (row_white)
		black.append (row_black)
		border.append (row_border)
		moves.append (row_total)

	if option == "corner_and_border" or option == "moves and cb":
		border [0][0] = border [0][size - 1] = border [size - 1][0] = border [size - 1][size - 1] = 4
		border [0][1] = border [1][0] =  border [1][1] = -1
		border [0][size - 2] = border [1][size - 1] =  border [1][size - 2] = -1
		border [size - 2][0] = border [size - 1][1] =  border [size - 2][1] = -1
		border [size - 2][size - 1] = border [size - 1][size - 2] = border [size - 1][size - 1] =  -1

	e = np.asarray (empty)
	w = np.asarray (white)
	bl = np.asarray (black)
	bd = np.asarray (border)

	board.append (e)
	board.append (w)
	board.append (bl)
	board.append (bd)

	if option == "moves and cb":

		state = State (board = moves)
		for i in range (size):
			for j in range (size):
				moves [i][j] = 0

		for (x, y, _) in state.validMoves:
			moves [x][y] = 1

		mv = np.asarray (moves)
		board.append (mv)

	# print ("e", e.shape)
	# print ("w", w.shape)
	# print ("bl", bl.shape)

	# b = np.asarray (board)
	# print ("b.shape", b.shape)
	return board

from keras.objectives import mean_squared_error
from keras.models import load_model
import tensorflow as tf

#-------------------------------------------

# Description: Helps calculate the mean squared error between testing set and prediction
# Input:
#	[(*, )FLOAT] Y_pred: a list of floats indidcating the prediction of the network
#	[(*, )INT] Y: a list of integers indicating the winner of the game in the end (1 if it is the current player, -1 if it is not, 0 if it is a draw)
# Output:
#	[FLOAT] the mean squared error 

def mse (Y_pred, Y):

	Y_pred = Y_pred.reshape (Y_pred.shape [0],)

	s = 0
	c = 0

	for (y, y_pred) in zip (Y_pred, Y):
		c += 1
		t = y - y_pred
		s += t * t

	return s/c


# Description: A snippet that does test
# Input:
#	[(*, 8, 8, )INT] X1: training set with feature 1
#	[(*, 8, 8, )INT] X2: training set with feature 2
#	[(*, )FLOAT] Y: a list of integers indicating the winner of the game in the end (1 if it is the current player, -1 if it is not, 0 if it is a draw)
# Output:
#	[(*, (STR, FLOAT))] list of tuples with first entry of tuple being the tag/name and second being the mean squared error
def doTests (X1, X2, Y):
	global result

	#-------------------------------------------

	# valueNN = "ValueNetwork/value_network.h5"
	# model = load_model (valueNN)
	# Y_pred = model.predict(X1, verbose=True)
	# result.append (("value_network.h5: ", mse (Y_pred, Y)))

	#-------------------------------------------

	# valueNN = "ValueNetwork/value_network5.h5"
	# model = load_model (valueNN)
	# Y_pred = model.predict(X2, verbose=True)
	# result.append (("value_network5.h5: ", mse (Y_pred, Y)))

	#-------------------------------------------

	valueNN = "ValueNetwork/final_network3.h5"
	model = load_model (valueNN)
	Y_pred = model.predict(X2, verbose=True)
	result.append (("final_network3.h5: ", mse (Y_pred, Y)))

	#-------------------------------------------

for order in range (8):

	filename = trainingFilename + str (order + 1)
	print (filename)

	list_X1 = []
	list_X2 = []
	list_move = []
	list_winner = []

	gameCounter = 0
	gameEnd = 100000000

	import numpy as np

	f = open (filename, "r")
	for line in f:
		if gameCounter > gameEnd:
			break
		gameCounter += 1
		board1 = convertToNN (line, "border")
		board2 = convertToNN (line, "moves and cb")

		x = int (line [65])
		y = int (line [68])
		if len (line) == 73:
			winner = int (line [70:72])
		else:
			winner = int (line [70])

		list_winner.append (winner)
		# list_move.append (createOutputGrid (x, y))
		list_X1.append (board1)
		list_X2.append (board2)

	import numpy as np

	X1 = np.asarray (list_X1)
	X2 = np.asarray (list_X2)
	Y = np.asarray (list_winner)
	# Y = np.asarray (list_move)

	print ("X1_shape", X1.shape)
	print ("X2_shape", X2.shape)
	print ("Y_shape", Y.shape)

	result.append ((order+1, "-------------------------------------"))
	doTests (X1, X2, Y)

clearScreen ()

for x in result:
	print (x)