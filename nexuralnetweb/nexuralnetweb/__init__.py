from flask import Flask
from flask_celery import make_celery

app = Flask(__name__)

app.config.from_object('config')
celery = make_celery(app)

import nexuralnetweb.views