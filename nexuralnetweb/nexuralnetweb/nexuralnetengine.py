import nexuralnet
from nexuralnetweb import app
import numpy as np
import cv2
import os
import json


def getStatsFromConfusionMatrix(projectName, trainingName, epochNum, classNum):
	dataInfoFilePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, "info", "trainerInfo.json")

	with open(dataInfoFilePath, 'r') as dataFile:
		data = json.load(dataFile)

	trainingStats = []
	validationStats = []

	validationConfusionMatrix = data['epochs']['epoch' + str(epochNum)]['validation_confusion_matrix']
	validationConfusionMatrixNP = np.array([d for d in validationConfusionMatrix])

	trainingConfusionMatrix = data['epochs']['epoch' + str(epochNum)]['training_confusion_matrix']
	trainingConfusionMatrixNP = np.array([d for d in trainingConfusionMatrix])
	

	trainingPrecision = trainingConfusionMatrixNP[classNum][classNum] / trainingConfusionMatrixNP.sum(axis=0)[classNum]
	trainingRecall = trainingConfusionMatrixNP[classNum][classNum] / trainingConfusionMatrixNP[classNum].sum()
	trainingF1score = 2 * ((trainingPrecision * trainingRecall) / (trainingPrecision + trainingRecall))
	statstr = {}
	statstr['recall'] = str(trainingRecall)
	statstr['precision'] = str(trainingPrecision)
	statstr['f1score'] = str(trainingF1score)
	trainingStats.append(statstr)

	
	precision = validationConfusionMatrixNP[classNum][classNum] / validationConfusionMatrixNP.sum(axis=0)[classNum]
	recall = validationConfusionMatrixNP[classNum][classNum] / validationConfusionMatrixNP[classNum].sum()
	f1score = 2 * ((precision * recall) / (precision + recall))
	stats = {}
	stats['class'] = str(classNum)
	stats['recall'] = str(recall)
	stats['precision'] = str(precision)
	stats['f1score'] = str(f1score)
	validationStats.append(stats)

	return trainingStats, validationStats

def getTrainingStats(projectName, trainingName):
	dataInfoFilePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, "info", "trainerInfo.json")

	with open(dataInfoFilePath, 'r') as dataFile:
		data = json.load(dataFile)

	trainingStats = []
	validationStats = []
	trainingInfo = {}
	trainingInfo['result_type'] = data['result_type']
	trainingInfo['stop_condition'] = data['stop_condition']
	trainingInfo['epochs_num'] = str(len(data['epochs'].items()) - 1)

	validationConfusionMatrix = data['epochs']['epoch' + str(len(data['epochs'].items()) - 1)]['validation_confusion_matrix']
	validationConfusionMatrixNP = np.array([d for d in validationConfusionMatrix])

	trainingConfusionMatrix = data['epochs']['epoch' + str(len(data['epochs'].items()) - 1)]['training_confusion_matrix']
	trainingConfusionMatrixNP = np.array([d for d in trainingConfusionMatrix])
	
	for classNum in range(trainingConfusionMatrixNP.shape[0]):
		precision = trainingConfusionMatrixNP[classNum][classNum] / trainingConfusionMatrixNP.sum(axis=0)[classNum]
		recall = trainingConfusionMatrixNP[classNum][classNum] / trainingConfusionMatrixNP[classNum].sum()
		f1score = 2 * ((precision * recall) / (precision + recall))
		statstr = {}
		statstr['class'] = str(classNum)
		statstr['recall'] = str(recall)
		statstr['precision'] = str(precision)
		statstr['f1score'] = str(f1score)
		trainingStats.append(statstr)

	for classNum in range(validationConfusionMatrixNP.shape[0]):
		precision = validationConfusionMatrixNP[classNum][classNum] / validationConfusionMatrixNP.sum(axis=0)[classNum]
		recall = validationConfusionMatrixNP[classNum][classNum] / validationConfusionMatrixNP[classNum].sum()
		f1score = 2 * ((precision * recall) / (precision + recall))
		stats = {}
		stats['class'] = str(classNum)
		stats['recall'] = str(recall)
		stats['precision'] = str(precision)
		stats['f1score'] = str(f1score)
		validationStats.append(stats)

	return trainingStats, validationStats, trainingInfo

def getInitialWeightsHistogram():
	return ''

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
