import json

def getBiddingSystem (filename):

	system = {}
	import os
	if os.path.getsize (filename) == 0:
		return system

	file = open (filename, "r")
	try:
		system = dict (json.loads (file.read ()))
	except:
		print ("Parsing Error")
		print ("")
	file.close ()

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

#Unreviewed#
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
#Unreviewed#

def getOpenings ():

	legal_bids = []
	rev_suit_conv = ['C', 'D', 'H', 'S', 'N']
	for i in range (1, 8):
		for j in range (0, 5):
			legal_bids.append (str (i) + rev_suit_conv [j])

	return legal_bids

def genBidding (sequence, mode):

	legal_bids = []

	if mode == "Uncontested":
		print ("Line 124")
	
	if mode == "Competitive":
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
	index = -1

		# --------------------------------------------------------------

	if mode == "Uncontested":
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

		output = []
		for i in legal_bids:
			output.append ("-".join (temp_arr) + "-" + i)

		return output

		# --------------------------------------------------------------

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

def fillBiddingSystem (filename, mode):
	
	system = getBiddingSystem (filename)
	biddings = []

	if system == {}:
		biddings = getOpenings ()
	else:
		for key in system.keys ():
			if system [key] != "":
				biddings = biddings + genBidding (key, mode)

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

def fillOpening (filename):

	system = getBiddingSystem (filename)
	biddings = getOpenings ()

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
							print ("\033c")
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

def fillSystem (system, biddings, filename):

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
					output = output + ", BAL"
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
							print ("\033c")
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
							output = output + str (high) + "- " + c.upper ()
							break
						if high == -1:
							output = output + str (low) + "+ " + c.upper ()
							break
						if low == high:
							output = output + str (high) + c.upper ()
						else:
							output = output + str (low) + "-" + str (high) + " " + c.upper ()
						
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
					if low != -1 and high != -1:
						if low == high:
							output = output + ", " + str (high) + " HCP"
						else:
							output = output + ", " + str (low) + "-" + str (high) + " HCP"
					else:
						if low == -1:
							output = output + ", " + str (high) + "- HCP"
						if high == -1:
							output = output + ", " + str (low) + "+ HCP"

			system [bid] = output
			writeBiddingSystem (filename = filename, system = system, overwrite = True)
	return

def concPrevBid (prevBid, mode):
	
	output = ""
	counter = 0
	
	if mode == "Uncontested":
		for bid in prevBid:
			output = output + bid
			counter += 1
			if counter == 2:
				counter = 0
				output = output + "\n"
			else:
				output = output + "-"
		return output

	length = len (prevBid)
	bracket = False

	if length % 2 == 1:
		bracket = True

	if mode == "Competitive":
		for bid in prevBid:
			if bracket:
				output = output + "(" + bid + ")"
			else:
				output = output + bid
			counter += 1
			if counter == 4:
				counter = 0
				output = output + "\n"
			else:
				output = output + "-"
		return output

	if mode != "Competitve" and mode != "Uncontested":
		print ("concPrevBid - Mode Error")
		return ""

def getHCP (header):

	integer = False
	output = ""
	low = -1
	high = -1

	while not integer:
		print (header)
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
		if high < low:
			integer = False

	if low == -1 and high == -1:
		return output
	else:
		if low == -1:
			return (str (high) + "- HCP")
		if high == -1:
			return (str (low) + "+ HCP")
		if low == high:
			return (str (high) + " HCP")
		return (str (low) + "-" + str (high) + " HCP")


def getCTRL (header, meaning):
	return

def getKC (header, meaning):
	return

def correctMeaning (meaning):

	if r in meaning or R in meaning:
		if len (meaning) != 1:
			return False
		else:
			return True

	bracket_counter = 0
	exclusive_counter = 0
	p_flag = False

	counter = 0

	for token in meaning:

		if token not in ["C","D","H","S", "c","d","h","s", "q","Q", ".", "A","a", "K","k", "B","b", "!", "F","f", "P","p", "(",")","/"]:
			return False
		
		if p_flag and (token != "c" or token != "C"):
			return False
		
		if token == "F" or token == "f":
			exclusive_counter += 1

		if token == "P" or token == "p":
			exclusive_counter += 1
			p_flag = True

		if exclusive_counter >1:
			return False

		if token == "(":
			bracket_counter += 1

		if token == ")":
			bracket_counter -= 1
			if bracket_counter < 0:
				return False

		counter += 1

	if bracket_counter > 0:
		return False


	pair = findBrackets (meaning)

	if pair == []:
		return correctSubToken (meaning)

	pair = pair.sort (reverse = True)
	new_meaning = ""

	for (o, c) in pair:
		if not correctSubMeaning (meaning [o+1, c]):
			return False
		new_meaning = meaning [:o]
		for i in range (o, c+1):
			new_meaning +=  "*"
		new_meaning += meaning [c+1:]
		meaning = new_meaning

	return True

def correctSubMeaning (meaning):

	meaning = meaning.upper ()
	counter = {"C": 0,"D": 0,"H": 0,"S": 0,"Q": 0,".": 0,"A": 0,"K": 0,"B": 0, "!": 0}
	p_flag = False

	for token in meaning:
		if token == "C" and p_flag:
			p_flag = False
			continue
		if token == "P":
			p_flag = True
			continue
		p_flag = False
		if token in counter.keys:
			counter [token] += 1
			if counter [token] > 1:
				return False

	return True

def translateMeaning (meaning):

	output = ""
	p_flag = False

	for token in meaning:
		if token == "F" or token == "f":
			continue
		if p_flag:
			if token == "c" or token == "C":
				output += "V"
				continue
			print ("How is this here? Error -- Translate Meaning")
		if token == "P" or token == "p":
			if p_flag:
				print ("How is this here? Error -- Translate Meaning")
			else:
				p_flag = True
				continue

		output += token

	if output [0] == "(" and output [-1] == "(":
		return output [1:-1]
	return output

def findBrackets (meaning):
	
	open_brac = []
	close_brac = []
	counter = 0

	for token in meaning:
		if token == "(":
			open_brac.append (counter)
		if token == ")":
			close_brac.append (counter)

	pair = []
	temp = (-1, -1)
	temp_o = -1

	for c in close_brac:
		for o in open_brac:
			if o < c:
				temp = (o, c)
				temp_o = o
			else:
				break
		pair.append (temp)
		open_brac.remove (temp_o)

	return pair

def combine (prevBidStr, bid, mode):
	return (prevBidStr + bid)

def translateToken (token):
	if meaning == "R" or meaning == "r":
		return "Relay"
	if token == "F" or "f":
		return "Forcing"
	return output

def fillBid (system, prevBidStr, bid, mode):
	
	header = "\033c\nLegend:	R = Relay, F = Forcing, PC = Pass/Correct\n	B = BAL, ! = Strength\n	Q = Cue, K = Keycard, . = HCP,　A = CTRL\nPrevious bid:	"
	header = header + prevBidStr + "Bid:		" + bid + "\n"
	fullBid = combine (prevBidStr, bid, mode)

	if fullBid in system.keys:
		while True:
			print (header)
			print ("Meaning:		" + system [prevBidStr])
			cont = input ("Do you wish to overwrite?")
			if cont == "n" or cont == "N":
				return
			if cont == "Y" or cont == "y":
				break

	while True:

		print (header)
		meaning = input ("What is this bidding about?\n")

		if not correctMeaning (meaning):
			continue

		if meaning == "":
			return

		meaning = translateMeaning (meaning)
		submeanings = getSubMeaning (meaning)
		sub_dict = {}
		for (d, o, c) in submeanings:
			sub_dict [(o, c)] = getMeaning (meaning [o+1: c], sub_dict)
			
def findSlashes (meaning):
	indices = []
	index = 0
	for token in meaning:
		if token == "/";
			indices.append (index)
		index += 1
	return indices

def getSubMeaning (meaning):

	brackets = findBrackets (meaning)
	slashes = findSlashes (meaning)
	brackets.sort ()
	submeanings = []

	for slash in slashes:
		temp = (-1, -1, -1)
		for (o, c) in brackets:
			if o < slash and c > slash:
				temp = (c-o, o, c)
		if temp != (-1, -1, -1):
			submeanings.append (temp)
		else:



	submeanings.sort ()
	return submeanings

def getMeaning (meaning, sub_dict):

	output = ""
	counter = 0
	open_dict = {}
	for (o, c) in sub_dict:
		open_dict [o] = c

	while counter < len (meaning) - 1:
		token = meaning [counter]
		counter += 1
		if counter in open_dict.keys ():
			c = open_dict [o]
			counter = c+1
			output += sub_dict [(o, c)]
		if token 




or ge 1 side have 2 and-ed tokens need print bracket




		



inputFilename = "../data/Bidding/Opening"
outputFilename = "../data/Bidding/Responses"
system = getBiddingSystem (inputFilename)
outputSystem = getBiddingSystem (outputFilename)

for key in system.keys ():
	if key == "1S":
		bidding = genBidding (key, "Uncontested")
		fillSystem (outputSystem, bidding, outputFilename)

# _biddingFilename = "../data/Bidding/Opening"
# fillOpening (_biddingFilename)
# fillBiddingSystem (_biddingFilename, "Uncontested")