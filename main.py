import os, sys
import numpy as np
import cv2 as cv

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

img = cv.imread(imgpath, cv.IMREAD_GRAYSCALE)

# binarização

th, img_bin = cv.threshold(img, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)

# detecção de pautas

img_bin = np.float32(img_bin)
hist = cv.reduce(img_bin, 1, cv.REDUCE_SUM)

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

bounds = segmentation.segment_staves(img, grouped_staff_rows)

adjusted_staff_rows = []
for i in range(len(bounds)):
	r = []
	for j in range(5):
		r.append([h-bounds[i][0] for h in grouped_staff_rows[i*5+j]])
	adjusted_staff_rows.append(r)

# remoção de pautas:

for i in staff_rows:
	for j in range(0, len(img[0])):
		if img[i-1][j] == 255:
			img[i][j] = 255

separated_staves = []
for b in bounds:
	separated_staves.append(img[b[0]:b[1]][:])

obj_detection.find_objs(separated_staves[0])