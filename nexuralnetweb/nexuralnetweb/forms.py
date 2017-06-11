from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

class CreateProjectForm(FlaskForm):
   projectName = TextField("Nume proiect:",[validators.Required(message='Va rugam sa alegeti un nume sugestiv pentru acest proiect.')])
   accessCode = TextField("Cod de acces:",[validators.Required(message='Va rugam sa introduceti un cod personal de acces.')])
   submit = SubmitField("Creeaza proiectul")

class SecureProjectForm(FlaskForm):
   accessCode = TextField("Cod de acces:",[validators.Required(message='Va rugam sa introduceti un cod personal de acces.')])
   submit = SubmitField("Trimite")

class AddTrainingFileForm(FlaskForm):
   trainingFile = FileField("Fisier de antrenament:", validators=[FileRequired(), FileAllowed(['json'], 'Sunt acceptate doar fisirele json!')])
   submit = SubmitField("Trimite")

class AddNetworkFileForm(FlaskForm):
   networkFile = FileField("Fisier de configurare:", validators=[FileRequired(), FileAllowed(['json'], 'Sunt acceptate doar fisirele json!')])
   submit = SubmitField("Trimite")

class AddNetworkTestForm(FlaskForm):
	testName = TextField("Nume test:", [validators.Required(message='Va rugam sa alegeti un nume sugestiv pentru acest test.')])
	networkArhitecture = SelectField('Arhitectura retelei:', [validators.Required()], choices = [])
	trainedFile = SelectField('Antrenament:', [validators.Required()], choices = [])
	imageFile = FileField("Imagine:", validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'bmp'], 'Sunt acceptate doar fisirele de tip imagine!')])
	readType = SelectField('Mod citire imagine:', [validators.Required()], choices = [('0', '1 canal'), ('1', '3 canale')])
	submit = SubmitField("Trimite")

	def setArhitecturesChoices(self, availableNetworkArhitectures, availableTrainedFiles):
		self.networkArhitecture.choices = availableNetworkArhitectures.items()
		self.trainedFile.choices = availableTrainedFiles.items()

class AddNetworkTrainingForm(FlaskForm):
	trainingName = TextField("Nume antrenament:", [validators.Required(message='Va rugam sa alegeti un nume sugestiv pentru acest antrenament.')])
	networkArhitecture = SelectField('Arhitectura retelei:', [validators.Required()], choices = [])
	trainingFile = SelectField('Fisier de antrenament:', [validators.Required()], choices = [])
	trainingDataSet = SelectField('Set de date:', [validators.Required()], choices = [])
	trainingDataType = SelectField('Tip date de antrenare:', [validators.Required()], choices = [('IMAGES_DIRECTORY', 'Director de imagini'), ('TXT_DATA_FILE', 'Fisier tensor'), ('MNIST_DATA_FILE', 'Fisier MNIST')])
	targetType = SelectField('Tip date:', [validators.Required()], choices = [('TXT_DATA_FILE', 'Fisier tensor'), ('MNIST_DATA_FILE', 'Fisier MNIST')])
	submit = SubmitField("Trimite")

	def setChoices(self, availableNetworkArhitectures, availableTrainingFiles, availableTrainingDataSets):
		self.networkArhitecture.choices = availableNetworkArhitectures.items()
		self.trainingFile.choices = availableTrainingFiles.items()
		self.trainingDataSet.choices = availableTrainingDataSets.items()