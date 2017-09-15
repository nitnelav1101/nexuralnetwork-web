import os, fnmatch, json, re, StringIO, base64
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from flask import session
from werkzeug.utils import secure_filename, MultiDict
from nexuralnetweb import app
import nexuralnetengine



def createDirectory(dirPath):
    if not os.path.isdir(dirPath) and not os.path.exists(dirPath):
    	os.makedirs(dirPath)



def fileExists(dirPath):
	return os.path.exists(dirPath)



def dirExists(currentTestPath):
	return os.path.isdir(currentTestPath) and os.path.exists(currentTestPath)



def cleanAlphanumericString(content):
	return re.sub(r'\W+', '', content)



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


def getProjectTrainingsNames(projectName):
	dirs = [d for d in os.listdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'])) if os.path.isdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], d))]
	return dirs

def getTrainingEpochsNames(projectName, trainingName):
	files = [f for f in os.listdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, "info")) if "weights-epoch_" in f]
	return files



def hasProjectTrainings(projectName):
	dirs = [d for d in os.listdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'])) if os.path.isdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], d))]
	return len(dirs) > 0



def getAllTrainingInfoFiles(projectName):
	dirs = [d for d in os.listdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'])) if os.path.isdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], d))]
	dic = []
	for x in dirs:
		dic.append(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], x, "info.json"))
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



def getPlotFromData(data, xlabel, ylabel, legendTitles = []):
    img = StringIO.StringIO()
    ax = plt.figure().gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    displayLegend = (len(data) > 1) and (len(data) == len(legendTitles))
    for i in range(0, len(data)):
    	if displayLegend == True:
    		plt.plot(data[i], label=legendTitles[i])
    	else:
    		plt.plot(data[i])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    resPlot = base64.b64encode(img.getvalue())
    plt.clf()
    return resPlot


def getTrainingInfoData(projectName, trainingName):
	trainingInfoData = {}

	# Get info about this web training project
	trainingInfoData['webTrainingProjectDetails'] = getWEBProjectTrainingDetails(projectName, trainingName)

	# Get info about training configuration and network configuration
	if trainingInfoData['webTrainingProjectDetails']['available'] == True:
		trainingInfoData['trainingConfigurationData'] = getTrainingConfigurationData(projectName, trainingInfoData['webTrainingProjectDetails']['training_file'])
		trainingInfoData['networkConfigurationData'] = getNetworkConfigurationData(projectName, trainingInfoData['webTrainingProjectDetails']['network_file'])

	# Get training stats
	trainingInfoData['trainingStats'] = getTrainingStats(projectName, trainingName)

	return trainingInfoData



def getWEBProjectTrainingDetails(projectName, trainingName):
	webTrainingProjectDetailsFilePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, "info.json")
	webTrainingProjectDetails = {}

	if fileExists(webTrainingProjectDetailsFilePath) == True:
		with open(webTrainingProjectDetailsFilePath) as jsonData:
			data = json.load(jsonData)
			webTrainingProjectDetails['available'] = True
			webTrainingProjectDetails['network_file'] = data['network_file']
			webTrainingProjectDetails['training_file'] = data['training_file']
			webTrainingProjectDetails['dataset'] = data['dataset']
			webTrainingProjectDetails['timestamp'] = data['timestamp']
	else:
		webTrainingProjectDetails['available'] = False
		webTrainingProjectDetails['network_file'] = "-in curs de actualizare"
		webTrainingProjectDetails['training_file'] = "-in curs de actualizare"
		webTrainingProjectDetails['dataset'] = "-in curs de actualizare"
		webTrainingProjectDetails['timestamp'] = "-in curs de actualizare"

	return webTrainingProjectDetails


def isTrainingDone(projectName, trainingName):
	trainerInfoFilePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, "info", "trainerInfo.json")

	if fileExists(trainerInfoFilePath) == True:
		with open(trainerInfoFilePath, 'r') as dataFile:
			data = json.load(dataFile)
			if 'stop_condition' in data:
				return True
			else:
				return False
	return False


def getNetworkConfigurationData(projectName, networkConfigFileName):
	networkConfigurationData = {}
	networkConfigurationFilePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['NETWORK_FILES_FOLDER_NAME'], networkConfigFileName)

	if fileExists(networkConfigurationFilePath) == True:
		with open(networkConfigurationFilePath) as jsonData:
			data = json.load(jsonData)
			networkConfigurationData['available'] = True
			networkConfigurationData['layers'] = {}
			for i in range(0, len(data['network_layers'])):
				networkConfigurationData['layers'][i] = {}
				networkConfigurationData['layers'][i]['type'] = data['network_layers'][i]['type']
				networkConfigurationData['layers'][i]['params'] = {}
				for key, value in data['network_layers'][i]['params'].items():
					networkConfigurationData['layers'][i]['params'][key] = value
	else:
		networkConfigurationData['available'] = False

	return networkConfigurationData


def getTrainingConfigurationData(projectName, trainingConfigFileName):
	trainingConfigurationData = {}
	trainingConfigurationFilePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAINING_FILES_FOLDER_NAME'], trainingConfigFileName)

	if fileExists(trainingConfigurationFilePath) == True:
		with open(trainingConfigurationFilePath) as jsonData:
			data = json.load(jsonData)
			trainingConfigurationData['available'] = True
			trainingConfigurationData['max_num_epochs'] = data['trainer_settings']['max_num_epochs']
			trainingConfigurationData['autosave_training_num_epochs'] = data['trainer_settings']['autosave_training_num_epochs']
			trainingConfigurationData['min_learning_rate_threshold'] = data['trainer_settings']['min_learning_rate_threshold']
			trainingConfigurationData['min_validation_error_threshold'] = data['trainer_settings']['min_validation_error_threshold']
			trainingConfigurationData['training_dataset_percentage'] = data['trainer_settings']['training_dataset_percentage']
			trainingConfigurationData['algorithm'] = data['solver']['algorithm']
			trainingConfigurationData['learning_rate'] = data['solver']['learning_rate']
			trainingConfigurationData['weight_decay'] = data['solver']['weight_decay']
	else:
		trainingConfigurationData['available'] = False
		trainingConfigurationData['max_num_epochs'] = "-in curs de actualizare"
		trainingConfigurationData['autosave_training_num_epochs'] = "-in curs de actualizare"
		trainingConfigurationData['min_learning_rate_threshold'] = "-in curs de actualizare"
		trainingConfigurationData['min_validation_error_threshold'] = "-in curs de actualizare"
		trainingConfigurationData['training_dataset_percentage'] = "-in curs de actualizare"
		trainingConfigurationData['algorithm'] = "-in curs de actualizare"
		trainingConfigurationData['learning_rate'] = "-in curs de actualizare"
		trainingConfigurationData['weight_decay'] = "-in curs de actualizare"

	return trainingConfigurationData



def getTrainingStats(projectName, trainingName, epochNum = -1, classNum = -1):
	trainingStats = {}
	trainerInfoFilePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, "info", "trainerInfo.json")

	if fileExists(trainerInfoFilePath) == True:
		with open(trainerInfoFilePath, 'r') as dataFile:
			data = json.load(dataFile)
			trainingStats['available'] = True
			trainingStats['result_type'] = getResultTypeMessage(data['result_type'])
			if 'stop_condition' in data:
				trainingStats['stop_condition'] = getStopConditionTypeMessage(data['stop_condition'])
				trainingStats['training_status'] = "antrenament complet"
				trainingStats['is_training_done'] = True
			else:
				trainingStats['stop_condition'] = "momentan indisponibil"
				trainingStats['training_status'] = "in curs de antrenare"
				trainingStats['is_training_done'] = False

			trainingStats['epochs_num'], trainingStats['clases_num'], trainingStats['trainingDatasetStats'], trainingStats['validationDatasetStats'] = getStatsFromConfusionMatrix(projectName, trainingName, epochNum, classNum)

			if int(trainingStats['epochs_num']) < 5:
				trainingStats['available'] = False

			learningRateData = []
			trainingDatasetMeanErrorData = []
			validationDatasetMeanErrorData = []

			for x in range(1, int(trainingStats['epochs_num'])):
				learningRateData.append(float(data['epochs']['epoch' + str(x)]['learning_rate']))
				trainingDatasetMeanErrorData.append(float(data['epochs']['epoch' + str(x)]['training_mean_error']))
				validationDatasetMeanErrorData.append(float(data['epochs']['epoch' + str(x)]['validation_mean_error']))

			learningRateStats = []
			epochMeanErrorStats = []
			learningRateStats.append(learningRateData)
			epochMeanErrorStats.append(trainingDatasetMeanErrorData)
			epochMeanErrorStats.append(validationDatasetMeanErrorData)

			trainingStats['plot_learning_rate'] = getPlotFromData(learningRateStats, 'Epoca', 'Rata de invatare')
			trainingStats['plot_epoch_mean_error'] = getPlotFromData(epochMeanErrorStats, 'Epoca', 'Eroarea medie', ["setul de antrenament", "setul de validare"])
	else:
		trainingStats['available'] = False
		trainingStats['is_training_done'] = False
		trainingStats['result_type'] = "in curs de actualizare"
		trainingStats['stop_condition'] = "in curs de actualizare"
		trainingStats['training_status'] = "in curs de antrenare"
		trainingStats['epochs_num'] = 0
		trainingStats['clases_num'] = 0

	return trainingStats




def getStatsFromConfusionMatrix(projectName, trainingName, epochNum, classNum):
	dataInfoFilePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, "info", "trainerInfo.json")

	totalEpochsNum = 0
	totalClassesNum = 0

	with open(dataInfoFilePath, 'r') as dataFile:
		data = json.load(dataFile)
		totalEpochsNum = str(len(data['epochs'].items()))

		if epochNum == -1:
			epochNum = str(int(totalEpochsNum))
		if classNum == -1:
			classNum = 0

		trainingDatasetStats = []
		validationDatasetStats = []

		validationConfusionMatrix = data['epochs']['epoch' + str(epochNum)]['validation_confusion_matrix']
		validationConfusionMatrixNP = np.array([d for d in validationConfusionMatrix])

		trainingConfusionMatrix = data['epochs']['epoch' + str(epochNum)]['training_confusion_matrix']
		trainingConfusionMatrixNP = np.array([d for d in trainingConfusionMatrix])

		totalClassesNum = trainingConfusionMatrixNP.shape[0]

		trainingPrecision = trainingConfusionMatrixNP[classNum][classNum] / trainingConfusionMatrixNP.sum(axis=0)[classNum]
		trainingRecall = trainingConfusionMatrixNP[classNum][classNum] / trainingConfusionMatrixNP[classNum].sum()
		trainingF1score = 2 * ((trainingPrecision * trainingRecall) / (trainingPrecision + trainingRecall))
		statstr = {}
		statstr['recall'] = str(trainingRecall)
		statstr['precision'] = str(trainingPrecision)
		statstr['f1score'] = str(trainingF1score)
		trainingDatasetStats.append(statstr)

		precision = validationConfusionMatrixNP[classNum][classNum] / validationConfusionMatrixNP.sum(axis=0)[classNum]
		recall = validationConfusionMatrixNP[classNum][classNum] / validationConfusionMatrixNP[classNum].sum()
		f1score = 2 * ((precision * recall) / (precision + recall))
		stats = {}
		stats['class'] = str(classNum)
		stats['recall'] = str(recall)
		stats['precision'] = str(precision)
		stats['f1score'] = str(f1score)
		validationDatasetStats.append(stats)

	return totalEpochsNum, totalClassesNum, trainingDatasetStats, validationDatasetStats



def getResultTypeMessage(resultType):
	if resultType == "classification":
		return "clasificare"
	elif resultType == "multiclass_classification":
		return "clasificare cu clase multiple"
	else:
		return "regresie"



def getStopConditionTypeMessage(stopConditionType):
	if stopConditionType == "reached_max_epochs_number":
		return "s-a atins numarul maxim de epoci"
	elif stopConditionType == "reached_min_validation_threshold":
		return "s-a atins eroarea minima pentrul setul de validare"
	elif stopConditionType == "reached_min_learning_rate_threshold":
		return "s-a atins valoarea minima a ratei de invatare"



def isSafeToDeleteThis(projectName, fileName, deletionType):
	searchMember = "none"
	if deletionType == "network_config":
		searchMember = "network_file"
	elif deletionType == "training_config":
		searchMember = "training_file"
	elif deletionType == "dataset":
		searchMember = "dataset"

	infoTrainingFiles = getAllTrainingInfoFiles(projectName)

	for i in range(0, len(infoTrainingFiles)):
		if fileExists(infoTrainingFiles[i]) == True:
			with open(infoTrainingFiles[i], 'r') as dataFile:
				data = json.load(dataFile)
				if fileName == data[searchMember]:
					return False
	return True
