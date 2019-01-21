import json

def getBiddingSystem (filename):

	system = {}
	file = open (filename, "r")
	try:
		system = dict (json.loads (file.read ()))
	except:
		print ("Parsing Error")
		print ("")
	file.close ()
	if system == {}:
		system [""] = ""
	return system

def writeBiddingSystem (filename, system, overwrite = False):

	import os.path
	from pathlib import Path

	if Path (filename).is_file() and not overwrite:
		print ("Cannot Overwrite System")
		return

	file = open (filename, "w")
	file.write (json.dumps (system))
	file.close ()
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

def genBidding (sequence):


	sequence = sequence.translate ({ord(c): None for c in '()'})

	legal_bids = ['P']
	suit_conv = {'C': 0, "D": 1, "H": 2, "S": 3, "N": 4}
	rev_suit_conv = ['C', 'D', 'H', 'S', 'N']

	if sequence == "":
		for i in range (1, 8):
			for j in range (0, 5):
				legal_bids.append (str(i) + rev_suit_conv [j])

		return legal_bids

		# --------------------------------------------------------------

	temp_arr = sequence.split ("-")

	pass_count = 0
	index = -1
	prev_level = -1
	prev_suit = -1

	while temp_arr [index] == "P":
		pass_count += 1
		if pass_count == len (temp_arr):
			for i in range (1, 8):
				for j in range (0, 5):
					legal_bids.append (str(i) + rev_suit_conv [j])
			return legal_bids			
		index -= 1

	if pass_count == 3:
		return

	if (pass_count == 0 or pass_count == 2) and temp_arr [index] != "XX":
		if temp_arr [index] == "X":
			legal_bids.append ("XX")
		else:
			legal_bids.append ("X")

	while temp_arr [index] == "P" or temp_arr [index] == "X" or temp_arr [index] == "XX":
		index -= 1

	try:
		prev_level = int (temp_arr [index][0])
		prev_suit = suit_conv [temp_arr [index][1]]
	except:
		print ("How did this get here?")
		print (temp_arr [index])

	if prev_suit != 4:
		for i in range (prev_suit + 1, 5):
			legal_bids.append (str (prev_level) + rev_suit_conv [i])

	prev_level += 1

	for i in range (prev_level, 8):
		for j in range (0, 5):
			legal_bids.append (str (i) + rev_suit_conv [j])

	if (len (temp_arr) % 2 == 0):
		for i in range (1, len (temp_arr), 2):
			temp_arr [i] = "(" + temp_arr [i] + ")"
	else:
		for i in range (0, len (temp_arr), 2):
			temp_arr [i] = "(" + temp_arr [i] + ")"


	output = []
	for i in legal_bids:
		output.append ("-".join (temp_arr) + "-" + i)

	return output

def fillBiddingSystem (filename):
	
	system = getBiddingSystem (filename)
	biddings = []

	for key in system.keys ():
		biddings = biddings + genBidding (key)

	for bid in biddings:
		if bid in system.keys ():
			continue

		valid = False

		while not valid:

			valid = True

			output = ""
			print ("\033c")
			print (bid)
			meaning = input ("What suit is this bidding about? (Blank for nothing special, B for Balance hand, STR for Strength, R for Relay, PC for P/C, F for forcing)\n")
		
			if meaning == "":
				system [bid] = ""
				break

			if meaning == "PC":
				system [bid] = "P/C"
				break

			if meaning == "R":
				system [bid] = "Relay"
				break

			if "f" in meaning or "F" in meaning:
				output = output + "Forcing; "

			meaning = meaning.translate ({ord(c): None for c in 'fF'})

			if meaning == "STR" or meaning == "str":
				integer = False
				low = -1
				high = -1

				while not integer:
					try:
						i1 = input ("What is the lower range of hcp?\n")
						i2 = input ("What is the higher range of hcp?\n")
						if i1 != "":
							low = int (i1)
						else:
							low = -1
						if i2 != "":
							high = int (i2)
						else:
							high = -1
						integer = True
					except:
						integer = False

				if low == -1 and high == -1:
					system [bid] = output
				else:
					if low == -1:
						system [bid] = output + str (high) + "- HCP"
						break
					if high == -1:
						system [bid] = output + str (low) + "+ HCP"
						break
					if low == high:
						system [bid] = output + str (high) + " HCP"
					else:
						system [bid] = output + str (low) + "-" + str (high) + " HCP"
														
				break

			for c in meaning:
				if c not in ['b','c','d','h','s','B','C','D','H','S','/']:
					valid = False
					break
				if c == "/":
					integer = False
					low = -1
					high = -1

					if valid:
						while not integer:
							try:
								i1 = input ("What is the lower range of hcp?\n")
								i2 = input ("What is the higher range of hcp?\n")
								if i1 != "":
									low = int (i1)
								else:
									low = -1
								if i2 != "":
									high = int (i2)
									print (high)
								else:
									high = -1
								integer = True
							except:
								integer = False

						if low == -1 and high == -1:
							output = output
						else:
							if low == -1:
								output = output + str (high) + "- HCP"
								break
							if high == -1:
								output = output + str (low) + "+ HCP"	
								break
							if low == high:
								output = output + str (high) + " HCP"
							else:
								output = output + str (low) + "-" + str (high) + " HCP"								
						
					output = output + " OR "
										
					continue

				if c == "B" or c == "b":
					output = output + "BAL, "
				else:
					suit = ""
					if c == "S" or c == "s":
						suit = "Spades"
					if c == "C" or c == "c":
						suit = "Clubs"
					if c == "D" or c == "d":
						suit = "Diamonds"
					if c == "H" or c == "h":
						suit = "Hearts"

					integer = False
					low = -1
					high = -1

					while not integer:
						try:
							# print ("\033c")
							i1 = input ("What is the lowest no. of " + suit + "?\n")
							i2 = input ("What is the highest no. of " + suit + "?\n")
							if i1 != "":
								low = int (i1)
							else:
								low = -1
							if i2 != "":
								high = int (i2)
							else:
								high = -1
							integer = True
							if low == -1 and high == -1:
								print ("Cannot Provide No Information!")
								integer = False
						except:
							integer = False

						if low == -1:
							output = output + str (high) + "- " + c.upper () + ", "
							break
						if high == -1:
							output = output + str (low) + "+ " + c.upper () + ", "
							break
						if low == high:
							output = output + str (high) + c.upper () + ", "
						else:
							output = output + str (low) + "-" + str (high) + " " + c.upper () + ", "
								

			integer = False
			low = -1
			high = -1

			if valid:
				while not integer:
					try:
						i1 = input ("What is the lower range of hcp?\n")
						i2 = input ("What is the higher range of hcp?\n")
						if i1 != "":
							low = int (i1)
						else:
							low = -1
						if i2 != "":
							high = int (i2)
						else:
							high = -1
						integer = True
					except:
						integer = False

				if low == -1 and high == -1:
					output = output
				else:
					if low == -1:
						output = output + str (high) + "- HCP"
						break
					if high == -1:
						output = output + str (low) + "+ HCP"
						break
					if low == high:
						output = output + str (high) + " HCP"
					else:
						output = output + str (low) + "-" + str (high) + " HCP"

			system [bid] = output

		writeBiddingSystem (filename = filename, system = system, overwrite = True)
	return

_biddingFilename = "../data/Bidding"
fillBiddingSystem (_biddingFilename)