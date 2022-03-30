from tokenize import String
from flask import Flask, render_template, session, request, flash, redirect, url_for
import sqlite3
import os
from os.path import join, dirname, abspath
from wtforms import TextAreaField, StringField, validators, PasswordField, Form, SubmitField, HiddenField, SelectField
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Sg4&gLK**23S'
UPLOADS_PATH = join(dirname(abspath(__file__)), 'static/uploads/')
UPLOAD_FOLDER = 'app/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_PATH'] = 157286400

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/admin")
def admin():
    return render_template('admin.html')

class AddEvent(Form):
    event = StringField('Event Name', [validators.Length(min=1, max=30)])
    location = StringField('Event Location', [validators.Length(min=1, max=30)])
    time = StringField('Event Time', [validators.Length(min=1, max=30)])
    description = StringField('Event Description', [validators.Length(min=1, max=75)])


@app.route("/event_manager", methods=['GET', 'POST'])
def event_manager():
    form = AddEvent(request.form)
    return render_template('event_manager.html', form=form)


class AddImage(Form):
    image = StringField('Image File', [validators.Length(min=1, max=30)])
    title = StringField('Image Title', [validators.Length(min=1, max=30)])
    description = StringField('Image Description', [validators.Length(min=1, max=75)])

@app.route("/gallery_manager", methods=['GET', 'POST'])
def gallery_manager():
    form = AddImage(request.form)
    return render_template('gallery_manager.html', form=form)


class AddOfficer(Form):
    username = StringField('Username', [validators.Length(min=1, max=30)])
    password = PasswordField('Password', [
            validators.DataRequired(),
            validators.EqualTo('confirm', message='Passwords do not match.')
        ])
    confirm = PasswordField('Confirm Password')

class EditOfficer(Form):
    id = HiddenField("ID")
    username = StringField('Username', [validators.Length(min=1, max=30)])
    password = PasswordField('Password', [
            validators.DataRequired(),
            validators.EqualTo('confirm', message='Passwords do not match.')
        ])
    confirm = PasswordField('Confirm Password')
    update_user = SubmitField()
    remove_user = SubmitField()

@app.route("/officer_manager", methods=['GET', 'POST'])
def officer_manager():
    add = AddOfficer(request.form)
    edit = EditOfficer(request.form)
    conn = get_db_connection()
    officers = conn.execute("SELECT * FROM officers").fetchall()
    conn.close()
    if request.method == 'POST' and add.data:
        flash('The add button was clicked', 'success')
        return render_template('officer_manager.html', officers=officers, add=add, edit=edit)
    return render_template('officer_manager.html', officers=officers, add=add, edit=edit)

class Login(Form):
    username = StringField('Username', [validators.Length(min=1, max=30)])
    password = PasswordField('Password', [validators.DataRequired()])

@app.route('/login', methods=["GET", "POST"])
def login():
    form = Login(request.form)
    try:
        if session['loggedIn'] == True:
            flash('You are already logged in!', 'warning')
            return redirect(url_for('index'))
        else:
            if request.method == 'POST' and form.validate():
                try:
                    username = form.username.data
                    password = form.password.data
                    conn = get_db_connection()
                    user = conn.execute('SELECT * FROM users WHERE username = ?',
                                            (username,)).fetchone()
                    dbPassword = user['password']
                    conn.close()
                    if bcrypt.checkpw(password.encode('utf-8'), dbPassword.encode('utf-8')):
                        session['loggedIn'] = True
                        flash('Login successful', 'success')
                        return redirect(url_for('admin'))
                    else:
                        flash('Username or password is incorrect!', 'danger')
                        return render_template('login.html', form=form)
                except:
                    flash('Username or password is incorrect!', 'danger')
                    return render_template('login.html', form=form)
            return render_template('login.html', form=form)
    except:
        if request.method == 'POST' and form.validate():
                try:
                    username = form.username.data
                    password = form.password.data
                    conn = get_db_connection()
                    user = conn.execute('SELECT * FROM users WHERE username = ?',
                                            (username,)).fetchone()
                    dbPassword = user['password']
                    conn.close()
                    if bcrypt.checkpw(password.encode('utf-8'), dbPassword):
                        session['loggedIn'] = True
                        flash('Login successful', 'success')
                        return redirect(url_for('admin'))
                    else:
                        flash('Username or password is incorrect!', 'danger')
                        return render_template('login.html', form=form)
                except:
                    flash('Username or password is incorrect!', 'danger')
                    return render_template('login.html', form=form)
        return render_template('login.html', form=form)


app.run(debug=True)