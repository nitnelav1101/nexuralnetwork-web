from flask import flash, redirect, render_template, request, url_for
from nexuralnetweb import app
from forms import CreateProjectForm
from engine import addProject

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title = 'neXuralNet Project'
    )

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """Renders the dashboadr page."""
    form = CreateProjectForm()
   
    if request.method == 'POST':
        if form.validate() == False:
            flash('Toate campurile sunt obligatorii!', 'danger')
            return render_template( 'dashboard.html', title = 'neXuralNet | Panou de control', form = form )
        else:
            if addProject(form.projectName.data) == True:
                flash('Proiectul a fost creat cu succes!', 'success')
                redirectUrl = '/project/' + form.projectName.data
                return redirect(redirectUrl)
            else:
                flash('Exista deja un proiect cu acest nume!', 'danger')
                return render_template( 'dashboard.html', title = 'neXuralNet | Panou de control', form = form )
    elif request.method == 'GET':
        return render_template( 'dashboard.html', title = 'neXuralNet | Panou de control', form = form )

@app.route('/project/<string:projectName>')
def project(projectName):
    return render_template('project.html', projectName = projectName)