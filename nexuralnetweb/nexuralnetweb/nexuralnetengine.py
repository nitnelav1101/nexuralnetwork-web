import os, json
import nexuralnet
from nexuralnetweb import app
import numpy as np
import cv2


def runNetwork(networkArhitecture, trainedFile, imageFile, openImageType, filtersFolderPath, resultFilePath):
	try:
		net = nexuralnet.network(networkArhitecture)
		net.deserialize(trainedFile)
		image = cv2.imread(imageFile, int(openImageType)) 
		net.run(image)

		net.saveFiltersImages(filtersFolderPath)
		result = net.getResultJSON()

		file = open(resultFilePath, 'w')
		file.write(result) 
		file.close()
	except RuntimeError as exc:
		print("[ERROR] " + str(exc))
	except:
		print("[ERROR] Unknown!")