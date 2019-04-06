from Bidding import possible_bids, POSSIBLE_BID_COUNT, generateBiddings
import numpy as np

_EXPLORE_RATIO_E = 0.25
_DIR_CONSTANT = 0.03

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

	def __init__ (self, bidding, player, p):

		self.player = player
		if player != 0 and player != 2:
			self.legal_bids = [possible_bids.index ("P")]
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

		if len (self.legal_bids) > 1:
			self.P = self.addNoise (p [0])

	def pickMove (self):

		if len (self.legal_bids) == 1:
			return 0

		sqrt_total = np.sqrt (sum (self.N))

		U = []
		for i in range (self.width):
			value = 0
			value += self.Q [i]
			value += sqrt_total * self.P [i] / (1 + self.N [i])
			U.append (value)

		return U.index (max (U))

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
