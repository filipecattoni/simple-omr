import os, sys, glob, time, itertools
from enum import Enum
import numpy as np
import cv2 as cv
import joblib
from sklearn import svm
from skimage.feature import hog

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

	return clf

def find_objs(image):

	if not os.path.exists("model.svm"):

		print("Generating new model...")
		clf = generate_model()
		with open("model.svm", "wb") as f:
			joblib.dump(clf, f, protocol=5)
		print("New model generated at ./model.svm")

	else:

		print("Existing model found, loading...")
		with open("model.svm", "rb") as f:
			try:
				clf = joblib.load(f)
			except:
				print("Unable to load model.svm. Try deleting the file to generate a new model.")

	boxes = get_obj_boxes(clf, image, Symbols.notehead_full.value)

	test_check_boxes(image, boxes)


def get_obj_boxes(clf, img, symbol):

	init_boxes = []
	window_size = symbol_sizes[symbol]

	# getting all bounding boxes in image

	for (x, y, window) in helpers.sliding_window(img, stepSize=8, windowSize=window_size):

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
		if im_predict == symbol:
			init_boxes.append([x, y])

	# combining overlapping boxes

	total_area = window_size[0] * window_size[1]
	combined_boxes = []
	for x, y in init_boxes:

		if not combined_boxes:
			combined_boxes.append([x, y, x+window_size[0], y+window_size[1]])
			continue

		# calculate overlap with existing boxes
		x2 = x + window_size[0]
		y2 = y + window_size[1]

		overlap = -1
		for i in range(len(combined_boxes)):

			xi1, yi1, xi2, yi2 = combined_boxes[i]

			xx1 = max(x, xi1)
			xx2 = min(x2, xi2)
			yy1 = max(y, yi1)
			yy2 = min(y2, yi2)

			if (xx2-xx1 < 0) or (yy2-yy1 < 0):
				continue

			overlap_area = (xx2-xx1) * (yy2-yy1)
			if overlap_area >= 0.5 * total_area:
				overlap = i
				break

		if overlap == -1:
			combined_boxes.append([x, y, x+window_size[0], y+window_size[1]])
		else:
			combined_boxes[i] = [
				min(x, combined_boxes[i][0]),
				min(y, combined_boxes[i][1]),
				max(x+window_size[0], combined_boxes[i][2]),
				max(y+window_size[1], combined_boxes[i][3])
			]

	return combined_boxes

def test_check_boxes(img, boxes):

	clone = img.copy()
	clone = cv.cvtColor(clone, cv.COLOR_GRAY2BGR)
	for x1, y1, x2, y2 in boxes:
		cv.rectangle(clone, 
			(x1, y1), 
			(x2, y2), 
			(0, 0, 255), 
			2)
	cv.imshow("Window", clone)
	cv.waitKey(0)