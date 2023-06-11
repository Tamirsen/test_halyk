import os
from flask import render_template, redirect, url_for, flash, request, send_from_directory, jsonify
from flask_login import current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from . import app, services


UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS').split(',')) 

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@login_required
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('/'))
    if request.method == 'POST':
        user = services.login(request.form['username'], request.form['password'], request.form.get('remember_me', False))
        if user is None:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        next_page = services.get_redirect_page(request.args.get('next'))
        return redirect(next_page)
    return render_template('login.html', title='Sign In')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/extract-signature', methods=['GET', 'POST'])
@login_required
def extract_signature():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # add check for file type
            ext = os.path.splitext(filename)[1].lower()
            if ext not in ['.pdf', '.jpg']:
                flash('Unsupported file format')
                return redirect(request.url)

            signatures = services.convert_and_extract_signature(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Return or do something with the signatures...
            return jsonify(signatures=signatures[0], count=signatures[1])
            #return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)