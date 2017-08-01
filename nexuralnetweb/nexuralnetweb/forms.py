from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField, PasswordField
from wtforms import validators, ValidationError
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

class CreateProjectForm(FlaskForm):
   projectName = TextField("Nume proiect:",[validators.Required(message='Va rugam sa alegeti un nume sugestiv pentru acest proiect.')])
   accessCode = PasswordField('Cod de acces:', [
        validators.DataRequired(message='Va rugam sa introduceti un cod personal de acces.'),
        validators.EqualTo('confirm', message='Parolele trebuie sa fie indentice!')
    ])
   confirm = PasswordField('Repetati codul de acces:')
   submit = SubmitField("Adauga")

class SecureProjectForm(FlaskForm):
   accessCode = PasswordField("Cod de acces:",[validators.DataRequired(message='Va rugam sa introduceti un cod personal de acces.')])
   submit = SubmitField("Trimite")

class AddTrainingFileForm(FlaskForm):
   trainingFile = FileField("Fisier de antrenament:", validators=[FileRequired(), FileAllowed(['json'], 'Sunt acceptate doar fisirele json!')])
   submit = SubmitField("Trimite")

class AddNetworkFileForm(FlaskForm):
   networkFile = FileField("Fisier de configurare:", validators=[FileRequired(), FileAllowed(['json'], 'Sunt acceptate doar fisirele json!')])
   submit = SubmitField("Trimite")

class AddNetworkTestForm(FlaskForm):
	testName = TextField("Nume test:", [validators.Required(message='Va rugam sa alegeti un nume sugestiv pentru acest test.')])
	networkArhitecture = TextField('Arhitectura retelei:', [validators.Required()])
	trainedFile = TextField('Antrenament:', [validators.Required()])
	imageFile = FileField("Imagine:", validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'bmp'], 'Sunt acceptate doar fisirele de tip imagine!')])
	readType = SelectField('Mod citire imagine:', [validators.Required()], choices = [('0', '1 canal'), ('1', '3 canale')])
	submit = SubmitField("Trimite")

class AddNetworkTrainingForm(FlaskForm):
	trainingName = TextField("Nume antrenament:", [validators.Required(message='Va rugam sa alegeti un nume sugestiv pentru acest antrenament.')])
	networkArhitecture = SelectField('Arhitectura retelei:', [validators.Required()], choices = [])
	trainingFile = SelectField('Fisier de antrenament:', [validators.Required()], choices = [])
	trainingDataSet = SelectField('Set de date:', [validators.Required()], choices = [])
	submit = SubmitField("Porneste antrenamentul")

	def setChoices(self, availableNetworkArhitectures, availableTrainingFiles, availableTrainingDataSets):
		self.networkArhitecture.choices = availableNetworkArhitectures.items()
		self.trainingFile.choices = availableTrainingFiles.items()
		self.trainingDataSet.choices = [(status, status) for status in availableTrainingDataSets]


class AddPredefinedDatSetForm(FlaskForm):
	datasetName = TextField("Nume set de date:", [validators.Required(message='Va rugam sa alegeti un nume sugestiv pentru acest set de date.')])
	predefinedDataSetType = SelectField('Alegeti setul predefinit:', [validators.Required()], choices = [('MNIST', 'Setul de date MNIST')])
	submit = SubmitField("Adauga")