from keras.models import Sequential
import numpy as np
import random
from Bidding import checkCompetitiveSequence, possible_bids, POSSIBLE_BID_COUNT
from Helper import toString

STAT_SIZE = 18

class Agent:

	def __init__ (self, network, bidding_base):

		self.network = network
		self.bidding_base = bidding_base
		self.inputHistory = []
		self.outputHistory = []
		self.moveHistory = []
		return

	def setCoefficient (self, alpha, explore_ratio):
		self.alpha = alpha
		self.explore_ratio = explore_ratio
		return

	def setStat (self):
		count = [0, 0, 0, 0]
		H_count = [0, 0, 0, 0, 0, 0]
		C_count = [0, 0, 0, 0, 0, 0, 0, 0]

		suit_counter = 0
		card_counter = 0
		for card in self.hand:
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

	def setHand (self, hand):
		self.hand = hand
		self.stat = self.setStat ()
		self.inputHistory = []
		self.outputHistory = []
		self.moveHistory = []
		return

	def updateStat (self, bids):
		key = toString (bids)
		if key in self.bidding_base.keys ():
			temp2 = list (map (lambda x: x * (1-self.alpha), self.stat))
			temp1 = list (map (lambda x: x * self.alpha, self.bidding_base [key]))
			temp3 = list (zip (temp1, temp2))
			self.bidding_base [key] = list (map (lambda x: x[0] + x[1], temp3))
		else:
			self.bidding_base [key] = self.stat
		return

	def biddingBase (self):
		return self.bidding_base

	def feedback (self):
		return (self.inputHistory, self.outputHistory, self.moveHistory)

	def calcStat (self, stats, player):
		res = []
		for i in range (player + 1, 4):
			for j in range (STAT_SIZE):
					res.append (stats [i * STAT_SIZE + j])
		for i in range (0, player):
			for j in range (STAT_SIZE):
					res.append (stats [i * STAT_SIZE + j])
		
		for j in range (STAT_SIZE):
			each = -1
			for i in range (3):
				known = self.stat [j]
				unknown_count = 0
				total = -1
				if res [i * STAT_SIZE + j] != -1:
					known += res [i * STAT_SIZE + j]
				else:
					unknown_count += 1
				if unknown_count != 0:
					if j < 10:
						total = 4
					else:
						total = 1
					total -= known
					if total < 0:
						total = 0
					each = total / unknown_count
			if each != -1:
				for i in range (3):
					if res [i * STAT_SIZE + j] == -1:
						res [i * STAT_SIZE + j] = each

		return res

	def one_hot_encode (self, bids):
		indices = []
		res = np.zeros (POSSIBLE_BID_COUNT * 3)
		for bid in bids [-3:]:
			indices.append (possible_bids.index (bid))
		base = 3 - len (indices)
		for i in range (len (indices)):
			res [indices [i] + POSSIBLE_BID_COUNT * (base + i)] = 1
		return list (res)

	def getBid (self, prev_bid, y):
		legal_bids = list (range (POSSIBLE_BID_COUNT))
		for i in range (POSSIBLE_BID_COUNT):
			temp_list = prev_bid.copy ()
			temp_list.append (possible_bids [i])
			if not checkCompetitiveSequence (temp_list):
				legal_bids.remove (i)
		cumulative = []
		display = []
		total = 0
		for index in legal_bids:
			if y [index] == 0:
				total += self.explore_ratio
			else:
				total += y [index]
			cumulative.append (total)
			display.append (str (y[index])[:4])
		print ("Output\n", display)
		pick = random.uniform (0, total)
		i = 0
		while pick > cumulative [i]:
			i += 1
		self.moveHistory.append ((legal_bids [i], legal_bids))
		return possible_bids [legal_bids [i]]

	def move (self, state):
		(stats, bids, player) = state
		x = self.hand.copy ()
		x = x + self.calcStat (stats, player)
		x = x + self.one_hot_encode (bids)
		x = np.asarray ([x])
		y = self.network.predict (x)
		self.inputHistory.append (x[0])
		self.outputHistory.append (y[0])
		bid = self.getBid (bids, y[0])
		return bid