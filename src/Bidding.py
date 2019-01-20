import json

def getBiddingSystem (filename):

	system = {}
	file = open (filename, "r")
	try:
		system = dict (json.loads (file.read ()))
	except:
		print ("Parsing Error")
	return system

def writeBiddingSystem (filename, system, overwrite = False):

	import os.path
	from pathlib import Path

	if Path (filename).is_file() and not overwrite:
		print ("Cannot Overwrite System")
		return

	file = open (filename, "w")
	json.dumps (system)
	return

def checkKey (sequence):

	temp_arr = sequence.split ("-")

	prev_level = -1
	prev_suit = -1
	suit_conv = {'C': 0, "D": 1, "H": 2, "S": 3, "N": 4}
	rev_suit_conv = ['C', 'D', 'H', 'S', 'N']

	illegal = False
	pass_count = 0
	
	bid = 0
	double = 0
	side = -1

	for i in temp_arr:

		side *= -1
		level = -1
		suit = -1
		
		try:
			if len (i) == 1:
				if i == 'X':
					if bid * side != -1:
						print ("Cannot Double Own Side")
						return False
					else:
						double = side

				if i == 'P':
					pass_count += 1

				if i != 'P' and i != 'X':
					print ("Unrecognizied Token")
					return False

				continue

			if len (i) >= 3:
				print ("Unrecognized Token")
				return False

			if i == 'XX':
				if double == 0:
					print ("Cannot Redouble Undoubled Contract")
					return False
				if double * side != -1:
					print ("Cannot Redouble Own Side")
					return False
				continue

			level = int (i [0])
			suit = suit_conv [i [1]]

		except:
			print ("Unsuccessful Conversion of ", "")
			print (i)
			return False

		if level < prev_level:
			illegal = True

		if level == prev_level and suit < prev_suit:
			illegal = True

		if level > 7 or level < 1:
			print ("Level Too High/Low")
			return False

		if illegal:

			print ("Illegal Bid")
			print ("Previous Bid: ", "")
			print (str(prev_level) + rev_suit_conv[prev_suit])
			print ("Current Bid:", "")
			print (i)

			return False

		prev_suit = suit
		prev_level = level
		bid = side
		double = 0

	return True

