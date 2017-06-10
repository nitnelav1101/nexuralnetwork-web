from nexuralnetweb import app
import os

def addProject(name):
    projectPath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], name)
    if not os.path.isdir(projectPath) and not os.path.exists(projectPath):
    	os.makedirs(projectPath)
        return True
    else:
        return False