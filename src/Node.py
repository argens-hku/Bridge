from Bidding import possible_bids, POSSIBLE_BID_COUNT, generateBiddings
import numpy as np

_EXPLORE_RATIO_E = 0.25
_DIR_CONSTANT = 0.03
_C_PUCT = 0.5

class Node:

	def getLegalBid (self, bidding):

		ret = []
		legal_bids = generateBiddings (bidding, "Competitive")
		for bid in legal_bids:
			ret.append (possible_bids.index (bid))

		return ret

	def addNoise (self, p):

		seed = list (_DIR_CONSTANT for i in self.legal_bids)
		noise = np.random.dirichlet (seed)
		ret = []
		for bid_index in range (self.width):
			ret.append (p [bid_index] * (1 - _EXPLORE_RATIO_E) + _EXPLORE_RATIO_E * noise [bid_index])

		return ret

	def __init__ (self, bidding, player, p, learning_p, active_P_count):

		self.player = player
		self.learning_p = learning_p
		if active_P_count == 2:
			if player != 0 and player != 2:
				self.legal_bids = [possible_bids.index ("P")]
			else:
				self.legal_bids = self.getLegalBid (bidding)
		else:
			self.legal_bids = self.getLegalBid (bidding)

		self.W = []
		self.N = []
		self.Q = []
		self.P = []
		self.children = []
		self.width = len (self.legal_bids)

		for i in range (self.width):
			self.W.append (0)
			self.N.append (0)
			self.Q.append (0)
			self.P.append (0)
			self.children.append (None)

		if len (self.legal_bids) > 1 and self.player != learning_p:
			self.P = self.addNoise (p [0])

	def pickMove (self, temp):

		if len (self.legal_bids) == 1:
			return 0

		if self.player != self.learning_p:
			index = self.P.index (max (self.P))
			return index

		sqrt_total = np.sqrt (sum (self.N))

		U = []
		for i in range (self.width):
			value = 0
			value += self.Q [i]
			value += sqrt_total * self.P [i] / (1 + self.N [i]) * _C_PUCT
			U.append (value)

		if self.player == 0 or self.player == 2:
			return U.index (max (U))

		return U.index (min (U))

	# def expand (self):

	# 	move = self.pickMove ()
	# 	if self.children [move] == None:
	# 		self.children = 

	def update (self, value, bid):

		index = self.legal_bids.index (possible_bids.index (bid))
		self.N [index] += 1
		self.W [index] += value
		self.Q [index] = self.W [index] / self.N [index]

		return
