import random
import dds
import functions
import ctypes

vul = 0
first = 0

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

DDS_SUITS = 4
DDS_HANDS = 4

deck = [(D, R2), (D, R3), (D, R4), (D, R5), (D, R6), (D, R7), (D, R8), (D, R9), (D, RT), (D, RJ), (D, RQ), (D, RK), (D, RA),
(C, R2), (C, R3), (C, R4), (C, R5), (C, R6), (C, R7), (C, R8), (C, R9), (C, RT), (C, RJ), (C, RQ), (C, RK), (C, RA),
(H, R2), (H, R3), (H, R4), (H, R5), (H, R6), (H, R7), (H, R8), (H, R9), (H, RT), (H, RJ), (H, RQ), (H, RK), (H, RA),
(S, R2), (S, R3), (S, R4), (S, R5), (S, R6), (S, R7), (S, R8), (S, R9), (S, RT), (S, RJ), (S, RQ), (S, RK), (S, RA)]

ret_arr = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

DDdeal = dds.ddTableDeal ()
DDresults = dds.ddTableResults ()
line = ctypes.create_string_buffer(80)
pres = dds.parResults()

def Gen_Hand ():
	random.shuffle (deck)

	for i in range (dds.DDS_HANDS):
		for j in range (dds.DDS_SUITS):
			DDdeal.cards [i][j] = 0
			ret_arr [i][j] = 0

	hand = 0
	counter = 0
	for (suit, rank) in deck:
		DDdeal.cards [hand][suit] |= rank
		ret_arr [hand][suit] |= rank
		counter += 1
		if counter == 13:
			hand += 1
			counter = 0

	dds.SetMaxThreads(0)
	res = dds.CalcDDtable (DDdeal, ctypes.pointer(DDresults))
	res = dds.Par(ctypes.pointer(DDresults),pres,vul)
	functions.PrintHand (line, DDdeal.cards)
	functions.PrintTable(ctypes.pointer(DDresults))
	functions.PrintPar(ctypes.pointer(pres))
	s = pres.parScore[0].value.decode('utf-8')
	try:
		i = int (s [s.find (" ")+1:])
	except:
		i = 0

	return (ret_arr, i)

for i in range (3):
	Gen_Hand ()