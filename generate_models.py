import os, sys, glob
import numpy as np
import cv2 as cv

paths = [
	'unknown',
	'notes',
	'notesFlags',
	'notesOpen',
	'rests1',
	'rests2',
	'sharps',
	'flat',
	'naturals',
	'time',
	'altoClef',
	'trebleClef'
]

n_data_per_path = []
train_ims = []
labels = []

for i in range(len(paths)):

	n_data_found = 0

	for file_path in glob.glob(os.path.join('training_data', paths[i], "*")):
		#print(file_path)
		n_data_found = n_data_found+1
		labels.append(i)
		im = cv.imread(file_path, cv.IMREAD_GRAYSCALE)
		resized = cv.resize(im, (64, 64))
		train_ims.append(np.array(resized, np.float32).reshape(-1))

	n_data_per_path.append(n_data_found)

train_data = np.array(train_ims).astype(np.float32)
print(train_data.shape)
model_train_data = cv.ml.TrainData_create(train_data, cv.ml.ROW_SAMPLE, np.array(labels, np.int32))

knn = cv.ml.KNearest_create()
knn.train(model_train_data)
knn.save('models/knn_model.yml')