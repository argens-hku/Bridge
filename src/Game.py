import dds
import GenDeal as gd
from Agent import Agent, STAT_SIZE
from Helper import unclash, toString, calcScore

from keras.models import Sequential, load_model
from keras.layers import Dense
from keras import regularizers
import numpy as np
import tensorflow as tf
from keras import backend as K

import os
import json

LAYER0 = 128
LAYER1 = 128
LAYER2 = 128
L2_REGULARIZER = 0.01
BIDDING_ALPHA = 0.1
EXPLORE_COEFFICIENT = 0.001


def _loss ():
	def custom_loss (y_pred, y_true):
		y_pred = tf.convert_to_tensor (y_pred)
		y_true = tf.convert_to_tensor (y_true)

		# val_loss = y_true[-1] - y_pred[-1]
		cross_entropy_loss = - K.sum (y_pred * K.log (y_true), 1)
		# return val_loss - cross_entropy_loss
		return cross_entropy_loss
	return custom_loss

def saveNetwork (model, filename):
	model.save (filename)
	return

def loadNetwork (filename = ""):
	if filename == "":
		model = Sequential ()
		model.add (Dense (LAYER0, input_shape = (220,))) #52 + (SHDC + AKOJT9s + AKs = 4 + 6 + 8) * 3 + 38 * 3
		model.add (Dense (LAYER1, activation = 'sigmoid', kernel_regularizer = regularizers.l2(L2_REGULARIZER)))
		model.add (Dense (LAYER2, activation = 'linear', kernel_regularizer = regularizers.l2(L2_REGULARIZER)))
		model.add (Dense (38, activation = 'sigmoid'))
		model.compile (loss = _loss(), optimizer = 'sgd')
		return model

	model = load_model (filename, custom_objects={'custom_loss': _loss()})
	return model

def play (agents):
	bids = []
	player = 0
	stats = list (-1 for i in range (STAT_SIZE * 4))
	passes = ["P","P","P"]
	while True:
		agent = agents [player]
		state = (stats, bids, player)
		bid = agent.move (state)
		bids.append (bid)
		if toString (bids) in agent.biddingBase().keys ():
			for i in range (STAT_SIZE):
				stats [player * STAT_SIZE + i] = agent.biddingBase()[toString(bids)][i]
		agent.updateStat (bids)
		player += 1
		if player == 4:
			player = 0
		if bids [-3:] == passes:
			break
	return bids

def loadBiddingBase (filename = ""):
	
	system = {}

	if filename == "":
		return system

	if os.path.getsize (filename) == 0:
		return system

	file = open (filename, "r")
	try:
		system = dict (json.loads (file.read ()))
	except:
		print ("Parsing Error")
		print ("")
	file.close ()

	return system

def writeBiddingBase (system, filename):

	# import os.path
	# from pathlib import Path

	# if Path (filename).is_file() and not overwrite:
	# 	print ("Cannot Overwrite System")
	# 	return

	file = open (filename, "w")
	file.write (json.dumps (system))
	file.close ()

def giveHands (agents, hands):
	
	for i in range (4):
		agents [i].setHand (hands [i])

def setTarget (outputHistory, moveHistory, par, score, position):

	utility = score - par

	if position % 2 == 1:
		utility *= -1

	if utility == 0:
		return outputHistory

	if utility < 0:
		reward = False
	else:
		reward = True

	# reward = utility / abs (par)

	target = []
	for i in range (len (outputHistory)):
		output = outputHistory [i]
		(choice, legalBids) = moveHistory [i]
		# penalty = 1 * reward / len (legalBids)
		for j in legalBids:
			if j == choice:
				if reward:
					output [j] = 1
				else:
					output [j] = 0 #< ---------- !!!!! < -------- !!!!! ??? Maybe use relu at output neurons?
			else:
				if reward:
					output [j] = 0
				else:
					output [j] = 1
				# output [j] = output [j] * np.exp (penalty)
		target.append (output)

	return target

def getScore (bids, resTable):
	double = 0
	level = 0
	suit = -1
	player = -1
	side = -1
	suit_conv = {'S': 0, "H": 1, "D": 2, "C": 3, "N": 4}
	first_NS = [-1,-1,-1,-1,-1]
	first_EW = [-1,-1,-1,-1,-1]

	for bid in bids:
		player += 1
		if player == 4:
			player = 0
		# print ("player, bid", player, bid)
		if bid == "P":
			continue
		if bid == "X":
			double = 1
			continue
		if bid == "XX":
			double = 2 
			continue
		double = 0
		try:
			level = int (bid [0])
			suit = suit_conv [bid [1]]
		except:
			print ("Bid Error -- getScore, Game.py, 129")
		if player % 2 == 0:
			if first_NS [suit] == -1:
				first_NS [suit] = player
			side = 0
		else:
			if first_EW [suit] == -1:
				first_EW [suit] = player
			side = 1

	if side == 0:
		decl = first_NS [suit]
	else:
		decl = first_EW [suit]

	result = resTable [suit * 4 + decl]
	# print ("side, level, suit, decl", side, level, suit, decl)
	score = calcScore (level, suit, double, result)
	if side != 0:
		score *= -1
	return score

def learn (network, results, par, score):
	# results = [(position, agent_feedback) NESW]
	# agent_feedback = ([inputHistory],[outputHistory],[moveHistory])
	# par = NS perspective

	Y_true = [] #target
	X = []

	for result in results:
		(position, feedback) = result
		(inputHistory, outputHistory, moveHistory) = feedback
		X = X + inputHistory
		Y_true = Y_true + setTarget (outputHistory, moveHistory, par, score, position)

	if K.backend () == "tensorflow":
		x = np.asarray (X)
		y = np.asarray (Y_true)
	print ("X_SHAPE", x.shape)
	print ("Y_SHAPE", y.shape)
	network.fit (x, y, epochs = 1, verbose = 0)
	return

def main ():

	NETWORK_1 = "../data/Networks/RL/Gen_1/network.h5"
	NETWORK_2 = "../data/Networks/RL/Gen_1/network.h5"
	NETWORK_3 = ""
	NETWORK_4 = ""

	BIDDING_1 = "../data/Networks/RL/Gen_1/bidding"
	BIDDING_2 = "../data/Networks/RL/Gen_1/bidding"
	BIDDING_3 = ""
	BIDDING_4 = ""

	network_1 = loadNetwork (NETWORK_1)
	biddingBase_1 = loadBiddingBase (BIDDING_1)

	agent_1 = Agent (network_1, biddingBase_1)
	agent_2 = Agent (network_1, biddingBase_1)
	agent_3 = Agent (network_1, biddingBase_1)
	agent_4 = Agent (network_1, biddingBase_1)

	agents = [agent_1, agent_2, agent_3, agent_4]
	for agent in agents:
		agent.setCoefficient (BIDDING_ALPHA, EXPLORE_COEFFICIENT)

	episodes = 1000
	deal = gd.genDeal ()
	gd.printHand (deal)
	(par, resTable) = gd.getPar (deal)
	print (resTable)
	for i in range (episodes):
		giveHands (agents, gd.getHand(deal))
		bids = play (agents)
		results = []
		counter = 0
		for agent in agents:
			results.append ((counter, agent.feedback ()))
			counter += 1

		(par, resTable) = gd.getPar (deal)
		score = getScore (bids, resTable)
		learn (network_1, results, par, score)
		writeBiddingBase (biddingBase_1, BIDDING_1)
		print (bids)
		print (par, score)
		print ("----")
		saveNetwork (network_1, NETWORK_2)

main ()