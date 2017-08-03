from wtforms import TextField, SubmitField, SelectField, PasswordField
from wtforms import validators, ValidationError
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired


class CreateProjectForm(FlaskForm):
   projectName = TextField("Nume proiect:",[validators.Required(message='Va rugam sa alegeti un nume sugestiv pentru acest proiect.')])
   accessCode = PasswordField('Cod de acces:', [
        validators.DataRequired(message='Va rugam sa introduceti un cod personal de acces.'),
        validators.EqualTo('confirm', message='Parolele trebuie sa fie indentice.')
    ])
   confirm = PasswordField('Repetati codul de acces:')
   submit = SubmitField("Adauga")


class SecureProjectForm(FlaskForm):
   accessCode = PasswordField("Cod de acces:",[validators.DataRequired(message='Va rugam sa introduceti un cod personal de acces.')])
   submit = SubmitField("Validare")


class AddTrainingFileForm(FlaskForm):
   trainingFile = FileField("Fisier de antrenament:", validators=[FileRequired(message='Va rugam sa selectati un fisier de configurare.'), FileAllowed(['json'], 'Sunt acceptate doar fisirele json.')])
   submit = SubmitField("Adauga")


class AddNetworkFileForm(FlaskForm):
   networkFile = FileField("Fisier de configurare:", validators=[FileRequired(message='Va rugam sa selectati un fisier de configurare.'), FileAllowed(['json'], 'Sunt acceptate doar fisirele json.')])
   submit = SubmitField("Adauga")


class AddNetworkTestForm(FlaskForm):
	testName = TextField("Nume test:", [validators.Required(message='Va rugam sa alegeti un nume sugestiv pentru acest test.')])
	networkArhitecture = TextField('Arhitectura retelei:', [validators.Required(message='Va rugam sa selectati o arhitectura din cele disponibile, sau daca nu exista, va rugam sa adaugati una.')])
	trainedFile = TextField('Antrenament:', [validators.Required(message='Va rugam sa selectati un antrenament sau daca nu exista, puteti efectua unul nou.')])
	imageFile = FileField("Imagine:", validators=[FileRequired(message='Va rugam sa selectati o imagine pentru care sa generati testul curent.'), FileAllowed(['jpg', 'jpeg', 'png', 'bmp'], 'Sunt acceptate doar fisirele de tip imagine.')])
	readType = SelectField('Mod citire imagine:', [validators.Required(message='Va rugam sa selectati tipul imaginii utilizate in testul curent.')], choices = [('0', '1 canal'), ('1', '3 canale')])
	submit = SubmitField("Adauga")


class AddNetworkTrainingForm(FlaskForm):
	trainingName = TextField("Nume antrenament:", [validators.Required(message='Va rugam sa alegeti un nume sugestiv pentru acest antrenament.')])
	networkArhitecture = SelectField('Arhitectura retelei:', [validators.Required(message='Va rugam sa selectati o arhitectura din cele disponibile, sau daca nu exista, va rugam sa adaugati una.')], choices = [])
	trainingFile = SelectField('Fisier de antrenament:', [validators.Required(message='Va rugam sa selectati un fisier de antrenament din cele disponibile, sau daca nu exista, va rugam sa adaugati unul.')], choices = [])
	trainingDataSet = SelectField('Set de date:', [validators.Required(message='Va rugam sa selectati un set de date, sau daca nu exista, va rugam sa adaugati unul nou din sectiunea corespunzatoare.')], choices = [])
	submit = SubmitField("Porneste antrenamentul")

	def setChoices(self, availableNetworkArhitectures, availableTrainingFiles, availableTrainingDataSets):
		self.networkArhitecture.choices = availableNetworkArhitectures.items()
		self.trainingFile.choices = availableTrainingFiles.items()
		self.trainingDataSet.choices = [(status, status) for status in availableTrainingDataSets]


class AddPredefinedDatSetForm(FlaskForm):
	datasetName = TextField("Nume set de date:", [validators.Required(message='Va rugam sa alegeti un nume sugestiv pentru acest set de date.')])
	predefinedDataSetType = SelectField('Alegeti setul predefinit:', [validators.Required(message="Va rugam sa selectati un set de date din cele predefinite.")], choices = [('MNIST', 'Setul de date MNIST')])
	submit = SubmitField("Adauga")