import os, fnmatch, json, re, StringIO, base64
import matplotlib.pyplot as plt
from flask import session
from werkzeug.utils import secure_filename, MultiDict
from nexuralnetweb import app
import nexuralnetengine


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


def getTestResultInternalNetFilters(projectName, trainingName, testName):
	files = [f for f in os.listdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, app.config['TESTS_FILES_FOLDER_NAME'], testName, 'filters'))]
	dic = []
	filtersNumSet = set()
	for x in files:
		layerNum = re.findall('\d+', x.split("_")[1].split("-")[0])[0]
		dic.append((x, layerNum))
		filtersNumSet.add(layerNum)
	return dic, list(filtersNumSet)

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



def getAllProjectTests(projectName, trainingName):
	dirs = [d for d in os.listdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, app.config['TESTS_FILES_FOLDER_NAME'])) if os.path.isdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, app.config['TESTS_FILES_FOLDER_NAME'], d))]
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


def addTest(projectName, trainingName, testName, networkArhitecture, trainedFile, formFile, readType):
    currentTestPath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, app.config['TESTS_FILES_FOLDER_NAME'], testName)
    resultFilePath = os.path.join(currentTestPath, 'result.json') 
    detailsFilePath = os.path.join(currentTestPath, 'details.json')
    filtersFolderPath = os.path.join(currentTestPath, app.config['TESTS_FILTERS_IMAGES_FOLDER_NAME'])
    networkArhitecturePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['NETWORK_FILES_FOLDER_NAME'], networkArhitecture)
    trainedFilePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, trainingName + ".json")

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


def getTestResult(projectName, trainingName, testName):
	path = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, app.config['TESTS_FILES_FOLDER_NAME'], testName, 'result.json')
	data = json.load(open(path))
	resultType = data['result_type']

	if resultType == "classification":
		resultMessage = "Cea mai buna clasa de potrivire: "
		resultTypeMessage = "clasificare"
	elif resultType == "multiclass_classification":
		resultMessage = "Cea mai buna clasa de potrivire: "
		resultTypeMessage = "clasificare cu clase multiple"
	else:
		resultMessage = "Rezultatul este: "
		resultTypeMessage = "regresie"

	resultMessage = resultMessage + data['best_class_0']
	return resultTypeMessage, resultMessage


def cleanAlphanumericString(content):
	return re.sub(r'\W+', '', content)


def getPlotFromData(data, plotTitle):
    img = StringIO.StringIO()
    plt.plot(data)
    plt.xlabel(plotTitle)
    plt.savefig(img, format='png')
    img.seek(0)
    resPlot = base64.b64encode(img.getvalue())
    plt.clf()
    return resPlot