import os, sys, glob, time, itertools, joblib

import numpy as np
import cv2 as cv

from sklearn import svm
from skimage.feature import hog

from config import *
import helpers

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

	cropped_img, crop_x, crop_y = helpers.crop_whitespace(image)
	symbols = []

	#get_obj_boxes(clf, cropped_img, Symbols.rest_wholehalf.value)
	
	print("Detecting whole/half notes...")
	for box in get_obj_boxes(clf, cropped_img, Symbols.notehead_empty.value):
		flags = find_flags(cropped_img, box)
		symbols.append([Symbols.notehead_empty.value, crop_x+int((box[0]+box[2])/2), crop_y+int((box[1]+box[3])/2), flags])
	
	print("Detecting other notes...")
	for box in get_obj_boxes(clf, cropped_img, Symbols.notehead_full.value):
		flags = find_flags(cropped_img, box)
		symbols.append([Symbols.notehead_full.value, crop_x+int((box[0]+box[2])/2), crop_y+int((box[1]+box[3])/2), flags])
	
	for i in range(Symbols.rest_wholehalf.value, len(Symbols)):
		print(f"Detecting {symbol_names[i]}...")
		for box in get_obj_boxes(clf, cropped_img, i):
			symbols.append([i, crop_x+int((box[0]+box[2])/2), crop_y+int((box[1]+box[3])/2)])

	return symbols

def get_obj_boxes(clf, img, symbol):

	init_boxes = []
	window_size = symbol_sizes[symbol]
	if window_size[1] > img.shape[0]:
		window_size[1] = img.shape[0]
	step_size = 8

	# getting all bounding boxes in image

	for (x, y, window) in helpers.sliding_window(img, stepSize=step_size, windowSize=window_size):

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

	#sys.exit(0)

	return combine_overlaps(init_boxes, window_size)

def combine_overlaps(boxes, window_size):

	total_area = window_size[0] * window_size[1]
	combined_boxes = []
	for x, y in boxes:

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

def find_flags(img, note_box):

	center_x = int((note_box[0] + note_box[2]) / 2)
	center_y = int((note_box[1] + note_box[3]) / 2)

	x_edge, x_dir, y_dir = find_stem_dir(img, center_x, center_y)

	if y_dir == 0:
		return -1

	x_left, x_right = x_edge-5, x_edge+5
	y = center_y + (15*y_dir)

	flags_found = 0
	flag_detecting = False
	flag_detecting_n = 0

	while True:

		if flag_detecting:
			if not (img[y][x_left] == 0 or img[y][x_right] == 0):
				if flag_detecting_n > 5:
					flags_found = flags_found+1
				flag_detecting = False
				flag_detecting_n = 0
			else:
				flag_detecting_n = flag_detecting_n+1
		else:
			if img[y][x_left] == 0 or img[y][x_right] == 0:
				flag_detecting = True
				flag_detecting_n = 1

		if img[y][x_edge] != 0 and img[y][x_edge-1] != 0 and img[y][x_edge+1] != 0:
			break

		y = y+y_dir
		if y<0 or y>len(img):
			break

	return flags_found

def find_stem_dir(img, x, y):

	x_threshold = 25
	y_threshold = 20
	beam_threshold = 15

	for y_dir in [-1, 1]:

		y_edge = y
		x_temp = x
		black_pixel_found = False

		for i in range(1, y_threshold+1):
			y_edge = y_edge+y_dir
			if not black_pixel_found:
				if img[y_edge][x_temp] == 0:
					black_pixel_found = True
			elif img[y_edge][x] != 0:
				if img[y_edge][x_temp-1] == 0:
					x_temp = x_temp=1
				elif img[y_edge][x_temp+1] == 0:
					x_temp = x_temp+1
				else:
					break

		for x_dir in [-1, 1]:

			x_edge = x
			stem_found = False
			stem_pixels = 0
			for i in range(1, x_threshold+1):
				x_edge = x_edge+x_dir
				if img[y_edge][x_edge] == 0:
					if not stem_found:
						stem_found = True
						stem_pixels = 1
					else:
						stem_pixels = stem_pixels+1
				elif stem_found:
					if stem_pixels >= 5:
						stem_found = False
					else:
						return x_edge-(x_dir*2), x_dir, y_dir

	return 0, 0

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