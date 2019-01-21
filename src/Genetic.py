import os
from Helper import getData, mse, unclash
import numpy as np
import math
import random
import json

from keras import backend as K
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten, GaussianNoise
from keras.layers import Convolution2D
from keras.optimizers import SGD
from sklearn.metrics import mean_squared_error
from keras.constraints import maxnorm
from keras.callbacks import EarlyStopping
from keras import regularizers

_trainingFilename = "../data/HandRecords/Large/HandRecord_700000_0"
_testingFilename = "../data/HandRecords/Shared/HandRecord_20000_0"
# _trainingFilename = "../data/HandRecords/Shared/HandRecord_100_0"
# _testingFilename = "../data/HandRecords/Shared/HandRecord_10_0"
_networkFoldername = "../data/Networks/Genetic/NT_by_N/Network"
# _networkFilename = "../data/Networks/NT_by_N/Network_201.h5"

_familyTree = "../data/Networks/Genetic/NT_by_N/Network/Result"
_firstGenResult = "../data/Networks/Genetic/NT_by_N/Network/First_Gen/Result"
_secondGenResult = "../data/Networks/Genetic/NT_by_N/Network/Second_Gen/Result"
_thirdGenResult = "../data/Networks/Genetic/NT_by_N/Network/Third_Gen/Result"

_dataSize = -1
_inputMode = "3D"
_outputMode = "NT_by_N"

(hand, res) = getData (filename = _trainingFilename, dataSize = _dataSize, inputMode = _inputMode, outputMode = _outputMode)

X = np.asarray (hand)
Y = np.asarray (res)

(hand, res) = getData (filename = _testingFilename, dataSize = _dataSize, inputMode = _inputMode, outputMode = _outputMode)

X_test = np.asarray (hand)
Y_test = np.asarray (res)

# ------------------------------

seed = 6
np.random.seed (seed)

_loss = "mse"
_epoch = 25
_batch_size = 50

# ------------------------------

def sigmoid(x):
	return 1 / (1 + math.exp(-x))

def calcScore (var, networkFoldername):

	_lr = sigmoid (var ["lr"])
	_momentum = sigmoid (var ["momentum"])
	_decay = _lr/_epoch

	_dropout_1 = sigmoid (var ["dropout_1"])
	_dropout_2 = sigmoid (var ["dropout_2"])
	_dropout_3 = sigmoid (var ["dropout_3"])
	_dropout_4 = sigmoid (var ["dropout_4"])

	_noise_1 = sigmoid (var ["noise_1"])
	_noise_2 = sigmoid (var ["noise_2"])
	_noise_3 = sigmoid (var ["noise_3"])
	_noise_4 = sigmoid (var ["noise_4"])

	_l1_reg_1 = sigmoid (var ["l1_reg_1"])
	_l2_reg_1 = sigmoid (var ["l2_reg_1"])
	_l1_reg_2 = sigmoid (var ["l1_reg_2"])
	_l2_reg_2 = sigmoid (var ["l2_reg_2"])

	_dense_1 = int (round (sigmoid (var ["dense_1"]) * 512)) + 2
	_dense_2 = int (round (sigmoid (var ["dense_2"]) * 512)) + 2

	_maxnorm_1 = int (round (sigmoid (var ["maxnorm_1"]) * 10)) + 1
	_maxnorm_2 = int (round (sigmoid (var ["maxnorm_2"]) * 10)) + 1
	_maxnorm_3 = int (round (sigmoid (var ["maxnorm_3"]) * 10)) + 1
	_maxnorm_4 = int (round (sigmoid (var ["maxnorm_4"]) * 10)) + 1

	_filter_layer_1 = int (round (sigmoid (var ["filter_layer_1"]) * 8)) + 1
	_filter_layer_2 = int (round (sigmoid (var ["filter_layer_2"]) * 8)) + 1
	_conv_window_1 = int (round (sigmoid (var ["conv_window_1"]) * 6)) + 2
	_conv_window_2 = int (round (sigmoid (var ["conv_window_2"]) * 6)) + 2

	_option_1 = var ["option_1"]
	_option_2 = var ["option_2"]

	if _conv_window_1 >= 6:
		_conv_window_1 = 5

	if _conv_window_2 >= 6:
		_conv_window_2 = 5

	# ---------------------------------- Builidng Model based on Hyper Datas -------------------------------------

	model = Sequential ()

	try:
		model.add (Convolution2D (_filter_layer_1, (_conv_window_1, _conv_window_1), input_shape = (7, 13, 4), border_mode = "valid", activation = "relu", kernel_constraint = maxnorm (_maxnorm_1)))
		model.add (Dropout(_dropout_1))
		model.add (GaussianNoise (_noise_1))

		if _option_1:
			model.add (Convolution2D (_filter_layer_2, (_conv_window_2, _conv_window_2), input_shape = (7, 13, 4), border_mode = "valid", activation = "relu", kernel_constraint = maxnorm (_maxnorm_2)))
			model.add (Dropout(_dropout_2))
			model.add (GaussianNoise (_noise_2))	

		model.add (Flatten())

		model.add (Dense (_dense_1, activation = 'relu', kernel_constraint = maxnorm (_maxnorm_3), kernel_regularizer = regularizers.l1_l2 (l1=_l1_reg_1, l2=_l2_reg_1)))
		model.add (Dropout(_dropout_3))
		model.add (GaussianNoise (_noise_3))

		if _option_2:
			model.add (Dense (_dense_2, activation = 'relu', kernel_constraint = maxnorm (_maxnorm_4), kernel_regularizer = regularizers.l1_l2 (l1= _l1_reg_2, l2=_l2_reg_1)))
			model.add (Dropout(_dropout_4))
			model.add (GaussianNoise (_noise_4))

		model.add (Dense (1))

		sgd = SGD(lr=_lr, momentum=_momentum, decay=_decay, nesterov=False)
		model.compile(loss=_loss, optimizer=sgd)
	except:
		print (_lr)
		print (_momentum)
		print (_decay)

		print (_dropout_1)
		print (_dropout_2)
		print (_dropout_3)
		print (_dropout_4)

		print (_noise_1)
		print (_noise_2)
		print (_noise_3)
		print (_noise_4)

		print (_l1_reg_1)
		print (_l2_reg_1)
		print (_l1_reg_2)
		print (_l2_reg_2)

		print (_dense_1)
		print (_dense_2)

		print (_maxnorm_1)
		print (_maxnorm_2)
		print (_maxnorm_3)
		print (_maxnorm_4)

		print (_filter_layer_1)
		print (_filter_layer_2)
		print (_conv_window_1)
		print (_conv_window_2)

		print (_option_1)
		print (_option_2)

	early_stopping = EarlyStopping (monitor = "val_loss", patience = 5, min_delta = 0, restore_best_weights=True)

	history = model.fit(X, Y, epochs = _epoch, batch_size=_batch_size, verbose = True, validation_split = 0.2, callbacks = [early_stopping])
	fn = unclash (networkFoldername + "/Network" , ".h5")
	model.save (fn)

	Y_pred = model.predict (X_test, verbose=True)
	mean_squared_error = mse (Y_pred, Y_test)

	from keras import backend as K

	K.clear_session ()

	return (mean_squared_error, fn)

def init_Population (var_list, subfoldername, no_of_network, resultfilename, mutation_chance):

	if mutation_chance > 0.3:
		print ("Mutation Chance Too High!")
		return

	networkCounter = 0

	var = {
		"score": -1,
		"filename": "",
		"lr": -7.0,
		"momentum": 2.2,

		"dropout_1": 0.0,
		"dropout_2": 0.0,
		"dropout_3": 0.0,
		"dropout_4": 0.0,

		"noise_1": 0.0,
		"noise_2": 0.0,
		"noise_3": 0.0,
		"noise_4": 0.0,

		"l1_reg_1": 0.0,
		"l2_reg_1": 0.0,
		"l1_reg_2": 0.0,
		"l2_reg_2": 0.0,

		"dense_1": -2.0,
		"dense_2": -2.0,

		"maxnorm_1": 1.0,
		"maxnorm_2": 2.0,
		"maxnorm_3": 3.0,
		"maxnorm_4": 3.0,

		"filter_layer_1": 4.0,
		"filter_layer_2": 4.0,
		"conv_window_1": 3.0,
		"conv_window_2": 3.0,

		"option_1": False,
		"option_2": False
	}

	nfn = _networkFoldername + subfoldername
	# (score, filename) = calcScore (var = var, networkFoldername = nfn)

	# networkCounter += 1

	# var ["score"] = score
	# var ["filename"] = filename
	# var_list.append (var)
	# var_list.sort (key=lambda x: x["score"])


	# f = open (_familyTree, "w")
	# f.write (filename)
	# f.write ("\n")
	# f.write (str (score))
	# f.write ("\n\n")
	# f.write (str (var))
	# f.write ("\n\n")
	# f.close ()

	while networkCounter <= no_of_network:

		var = dict (var)

		for key in var.keys ():
			if key != "option_1" and key != "option_2":
				var [key] = (random.random () - 1) * 100

		if random.random () <= mutation_chance:
			var ["option_1"] = not var ["option_1"]

		if random.random () <= mutation_chance:
			var ["option_2"] = not var ["option_2"]

		(score, filename) = calcScore (var = var, networkFoldername = nfn)
		networkCounter += 1

		var ["score"] = score
		var ["filename"] = filename
		var_list.append (var)
		var_list.sort (key=lambda x: x["score"])

		f = open (resultfilename, "w")
		for x in var_list:
			f.write (x ["filename"])
			f.write ("\n")
			f.write (str (x ["score"]))
			f.write ("\n\n")
			f.write (json.dumps (x))
			f.write ("\n\n")

		f.close ()

def selection (var_list, elitism):

	if elitism > 1:
		print ("Error! Population ratio cannot be greater than 1")
		return []

	var_list.sort (key=lambda x: x["score"])
	var_list = var_list [:int (len (var_list) * elitism)]

	return var_list

def get_var_list (filename):
	
	var_list = []
	file = open (filename, "r")

	for line in file:

		try:
			var = dict (json.loads (line))
			var_list.append (var)
		except:
			continue

	return var_list

	file.close ()

def cross_breed (var_list, subfoldername, breed_size, resultfilename, mutation_chance):

	if mutation_chance > 0.3:
		print ("MutationChance Too High!")
		return

	nfn = _networkFoldername + subfoldername

	li = []

	if breed_size == -1:

		for i in range (len (var_list)):
			for j in range (len (var_list)):
				if i == j:
					continue
					
				var = dict (var_list [0])
				for key in var.keys ():

					if random.random () > 0.5:
						var [key] = var_list [j][key]
					else:
						var [key] = var_list [i][key]

					if random.random () < mutation_chance:

						if isinstance (var [key], str):
							continue

						if key != "option1" and key != "option2":
							var [key] += (random.random () - 1) * 200
						else:
							var [key] = not var [key]

				(score, filename) = calcScore (var = var, networkFoldername = nfn)
				var ["score"] = score
				var ["filename"] = filename
				var ["parent_1"] = var_list [i]["filename"]
				var ["parent_2"] = var_list [j]["filename"]

				li.append (var)
				li.sort (key=lambda x: x["score"])

				f = open (resultfilename, "w")
				for x in li:
					f.write (x ["filename"])
					f.write ("\n")
					f.write (str (x ["score"]))
					f.write ("\n\n")
					f.write (x ["parent_1"])
					f.write ("\n")
					f.write (x ["parent_2"])
					f.write ("\n\n")
					f.write (json.dumps (x))
					f.write ("\n\n")

				f.close ()
	else:

		print ("Unimplemented Idea!")
		return

	return

def combine_result (inputFilenames, outputFilename):

	li = []
	for fn in inputFilenames:
		var_list = get_var_list (fn)
		for var in var_list:
			li.append (var)

	li.sort (key = lambda x: x["score"])

	f = open (outputFilename, "w")
	for x in li:
		f.write (x ["filename"])
		f.write ("\n")
		f.write (str (x ["score"]))
		f.write ("\n\n")
		try:
			f.write (x ["parent_1"])
			f.write ("\n")
			f.write (x ["parent_2"])
			f.write ("\n\n")
		except:
			print ("First_Gen")
		f.write (json.dumps (x))
		f.write ("\n\n")

	f.close ()

var_list = get_var_list (_secondGenResult)
var_list = selection (var_list = var_list, elitism = 0.1)
cross_breed (var_list = var_list, subfoldername = "/Third_Gen", breed_size = -1, resultfilename = _thirdGenResult, mutation_chance = 0.05)
# combine_result ([_familyTree, _secondGenResult], _familyTree)

# init_Population (var_list = var_list, subfoldername = "/First_Gen", no_of_network = 5, resultfilename = _familyTree, mutation_chance = 0.01)
