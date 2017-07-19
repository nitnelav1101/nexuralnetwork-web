from flask import session
from nexuralnetweb import app
import os
import fnmatch
import glob
from werkzeug.utils import secure_filename, MultiDict
import nexuralnetengine
import json
import re


def addProject(projectName, accessCode):
    projectPath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName)
    accessCodeFilePath = os.path.join(projectPath, 'access.txt')
    if not os.path.isdir(projectPath) and not os.path.exists(projectPath):
    	os.makedirs(projectPath)
    	file = open(accessCodeFilePath, 'w')
    	file.write(accessCode) 
        file.close()
        session.pop('access_code', None)
    	session['access_code'] = accessCode
    	createDirectory(os.path.join(projectPath, app.config['TRAINING_FILES_FOLDER_NAME']))
    	createDirectory(os.path.join(projectPath, app.config['NETWORK_FILES_FOLDER_NAME']))
    	createDirectory(os.path.join(projectPath, app.config['PROJECT_DATASETS_FOLDER_NAME']))
    	createDirectory(os.path.join(projectPath, app.config['TRAININGS_FOLDER_NAME']))
        return True
    else:
        return False


def getAllProjects():
	dirs = [d for d in os.listdir(app.config['BASE_PROJECTS_FOLDER_NAME']) if os.path.isdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], d))]
	return dirs


def getAllProjectDatasets(projectName):
	dirs = [d for d in os.listdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['PROJECT_DATASETS_FOLDER_NAME'])) if os.path.isdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['PROJECT_DATASETS_FOLDER_NAME'], d))]
	return dirs


def getAllTestFilters(projectName, testName):
	files = [f for f in os.listdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TESTS_FILES_FOLDER_NAME'], testName, 'filters'))]
	dic = []
	for x in files:
		dic.append(os.path.basename(x))
	return dic

def getAllTrainings(projectName):
	dirs = [d for d in os.listdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'])) if os.path.isdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], d))]
	dic = MultiDict()
	for x in dirs:
		dic.add(os.path.basename(x), os.path.basename(x))
	return dic


def getAllNetworkArhitecturesFiles(projectName):
	files = [f for f in os.listdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['NETWORK_FILES_FOLDER_NAME'])) if fnmatch.fnmatch(f, '*.json')]
	dic = MultiDict()
	for x in files:
		dic.add(os.path.basename(x), os.path.basename(x))
	return dic


def getAllTriningFiles(projectName):
	files = [f for f in os.listdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAINING_FILES_FOLDER_NAME'])) if fnmatch.fnmatch(f, '*.json')]
	dic = MultiDict()
	for x in files:
		dic.add(os.path.basename(x), os.path.basename(x))
	return dic



def getAllProjectTests(projectName):
	dirs = [d for d in os.listdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, 'tests')) if os.path.isdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, 'tests', d))]
	return dirs



def isProjectOwner(projectName):
	projectPath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName)
	accessCodeFilePath = os.path.join(projectPath, 'access.txt')
	if not os.path.isdir(projectPath) and not os.path.exists(projectPath):
		return False
	else:
		file = open(accessCodeFilePath, 'r')
		storedAccessCode = file.read() 
		file.close()
		if session.get('access_code'):
			if session['access_code'] == storedAccessCode:
				return True
	return False



def checkAccessCode(projectName, accessCode):
	projectPath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName)
	accessCodeFilePath = os.path.join(projectPath, 'access.txt')
	if not os.path.isdir(projectPath) and not os.path.exists(projectPath):
		return False
	else:
		file = open(accessCodeFilePath, 'r')
		storedAccessCode = file.read() 
		file.close()
		if accessCode == storedAccessCode:
			session.pop('access_code', None)
			session['access_code'] = accessCode
			return True
	return False



def createDirectory(dirPath):
    if not os.path.isdir(dirPath) and not os.path.exists(dirPath):
    	os.makedirs(dirPath)


def fileExists(dirPath):
	return os.path.exists(dirPath)


def dirExists(currentTestPath):
	return os.path.isdir(currentTestPath) and os.path.exists(currentTestPath)


def addTest(projectName, testName, networkArhitecture, trainedFile, formFile, readType):
    currentTestPath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TESTS_FILES_FOLDER_NAME'], testName)
    resultFilePath = os.path.join(currentTestPath, 'result.json') 
    detailsFilePath = os.path.join(currentTestPath, 'details.json')
    filtersFolderPath = os.path.join(currentTestPath, app.config['TESTS_FILTERS_IMAGES_FOLDER_NAME'])
    networkArhitecturePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['NETWORK_FILES_FOLDER_NAME'], networkArhitecture)
    trainedFilePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAINED_NETWORK_FILES_FOLDER_NAME'], trainedFile)


    createDirectory(filtersFolderPath)

    filename, fileExtension = os.path.splitext(secure_filename(formFile.filename))
    filename = "image" + fileExtension
    completeFilename = os.path.join(currentTestPath, filename)
    formFile.save(completeFilename)

    details = "{ \"network_config\": \"" + networkArhitecture + "\", \"trained_file\": \"" + trainedFile + "\", \"image_file\": \"" + filename + "\", \"readType\": \"" + readType + "\"}"
    file = open(detailsFilePath, 'w')
    file.write(details)
    file.close()

    nexuralnetengine.runNetwork(networkArhitecturePath, trainedFilePath, completeFilename, readType, filtersFolderPath, resultFilePath)


def getResult(projectName, testName):
	path = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TESTS_FILES_FOLDER_NAME'], testName, 'result.json')
	data = json.load(open(path))
	resultType = data['result_type']

	if resultType == "classification":
		resultMessage = "Cea mai buna clasa de potrivire: "
	else:
		resultMessage = "Rezultatul este: "

	resultMessage = resultMessage + data['best_class']
	return resultType, resultMessage


def cleanAlphanumericString(content):
	return re.sub(r'\W+', '', content)


def getTrainingStatus(projectName, trainingName):
	return 'train'


def trainedFileExists(projectName, trainingName):
	return False