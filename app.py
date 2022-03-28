from flask import Flask, render_template
import sqlite3
import os


app = Flask(__name__)



@app.route("/")
def index():
    return render_template('index.html')


@app.route("/admin")
def admin():
    return render_template('admin.html')


@app.route("/event_manager")
def event_manager():
    return render_template('event_manager.html')

@app.route("/gallery_manager")
def gallery_manager():
    return render_template('gallery_manager.html')

@app.route("/officer_manager")
def officer_manager():
    return render_template('officer_manager.html')

app.run(debug=True)