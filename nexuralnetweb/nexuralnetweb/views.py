from nexuralnetweb import app

@app.route('/')
def index():
    return 'NeXuraNet project is alive!'