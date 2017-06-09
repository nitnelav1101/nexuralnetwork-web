from flask import render_template
from nexuralnetweb import app

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='neXuralNet Project'
    )

@app.route('/panou')
def dashboard():
    """Renders the dashboadr page."""
    return render_template(
        'dashboard.html',
        title='neXuralNet | Panou de control'
    )
