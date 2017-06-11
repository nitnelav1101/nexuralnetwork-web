from flask import session
from nexuralnetweb import app
import os
import fnmatch
import glob
from werkzeug.utils import secure_filename, MultiDict

def isAllowedFile(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



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
        return True
    else:
        return False


def getAllProjects():
	dirs = [d for d in os.listdir(app.config['BASE_PROJECTS_FOLDER_NAME']) if os.path.isdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], d))]
	return dirs



def getAllTrainedNetworkFiles(projectName):
	files = [f for f in os.listdir(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAINED_NETWORK_FILES_FOLDER_NAME'])) if fnmatch.fnmatch(f, '*.json')]
	dic = MultiDict()
	for x in files:
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