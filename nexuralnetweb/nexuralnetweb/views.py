from flask import flash, redirect, render_template, request, url_for, session, send_file, send_from_directory
from werkzeug.utils import secure_filename, MultiDict
from nexuralnetweb import app
from forms import CreateProjectForm, SecureProjectForm, AddTrainingFileForm, AddNetworkFileForm, AddNetworkTestForm, AddNetworkTrainingForm
import engine
import os
import shutil


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
    availableTrainedFiles = engine.getAllTrainedNetworkFiles(projectName)
    availableNetworkArhitectures = engine.getAllNetworkArhitecturesFiles(projectName)
    availableTrainingFiles = engine.getAllTriningFiles(projectName)
    availableTrainingDataSets = engine.getAllTrainedNetworkFiles(projectName)
    availableTests = engine.getAllProjectTests(projectName)

    formAddTrainingFile = AddTrainingFileForm()
    formAddNetworkFile = AddNetworkFileForm()

    formAddNetworkTest = AddNetworkTestForm()
    formAddNetworkTest.setArhitecturesChoices(availableNetworkArhitectures, availableTrainedFiles)

    formAddNetworkTraining = AddNetworkTrainingForm()
    formAddNetworkTraining.setChoices(availableNetworkArhitectures, availableTrainingFiles, availableTrainingDataSets)

    return render_template('project.html', title = 'Vizualizare proiect | neXuralNet Project', projectName = projectName, isProjectOwner = isProjectOwner, formAddTrainingFile = formAddTrainingFile, 
        formAddNetworkFile = formAddNetworkFile, formAddNetworkTest = formAddNetworkTest, formAddNetworkTraining = formAddNetworkTraining, 
        availableNetworkArhitectures = availableNetworkArhitectures, availableTrainingFiles = availableTrainingFiles, availableTests = availableTests)



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
    availableDataSets = MultiDict([('a', 'b'), ('b', 'c')])
    return render_template('manage_project_datasets.html', title = 'Gestionare dataseturi | neXuralNet Project', projectName = projectName, isProjectOwner = isProjectOwner, availableDataSets = availableDataSets)



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
    redirectUrlFail = '/project/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrlFail)

    availableNetworkArhitectures = engine.getAllNetworkArhitecturesFiles(projectName)
    availableTrainingFiles = engine.getAllTriningFiles(projectname)
    availableTrainingDataSets = engine.getAllTrainedNetworkFiles(projectName)

    form = AddNetworkTrainingForm()
    form.setChoices(availableNetworkArhitectures, availableTrainingFiles, availableTrainingDataSets)

    if request.method == 'POST':
        if form.validate() == False:
            for fieldName, errorMessages in form.errors.iteritems():
                for err in errorMessages:
                    flash(err, 'danger')
            return redirect(redirectUrlFail)
        else:
            # TODO: Add the logic
            testName = engine.cleanAlphanumericString(form.testName.data)
            redirectUrlSuccess = '/viewTest/' + projectName + '/' + testName
            flash('Antrenamentul a fost adaugat cu succes!', 'success')
            return redirect(redirectUrlSuccess)




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
    os.remove(path)

    flash('Fisierul de configurare a fost adaugat cu succes!', 'success')
    return redirect(redirectUrl)



@app.route('/deleteTrainingFile/<string:projectName>/<string:trainingConfigFile>')
def deleteTrainingFile(projectName, trainingConfigFile):
    redirectUrl = '/project/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    path = os.path.join(app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TRAINING_FILES_FOLDER_NAME'], trainingConfigFile)
    os.remove(path)

    flash('Fisierul de configurare a fost adaugat cu succes!', 'success')
    return redirect(redirectUrl)



@app.route('/deleteTest/<string:projectName>/<string:testName>')
def deleteTest(projectName, testName):
    redirectUrl = '/project/' + projectName

    if engine.isProjectOwner(projectName) == False:
        flash('Deoarece nu sunteti proprietarul acestui proiect nu puteti efectua aceasta operatiune!', 'warning')
        return redirect(redirectUrl)

    path = os.path.join(os.getcwd(), app.config['BASE_PROJECTS_FOLDER_NAME'], projectName, app.config['TESTS_FILES_FOLDER_NAME'], testName)
    shutil.rmtree(path, ignore_errors=True)

    flash('Fisierul de configurare a fost adaugat cu succes!', 'success')
    return redirect(redirectUrl)