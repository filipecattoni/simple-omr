import os, sys, glob, time, itertools
from enum import Enum
import numpy as np
import cv2 as cv
from skimage.feature import hog
from sklearn import svm

import helpers

class Symbols(Enum):
	empty                = 0
	unknown              = 1
	notehead_full        = 2
	notehead_empty       = 3
	rest_wholehalf       = 4
	rest_quarter         = 5
	rest_eighth          = 6
	rest_sixteenth       = 7
	rest_thirtysecond    = 8
	accidental_flat      = 9
	accidental_natural   = 10
	accidental_sharp     = 11
	clef_alto            = 12
	clef_bass            = 13
	clef_treble          = 14

paths = [
	'empty',
	'unknown',
	'noteheads/full',
	'noteheads/empty',
	'rests/wholehalf',
	'rests/quarter',
	'rests/eighth',
	'rests/sixteenth',
	'rests/thirtysecond',
	'accidentals/flat',
	'accidentals/natural',
	'accidentals/sharp',
	'clefs/alto',
	'clefs/bass',
	'clefs/treble'
]

symbol_sizes = [
	[0, 0],
	[0, 0],
	[40, 35],
	[40, 35],
	[32, 26],
	[40, 70],
	[30, 50],
	[30, 70],
	[30, 90],
	[30, 70],
	[25, 50],
	[30, 70],
	[70, 160],
	[70, 160],
	[70, 160]
]

hog_or = 9
hog_ppc = [4, 4]
hog_cpb = [2, 2]

def generate_model():

	n_data_per_path = []
	train_ims = []
	labels = []

	for i in range(len(paths)):

		n_data_found = 0

		for file_path in glob.glob(os.path.join('training_data', paths[i], "*")):
			n_data_found = n_data_found+1
			labels.append(i)
			im = cv.imread(file_path, cv.IMREAD_GRAYSCALE)
			resized = cv.resize(im, (32, 32))
			im_hog = hog(resized,
				orientations=hog_or,
				pixels_per_cell=hog_ppc,
				cells_per_block=hog_cpb)
			train_ims.append(im_hog)

		n_data_per_path.append(n_data_found)

	clf = svm.SVC()
	clf.fit(train_ims, labels)

	return clf, labels

def find_objs(image):

	clf, labels = generate_model()

	clf_data = []

	symbol = Symbols.notehead_full.value
	window_size = symbol_sizes[symbol]

	for (x, y, window) in helpers.sliding_window(image, stepSize=8, windowSize=window_size):

		if (window.shape[1] < window_size[0]) or (window.shape[0] < window_size[1]):
			continue
		
		#cv.imwrite("data_temp/a1_{}_{}.png".format(x, y), window)
		#continue

		resized = cv.resize(window, (32, 32))
		im_hog = hog(resized,
				orientations=hog_or,
				pixels_per_cell=hog_ppc,
				cells_per_block=hog_cpb)
		im_predict = clf.predict([im_hog])
		clf_data.append([im_predict, x, y])

	clone = image.copy()
	clone = cv.cvtColor(clone, cv.COLOR_GRAY2BGR)
	for pred, x, y in clf_data:
		if pred == symbol:
			cv.rectangle(clone, 
				(x, y), 
				(x+window_size[0], y+window_size[1]), 
				(0, 0, 255), 
				2)
	cv.imshow("Window", clone)
	cv.waitKey(0)