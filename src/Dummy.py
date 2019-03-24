from keras.models import Sequential
import numpy as np
import random
from Bidding import checkCompetitiveSequence, possible_bids, POSSIBLE_BID_COUNT
from Helper import toString

STAT_SIZE = 18

class Dummy:

	def __init__ (self):
		return

	def setCoefficient (self, alpha, explore_ratio):
		return

	def setStat (self):
		return (count + H_count + C_count)

	def setHand (self, hand):
		return

	def updateStat (self, bids):
		return

	def biddingBase (self):
		return {}

	def feedback (self):
		return (self.inputHistory, self.outputHistory, self.moveHistory)

	def move (self, state):
		return "P"