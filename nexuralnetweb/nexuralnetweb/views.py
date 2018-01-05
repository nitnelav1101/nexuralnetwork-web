import os, shutil, json
from flask import flash, redirect, render_template, request, url_for, session, send_file, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from nexuralnetweb import app
import nexuralnet
import engine, nexuralnetengine, webtasks
from forms import CreateProjectForm, SecureProjectForm, AddTrainingFileForm, AddNetworkFileForm, AddNetworkTestForm, AddNetworkTrainingForm, AddPredefinedDatSetForm
import time
from markupsafe import Markup


# -------------------------------------------------------------------------------------
#### AJAX services
# -------------------------------------------------------------------------------------
@app.route('/services/getTestResult/<string:projectName>/<string:trainingName>/<string:testName>', methods=['GET'])
def getTestResult(projectName, trainingName, testName):
    result = {}
    result['resultType'], result['resultMessage'] = engine.getTestResult(projectName, trainingName, testName)
    result['layerFiltersImages'], result['filtersByLayerNum'] = engine.getTestResultInternalNetFilters(projectName, trainingName, testName)
    return jsonify({'data': render_template('ajax_test_results.html', projectName = projectName, trainingName = trainingName, testName = testName, result = result)})

# ---------------------------

@app.route('/services/getTrainingStats/<string:projectName>/<string:trainingName>/<int:epochNum>/<int:classNum>', methods=['GET'])
def getTrainingStats(projectName, trainingName, epochNum, classNum):
    result = {}
    epochs, classes, result['trainingStats'], result['validationStats'] = engine.getStatsFromConfusionMatrix(projectName, trainingName, epochNum, classNum)
    return jsonify({'data': render_template('ajax_training_stats.html', result = result)})

# ---------------------------

@app.route('/services/isTrainingDone/<string:projectName>/<string:trainingName>', methods=['GET'])
def isTrainingDone(projectName, trainingName):
    result = engine.isTrainingDone(projectName, trainingName)
    return jsonify({'data': result})

# ---------------------------

@app.route('/services/UpdateTrainingPage/<string:projectName>/<string:trainingName>/<string:returnType>', methods=['GET'])
def UpdateTrainingPage(projectName, trainingName, returnType):

    # Check if the current user is the project owner
    isProjectOwner = engine.isProjectOwner(projectName)

    # Get all available tests for this training
    availableTests = engine.getAllProjectTests(projectName, trainingName)

    # Get training info data
    trainingInfoData = engine.getTrainingInfoData(projectName, trainingName)

    # Init the AddNetworkTest form data
    formAddNetworkTest = AddNetworkTestForm()
    if trainingInfoData['webTrainingProjectDetails']['available'] == True:
        formAddNetworkTest.networkArhitecture.data = trainingInfoData['webTrainingProjectDetails']['network_file']
        formAddNetworkTest.trainedFile.data = trainingInfoData['webTrainingProjectDetails']['training_file']

    if returnType == "html":
        return render_template('ajax_training_page.html', projectName = projectName, trainingName = trainingName, 
        isProjectOwner = isProjectOwner, formAddNetworkTest = formAddNetworkTest, trainingInfoData = trainingInfoData, availableTests = availableTests)
    elif returnType == "json":
        return jsonify({'data': render_template('ajax_training_page.html', projectName = projectName, trainingName = trainingName, 
        isProjectOwner = isProjectOwner, formAddNetworkTest = formAddNetworkTest, trainingInfoData = trainingInfoData, availableTests = availableTests)})

# ---------------------------

@app.route('/services/displayNetworkConfig/<string:projectName>/<string:networkConfigName>', methods=['GET'])
def displayNetworkConfig(projectName, networkConfigName):
    print "blaaa: " + networkConfigName
    result = {}
    result['networkConfigurationData'] = engine.getNetworkConfigurationData(projectName, networkConfigName)
    return jsonify({'data': render_template('ajax_display_network_config.html', result = result)})

# ---------------------------

@app.route('/services/displayTrainingConfig/<string:projectName>/<string:trainingConfigName>', methods=['GET'])
def displayTrainingConfig(projectName, trainingConfigName):
    result = {}
    result['trainingConfigurationData'] = engine.getTrainingConfigurationData(projectName, trainingConfigName)
    return jsonify({'data': render_template('ajax_display_training_config.html', result = result)})

@app.route('/services/getProjectTrainingsName/<string:projectName>', methods=['GET'])
def getProjectTrainingsName(projectName):
    result = engine.getProjectTrainingsNames(projectName)
    return jsonify({'data': result})

# ---------------------------

@app.route('/services/getTrainingEpochsName/<string:projectName>/<string:trainingName>', methods=['GET'])
def getTrainingEpochsName(projectName, trainingName):
    result = engine.getTrainingEpochsNames(projectName, trainingName)
    return jsonify({'data': result})


# ---------------------------

@app.route('/services/SaveNetworkConfigFileFromGUI', methods=["POST"])
def saveNetworkConfigFileFromGUI():
    if request.method == "POST":
        data = json.loads(request.form['json_str'])
        projectName = request.form['project_name']
        networkConfigName = request.form['cfg_name']
        return engine.saveNetworkConfigFile(data, projectName, networkConfigName)

# -------------------------------------------------------------------------------------
#### Home page
# -------------------------------------------------------------------------------------
@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', title = 'neXuralNet Project')




# -------------------------------------------------------------------------------------
#### Dashboard page
# -------------------------------------------------------------------------------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    form = CreateProjectForm()
    existingProjects = engine.getAllProjects()
   
    if request.method == 'POST':
        if form.validate() == False:
            for fieldName, errorMessages in form.errors.iteritems():
                for err in errorMessages:
                    flash(err, 'danger')
            return render_template('dashboard.html', title = 'Panou de control | neXuralNet Project', form = form, existingProjects = existingProjects)
        else:
            projectName = engine.cleanAlphanumericString(form.projectName.data)
            if engine.addProject(projectName, form.accessCode.data) == True:
                flash('Proiectul a fost creat cu succes!', 'success')
                redirectUrl = '/project/' + projectName
                return redirect(redirectUrl)
            else:
                flash('Exista deja un proiect cu acest nume!', 'danger')
                return render_template('dashboard.html', title = 'Panou de control | neXuralNet Project', form = form, existingProjects = existingProjects)
    elif request.method == 'GET':
        return render_template('dashboard.html', title = 'Panou de control | neXuralNet Project', form = form, existingProjects = existingProjects)




# -------------------------------------------------------------------------------------
#### Manage project pages
# -------------------------------------------------------------------------------------
@app.route('/project/<string:projectName>')
def project(projectName):
    isProjectOwner = engine.isProjectOwner(projectName)
    availableNetworkArhitectures = engine.getAllNetworkArhitecturesFiles(projectName)
    availableTrainingFiles = engine.getAllTriningFiles(projectName)
    availableTrainingDataSets = engine.getAllProjectDatasets(projectName)
    availableTrainings = engine.getAllTrainings(projectName)

    formAddTrainingFile = AddTrainingFileForm()
    formAddNetworkFile = AddNetworkFileForm()

    formAddNetworkTraining = AddNetworkTrainingForm()
    formAddNetworkTraining.setChoices(availableNetworkArhitectures, availableTrainingFiles, availableTrainingDataSets)
    
    hasProjectTrainings = engine.hasProjectTrainings(projectName)

    return render_template('project.html', title = 'Vizualizare proiect | neXuralNet Project', projectName = projectName, isProjectOwner = isProjectOwner, 
        formAddTrainingFile = formAddTrainingFile, formAddNetworkFile = formAddNetworkFile, formAddNetworkTraining = formAddNetworkTraining, hasProjectTrainings = hasProjectTrainings,
        availableNetworkArhitectures = availableNetworkArhitectures, availableTrainingFiles = availableTrainingFiles, availableTrainings = availableTrainings)

# ---------------------------

@app.route('/secureProject/<string:projectName>', methods=['GET', 'POST'])
def secureProject(projectName):
    if engine.isProjectOwner(projectName) == True:
        flash('Ati fost autentificat ca proprietar al acestui proiect!', 'success')
        redirectUrl = '/project/' + projectName
        return redirect(redirectUrl)

    form = SecureProjectForm()
   
    if request.method == 'POST':
        if form.validate() == False:
            for fieldName, errorMessages in form.errors.iteritems():
                for err in errorMessages:
                    flash(err, 'danger')
            return render_template('secure_project.html', title = 'Validare acces proiect | neXuralNet Project', form = form, projectName = projectName)
        else:
            if engine.checkAccessCode(projectName, form.accessCode.data) == True:
                flash('Ati fost autentificat ca proprietar al acestui proiect!', 'success')
                redirectUrl = '/project/' + projectName
                return redirect(redirectUrl)
            else:
                flash('Codul de acces nu este corect!', 'danger')
                return render_template('secure_project.html', title = 'Validare acces proiect | neXuralNet Project', form = form, projectName = projectName)
    elif request.method == 'GET':
        return render_template('secure_project.html', title = 'Validare acces proiect | neXuralNet Project', form = form, projectName = projectName)

# ---------------------------

@app.route('/AddNetworkFile/<string:projectName>', methods=['POST'])
def addNetworkFile(projectName):
    redirectUrl = '/project/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    form = AddNetworkFileForm()
    if request.method == 'POST':
        if form.validate() == False:
            for fieldName, errorMessages in form.errors.iteritems():
                for err in errorMessages:
                    flash(err, 'danger')
        else:
            f = form.networkFile.data
            filename = secure_filename(f.filename)
            networkFilesDirectory = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['NETWORK_FILES_FOLDER_NAME'])
            engine.createDirectory(networkFilesDirectory)
            fileSave = os.path.join(networkFilesDirectory, filename)
            if engine.fileExists(fileSave) == True:
                flash('Exista deja un fisier de configurare cu acest nume!', 'warning')
                return redirect(redirectUrl)
            f.save(fileSave)
            flash('Fisierul de configurare a fost adaugat cu succes!', 'success')
        return redirect(redirectUrl)

# ---------------------------

@app.route('/deleteConfigFile/<string:projectName>/<string:networkConfigFile>')
def deleteConfigFile(projectName, networkConfigFile):
    redirectUrl = '/project/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    if engine.isSafeToDeleteThis(projectName, networkConfigFile, "network_config") == False:
        flash('Fisierul este utilizat intr-unul sau mai multe antrenamente. Pentru a-l sterge, va rugam sa stergeti prma data antrenamentele ce il utilizeaza!', 'warning')
        return redirect(redirectUrl)

    path = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['NETWORK_FILES_FOLDER_NAME'], networkConfigFile)
    if engine.fileExists(path) == True:
        os.remove(path)
    else:
        flash('Fisierul nu exista sau nu a putut fi sters!', 'warning')
        return redirect(redirectUrl)

    flash('Fisierul de configurare a fost sters cu succes!', 'success')
    return redirect(redirectUrl)

# ---------------------------

@app.route('/AddTrainingFile/<string:projectName>', methods=['POST'])
def addTrainingFile(projectName):
    redirectUrl = '/project/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    form = AddTrainingFileForm()
    if request.method == 'POST':
        if form.validate() == False:
            for fieldName, errorMessages in form.errors.iteritems():
                for err in errorMessages:
                    flash(err, 'danger')
        else:
            f = form.trainingFile.data
            filename = secure_filename(f.filename)
            trainingFilesDirectory = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAINING_FILES_FOLDER_NAME'])
            engine.createDirectory(trainingFilesDirectory)
            fileSave = os.path.join(trainingFilesDirectory, filename)
            if engine.fileExists(fileSave):
                flash('Exista deja un fisier de configurare cu acest nume!', 'warning')
                return redirect(redirectUrl)
            f.save(fileSave)
            flash('Fisierul de antrenament a fost adaugat cu succes!', 'success')
        return redirect(redirectUrl)

# ---------------------------

@app.route('/deleteTrainingFile/<string:projectName>/<string:trainingConfigFile>')
def deleteTrainingFile(projectName, trainingConfigFile):
    redirectUrl = '/project/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    if engine.isSafeToDeleteThis(projectName, trainingConfigFile, "training_config") == False:
        flash('Fisierul este utilizat intr-unul sau mai multe antrenamente. Pentru a-l sterge, va rugam sa stergeti prma data antrenamentele ce il utilizeaza!', 'warning')
        return redirect(redirectUrl)

    path = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAINING_FILES_FOLDER_NAME'], trainingConfigFile)
    if engine.fileExists(path) == True:
        os.remove(path)
    else:
        flash('Fisierul nu exista sau nu a putut fi sters!', 'warning')
        return redirect(redirectUrl)

    flash('Fisierul de configurare a fost sters cu succes!', 'success')
    return redirect(redirectUrl)

# ---------------------------

@app.route('/downloadConfigFile/<string:projectName>/<string:configType>/<string:fileName>')
def downloadConfigFile(projectName, configType, fileName):
    if configType == "netConfig":
        filePath = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['NETWORK_FILES_FOLDER_NAME'], fileName)
    elif configType == "trainConfig":
        filePath = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAINING_FILES_FOLDER_NAME'], fileName)
    else:
        flash('Fisierul selectat nu se poate descarca!', 'danger')
        return redirect('/project/' + projectName)
    return send_file(filePath)

# ---------------------------

@app.route('/downloadExampleFile/<string:fileName>')
def downloadExampleFile(fileName):
    filePath = os.path.join('..', app.config['GENERAL_FILES_FOLDER_NAME'], fileName)
    return send_file(filePath)




# -------------------------------------------------------------------------------------
#### Manage project datasets
# -------------------------------------------------------------------------------------
@app.route('/manageProjectDatasets/<string:projectName>')
def manageProjectDatasets(projectName):
    isProjectOwner = engine.isProjectOwner(projectName)
    formAddPredefinedDatSet = AddPredefinedDatSetForm()
    availableDataSets = engine.getAllProjectDatasets(projectName)
    return render_template('manage_project_datasets.html', title = 'Gestionare dataseturi | neXuralNet Project', projectName = projectName, isProjectOwner = isProjectOwner, availableDataSets = availableDataSets, formAddPredefinedDatSet = formAddPredefinedDatSet)

# ---------------------------

# TODO: Rewrite this function !!!
@app.route('/addPredefinedDataSet/<string:projectName>', methods=['POST'])
def addPredefinedDataSet(projectName):
    redirectUrl = '/manageProjectDatasets/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    form = AddPredefinedDatSetForm()

    if request.method == 'POST':
        if form.validate() == False:
            for fieldName, errorMessages in form.errors.iteritems():
                for err in errorMessages:
                    flash(err, 'danger')
            return redirect(redirectUrl)
        else:
            datasetName = engine.cleanAlphanumericString(form.datasetName.data)
            datasetNamePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['PROJECT_DATASETS_FOLDER_NAME'], datasetName)
            predefinedDataSetType = form.predefinedDataSetType.data

            if engine.dirExists(datasetNamePath) == True:
                flash('Exista deja un set de date cu acest nume!', 'warning')
                return redirect(redirectUrl)

            infoData = {}
            if predefinedDataSetType == "MNIST":
                infoData['trainingDataSource'] = 'MNIST_DATA_FILE'
                infoData['targetDataSource'] = 'MNIST_DATA_FILE'
            else:
                flash('Setul predefinit nu este bun !', 'warning')
                return redirect(redirectUrl)

            engine.createDirectory(datasetNamePath)
            trainDir = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['PROJECT_DATASETS_FOLDER_NAME'], datasetName, "train")
            engine.createDirectory(trainDir)
            targetDir = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['PROJECT_DATASETS_FOLDER_NAME'], datasetName, "target")
            engine.createDirectory(targetDir)
            infoDatasetFile = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['PROJECT_DATASETS_FOLDER_NAME'], datasetName, "info.json")

            if predefinedDataSetType == "MNIST":
                predefinedTrainPath = os.path.join(os.getcwd(), app.config['PROJECT_PREDEFINED_DATASETS_FOLDER_NAME'], "mnist", "train", "train-images.idx3-ubyte")
                predefinedTargetPath = os.path.join(os.getcwd(), app.config['PROJECT_PREDEFINED_DATASETS_FOLDER_NAME'], "mnist", "target", "train-labels.idx1-ubyte")
                shutil.copyfile(predefinedTrainPath, os.path.join(trainDir, "train-images.idx3-ubyte"))
                shutil.copyfile(predefinedTargetPath, os.path.join(targetDir, "train-labels.idx1-ubyte"))

            with open(infoDatasetFile, 'w') as outfile:
                json.dump(infoData, outfile)

            flash('Setul de date a fost adaugat cu succes!', 'success')
            return redirect(redirectUrl)

# ---------------------------

@app.route('/deleteDataset/<string:projectName>/<string:datasetName>')
def deleteDataset(projectName, datasetName):
    redirectUrl = '/manageProjectDatasets/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    if engine.isSafeToDeleteThis(projectName, datasetName, "dataset") == False:
        flash('Setul mde date este utilizat intr-unul sau mai multe antrenamente. Pentru a-l sterge, va rugam sa stergeti prma data antrenamentele ce il utilizeaza!', 'warning')
        return redirect(redirectUrl)

    path = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['PROJECT_DATASETS_FOLDER_NAME'], datasetName)
    if engine.dirExists(path) == True:
        shutil.rmtree(path, ignore_errors=True)
    else:
        flash('Setul de date nu exista sau nu a putut fi sters!', 'warning')
        return redirect(redirectUrl)

    flash('Setul de date a fost sters cu succes!', 'success')
    return redirect(redirectUrl)




# -------------------------------------------------------------------------------------
#### Manage project trainings 
# -------------------------------------------------------------------------------------
# TODO: Rewrite this function !!! A lot of mess here!
@app.route('/addNetworkTraining/<string:projectName>', methods=['POST'])
def addNetworkTraining(projectName):
    redirectUrl = '/project/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrlFail)

    availableNetworkArhitectures = engine.getAllNetworkArhitecturesFiles(projectName)
    availableTrainingFiles = engine.getAllTriningFiles(projectName)
    availableTrainingDataSets = engine.getAllProjectDatasets(projectName)

    form = AddNetworkTrainingForm()
    form.setChoices(availableNetworkArhitectures, availableTrainingFiles, availableTrainingDataSets)

    if request.method == 'POST':
        if form.validate() == False:
            for fieldName, errorMessages in form.errors.iteritems():
                for err in errorMessages:
                    flash(err, 'danger')
            return redirect(redirectUrl)
        else:
            trainingName = engine.cleanAlphanumericString(form.trainingName.data)
            trainingPath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName)
            continueExistingTraining = form.continueExistingTraining.data == "yes"

            if engine.dirExists(trainingPath) == True:
                flash('Exista deja un antrenament cu acest nume!', 'warning')
                return redirect(redirectUrl)

            outputTrainedDataFilePath = os.path.join(trainingPath, trainingName + ".json")
            outputTrainerInfoFolderPath = os.path.join(trainingPath, "info/")
            commandsDataFile = os.path.join(outputTrainerInfoFolderPath, "commands.json")
            infoDataFile = os.path.join(trainingPath, "info.json")
            engine.createDirectory(trainingPath)
            engine.createDirectory(outputTrainerInfoFolderPath)
            engine.createDirectory(os.path.join(trainingPath, "tests"))

            if continueExistingTraining == True:
                engine.createDirectory(os.path.join(trainingPath, "weightstocontinue/"))
                # Copy the weights file to this project
                existingTrainingName = form.existingTrainingNameHidden.data
                existingTrainingEpoch = form.existingTrainingEpochHidden.data
                weightsSource = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], existingTrainingName, "info", existingTrainingEpoch)
                if engine.fileExists(weightsSource):
                    weightsToContinueFilePath = os.path.join(os.getcwd(), trainingPath, "weightstocontinue", "weights.json")
                    shutil.copyfile(weightsSource, weightsToContinueFilePath)
                else:
                    flash('Nu s-a putut localiza fisierul ponderilor de pornire pentru noul antrenament!', 'warning')
                    # TODO: Remove created project
                    return redirect(redirectUrl)


            datasetName = engine.cleanAlphanumericString(form.trainingDataSet.data)
            networkArhitecture = form.networkArhitecture.data
            networkArhitecturePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['NETWORK_FILES_FOLDER_NAME'], networkArhitecture)
            trainingFile = form.trainingFile.data
            trainingFilePath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAINING_FILES_FOLDER_NAME'], trainingFile)

            if not engine.fileExists(networkArhitecturePath) == True or not engine.fileExists(trainingFilePath) == True:
                flash('S-au detectat probleme la fisierele de configurare!', 'warning')
                return redirect(redirectUrl)

            infoDatasetFile = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['PROJECT_DATASETS_FOLDER_NAME'], datasetName, "info.json")
            with open(infoDatasetFile) as json_data:
                d = json.load(json_data)
                trainingDS = d['trainingDataSource']

            if trainingDS == "MNIST_DATA_FILE":
                trainDir = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['PROJECT_DATASETS_FOLDER_NAME'], datasetName, "train")
                targetDir = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['PROJECT_DATASETS_FOLDER_NAME'], datasetName, "target")
                dataPath = os.path.join(trainDir, "train-images.idx3-ubyte")
                labelsPath = os.path.join(targetDir, "train-labels.idx1-ubyte")

                if not engine.fileExists(dataPath) == True or not engine.fileExists(labelsPath) == True:
                    flash('Setul de date este invalid!', 'warning')
                    return redirect(redirectUrl)

                trainingDataSource = nexuralnet.trainer.trainingDataSource.MNIST_DATA_FILE
                targetDataSource = nexuralnet.trainer.targetDataSource.MNIST_DATA_FILE
            else:
                flash('Momentan doar setul de date MNIST este suportat!', 'warning')
                return redirect(redirectUrl)

            commandsData = {}
            commandsData['server_command'] = 'train'
            commandsData['network_command'] = 'train'

            with open(commandsDataFile, 'w') as outfile:
                json.dump(commandsData, outfile)

            infoData = {}
            infoData['network_file'] = networkArhitecture
            infoData['training_file'] = trainingFile
            infoData['dataset'] = datasetName
            infoData['timestamp'] = time.strftime("%H:%M:%S - (%d/%m/%Y)")

            with open(infoDataFile, 'w') as outfile:
                json.dump(infoData, outfile)


            if continueExistingTraining == True:
                result = webtasks.trainNetworkTaskFromOtherTraining.delay(networkArhitecturePath, trainingFilePath, weightsToContinueFilePath, dataPath, labelsPath, outputTrainedDataFilePath, outputTrainerInfoFolderPath, trainingDS, trainingDS)
            else:
                result = webtasks.trainNetworkTask.delay(networkArhitecturePath, trainingFilePath, dataPath, labelsPath, outputTrainedDataFilePath, outputTrainerInfoFolderPath, trainingDS, trainingDS)
            flash('Antrenamentul a fost adaugat cu succes!', 'success')
            return redirect(redirectUrl)

# ---------------------------

@app.route('/viewTraining/<string:projectName>/<string:trainingName>')
def viewTraining(projectName, trainingName):
    htmlPage = UpdateTrainingPage(projectName, trainingName, "html")
    return render_template('view_training.html', title = 'Vizualizare antrenament | neXuralNet Project', projectName = projectName, trainingName = trainingName, htmlPage = Markup(htmlPage))

# -----------------------------------------------------------------------------------------------------------------------

@app.route('/deleteTraining/<string:projectName>/<string:trainingName>')
def deleteTraining(projectName, trainingName):
    redirectUrl = '/project/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    path = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName)
    if engine.dirExists(path) == True:
        shutil.rmtree(path, ignore_errors=True)
    else:
        flash('Antrenamentul nu exista sau nu a putut fi sters!', 'warning')
        return redirect(redirectUrl)

    flash('Antrenamentul a fost sters cu succes!', 'success')
    return redirect(redirectUrl)




# -------------------------------------------------------------------------------------
#### Manage project tests
# -------------------------------------------------------------------------------------
@app.route('/addNetworkTest/<string:projectName>/<string:trainingName>', methods=['POST'])
def addNetworkTest(projectName, trainingName):
    redirectUrl = '/viewTraining/' + projectName + "/" + trainingName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    form = AddNetworkTestForm()

    if request.method == 'POST':
        if form.validate() == False:
            for fieldName, errorMessages in form.errors.iteritems():
                for err in errorMessages:
                    flash(err, 'danger')
            return redirect(redirectUrl)
        else:
            testName = engine.cleanAlphanumericString(form.testName.data)
            testDir = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, app.config['TESTS_FILES_FOLDER_NAME'], testName)
            if engine.dirExists(testDir) == True:
                flash('Exista un test cu acest nume!', 'danger')
                return redirect(redirectUrl)
            else:
                engine.addTest(projectName, trainingName, testName, form.networkArhitecture.data, form.trainedFile.data, form.imageFile.data, form.readType.data)
                flash('Testul a fost adaugat cu succes!', 'success')
                return redirect(redirectUrl)

# ---------------------------

@app.route('/getTestFilterImage/<string:projectName>/<string:trainingName>/<string:testName>/<path:filename>')
def getTestFilterImage(projectName, trainingName, testName, filename):
    path = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, app.config['TESTS_FILES_FOLDER_NAME'], testName)
    return send_from_directory(path, filename)

# ---------------------------

@app.route('/deleteTest/<string:projectName>/<string:trainingName>/<string:testName>')
def deleteTest(projectName, trainingName, testName):
    redirectUrl = '/viewTraining/' + projectName + "/" + trainingName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    path = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, app.config['TESTS_FILES_FOLDER_NAME'], testName)
    if engine.dirExists(path) == True:
        shutil.rmtree(path, ignore_errors=True)
    else:
        flash('Testul nu exista sau nu a putut fi sters!', 'warning')
        return redirect(redirectUrl)

    flash('Fisierul de configurare a fost sters cu succes!', 'success')
    return redirect(redirectUrl)