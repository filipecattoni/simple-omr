# scripts de fontes externas utilizadas para auxiliar o desenvolvimento.
import cv2 as cv
import imutils, sys

# retorna uma piramide de imagens para fazer deslizamento de janela.
# fonte: https://pyimagesearch.com/2015/03/16/image-pyramids-with-python-and-opencv/
def pyramid(image, scale=1.5, minSize=(50, 50)):
	# yield the original image
	yield image
	# keep looping over the pyramid
	while True:
		# compute the new dimensions of the image and resize it
		w = int(image.shape[1] / scale)
		image = imutils.resize(image, width=w)
		# if the resized image does not meet the supplied minimum
		# size, then stop constructing the pyramid
		if image.shape[0] < minSize[1] or image.shape[1] < minSize[0]:
			break
		# yield the next image in the pyramid
		yield image

# retorna uma lista de janelas da imagem de input 
# fonte: https://pyimagesearch.com/2015/03/23/sliding-windows-for-object-detection-with-python-and-opencv/
def sliding_window(image, stepSize, windowSize):
	# slide a window across the image
	for y in range(0, image.shape[0], stepSize):
		for x in range(0, image.shape[1], stepSize):
			# yield the current window
			yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])

# corta o espaco branco ao redor da imagem e retorna as coordenadas da caixa de contorno
# adaptado de: https://python.plainenglish.io/effortlessly-remove-unwanted-whitespaces-from-images-with-opencv-and-python-e6707aac32c3
def crop_whitespace(image):
    
    # Find contours in the expanded binary mask
    contours, _ = cv.findContours(cv.bitwise_not(image), cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    
    left = image.shape[1]
    top = image.shape[0]
    right = 0
    bottom = 0

    for x, y, w, h in (cv.boundingRect(c) for c in contours):
    	if x < left:
    		left = x
    	if y < top:
    		top = y
    	if x+w > right:
    		right = x+w
    	if y+h > bottom:
    		bottom = y+h

    # Ensure the bounding box coordinates are within image boundaries
    #x = max(x, 0)
    #y = max(y, 0)
    #w = min(w, image.shape[1] - x)
    #h = min(h, image.shape[0] - y)
    
    # Crop the image based on the adjusted bounding box
    cropped_image = image[top:bottom, left:right]

    return cropped_image, left, top