#! /usr/bin/python

import dds
import hands
import functions
import ctypes
import random

dds.SetMaxThreads(0)

# --- Static Definitions --- #

S = 0
H = 1
D = 2
C = 3

R2 = 0x0004
R3 = 0x0008
R4 = 0x0010
R5 = 0x0020
R6 = 0x0040
R7 = 0x0080
R8 = 0x0100
R9 = 0x0200
RT = 0x0400
RJ = 0x0800
RQ = 0x1000
RK = 0x2000
RA = 0x4000

ranks = [RA, RK, RQ, RJ, RT, R9, R8, R7, R6, R5, R4, R3, R2]

deck = [(D, R2), (D, R3), (D, R4), (D, R5), (D, R6), (D, R7), (D, R8), (D, R9), (D, RT), (D, RJ), (D, RQ), (D, RK), (D, RA),
(C, R2), (C, R3), (C, R4), (C, R5), (C, R6), (C, R7), (C, R8), (C, R9), (C, RT), (C, RJ), (C, RQ), (C, RK), (C, RA),
(H, R2), (H, R3), (H, R4), (H, R5), (H, R6), (H, R7), (H, R8), (H, R9), (H, RT), (H, RJ), (H, RQ), (H, RK), (H, RA),
(S, R2), (S, R3), (S, R4), (S, R5), (S, R6), (S, R7), (S, R8), (S, R9), (S, RT), (S, RJ), (S, RQ), (S, RK), (S, RA)]

# --- Allocate Memories --- #

def genDeal ():
	random.shuffle (deck)
	dl = dds.deal ()

	dl.currentTrickSuit[0] = 0
	dl.currentTrickSuit[1] = 0
	dl.currentTrickSuit[2] = 0

	dl.currentTrickRank[0] = 0
	dl.currentTrickRank[1] = 0
	dl.currentTrickRank[2] = 0	

	for h in range (dds.DDS_HANDS):
		for s in range (dds.DDS_SUITS):
			dl.remainCards[h][s] = 0

	hand = 0
	counter = 0
	for (suit, rank) in deck:
		dl.remainCards [hand][suit] |= rank
		counter += 1
		if counter == 13:
			hand += 1
			counter = 0

	return dl

def getDealFromPreset (handno):
	dl = dds.deal ()

	dl.currentTrickSuit[0] = 0
	dl.currentTrickSuit[1] = 0
	dl.currentTrickSuit[2] = 0

	dl.currentTrickRank[0] = 0
	dl.currentTrickRank[1] = 0
	dl.currentTrickRank[2] = 0

	for h in range(dds.DDS_HANDS):
	    for s in range(dds.DDS_SUITS):
	        dl.remainCards[h][s] = hands.holdings[handno][s][h]

	return dl

def getPar (dl):

	target = -1
	mode = 0
	solutions = 2
	threadIndex = 0

	trump = [0,1,2,3,4]
	decl = [0,1,2,3]
	first = [1,2,3,0]
	vul = 1

	fut2 = dds.futureTricks ()
	# line = ctypes.create_string_buffer (80)
	DDtable = dds.ddTableResults()
	pres = dds.parResults ()

	result = []

	for t in trump:
		for d in decl:

			dl.trump = t
			dl.first = first [d]

			# print (t, d)
			res = dds.SolveBoard(dl, target, solutions, mode, ctypes.pointer(fut2), threadIndex)
			# functions.PrintFut(line, ctypes.pointer(fut2))

			maxScore = -1
			# print (maxScore)
			for i in range (fut2.cards):
				if fut2.score [i] > maxScore:
					maxScore = fut2.score [i]
					# print (i, maxScore)
			# print (maxScore)
			result.append (13 - maxScore)
			DDtable.resTable [t][d] = 13 - maxScore

	# print (result)
	res = dds.Par(ctypes.pointer(DDtable),pres,vul)
	s = pres.parScore[0].value.decode('utf-8')
	try:
		parValue = int (s [s.find (" ")+1:])
	except:
		parValue = 0

	# print (parValue)
	return (parValue, result)

def getHand (dl):
	return_list = []
	for h in range (dds.DDS_HANDS):
		temp_list = []
		for s in range (dds.DDS_SUITS):
			card = dl.remainCards[h][s]
			for r in ranks:
				if r & card:
					temp_list.append (1)
				else:
					temp_list.append (0)
		return_list.append (temp_list)
	return return_list

def printHand (dl):
	line = ctypes.create_string_buffer(80)
	functions.PrintHand (line, dl.remainCards)
	return