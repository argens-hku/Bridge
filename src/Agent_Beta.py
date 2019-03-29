from keras.models import Sequential
import numpy as np
import random
from Bidding import checkCompetitiveSequence, possible_bids, POSSIBLE_BID_COUNT
from Helper import toString

STAT_SIZE = 18
_DEBUG = 0

class Agent_Beta:

	def __init__ (self, network, bidding_base, explore_ratio):

		self.network = network
		self.bidding_base = bidding_base
		self.explore_ratio = explore_ratio
		self.visit_count = list (0 for i in range (POSSIBLE_BID_COUNT))
		self.value = -10000
		self.children = list (None for i in range (POSSIBLE_BID_COUNT))
		self.values = list (0 for i in range (POSSIBLE_BID_COUNT))
		self.selfVisitValue = 0
		self.updated = False
		self.childUpdated = False
		self.ratio = []
		return

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
		res = np.zeros (POSSIBLE_BID_COUNT * 10)
		for bid in bids [-10:]:
			indices.append (possible_bids.index (bid))
		base = 10 - len (indices)
		for i in range (len (indices)):
			res [indices [i] + POSSIBLE_BID_COUNT * (base + i)] = 1
		return list (res)

	def setState (self, state, hand):
		(stats, bids, player) = state
		self.prev_bid = bids
		self.player = player
		self.stat = stats [STAT_SIZE * player : STAT_SIZE * (player + 1)]

		legal_bids = list (range (POSSIBLE_BID_COUNT))
		for i in range (POSSIBLE_BID_COUNT):
			temp_list = bids.copy ()
			temp_list.append (possible_bids [i])
			if not checkCompetitiveSequence (temp_list):
				legal_bids.remove (i)
		self.legal_bids = legal_bids

		x = hand.copy ()
		x = x + self.calcStat (stats, player)
		x = x + self.one_hot_encode (bids)
		self.X = np.asarray ([x])
		return

	def updateRatio (self):

		minimum = min (self.values)
		second_min = max (self.values)
		for value in self.values:
			if value < second_min and value != minimum:
				second_min = value
		ratio = []
		if minimum != 0 and second_min != minimum:
			second_min -= minimum
			for value in self.values:
				ratio.append ((value - minimum + self.explore_ratio) / second_min)
		self.ratio = ratio
		for child in self.children:
			if child != None:
				child.updated = False
		return

	def getBid (self, y):

		cumulative = []
		display = []
		total = 0
		if self.childUpdated:
			self.updateRatio ()

		for index in self.legal_bids:
			if self.ratio != []:
				rat = self.ratio [index]
			else:
				rat = 1
			if y [index] == 0:
				total += self.explore_ratio * rat
			else:
				total += y [index] * rat
			cumulative.append (total)
			display.append (possible_bids [index] + " " + str (cumulative [len (cumulative) - 1] - cumulative [len (cumulative) - 2])[:4])
		if _DEBUG > 1 and self.prev_bid == [] and self.childUpdated:		
			self.childUpdated = False
			print ("Agent_Open_Hand_Output\n", display)
		pick = random.uniform (0, total)
		i = 0
		while pick > cumulative [i]:
			i += 1
		return self.legal_bids [i]

	def quickMove (self):
		self.selfVisitValue += 1
		accepted = False
		visit_total = 0
		for visit in self.visit_count:
			visit_total += visit
		while not accepted:
			y = self.network.predict (self.X)
			bid = self.getBid (y[0])
			if self.visit_count [bid] != 0:
				acceptance = np.sqrt (np.sqrt (1/self.visit_count [bid])) * self.values [bid]
				if acceptance <= 0:
					acceptance = self.explore_ratio
				if random.random () < acceptance:
					accepted = True
			else:
				accepted = True
			
		self.visit_count [bid] += 1
		return possible_bids [bid]

	def updateValues (self, value):
		maximum = self.value
		for i in range (len(self.children)):
			child = self.children [i]
			if child != None and child.updated:
				childUpdated = True
				self.values [i] = child.value
				if child.value > maximum:
					maximum = child.value
		if self.value != maximum:
			self.value = maximum
			self.updated = True
		if self.value == -10000:
			self.value = value
		return


