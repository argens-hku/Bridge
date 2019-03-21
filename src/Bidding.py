_debug_level = 0

#--------- Low Tier Functions ----------#

def clearScreen ():
	print ("\033c")

def sequenceToKey (sequence):

	output = ""
	for bid in sequence:
		output += (bid + "-")
	return output [:-1]

def padBid (bid, bracket = False):

	pad = ""

	if len (bid) == 1:
		pad = " "

	if bracket:
		return "(" + bid + ")" + pad
	return bid + pad

def sequenceToString (sequence, mode):

	if mode == "Uncontested":

		output = ""
		counter = 0

		for bid in sequence:
			output += padBid (bid)
			counter += 1
			if counter == 2:
				counter = 0
				output += "\n"
			else:
				output += "-"

		return output [:-1]

	if mode == "Competitive":

		output = ""
		
		if len (sequence) % 2 == 1 and len (sequence) > 3:
			brac_flag = True
			counter = 1
			output += "   "
		else:
			brac_flag = False
			counter = 0

		for bid in sequence:
			

			if brac_flag:
				output += padBid (bid, True)
			else:
				output += padBid (bid)

			brac_flag = not brac_flag
			counter += 1

			if counter == 4:
				counter = 0
				output += "\n"
			else:
				output += "-"

		return output [:-1]

	if _debug_level >= 2:
		print ("Unsupported Mode -- sequenceToString")
	return ""

def getLegend ():

	legend = align ("Legend:") + "R = Relay, F = Forcing, PC = Pass/Correct\n" + align ("") + "B = BAL, ! = Strength\n" + align ("") + "Q = Cue, K = Keycard, . = HCP,　A = CTRL"
	return legend

def readSystem (filename):

	import os
	import json
	system = {}

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

def writeSystem (filename, system, overwrite = False):

	import os.path
	from pathlib import Path
	import json

	if Path (filename).is_file() and not overwrite:
		print ("Cannot Overwrite System")
		return

	file = open (filename, "w")
	file.write (json.dumps (system))
	file.close ()

	return

def checkCompetitiveSequence (sequence):

	prev_level = -1
	prev_suit = -1
	suit_conv = {'C': 0, "D": 1, "H": 2, "S": 3, "N": 4}
	rev_suit_conv = ['C', 'D', 'H', 'S', 'N']

	pass_count = 0
	contract = 0
	double = 0
	redouble = 0
	side = -1

	illegal = False
	errorMessages = ""
	counter = 0
	passed_out = False

	sequence = list(map (lambda x: x.upper(), sequence))

	for bid in sequence:

		side *= -1
		level = -1
		suit = -1
		counter += 1
		
		if passed_out:
			errorMessages += str(counter) + "-" + bid + ")	" + "Contract already passed out.\n"
			illegal = True

		try:
			if len (bid) == 1:
				if bid == 'X':
					if double != 0:
						errorMessages += str(counter) + "-" + bid + ")	" + "Cannot be 2 consecutive doubles.\n"
						illegal = True

					if redouble != 0:
						errorMessages += str(counter) + "-" + bid + ")	" + "Cannot double redoubled contracts.\n"
						illegal = True

					if contract == 0:
						errorMessages += str(counter) + "-" + bid + ")	" + "Double cannot be first bid.\n"
						illegal = True
					else:
						if contract * side != -1:
							errorMessages += str(counter) + "-" + bid + ")	" + "Cannot double own side.\n"
							illegal = True

					double = side
					redouble = 0
					pass_count = 0

				if bid == 'P':
					pass_count += 1
					if pass_count > 2 and contract != 0:
						passed_out = True
					if pass_count > 3:
						passed_out = True
						if contract != 0:
							errorMessages += str(counter) + "-" + bid + ")	" + "There cannot be 4 consecutive passes.\n"
							illegal = True

				if bid != 'P' and bid != 'X':
					errorMessages += str(counter) + "-" + bid + ")	" + "Unrecognizied Token: " + bid + ".\n"
					illegal = True

					contract = side
					double = 0
					redouble = 0
					pass_count = 0

				continue

			if len (bid) >= 3:
				errorMessages += str(counter) + "-" + bid + ")	" + "Unrecognizied Token: " + bid + ".\n"
				illegal = True
				pass_count = 0
				contract = side
				double = 0
				redouble = 0
				continue

			if bid == 'XX':
				if redouble != 0:
					errorMessages += str(counter) + "-" + bid + ")	" + "Cannot redouble redoubled contract.\n"
					illegal = True
				if double == 0:
					errorMessages += str(counter) + "-" + bid + ")	" + "Cannot redouble undoubled contract.\n"
					illegal = True
				if double * side == 1:
					errorMessages += str(counter) + "-" + bid + ")	" + "Cannot redouble own double.\n"
					illegal = True
				redouble = side
				pass_count = 0
				double = 0
				continue

			pass_count = 0
			contract = side
			double = 0
			redouble = 0
			conversion = True
			level = int (bid [0])
			suit = suit_conv [bid [1]]

		except:
			errorMessages += str(counter) + "-" + bid + ")	" + "Unsuccessful Conversion of: " + bid + ".\n"
			illegal = True
			conversion = False

		if conversion:

			if (level < prev_level) or (level == prev_level and suit < prev_suit):
				errorMessages += str(counter) + "-" + bid + ")	" + "Underbid; Previous bid: " + str(prev_level) + rev_suit_conv[prev_suit] + "\n"
				illegal = True

			if level > 7:
				errorMessages += str(counter) + "-" + bid + ")	" + "Level too high.\n"
				illegal = True

			if level < 1:
				errorMessages += str(counter) + "-" + bid + ")	" + "Level too low.\n"
				illegal = True

			prev_suit = suit
			prev_level = level
	
	if illegal:
		if _debug_level >= 2:
			print (errorMessages, end = "")
		return False
	else:
		return True

def getLastBid (prevBids):

	pass_count = 0

	for bid in reversed (prevBids):
		temp = bid.upper ()
		if temp == "X" or temp == "X" or temp == "XX":
			continue
		if temp == "P":
			pass_count += 1
			continue
		return temp

	if pass_count == len (prevBids):
		return "Empty Sequence"

def getResponse (header, question, background = ""):
	
	if _debug_level == 0:
		clearScreen ()
	print (header)
	if background != "":
		print (background)
	response = input ("\n" + question + "\n")
	return response

def align (string, length = 14):

	output = string
	for i in range (len (string), length):
		output += " "
	return output

def validTokenLevel (response):

	response = response.strip ()

	if "r" in response or "R" in response:
		if len (response) != 1:
			if _debug_level > 2:
				print ("Relay flag cannot have other meanings")
			return (False, "")
		else:
			return (True, response)

	bracket_counter = 0
	exclusive_counter = 0
	p_flag = False
	output = ""

	for token in response:

		token_U  = token.upper ()
		if token_U not in ["C","D","H","S","B", "F","P", "!","Q","K","A", ".","(",")","/","+"]:
			if _debug_level > 2:
				print (token_U)
			return (False, output)
		
		if p_flag:
			if token_U != "C":
				if _debug_level > 2:
					print ("Lone P")
				return (False, "")
			else:
				output += "V"
				p_flag = False
				continue

		if token_U == "F":
			exclusive_counter += 1
			if exclusive_counter >1:
				if _debug_level > 2:
					print ("Too many exclusive Tokens")
				return (False, "")
			output += "F"
			continue

		if token_U == "P":
			exclusive_counter += 1
			p_flag = True
			if exclusive_counter >1:
				if _debug_level > 2:
					print ("Too many exclusive Tokens")
				return (False, "")
			continue

		if token == "(":
			bracket_counter += 1
			output += "("
			continue

		if token == ")":
			bracket_counter -= 1
			if bracket_counter < 0:
				return (False, "")
			output += ")"
			continue

		if token_U in ["C","D","H","S"]:
			output += token
		else:
			output += token_U

	if bracket_counter > 0:
		return (False, "")

	return (True, output)

def findBrackets (response):
	
	open_brac = []
	close_brac = []
	counter = 0

	for token in response:
		if token == "(":
			open_brac.append (counter)
		if token == ")":
			close_brac.append (counter)
		counter += 1

	pairs = []
	temp = (-1, -1)
	temp_o = -1

	for c in close_brac:
		for o in open_brac:
			if o < c:
				temp = (o, c)
				temp_o = o
			else:
				break
		pairs.append (temp)
		open_brac.remove (temp_o)

	if len (open_brac) != 0:
		return (False, [])
	return (True, pairs)

def findExclusive (response):

	index = -1
	for token in response:
		index += 1
		if token.upper () == "V" or token.upper () == "F":
			return index
	return -1

def validLogical (response):

	flag = False

	for token in response:
		if flag and token in ["+", "/", ")"]:
			return False
		if token == "+" or token == "/" or token == "(":
			flag = True
			continue
		flag = False
	return True

def addBracket (response):

	# --- Add Brackets For Token Level And/Or Conflicts --- #

	and_or = []
	or_and = []
	open_brac = []
	close_brac = []
	pairs = findBrackets (response)

	for i in range (1, len (response) - 1):
		left = response [i-1]
		right = response [i+1]
		if left == "+" and right == "/":
			and_or.append (i)
		if left == "/" and right == "+":
			or_and.append (i)

	for index in or_and:
		open_brac.append (index-1)
		close_index = len (response) - 1
		i = index + 2
		while i < len (response) - 1:
			if response [i] == "/" or response [i] == ")":
				close_index = i - 1
				i += 1
				break
			if response [i] == "(":
				for (o, c) in pairs:
					if o == i:
						i = c+1
				continue
			i += 1
		if close_index not in close_brac:
			close_brac.append (close_index)

	for index in and_or:
		if index not in close_brac:
			close_brac.append (index)
		open_index = -1
		i = index - 2
		while i > -1:
			if response [i] == "/" or response [i] == "(":
				open_index = i
				i -= 1
				break
			if response [i] == ")":
				for (o, c) in pairs:
					if c == i:
						i = o-1
				continue
			i -= 1
		if open_index not in open_brac:
			open_brac.append (open_index)

	output = ""
	counter = -1
	for token in response:
		if counter in open_brac:
			output += "("
		output += token
		counter += 1
		if counter in close_brac:
			output += ")"

	response = output

	# --- Add Brackets For Bracket-Level And/Or Conflicts --- #

	(_, pairs) = findBrackets (response)

	and_or = []
	or_and = []
	open_brac = []
	close_brac = []

	for (o, c) in pairs:
		if o <= 0:
			continue
		if c >= len (response) - 1:
			continue
		left = response [o-1]
		right = response [c+1]
		if left == "+" and right == "/":
			and_or.append ((o, c))
		if left == "/" and right == "+":
			or_and.append ((o, c))

	for (o, c) in or_and:
		open_brac.append (o-1)
		close_index = len (response) - 1
		i = c+2
		while i < len (response) - 1:
			if response [i] == "/" or response [i] == ")":
				close_index = i - 1
				i += 1
				break
			if response [i] == "(":
				for (j, k) in pairs:
					if j == i:
						i = k+1
			i += 1
		if close_index not in close_brac:
			close_brac.append (close_index)

	for (o, c) in and_or:
		if c not in close_brac:
			close_brac.append (c)
		open_index = -1
		i = o-2
		while i > -1:
			if response [i] == "/" or response [i] == "(":
				open_index = i
				i -= 1
				break
			if response [i] == ")":
				for (j, k) in pairs:
					if k == i:
						i = j-1
						continue
			i -= 1
		if open_index not in open_brac:
			open_brac.append (open_index)

	output = ""
	counter = -1
	for token in response:
		if counter in open_brac:
			output += "("
		output += token
		counter += 1
		if counter in close_brac:
			output += ")"

	return output

def removeBracket (response):

	removable = []
	(valid, pairs) = findBrackets (response)
	for (o, c) in pairs:
		and_flag = False
		or_flag = False
		i = o + 1
		while i < c:
			if response [i] == "+":
				and_flag = True
			if response [i] == "/":
				or_flag = True
			if response [i] == "(":
				for (j, k) in pairs:
					if i == j:
						i = k+1
						break
				continue
			i += 1

		if and_flag and or_flag:
			if _debug_level != 0:
				print ("Error! translateResponse -- addBracket missing brackets.")
			return False

		if not or_flag and not and_flag:
			removable.append (o)
			removable.append (c)
			continue

		if or_flag:
			removable.append (o)
			removable.append (c)
			continue

		if and_flag:
			i = o-1
			j = c+1
			if i < 0:
				left = "+"
			else:
				left = response [i]
			if j > len (response) - 1:
				right = "+"
			else:
				right = response [j]
			if left == "(":
				left = "+"
			if right == ")":
				right = "+"
			if left == "+" and right == "+":
				removable.append (o)
				removable.append (c)

	counter = 0
	output = ""
	for token in response:
		if counter in removable:
			counter += 1
			continue
		counter += 1
		output += token

	return output

def rearrangeOrResponse (response):

	(_, brackets) = findBrackets (response)

	length = len (response)
	output = ""
	temp_list = []
	temp_arr = []

	i = 0
	while i < len (response):
		if response [i] == "(":
			for (o, c) in brackets:
				if i == o:
					i = c+1
					temp_arr.append (response [o: c+1])
					break
			continue
		if response [i] != "/":
			temp_arr.append (response [i])
		i += 1

	for blob in temp_arr:
		temp_list.append ((len (blob), blob))
	temp_list.sort ()
	for (_, blob) in temp_list:
		output += blob + "/"
	return (length, output [:-1])

def rearrangeAndResponse (tokens, orSequences):

	output = ""
	for token in tokens:
		output += token + "+"

	for (_, sequence) in orSequences:
		output += sequence + "+"

	return output [:-1]

def rearrangeResponse (response):
	
	response = "(" + response + ")"
	(_, pairs) = findBrackets (response)

	for (o, c) in pairs:
		ands = []
		brackets = []
		i = o+1
		while i < c:
			if response [i] == "(":
				for (j, k) in pairs:
					if i == j:
						i = k+1
						brackets.append ((j, k))
						break
				continue
			if response [i] == "+":
				ands.append (i)
			i += 1

		if _debug_level > 2:
			print ("rearrangeResponse -- Intermediate Result (o, c, brackets, ands)", o, c, brackets, ands)

		# --- Handle Slashes --- #
		if ands == []:
			(_, temp) = rearrangeOrResponse (response [o+1:c])
			response = response [0:o] + "(" + temp + ")" + response [c+1:]
			continue

		tokens = []
		orSequences = []
		ands.append (o)
		ands.append (c)
		ands.sort ()

		for i in range (0, len (ands)-1):
			if ands [i+1] - ands [i] == 2:
				tokens.append (response [ands [i]+1])
			else:
				orSequences.append (rearrangeOrResponse (response [ands [i] + 1: ands [i+1]]))

		if _debug_level > 2:
			print ("rearrangeResponse -- Intermediate Result (tokens, orSequences)", tokens, orSequences)

		orSequences.sort ()
		response = response [0:o] + "(" + rearrangeAndResponse (tokens, orSequences) + ")" + response [c+1:]

		# for andIndices in ands:

		# buf = ""
		# avoid_list = []
		# for slash in slashes:
		# 	if (slash - 1) not in avoid_list and (slash + 1) not in avoid_list and buf != "":
		# 		orSequences.append (rearrangeOrResponse (buf))
		# 		buf = ""
		# 	if slash - 1 > -1:
		# 		if response [slash - 1] == ")" and (slash - 1) not in avoid_list:
		# 			for (j, k) in brackets:
		# 				if k == slash - 1:
		# 					buf += response [j:k+1]
		# 					avoid_list += list (range (j, k+1))
		# 					if j - 1 >= 0:
		# 						if response [j-1] == "+":
		# 							avoid_list.append (j-1)
		# 					break
		# 		else:
		# 			buf += response [slash - 1]
		# 			avoid_list.append (slash - 1)
		# 	buf += "/"
		# 	avoid_list.append (slash)
		# 	if slash + 1 < len (response) - 1:
		# 		if response [slash + 1] == "(" and (slash + 1) not in avoid_list:
		# 			for (j, k) in brackets:
		# 				if j == slash + 1:
		# 					buf += response [j:k+1]
		# 					avoid_list += list (range (j, k+1))
		# 					break
		# 		else:
		# 			buf += response [slash + 1]
		# 			avoid_list.append (slash + 1)

		# if buf != "":
		# 	orSequences.append (rearrangeOrResponse (buf))
		# 	buf = ""

		# orSequences.sort ()
		# for (_, seq) in orSequences:
		# 	buf += seq + "+"

		# buf = buf [:-1]

		# if _debug_level >= 3:
		# 	print ("rearrangeResponse -- Intermediate Result (avoid_list, buf)", avoid_list, buf)
		# counter = 0
		# output = ""
		# for token in response:
		# 	if counter not in avoid_list:
		# 		output += token
		# 		counter += 1
		# 	if counter == c or counter == len (response) - 1:
		# 		if buf != "":
		# 			output += buf
		# 			buf = ""
		# response = output


		# buf = ""
		# avoid_list = []
		# lastSlash = -1
		# for slash in slashes:
		# 	lastSlash = slash
		# 	if response [slash - 1] == ")":
		# 		for (j, k) in brackets:
		# 			if k == slash - 1:
		# 				buf += response [j:k+2]
		# 				avoid_list += list (range (j, k +2))
		# 				break
		# 		else:
		# 			avoid_list.append (slash - 1)
		# 			avoid_list.append (slash)
		# 			buf += response [slash - 1 : slash + 1]
		# 	i = lastSlash + 1
		# 	if response [i] ==  "(":
		# 		for (j, k) in brackets:
		# 			if j == i:
		# 				buf += response [j:k+1]
		# 				avoid_list += list (range (j, k + 2))
		# 				break
		# 	else:
		# 		avoid_list.append (i)
		# 		avoid_list.append (i + 1)
		# 		buf += response [i]

		# 	print (buf, avoid_list)
		# 	output = ""
		# 	counter = 0
		# 	copiedFlag = False
			
		# 	for token in response:
		# 		if counter == c:
		# 			output += buf
		# 			copiedFlag = True
		# 		if counter not in avoid_list:
		# 			output += token
		# 		counter += 1
		# 	if not copiedFlag:
		# 		output += buf
		# 	response = output

		if _debug_level >= 3:
			print ("rearrangeResponse -- Result after rearranging slashes.", response)
		# else:
		# 	brackets.sort ()
		# 	avoid_list = []
		# 	buf = []
		# 	for (_, j, k) in brackets:
		# 		if k + 1 < len (response) - 1:
		# 			if response [k+1] == "/":
		# 				avoid_list += list (range (j, k+2))
		# 				buf.append ("/" + response [j:k+1])
		# 				continue
		# 		avoid_list += list (range (j, k+1))
		# 		buf.append ("/" + response [j:k+1])


		# 	print (buf, avoid_list)
		# 	output = ""
		# 	counter = 0
		# 	copiedFlag = False

		# 	for token in response:
		# 		if counter == c:
		# 			output += buf
		# 			copiedFlag = True
		# 		if counter not in avoid_list:
		# 			output += token
		# 		counter += 1
		# 	if not copiedFlag:
		# 		output += buf
		# 	response = output

		# 	if _debug_level >= 3:
		# 		print ("rearrangeResponse -- Result after rearranging brackets.", response)

	return response[1:-1]

#--------- Mid Tier Functions ----------#

def generateBiddings (prevBids, mode):
	
	lastBid = getLastBid (prevBids)
	if mode == "Uncontested" and len (prevBids) >= 1:
		if prevBids [-1].upper () == "P":
			return []

	suit_conv = {'C': 0, "D": 1, "H": 2, "S": 3, "N": 4}
	rev_suit_conv = ['C', 'D', 'H', 'S', 'N']

	level = -1
	suit = -1
	biddings = []
	bid = ""
	errorMessages = ""
	illegal = False

	if lastBid != "Empty Sequence":
		try:
			level = int (lastBid [0])
			suit = suit_conv [lastBid [1]]
		except:
			errorMessages += "Unsuccessful conversion of " + lastBid + "-- generateBiddings.\n"
			illegal = True

		if level < 1 or level > 7:
			errorMessages += "Level too high/low: " + lastBid + "-- generateBiddings.\n"
			illegal = True
	else:
		level = 0
		suit = 5

	if mode != "Competitive" and mode != "Uncontested":
		errorMessages += "Unsupported mode " + mode + "-- generateBiddings.\n"
		illegal = True

	if mode == "Competitive":
		biddings.append ("X")
		biddings.append ("XX")

	biddings.append ("P")

	if illegal:
		if _debug_level:
			print (errorMessages, end = "")
		return []

	if suit != 4:
		for s in range (suit+1, 5):
			bid = str (level) + rev_suit_conv [s]
			biddings.append (bid)
	for l in range (level+1, 8):
		for s in range (0, 5):
			bid = str (l) + rev_suit_conv [s]
			biddings.append (bid)

	if mode == "Uncontested":
		return biddings

	output = []
	for bid in biddings:
		temp_arr = prevBids.copy ()
		temp_arr.append (bid)
		if checkCompetitiveSequence (temp_arr):
			output.append (bid)

	return output

def fillMeaning (prevBid, bid, system, mode):

	header = ""
	header += getLegend () + "\n"
	header += align ("Previous Bid:") + sequenceToString (prevBid, mode) + "\n"
	header += align ("Current Bid:") + bid

	while True:

		# -- Preperational Work -- #
		temp_arr = prevBid.copy()
		temp_arr.append (bid)
		key = sequenceToKey (temp_arr)

		# -- Overwite Guard -- #
		if key in system.keys ():
			if system[key] != "":
				background = align ("Meaning:") + system [key]
				question = "Do you wish to overwrite the above meaning?"
				response = getResponse (header, question, background)
				if response.upper () != "Y" and response.upper () != "YES":
					break

		# -- Get Meaning -- #
		(legal, meaning) = getMeaning (header, temp_arr, mode)
		if _debug_level > -1:
			print (meaning)
		if legal:
			if meaning != "":
				system [key] = meaning
			break
	return

def translateResponse (response):
	
	output = ""
	(valid, response) = validTokenLevel (response)
	if not valid:
		if _debug_level != 0:
			print ("translateResponse -- Token Level Incorrectness")
		return (False, "")

	(valid, pairs) = findBrackets (response)
	if not valid:
		if _debug_level != 0:
			print ("translateResponse -- Bracket Level Incorrectness")
		return (False, "")

	e_index = findExclusive (response)

	for (o, c) in pairs:
		if e_index > o and e_index < c and (o != 0 or c != len (response) - 1):
			if _debug_level != 0:
				print ("translateResponse -- Exclusive token within Bracket")
			return (False, "")

	# --- Add addition signs --- #
	temp_response = ""
	tokenFlag = False
	for token in response:
		if token not in ["+","(","/",")"]:
			if tokenFlag:
				temp_response += "+"
			tokenFlag = True
		else:
			if tokenFlag and token == "(":
				temp_response += "+"
			if token == ")":
				tokenFlag =True
			else:
				tokenFlag = False
		temp_response += token
	response = temp_response
	if not validLogical (response):
		if _debug_level != 0:
			print ("translateResponse -- Illogical")
		return (False, "")

	if _debug_level >= 2:
		print ("Response after adding additions", response)
	# --- Add Necessary Brackets (In Human Language) --- #
	response = addBracket (response)
	if _debug_level >= 2:
		print ("Response after adding brackets", response)
	# --- Remove Extra Brackets --- #
	response = removeBracket (response)
	if _debug_level >= 2:
		print ("Response after removing brackets", response)
	# --- Rearrange Tokens --- #
	response = rearrangeResponse (response)
	if _debug_level >= 2:
		print ("Response after rearranging response", response)

	# 	print 
	return (True, response)

def askMinMax (header, variable, background = ""):

	ans = False
	while True:
		temp_background = background
		output = ""
		minimum = -1
		maximum = -1
		while not ans:
			ans = True
			question = "How many " + variable + " minimum?"
			r = getResponse (header, question, background)
			if r != "":
				try:
					r_int = int (r)
					if r_int < 0:
						ans = False
						continue
				except:
					ans = False
					continue
				minimum = r_int
				temp_background += "\n" + question + " " + str (minimum) + "."
			else:
				temp_background += "\n" + question + " Dunno."

		ans = False
		while not ans:
			ans = True
			question = "How many " + variable + " maximum?"
			r = getResponse (header, question, temp_background)
			if r != "":
				try:
					r_int = int (r)
					if r_int < 0:
						ans = False
						break
				except:
					ans = False
					break
				maximum = r_int

		if not ans:
			continue
			
		if minimum == -1 and maximum == -1:
			ans = False
			continue

		if minimum > maximum and maximum != -1:
			ans = False
			continue

		if minimum == maximum:
			output += str (maximum) + " " + variable
			break

		if maximum == -1:
			output += str (minimum) + "+ " + variable
			break

		if minimum == -1:
			output += str (maximum) + "- " + variable
			break

		output += str (minimum) + "-" +  str (maximum) + " " + variable
		break
	return output

def getFurtherResponse (token, header, response, counter, double_or):

	output = ""
	background = response + "\n"
	for i in range (counter):
		background += " "
	background += "^"

	if token == "Q":
		first_ans = False
		second_ans = False
		positive = False
		suit = ""
		first_round = False
		while True:
			while not second_ans:
				while not first_ans:
					r = getResponse (header, "Positive Cue Bid?", background)
					if r.upper () == "N":
						positive = False
						background += "\nPositive Cue Bid? No."
						first_ans = True
						break
					if r == "" or r.upper () == "Y":
						positive = True
						background += "\nPositive Cue Bid? Yes."
						first_ans = True
						break
				r = getResponse (header, "Which suit is this about?", background)
				if r.upper() == "C":
					suit = "C"
					background += "\nWhich suit is this about? Clubs."
					second_ans = True
					break
				if r.upper() == "D":
					suit = "D"
					background += "\nWhich suit is this about? Diamonds."
					second_ans = True
					break
				if r.upper() == "H":
					suit = "H"
					background += "\nWhich suit is this about? Hearts."
					second_ans = True
					break
				if r.upper() == "S":
					suit = "S"
					background += "\nWhich suit is this about? Spades."
					second_ans = True
					break
			r = getResponse (header, "First or Second Round?", background)
			if r.upper () == "N":
				first_round = True
				break
			if r.upper () == "Y" or r == "":
				first_round = False
				break
		cue = ["A", "K"]	
		if first_round:
			cue.remove ("K")
		if positive:
			cue = list (map (lambda x: suit+x, cue))
			output += (" OR ").join (cue)
		else:
			suit_list = ["C", "D", "H", "S"]
			suit_list.remove (suit)
			temp = []
			for s in suit_list:
				temp += list (map (lambda x: s+x, cue))
			output += (" OR ").join (temp)
		return output
	if token == "K":
		first_ans = False
		second_ans = False
		third_ans = False

		suit = ""
		keycard_count = []
		exclusive = ""
		queen = -1

		while True:
			while not third_ans:
				while not second_ans:
					while not first_ans:
						r = getResponse (header, "Which suit is this about?", background)
						if r.upper() == "C":
							suit = "C"
							background += "\nWhich suit is this about? Clubs."
							first_ans = True
							break
						if r.upper() == "D":
							suit = "D"
							background += "\nWhich suit is this about? Diamonds."
							first_ans = True
							break
						if r.upper() == "H":
							suit = "H"
							background += "\nWhich suit is this about? Hearts."
							first_ans = True
							break
						if r.upper() == "S":
							suit = "S"
							background += "\nWhich suit is this about? Spades."
							first_ans = True
							break
						if r.upper() == "N":
							suit = "N"
							background += "\nWhich suit is this about? NT."
							first_ans = True
							break
					r = getResponse (header, "How many keycards does this represent?", background)
					second_ans = True
					for kc in r:
						try:
							kc_int = int (kc)
							if kc_int < 0 or kc_int > 5:
								keycard_count = []
								second_ans = False
								break
							keycard_count.append (kc_int)
						except:
							keycard_count = []
							second_ans = False
							break
					keycard_count = list (map (lambda x: str(x), keycard_count))
					background += "\nHow many keycards does this represent? " + (" OR ").join (keycard_count)	
				r = getResponse (header, "Trump Queen?", background)
				if r.upper () == "N":
					queen = 0
					third_ans = True
					background += "\nTrump Queen? No."
					break
				if r.upper () == "Y":
					queen = 2
					third_ans = True
					background += "\nTrump Queen? Yes."
					break
				if r.upper () == "":
					queen = 1
					third_ans = True
					background += "\nTrump Queen? Dunno."
					break
			r = getResponse (header, "Exclusive?", background)
			if r.upper () == "N" or r == "":
				exclusive = ""
				break
			if r.upper () == "C":
				exclusive = "C"
				break
			if r.upper () == "D":
				exclusive = "D"
				break
			if r.upper () == "H":
				exclusive = "H"
				break
			if r.upper () == "S":
				exclusive = "S"
				break

		output += (" OR ").join (keycard_count) + " "
		if exclusive != "":
			output += "(" +  exclusive + ")" + "e"
		output += "RKC in " + suit
		if queen == 0:
			output += " w/o Queen"
		if queen == 2:
			output += " w/ Queen"
		return output
	# if token == "A":
		ans = False
		minimum = -1
		maximum = -1
		while True:
			temp_background = background
			while not ans:
				ans = True
				r = getResponse (header, "How many controls minimum?", background)
				if r != "":
					try:
						r_int = int (r)
						if r_int < 0:
							ans = False
							break
					except:
						ans = False
						break
					minimum = r_int
					temp_background += "\nHow many controls minimum? " + str (minimum) + "."
				else:
					temp_background += "\nHow many controls minimum? Dunno."

			ans = False
			while not ans:
				ans = True
				r = getResponse (header, "How many controls maximum?", temp_background)
				if r != "":
					try:
						r_int = int (r)
						if r_int <= 0:
							ans = False
							break
					except:
						ans = False
						break
					maximum = r_int
			
			if not ans:
				continue

			if minimum == -1 and maximum == -1:
				ans = False
				continue

			if minimum > maximum and maximum != -1:
				ans = False
				continue

			if minimum == maximum:
				output += str (maximum) + " Control"
				break

			if maximum == -1:
				output += str (minimum) + "+ Controls"
				break

			if minimum == -1:
				output += str (maximum) + "- Controls"
				break
		return output
	# if token == ".":
		ans = False
		minimum = -1
		maximum = -1
		while True:
			temp_background = background
			while not ans:
				ans = True
				r = getResponse (header, "How many HCP minimum?", background)
				if r != "":
					try:
						r_int = int (r)
						if r_int < 0:
							ans = False
							break
					except:
						ans = False
						break
					minimum = r_int
					temp_background += "\nHow many HCP minimum? " + str (minimum) + "."
				else:
					temp_background += "\nHow many HCP minimum? Dunno."

			ans = False
			while not ans:
				ans = True
				r = getResponse (header, "How many HCP maximum?", temp_background)
				if r != "":
					try:
						r_int = int (r)
						if r_int <= 0:
							ans = False
							break
					except:
						ans = False
						break
					maximum = r_int

			if not ans:
				continue
				
			if minimum == -1 and maximum == -1:
				ans = False
				continue

			if minimum > maximum and maximum != -1:
				ans = False
				continue

			if minimum == maximum:
				output += str (maximum) + " Control"
				break

			if maximum == -1:
				output += str (minimum) + "+ Controls"
				break

			if minimum == -1:
				output += str (maximum) + "- Controls"
				break
		return output
	if token == "A":
		return askMinMax (header, "Control", background)
	if token == ".":
		return askMinMax (header, "HCP", background)

	suit = ""
	if token.upper() == "C":
		suit = "C"
		suit_count = askMinMax (header, "Clubs", background)
		output += suit_count
		background += "\n" + suit_count
	if token.upper() == "D":
		suit = "D"
		suit_count = askMinMax (header, "Diamonds", background)
		output += suit_count
		background += "\n" + suit_count
	if token.upper() == "H":
		suit = "H"
		suit_count = askMinMax (header, "Hearts", background)
		output += suit_count
		background += "\n" + suit_count
	if token.upper() == "S":
		suit = "S"
		suit_count = askMinMax (header, "Spades", background)
		output += suit_count
		background += "\n" + suit_count
	if token in ["C","D","H","S"]:
		while True:
			r = getResponse (header, "Any concrete information on suit honors?", background)
			r = r.upper ()
			if r == "":
				return output
			valid = True
			for h in r:
				if h not in ["A","K","Q","J","+"]:
					valid = False
					break
			if not valid:
				continue
			if "+" not in r:
				output += "; "
				r = list (map (lambda x: suit + x, r))
				s = "; ".join (r)
				output += s
				if double_or:
					output = "(" + output + ")"
				break

			valid = True
			hon_count = {"A": 0, "K": 0, "Q": 0, "J": 0}
			for h in r:
				if h != "+":
					hon_count [h] += 1
					if hon_count [h] > 1:
						valid = False
						break
			if not valid:
				continue

			hon_conv = ["J", "Q", "K", "A"]
			rev_conv = {"A": 3, "K": 2, "Q": 1, "J": 0}
			if len (r) == 2:
				try:
					score = rev_conv [r[0]]
				except:
					continue
				arr = []
				for s in range (score, 4):
					arr.append (suit + hon_conv [s])
				percent = str (1/len (arr)*100)
				loc = percent.find (".")
				if loc != -1:
					percent_trunc = percent [0:loc]
				else:
					percent_trunc = percent
				output += "; " + percent_trunc + "% "
				output += ("; " + percent_trunc + "% ").join (arr)
				if double_or:
					output = "(" + output + ")"
				break

			# ---- Complicated + Case ----- #

			arr = []
			for key in hon_count.keys ():
				if hon_count [key] != 0:
					arr.append (rev_conv[key])
			arr.sort (reverse = True)
			token_arr = []
			for j in arr:
				temp_arr = []
				for i in range (3, j-1, -1):
					temp_arr.append (hon_conv[i])
				token_arr.append (temp_arr)

			result_arr = []
			for arr in token_arr:
				if result_arr == []:
					result_arr = arr
				else:
					temp_arr = []
					for r in result_arr:
						for t in arr:
							if rev_conv [r[-1]] > rev_conv [t]:
								temp_arr.append (r+t)
					result_arr = temp_arr

			hon_count = {"A": 0, "K": 0, "Q": 0, "J": 0}
			total = len (result_arr)
			for case in result_arr:
				if "A" in case:
					hon_count ["A"] += 1
				if "K" in case:
					hon_count ["K"] += 1
				if "Q" in case:
					hon_count ["Q"] += 1
				if "J" in case:
					hon_count ["J"] += 1

			for key in hon_count.keys ():
				hon_count [key] = hon_count [key] / total * 100
				temp = str (hon_count [key])
				loc = temp.find (".")
				hon_count [key] = temp [0:loc]

			output_arr = []
			for i in range (3, -1, -1):
				hon = hon_conv [i]
				if hon_count [hon] != "0":
					output_arr.append (hon_count [hon] + "% " + suit + hon)

			output += "; " + "; ".join (output_arr)
			if double_or:
				output = "(" + output + ")"
			break

		return output
	else:
		if token not in ["c","d","h","s"]:
			if _debug_level > 2:
				print ("Invalid Token")
	return output

def getMeaning (header, fullBid, mode):
	question = "What is the meaning of the above bid?"
	while True:
		response = getResponse (header, question)
		(valid, response) = translateResponse (response)
		if not valid:
			continue
		if response.upper () == "R":
			return (True, "Relay")

		#--- Do Stuff ---#
		meaning = ""
		counter = -1
		or_flag = False
		for token in response:
			counter += 1
			if token in ["(",")","/","+"]:
				or_flag = False
				if token == "/":
					meaning += " OR "
					or_flag = True
					continue
				if token == "+":
					meaning += "; "
					continue
				meaning += token
				continue
			if token == "F":
				meaning += "Forcing"
				continue
			if token == "V":
				meaning += "Pass or Correct"
				continue
			if token == "B":
				meaning += "BAL"
				continue
			if token == "!":
				meaning += "STR"
				continue
			double_or = False
			if or_flag:
				if counter + 1 < len (response):
					if response [counter + 1] == "/":
						double_or = True
				else:
					double_or = True
			else:
				if counter == 0 and counter + 1 < len (response):
					if response [counter + 1] == "/":
						double_or = True

			meaning += getFurtherResponse (token, header + "\n" + meaning, response, counter, double_or)
		break
	return (True, meaning)

#--------- High Tier Functions ----------#

# inputFilename = ""
# outputFilename = ""

# inputSystem = readSystem (inputFilename)
# outputSystem = readSystem (outputFilename)
# for key in inputSystem.keys ():
# 	biddings = generateBiddings (key, "Uncontested")
# 	for bid in biddings:
# 		fillMeaning (key, bid, outputSystem, "Uncontested")
# writeSystem (outputFilename, outputSystem, True)

# inputFilename = "../data/Bidding/Opening"
# outputFilename = "../data/Bidding/Responses_1C_2C"
# outputFilename = "../data/Bidding/3_4_Responses"
# outputFilename = "../data/Bidding/Responses_1NT"
# outputFilename = "../data/Bidding/Responses_2NT"
# outputFilename = "../data/Bidding/Responses_Preempt"
outputFilename = "../data/Bidding/Competitive"
mode = "Competitive"
if mode == "Competitive" and outputFilename != "../data/Bidding/Competitive":
	r = input ("Warn")
# mode = "Uncontested"
# inputSystem = readSystem (inputFilename)
# outputSystem = {}
outputSystem = readSystem (outputFilename)
# for key in inputSystem.keys ():
# 	prev_bid = key.split ("-")
# for key in outputSystem.keys ():
# 	prev_bid = key.split ("-")
# 	fillMeaning (prev_bid [:-1], prev_bid [-1], outputSystem, mode)
prev_bid = ["1S"]
biddings = generateBiddings (prev_bid, mode)
for bid in biddings:
	fillMeaning (prev_bid, bid, outputSystem, mode)
	writeSystem (outputFilename, outputSystem, True)
