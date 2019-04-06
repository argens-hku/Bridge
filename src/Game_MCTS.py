import GenDeal as gd
from Game import loadNetwork, saveNetwork, getScore
import json
from Bidding import possible_bids, POSSIBLE_BID_COUNT
import numpy as np
from Node import Node

STAT_SIZE = 18
PLAYER_COUNT = 2

def writeJson (item, filename):

	file = open (filename, "w")
	file.write (json.dumps (item))
	file.close ()

def getStat (hand):

	count = [0, 0, 0, 0]
	H_count = [0, 0, 0, 0, 0, 0]
	C_count = [0, 0, 0, 0, 0, 0, 0, 0]

	suit_counter = 0
	card_counter = 0
	for card in hand:
		if card == 1:
			if card_counter < 6:
				H_count [card_counter] += 1
			if card_counter < 2:
				C_count [suit_counter * 2 + card_counter] += 1
			count [suit_counter] += 1
		card_counter += 1
		if card_counter == 13:
			suit_counter += 1
			card_counter = 0
	return (count + H_count + C_count)

def one_hot_encode (bids):
	indices = []
	res = np.zeros (POSSIBLE_BID_COUNT * 10)
	for bid in bids [-10:]:
		indices.append (possible_bids.index (bid))
	base = 10 - len (indices)
	for i in range (len (indices)):
		res [indices [i] + POSSIBLE_BID_COUNT * (base + i)] = 1
	return list (res)

def calcStat (stats, player):
	res = []
	for i in range (player + 1, 4):
		for j in range (STAT_SIZE):
				res.append (stats [i * STAT_SIZE + j])
	for i in range (0, player):
		for j in range (STAT_SIZE):
				res.append (stats [i * STAT_SIZE + j])
		
	for j in range (STAT_SIZE):
		each = -1
		known = stats [player * STAT_SIZE + j]
		unknown_count = 0
		total = -1
		for i in range (3):
			if res [i * STAT_SIZE + j] != -1:
				known += res [i * STAT_SIZE + j]
			else:
				unknown_count += 1

		if unknown_count != 0:
			if j < 10:
				total = 4
			else:
				total = 1
			if j < 4:
				total = 13
			total -= known
			if total < 0:
				total = 0
			each = total / unknown_count

		if each != -1:
			for i in range (3):
				if res [i * STAT_SIZE + j] == -1:
					res [i * STAT_SIZE + j] = each

	return res

def transformInput (hands, stats, bids, player):
	 x = hands [player].copy ()
	 x = x + stats [player]
	 x = x + one_hot_encode (bids)
	 x = np.asarray ([x])

	 return x

_DEBUG = 1
_EPISODE = 100000
_SIMULATION = 800

RESULT = "../data/Networks/RL/Gen_4/result"
NETWORK_1 = "../data/Networks/RL/Gen_4/network1.h5"
# NETWORK_2 = "../data/Networks/RL/Gen_4/network2.h5"

network_1 = loadNetwork (NETWORK_1)
# network_2 = loadNetwork (NETWORK_2)



for i in range (_EPISODE):

	learning_data = []
	# learning_player = 0

	deal = gd.genDeal ()
	hands = gd.getHand (deal)
	(par, resTable) = gd.getPar (deal)

	bids = []
	raw_stats = []
	for hand in hands:
		raw_stats = raw_stats + getStat (hand)
	if PLAYER_COUNT == 2:
		for a in [1 ,3]:
			for b in range (STAT_SIZE):
				raw_stats [a * STAT_SIZE + b] = -1
	stats = []
	for player in range (4):
		stats.append (calcStat (raw_stats, player))

	# initBid ()
	player = 0
	hands = hands
	bids = bids
	stats= stats
	p = network_1.predict (transformInput (hands, stats, bids, player))

	root = Node ([], player, p)

	# Start Self Play
	while bids [-3:] != ["P","P","P"] or len (bids) < 4:
		# Start MCTS
		for j in range (_SIMULATION):
			node = root
			bid_sim = bids.copy ()
			update_Q = []
			player_sim = player

			while bid_sim [-3:] != ["P","P","P"] or len (bid_sim) < 4:
				move = node.pickMove ()

				bid_sim.append (possible_bids [node.legal_bids [move]])
				player_sim += 1
				if player_sim == 4:
					player_sim = 0

				if node.children [move] == None:
					# if player == 0:
					# 	p = network_1.predict (transformInput (hands, stats, bid_sim, player))
					# if player == 2:
					# 	p = network_2.predict (transformInput (hands, stats, bid_sim, player))
					# if player == 1 or player == 3:
					p = network_1.predict (transformInput (hands, stats, bid_sim, player_sim))

					node.children [move] = Node (bid_sim, player_sim, p)
				
				update_Q.append (node)
				node = node.children [move]

			if bid_sim [-3:] == ["P","P","P"]:
				print (bid_sim)
				(_, score) = getScore (bid_sim, resTable)
				index = -1
				for n in reversed (update_Q):
					n.update (score - par, bid_sim [index])
					index -= 1

		# Get Return From MCTS
		move_index = root.N.index (max (root.N))

		bid = possible_bids [root.legal_bids [move_index]]
		learning_data.append ((root.N.copy (), root.legal_bids.copy (), bids, player))

		bids.append (bid)
		player += 1
		if player == 4:
			player = 0
		root = root.children [move_index]

	gd.printHand (deal)
	print (bids)
	(_, score) = getScore (bids, resTable)
	print (score, par)


	# End Self Play
	# Start Update

	X = []
	Y = []
	for (N, legal_bids, att_bid, player) in learning_data:

		x = transformInput (hands, stats, att_bid, player)
		y = network_1.predict (x)
		for i in range (len (legal_bids)):
			y [0][legal_bids [i]] = N [i]

		X.append (x[0])
		Y.append (y[0])

	X = np.asarray (X)
	Y = np.asarray (Y)
	
	network_1.fit (X, Y, epochs = 5, verbose = 1)

saveNetwork (network_1, NETWORK_1)