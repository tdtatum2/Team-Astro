from flask import Flask, render_template, session, request, flash
import sqlite3
import os
from wtforms import TextAreaField, StringField, validators, PasswordField, Form, SubmitField, HiddenField, SelectField

app = Flask(__name__)



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

@app.route("/gallery_manager")
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

@app.route("/officer_manager")
def officer_manager():
    form = AddOfficer(request.form)
    return render_template('officer_manager.html', form=form)

app.run(debug=True)