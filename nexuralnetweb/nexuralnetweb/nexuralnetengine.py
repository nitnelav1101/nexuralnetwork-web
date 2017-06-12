import nexuralnet
import cv2
import os

def runNetwork(networkArhitecture, trainedFile, imageFile, openImageType, filtersFolderPath, resultFilePath):
	net = nexuralnet.network(networkArhitecture)
	net.deserialize(trainedFile)
	image = cv2.imread(imageFile, int(openImageType)) 
	net.run(image)

	net.saveFiltersImages(filtersFolderPath)
	result = net.getResultJSON()

	file = open(resultFilePath, 'w')
	file.write(result) 
	file.close()
