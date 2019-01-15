from Header import dbitMapRank

def decodeGameRecord (line, inputMode, outputMode):
	temp_arr = line.split ("|")
	hand_list = list (map (int, temp_arr [0].split (",")))
	result_list = list (map (int, temp_arr [1].split (",")))
	hand_ret = []
	res_ret = -1
	# =======================================
	if inputMode == "Full":
		for cards in hand_list:
			for bits in dbitMapRank:
				if bits & cards:
					hand_ret.append (1)
				else:
					hand_ret.append (0)
	else:
		print ("Input Mode Error.")
		return ([], -1)
	# =======================================
	if outputMode == "NT_by_N":
		res_ret = result_list [16]
	else:
		print ("Output Mode Error.")
		return ([], -1)
	return (hand_ret, res_ret)


def getData (filename, dataSize, inputMode, outputMode):

	hand = []
	res = []

	dealFile = open (filename, "r")

	counter = 0
	for line in dealFile:
		
		(one_hand, one_res) = decodeGameRecord (line, inputMode = inputMode, outputMode = outputMode)
		if one_hand == [] or one_res == -1:
			print ("Unsuccessful Decode.")
			return ([], [])

		hand.append (one_hand)
		res.append (one_res)

		counter += 1
		if counter == dataSize:
			break

	return (hand, res)

import os.path
from pathlib import Path

def unclash (name, extension):
	
	counter = 0
	filepath = Path (name + "_" + str(counter) + extension)

	while filepath.is_file():
		counter += 1
		filepath = Path (name + "_" + str (counter) + extension)

	return (name + "_" + str (counter) + extension)