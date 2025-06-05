import os, sys
from statistics import fmean
import numpy as np
import cv2 as cv
from skimage.transform import rescale

from config import *
import helpers
import segmentation
import obj_detection

def check_img(img):
	imgS = cv.resize(img, (int(len(img[0])/2), int(len(img)/2)))
	cv.imshow("Image", imgS);
	cv.waitKey(0)
	cv.destroyAllWindows()

if len(sys.argv) < 2:
	print("Please enter the image path as an argument.")
	sys.exit(0)

imgpath = sys.argv[1]
if not os.path.exists(imgpath):
	print("Invalid image path.")
	sys.exit(0)

visualize = False
for i in range(2, len(sys.argv)):
	if sys.argv[i] == "-v":
		visualize = True

img = cv.imread(imgpath, cv.IMREAD_GRAYSCALE)

# binarização

print("Binarizing image...")
th, img_bin = cv.threshold(img, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)

# detecção de pautas

print("Detecting stafflines...")
hist = cv.reduce(np.float32(img_bin), 1, cv.REDUCE_SUM)

staff_range = min(hist)*1.1 # numero magico... arrumar depois
staff_rows = []
for i in range(len(hist)):
	if hist[i] < staff_range:
		staff_rows.append(i)

# agrupando valores da mesma pauta:

grouped_staff_rows = []
l = []

for n in staff_rows:

	if l == [] or n == l[-1] + 1:
		l.append(n)
	else:
		grouped_staff_rows.append(l)
		l = []
		l.append(n)

grouped_staff_rows.append(l)

if len(grouped_staff_rows) < 5:
	print("Unable to detect enough stafflines in image.")
	sys.exit(0)

bounds = segmentation.segment_staves(img_bin, grouped_staff_rows)

adjusted_staff_rows = []
for i in range(len(bounds)):
	r = []
	for j in range(5):
		r.append([h-bounds[i][0] for h in grouped_staff_rows[i*5+j]])
	adjusted_staff_rows.append(r)

# calculando staffline_height e staffspace_height

sl_avg_heights = []
sl_thickness = []
for i in range(5):
	sl_thickness.append(len(adjusted_staff_rows[0][i]))
	sl_avg_heights.append(fmean(adjusted_staff_rows[0][i]))

staffline_height = fmean(sl_thickness)
staffspace_height = fmean(list(sl_avg_heights[i+1]-sl_avg_heights[i] for i in range(4)))

print(f"{len(adjusted_staff_rows)} staff/staves detected. Staffline height: {staffline_height}, Staffspace height: {staffspace_height}")

# setting scale value

scale = 20.625 / staffspace_height

# remoção de pautas:

img_nosl = img_bin.copy()

for i in staff_rows:
	for j in range(0, len(img_nosl[0])):
		if img_nosl[i-1][j] == 255:
			img_nosl[i][j] = 255

separated_staves = []
for b in bounds:
	separated_staves.append(img_nosl[b[0]:b[1]][:])

# recebendo listas de simbolos

print("Running symbol detection...")

scaled_staff = cv.resize(separated_staves[0], (0, 0), fx=scale, fy=scale, interpolation=cv.INTER_NEAREST)
symbols = obj_detection.find_objs(scaled_staff)

# arrumando pausas meias/inteiras

for i in range(len(symbols)):
	if symbols[i][0] == 4:

		second_staffline_y = grouped_staff_rows[1][-1]
		third_staffline_y = grouped_staff_rows[2][0]
		x = int(symbols[i][1]/scale)

		whole = True
		half = True
		for j in range(1, 4):
			if img_bin[second_staffline_y+j][x] != 0:
				whole = False
			if img_bin[third_staffline_y-j][x] != 0:
				half = False

		if whole and not half:
			symbols[i].append(0)
		elif half and not whole:
			symbols[i].append(1)

for s in symbols:
	print(s)

if visualize:

	print("Creating visualization...")
	clone = scaled_staff.copy()
	clone = cv.cvtColor(clone, cv.COLOR_GRAY2BGR)

	for s in symbols:

		if s[0] != 4:
			cv.rectangle(clone,
				(int(s[1]-(symbol_sizes[s[0]][0]/2)), int(s[2]-(symbol_sizes[s[0]][1]/2))), 
				(int(s[1]+(symbol_sizes[s[0]][0]/2)), int(s[2]+(symbol_sizes[s[0]][1]/2))), 
				vis_symbol_colors[s[0]],
				2
				)

		if s[0] == 2 or s[0] == 3:
			if s[0] == 3:
				i = 0 if s[3] == -1 else 1
			else:
				i = 2 + s[3]
			clone = cv.putText(clone,
				flags_to_dur[i],
				(int(s[1]-(symbol_sizes[s[0]][0]/2)), int(s[2]+(symbol_sizes[s[0]][1]/2)+24)),
				cv.FONT_HERSHEY_SIMPLEX,
				1,
				vis_symbol_colors[s[0]],
				2,
				cv.FILLED
				)

		if s[0] == 4 and len(s) == 4:
			cv.rectangle(clone,
				(int(s[1]-(symbol_sizes[s[0]][0]/2)), int(s[2]-(symbol_sizes[s[0]][1]/2))), 
				(int(s[1]+(symbol_sizes[s[0]][0]/2)), int(s[2]+(symbol_sizes[s[0]][1]/2))), 
				vis_symbol_colors[s[0]],
				2
				)
			clone = cv.putText(clone,
				("1" if s[3]==0 else "2"),
				(int(s[1]-(symbol_sizes[s[0]][0]/2)), int(s[2]+(symbol_sizes[s[0]][1]/2)+24)),
				cv.FONT_HERSHEY_SIMPLEX,
				1,
				vis_symbol_colors[s[0]],
				2,
				cv.FILLED
				)

	cv.imshow("Visualization", clone)
	cv.waitKey(0)