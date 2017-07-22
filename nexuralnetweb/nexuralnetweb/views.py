from flask import flash, redirect, render_template, request, url_for, session, send_file, send_from_directory
from werkzeug.utils import secure_filename, MultiDict
from nexuralnetweb import app
from forms import CreateProjectForm, SecureProjectForm, AddTrainingFileForm, AddNetworkFileForm, AddNetworkTestForm, AddNetworkTrainingForm, AddPredefinedDatSetForm
import engine
import os
import shutil
import json
import nexuralnet
import threading
import nexuralnetengine
import StringIO
import base64
import matplotlib.pyplot as plt
from nexuralnetweb import celery

@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'index.html',
        title = 'neXuralNet Project'
    )



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

    return render_template('project.html', title = 'Vizualizare proiect | neXuralNet Project', projectName = projectName, isProjectOwner = isProjectOwner, formAddTrainingFile = formAddTrainingFile, 
        formAddNetworkFile = formAddNetworkFile, formAddNetworkTraining = formAddNetworkTraining, 
        availableNetworkArhitectures = availableNetworkArhitectures, availableTrainingFiles = availableTrainingFiles, availableTrainings = availableTrainings)



@app.route('/getFileFromTest/<string:projectName>/<string:testName>/<path:filename>')
def getFileFromTest(projectName, testName, filename):
    path = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TESTS_FILES_FOLDER_NAME'], testName)
    return send_from_directory(path, filename)



@app.route('/viewTest/<string:projectName>/<string:testName>')
def viewTest(projectName, testName):
    isProjectOwner = engine.isProjectOwner(projectName)
    filtersImages = engine.getAllTestFilters(projectName, testName)
    
    resultType, resultMessage = engine.getResult(projectName, testName)
    return render_template('view_test.html', title = 'Vizualizare test | neXuralNet Project', projectName = projectName, testName = testName, isProjectOwner = isProjectOwner, 
        resultType = resultType, resultMessage = resultMessage, filtersImages = filtersImages)



@app.route('/manageProjectDatasets/<string:projectName>')
def manageProjectDatasets(projectName):
    isProjectOwner = engine.isProjectOwner(projectName)
    formAddPredefinedDatSet = AddPredefinedDatSetForm()
    availableDataSets = engine.getAllProjectDatasets(projectName)
    return render_template('manage_project_datasets.html', title = 'Gestionare dataseturi | neXuralNet Project', projectName = projectName, isProjectOwner = isProjectOwner, availableDataSets = availableDataSets, formAddPredefinedDatSet = formAddPredefinedDatSet)



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



@app.route('/addNetworkTest/<string:projectName>', methods=['POST'])
def addNetworkTest(projectName):
    redirectUrlFail = '/project/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrlFail)

    availableTrainedFiles = engine.getAllTrainedNetworkFiles(projectName)
    availableNetworkArhitectures = engine.getAllNetworkArhitecturesFiles(projectName)
    form = AddNetworkTestForm()
    form.setArhitecturesChoices(availableNetworkArhitectures, availableTrainedFiles)

    if request.method == 'POST':
        if form.validate() == False:
            for fieldName, errorMessages in form.errors.iteritems():
                for err in errorMessages:
                    flash(err, 'danger')
            return redirect(redirectUrlFail)
        else:
            testName = engine.cleanAlphanumericString(form.testName.data)
            testDir = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TESTS_FILES_FOLDER_NAME'], testName)
            if engine.dirExists(testDir) == True:
                flash('Exista un test cu acest nume!', 'danger')
                return redirect(redirectUrlFail)
            else:
                engine.addTest(projectName, testName, form.networkArhitecture.data, form.trainedFile.data, form.imageFile.data, form.readType.data)
                redirectUrlSuccess = '/viewTest/' + projectName + '/' + testName
                flash('Testul a fost adaugat cu succes!', 'success')
                return redirect(redirectUrlSuccess)



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

            if engine.dirExists(trainingPath) == True:
                flash('Exista deja un antrenament cu acest nume!', 'warning')
                return redirect(redirectUrl)

            outputTrainedDataFilePath = os.path.join(trainingPath, trainingName + ".json")
            outputTrainerInfoFolderPath = os.path.join(trainingPath, "info/")
            commandsDataFile = os.path.join(outputTrainerInfoFolderPath, "commands.json")
            infoDataFile = os.path.join(trainingPath, "info.json")
            engine.createDirectory(trainingPath)
            engine.createDirectory(outputTrainerInfoFolderPath)

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

            with open(infoDataFile, 'w') as outfile:
                json.dump(infoData, outfile)

            result = trainQuery.delay(networkArhitecturePath, trainingFilePath, dataPath, labelsPath, outputTrainedDataFilePath, outputTrainerInfoFolderPath, trainingDS, trainingDS)
            flash('Antrenamentul a fost adaugat cu succes!', 'success')
            return redirect(redirectUrl)

@celery.task()
def trainQuery(networkArhitecturePath, trainingFilePath, dataPath, labelsPath, outputTrainedDataFilePath, outputTrainerInfoFolderPath, trainingDataSource, targetDataSource):
	print 'Started training...'
	if trainingDataSource == "MNIST_DATA_FILE":
		internalTrainingDataSource = nexuralnet.trainer.trainingDataSource.MNIST_DATA_FILE
		internalTargetDataSource = nexuralnet.trainer.targetDataSource.MNIST_DATA_FILE
	trainer = nexuralnet.trainer(networkArhitecturePath, trainingFilePath)
	trainer.train(dataPath, labelsPath, outputTrainedDataFilePath, outputTrainerInfoFolderPath, internalTrainingDataSource, internalTargetDataSource)
	print 'Finished training.'

@app.route('/viewTraining/<string:projectName>/<string:trainingName>')
def viewTraining(projectName, trainingName):
    isProjectOwner = engine.isProjectOwner(projectName)
    trainingStatus = engine.getTrainingStatus(projectName, trainingName)
    trainedFileExists =  engine.trainedFileExists(projectName, trainingName)
    formAddNetworkTest = AddNetworkTestForm()

    infoTrainingDataPath = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, "info.json")
    infoTrainingData = {}
    with open(infoTrainingDataPath) as json_data:
        d = json.load(json_data)
        infoTrainingData['network_file'] = d['network_file']
        infoTrainingData['training_file'] = d['training_file']
        infoTrainingData['dataset'] = d['dataset']

    trainingStats, validationStats, trainingInfo = nexuralnetengine.getTrainingStats(projectName, trainingName)

    img = StringIO.StringIO()

    data = json.load(open(os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAININGS_FOLDER_NAME'], trainingName, "info", "trainerInfo.json")))
    learning_rate_data = []
    epoch_mean_error_data = []
    validation_mean_error = []

    for x in range(0, int(trainingInfo['epochs_num'])):
    	learning_rate_data.append(float(data['epochs']['epoch' + str(x)]['learning_rate']))
    	epoch_mean_error_data.append(float(data['epochs']['epoch' + str(x)]['training_mean_error']))
    	validation_mean_error.append(float(data['epochs']['epoch' + str(x)]['validation_mean_error']))

    plt.plot(learning_rate_data)
    plt.xlabel('Graficul ratei de invatare')
    plt.savefig(img, format='png')
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue())

    formAddNetworkTest.networkArhitecture.data = infoTrainingData['network_file']
    formAddNetworkTest.trainedFile.data = infoTrainingData['training_file']
    return render_template('view_training.html', title = 'Vizualizare antrenament | neXuralNet Project', projectName = projectName, trainingName = trainingName, 
        isProjectOwner = isProjectOwner, trainingStatus = trainingStatus, trainedFileExists = trainedFileExists, formAddNetworkTest = formAddNetworkTest, infoTrainingData = infoTrainingData,
        trainingStats = trainingStats, validationStats = validationStats, trainingInfo = trainingInfo, plot_url=plot_url)




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



@app.route('/downloadExampleFile/<string:filename>')
def downloadExampleFile(filename):
    filePath = os.path.join('..', app.config['GENERAL_FILES_FOLDER_NAME'], filename)
    return send_file(filePath)


@app.route('/deleteConfigFile/<string:projectName>/<string:networkConfigFile>')
def deleteConfigFile(projectName, networkConfigFile):
    redirectUrl = '/project/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    path = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['NETWORK_FILES_FOLDER_NAME'], networkConfigFile)
    if engine.fileExists(path) == True:
        os.remove(path)
    else:
        flash('Fisierul nu exista sau nu a putut fi sters!', 'warning')
        return redirect(redirectUrl)

    flash('Fisierul de configurare a fost sters cu succes!', 'success')
    return redirect(redirectUrl)



@app.route('/deleteTrainingFile/<string:projectName>/<string:trainingConfigFile>')
def deleteTrainingFile(projectName, trainingConfigFile):
    redirectUrl = '/project/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    path = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAINING_FILES_FOLDER_NAME'], trainingConfigFile)
    if engine.fileExists(path) == True:
        os.remove(path)
    else:
        flash('Fisierul nu exista sau nu a putut fi sters!', 'warning')
        return redirect(redirectUrl)

    flash('Fisierul de configurare a fost sters cu succes!', 'success')
    return redirect(redirectUrl)



@app.route('/deleteTest/<string:projectName>/<string:testName>')
def deleteTest(projectName, testName):
    redirectUrl = '/project/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    path = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TESTS_FILES_FOLDER_NAME'], testName)
    if engine.dirExists(path) == True:
        shutil.rmtree(path, ignore_errors=True)
    else:
        flash('Testul nu exista sau nu a putut fi sters!', 'warning')
        return redirect(redirectUrl)

    flash('Fisierul de configurare a fost sters cu succes!', 'success')
    return redirect(redirectUrl)


@app.route('/deleteDataset/<string:projectName>/<string:datasetName>')
def deleteDataset(projectName, datasetName):
    redirectUrl = '/manageProjectDatasets/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    path = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['PROJECT_DATASETS_FOLDER_NAME'], datasetName)
    if engine.dirExists(path) == True:
        shutil.rmtree(path, ignore_errors=True)
    else:
        flash('Setul de date nu exista sau nu a putut fi sters!', 'warning')
        return redirect(redirectUrl)

    flash('Setul de date a fost sters cu succes!', 'success')
    return redirect(redirectUrl)


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