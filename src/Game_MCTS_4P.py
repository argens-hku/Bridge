import GenDeal as gd
from Game import loadNetwork, saveNetwork, getScore, imp
import json
from Bidding import possible_bids, POSSIBLE_BID_COUNT, generateBiddings
import numpy as np
from Node import Node

STAT_SIZE = 18
TEMP = 1

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

def getLegalBid (bidding):

	ret = []
	legal_bids = generateBiddings (bidding, "Competitive")
	for bid in legal_bids:
		ret.append (possible_bids.index (bid))

	return ret

_DEBUG = 1
_EPISODE = 100000
# _EPISODE = 1000
_SIMULATION = 800
_EP_PER_PLAYER = 10
_ACTIVE_PLAYER = 4

RESULT = "../data/Networks/RL/Gen_4/result"
# NETWORK_1 = "../data/Networks/RL/Gen_4/network1.h5"
NETWORK_1 = "../data/Networks/RL/Gen_4/network2.h5"

# # --- Train --- #

network_1 = loadNetwork ("")
# network_1 = loadNetwork (NETWORK_1)
# network_2 = loadNetwork (NETWORK_2)

for i in range (_EPISODE):

	learning_data = []

	deal = gd.genDeal ()
	hands = gd.getHand (deal)
	(par, resTable) = gd.getPar (deal)

	bids = []
	raw_stats = []
	for hand in hands:
		raw_stats = raw_stats + getStat (hand)
	if _ACTIVE_PLAYER == 2:
		for a in [1 ,3]:
			for b in range (STAT_SIZE):
				raw_stats [a * STAT_SIZE + b] = -1
	stats = []
	for player in range (4):
		stats.append (calcStat (raw_stats, player))

	# initBid ()
	player = 0
	learning_player = player // _EP_PER_PLAYER % _ACTIVE_PLAYER
	learning_player *= (4 / _ACTIVE_PLAYER)
	hands = hands
	bids = bids
	stats= stats
	p = network_1.predict (transformInput (hands, stats, bids, player))
	print (p)

	root = Node ([], player, p, learning_player, _ACTIVE_PLAYER)

	# Start Self Play
	while bids [-3:] != ["P","P","P"] or len (bids) < 4:
		# Start MCTS
		for j in range (_SIMULATION):
			node = root
			bid_sim = bids.copy ()
			update_Q = []
			player_sim = player

			while bid_sim [-3:] != ["P","P","P"] or len (bid_sim) < 4:
				move = node.pickMove (TEMP)

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

					node.children [move] = Node (bid_sim, player_sim, p, learning_player, _ACTIVE_PLAYER)
				
				update_Q.append (node)
				node = node.children [move]

			if bid_sim [-3:] == ["P","P","P"]:
				print (bid_sim)
				(_, score) = getScore (bid_sim, resTable)
				index = -1
				for n in reversed (update_Q):
					if par == 0:
						par = 1
					n.update ((score - par) / abs (par), bid_sim [index])
					index -= 1

		# Get Return From MCTS
		move_index = root.N.index (max (root.N))

		bid = possible_bids [root.legal_bids [move_index]]
		total = sum (root.N)
		percentage = list (i / total for i in root.N)
		if player == learning_player:
			learning_data.append ((percentage, root.legal_bids.copy (), bids, player))

		bids.append (bid)
		player += 1
		if player == 4:
			player = 0
		root = root.children [move_index]

	print (i)
	gd.printHand (deal)
	print (bids)
	(_, score) = getScore (bids, resTable)
	print (score, par)


	# End Self Play
	# Start Update

	X = []
	Y = []
	for (percentage, legal_bids, att_bid, player) in learning_data:

		print (percentage, legal_bids, att_bid, player)

		x = transformInput (hands, stats, att_bid, player)
		y = network_1.predict (x)
		for i in range (len (legal_bids)):
			y [0][legal_bids [i]] = percentage [i]

		X.append (x[0])
		Y.append (y[0])

	X = np.asarray (X)
	Y = np.asarray (Y)
	
	network_1.fit (X, Y, epochs = 5, verbose = 1)

	saveNetwork (network_1, NETWORK_1)


# --- Test --- #

# network_1 = loadNetwork (NETWORK_1)

# maximum_gain = 0
# maximum_lost = 0
# total_gain_lost = 0
# squared_total_error = 0
# total_imp = 0
# level_7_count = 0

# for i in range (_EPISODE):

# 	deal = gd.genDeal ()
# 	hands = gd.getHand (deal)
# 	(par, resTable) = gd.getPar (deal)

# 	bids = []
# 	raw_stats = []
# 	for hand in hands:
# 		raw_stats = raw_stats + getStat (hand)
# 	if PLAYER_COUNT == 2:
# 		for a in [1 ,3]:
# 			for b in range (STAT_SIZE):
# 				raw_stats [a * STAT_SIZE + b] = -1
# 	stats = []
# 	for player in range (4):
# 		stats.append (calcStat (raw_stats, player))

# 	# initBid ()
# 	player = 0
# 	hands = hands
# 	bids = bids
# 	stats= stats

# 	while bids [-3:] != ["P", "P", "P"] or len (bids) < 4:

# 		if player == 1 or player == 3:
# 			bids.append ("P")
# 			player += 1
# 			if player == 4:
# 				player = 0
# 			continue

# 		moves_legal = getLegalBid (bids)
# 		p = network_1.predict (transformInput (hands, stats, bids, player))
# 		print (p)
# 		moves_p = list (p[0][i] for i in moves_legal)
# 		bid_index = moves_legal [moves_p.index (max (moves_p))]
# 		bids.append (possible_bids [bid_index])
# 		player += 1
# 		if player == 4:
# 			player = 0

# 	(level, score) = getScore (bids, resTable)
# 	diff = score - par
# 	if diff > maximum_gain:
# 		maximum_gain = diff
# 	if diff < maximum_lost:
# 		maximum_lost = diff
# 	total_gain_lost += diff
# 	squared_total_error += np.square (diff)
# 	total_imp += imp (diff)
# 	if level:
# 		level_7_count += 1

# 	print (bids, score, par, diff, imp (diff))

# print ("maximum_gain", maximum_gain)
# print ("maximum_lost", maximum_lost)
# print ("total_gain_lost", total_gain_lost)
# print ("squared_total_error", squared_total_error)
# print ("episodes", _EPISODE)
# print ("total_imp", total_imp)
# print ("level_7_count", level_7_count)

