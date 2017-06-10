from flask_wtf import Form
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField

from wtforms import validators, ValidationError

class CreateProjectForm(Form):
   projectName = TextField("Nume",[validators.Required(message='Va rugam sa alegeti un nume sugestiv pentru acest proiect.')])
   accessCode = TextField("Cod de acces",[validators.Required(message='Va rugam sa introduceti un cod personal de acces.')])
   
   submit = SubmitField("Creeaza proiectul")