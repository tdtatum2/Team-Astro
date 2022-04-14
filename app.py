from datetime import datetime, time, date
from random import choices
from flask import Flask, render_template, session, request, flash, redirect, url_for
from flask_mail import Mail, Message
import sqlite3
import os
from os.path import join, dirname, abspath
from wtforms import StringField, validators, PasswordField, Form, SubmitField, HiddenField, SelectField, TimeField, DateField, EmailField, TextAreaField, IntegerField, RadioField
import bcrypt
from werkzeug.utils import secure_filename

mail = Mail()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Sg4&gLK**23S'
UPLOADS_PATH = join(dirname(abspath(__file__)), 'static/uploads/')
UPLOAD_FOLDER = 'app/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_PATH'] = 157286400
app.config.update(dict(
    MAIL_SERVER = 'smtp.googlemail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'fhsu.astronomy.inquiries',
    MAIL_PASSWORD = 'wtapiefwsmsqvzrk',
))
mail.init_app(app)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.template_filter()
def format_time(value):
    new_time = datetime.strptime(value, '%H:%M:%S').time()
    new_time = time.strftime(new_time, '%I:%M %p')
    return new_time

@app.template_filter()
def format_date(value):
    new_date = datetime.strptime(value, '%Y-%m-%d').date()
    new_date = date.strftime(new_date, "%B %d, %Y")
    return new_date


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/admin")
def admin():
    try:
        if(session['loggedIn'] == False):
            return redirect(url_for('login'))
    except:
        session['loggedIn'] = False
        return redirect(url_for('login'))
    return render_template('admin.html')

class AddEvent(Form):
    event = StringField('Event Name', [validators.Length(min=1, max=30)])
    location = StringField('Event Location', [validators.Length(min=1, max=30)])
    date = DateField('Event Date')
    time = TimeField('Event Time', format='%H:%M')
    description = StringField('Event Description', [validators.Length(min=0, max=75)])
    weather = SelectField('Event Weather', choices=[('question-circle', 'TBD'), ('sun', 'Clear Day'), ('stars', 'Clear Night'), ('cloud-moon', 'Cloudy Night'), ('cloud-sun', 'Cloudy Day'), ('cloud-rain', 'Rainy'), ('wind', 'Windy'), ('cloud-snow', 'Snowy'), ('x-circle', 'Canceled')])
    add_event = SubmitField()

class EditEvent(Form):
    id = HiddenField()
    event = StringField('Event Name', [validators.Length(min=1, max=30)])
    location = StringField('Event Location', [validators.Length(min=1, max=30)])
    date = DateField('Event Date')
    time = TimeField('Event Time', format='%H:%M:%S')
    description = StringField('Event Description', [validators.Length(min=0, max=75)])
    weather = SelectField('Event Weather', choices=[('question-circle', 'TBD'), ('sun', 'Clear Day'), ('stars', 'Clear Night'), ('cloud-moon', 'Cloudy Night'), ('cloud-sun', 'Cloudy Day'), ('cloud-rain', 'Rainy'), ('wind', 'Windy'), ('cloud-snow', 'Snowy'), ('x-circle', 'Canceled')])
    edit_event = SubmitField()

class RemoveEvent(Form):
    id = HiddenField()
    remove_event = SubmitField()

@app.route("/event_manager", methods=['GET', 'POST'])
def event_manager():
    add_event = AddEvent(request.form)
    edit_event = EditEvent(request.form)
    remove_event = RemoveEvent(request.form)
    date = datetime.today()
    check = date.strftime("%Y-%m-%d")
    conn = get_db_connection()
    events = conn.execute("SELECT * FROM events").fetchall()
    for event in events:
        if (event[3] < check):
            conn.execute("DELETE FROM events WHERE id = ?", (event[0],))
            conn.commit()
    events = conn.execute("SELECT * FROM events").fetchall()
    conn.close()
    try:
        if(session['loggedIn'] == False):
            return redirect(url_for('login'))
    except:
        session['loggedIn'] = False
        return redirect(url_for('login'))
    try:
        if request.method == 'POST':
            if add_event.add_event.data and add_event.validate():
                try:
                    event = add_event.event.data
                    location = add_event.location.data
                    raw_date = add_event.date.data
                    date = str(raw_date)
                    raw_time = add_event.time.data
                    time = str(raw_time)
                    description = add_event.description.data
                    weather = add_event.weather.data
                    conn = get_db_connection()
                    conn.execute("INSERT INTO events(event, location, date, time, description, weather) VALUES(?, ?, ?, ?, ?, ?)", (event, location, date, time, description, weather))
                    conn.commit()
                    events = conn.execute("SELECT * FROM events").fetchall()
                    conn.close()
                    flash('Event successfully added!', 'success')
                    return render_template('event_manager.html', events=events, add_event=add_event, edit_event=edit_event, remove_event=remove_event)
                except:
                    flash('Event add failed. Please try again.', 'danger')
                    return render_template('event_manager.html', events=events, add_event=add_event, edit_event=edit_event, remove_event=remove_event)
            elif edit_event.edit_event.data and edit_event.validate():
                try:
                    id = edit_event.id.data
                    event = edit_event.event.data
                    location = edit_event.location.data
                    raw_date = edit_event.date.data
                    date = str(raw_date)
                    raw_time = edit_event.time.data
                    time = str(raw_time)
                    description = edit_event.description.data
                    weather = edit_event.weather.data
                    conn = get_db_connection()
                    conn.execute("UPDATE events SET event = ?, location = ?, date = ?, time = ?, description = ?, weather = ? WHERE id = ?", (event, location, date, time, description, weather, id))
                    conn.commit()
                    events = conn.execute("SELECT * FROM events").fetchall()
                    conn.close()
                    flash('Event successfully edited!', 'success')
                    return render_template('event_manager.html', events=events, add_event=add_event, edit_event=edit_event, remove_event=remove_event)
                except:
                    flash('Event edit failed. Please try again.', 'danger')
                    return render_template('event_manager.html', events=events, add_event=add_event, edit_event=edit_event, remove_event=remove_event)
            elif remove_event.remove_event.data:
                try:
                    id = remove_event.id.data
                    conn = get_db_connection()
                    conn.execute("DELETE FROM events WHERE id = ?", (id,))
                    conn.commit()
                    events = conn.execute("SELECT * FROM events").fetchall()
                    conn.close()
                    flash('Event successfully removed!', 'success')
                    return render_template('event_manager.html', events=events, add_event=add_event, edit_event=edit_event, remove_event=remove_event)
                except:
                    flash('Event removal failed. Please try again.', 'danger')
                    return render_template('event_manager.html', events=events, add_event=add_event, edit_event=edit_event, remove_event=remove_event)
    except:
        return render_template('event_manager.html', events=events, add_event=add_event, edit_event=edit_event, remove_event=remove_event)
    return render_template('event_manager.html', events=events, add_event=add_event, edit_event=edit_event, remove_event=remove_event)


class EditImage(Form):
    id = HiddenField()
    title = StringField('Image Title')
    description = StringField('Image Description')
    update_image = SubmitField()

class RemoveImage(Form):
    id = HiddenField()
    filename = HiddenField()
    remove_image = SubmitField()

@app.route("/gallery_manager", methods=['GET', 'POST'])
def gallery_manager():
    edit_image = EditImage(request.form)
    remove_image = RemoveImage(request.form)
    conn = get_db_connection()
    images = conn.execute("SELECT * FROM images").fetchall()
    conn.close()
    try:
        if(session['loggedIn'] == False):
            return redirect(url_for('login'))
    except:
        session['loggedIn'] = False
        return redirect(url_for('login'))
    try:
        if request.method == 'POST':
            if edit_image.update_image.data:
                id = edit_image.id.data
                conn = get_db_connection()
                if edit_image.title.data:
                    title = edit_image.title.data
                    if edit_image.description.data:
                        try:
                            desc = edit_image.description.data
                            conn.execute('UPDATE images SET title = ?, description = ? WHERE id = ?', (title, desc, id))
                            conn.commit()
                            conn.close()
                            flash('Image Updated: Title and Description Changed.', 'success')
                            return(redirect(url_for('gallery_manager')))
                        except:
                            flash('Image Update Failed! Please try again.', 'danger')
                            return(redirect(url_for('gallery_manager')))
                    else:
                        try:
                            conn.execute('UPDATE images SET title = ? WHERE id = ?', (title, id))
                            conn.commit()
                            conn.close()
                            flash('Image Updated: Title Changed.', 'success')
                            return(redirect(url_for('gallery_manager')))
                        except:
                            flash('Image Update Failed! Please try again.', 'danger')
                            return(redirect(url_for('gallery_manager')))
                elif edit_image.description.data:
                    desc = edit_image.description.data
                    try:
                        conn.execute('UPDATE images SET description = ? WHERE id = ?', (desc, id))
                        conn.commit()
                        conn.close()
                        flash('Image Updated: Description Changed.', 'success')
                        return(redirect(url_for('gallery_manager')))
                    except:
                        flash('Image Update Failed! Please try again.', 'danger')
                        return(redirect(url_for('gallery_manager')))
            elif remove_image.remove_image.data:
                id = remove_image.id.data
                file_name = remove_image.filename.data
                try:
                    conn = get_db_connection()
                    conn.execute('DELETE FROM images WHERE id = ?', (id,))
                    conn.commit()
                    conn.close()
                    os.remove(os.path.join(UPLOADS_PATH + '/', file_name))
                    flash('Image removed successfully.', 'success')
                    return(redirect(url_for('gallery_manager')))
                except:
                    flash('Image could not be removed. Please try again.', 'danger')
                    return(redirect(url_for('gallery_manager')))
    except:
        return render_template('gallery_manager.html', images=images, edit_image=edit_image, remove_image=remove_image)
    return render_template('gallery_manager.html', images=images, edit_image=edit_image, remove_image=remove_image)

@app.route("/uploader", methods=['GET','POST'])
def uploader():
    try:
        if(session['loggedIn'] == False):
            return redirect(url_for('login'))
    except:
        session['loggedIn'] = False
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['file']
        file_name = secure_filename(file.filename)
        os.makedirs(os.path.dirname(UPLOADS_PATH + '/' + file_name), exist_ok=True)
        exists = os.path.exists(os.path.join(UPLOADS_PATH + '/', file_name))
        if not exists:
            file.save(os.path.join(UPLOADS_PATH + '/', file_name))
            flash('File uploaded successfully!', 'success')
            conn = get_db_connection()
            conn.execute('INSERT INTO images (path, file_name) VALUES (?, ?)', (os.path.join('static/uploads' + '/', file_name), file_name))
            conn.commit()
            conn.close()
        else:
            conn = get_db_connection()
            image = conn.execute('SELECT * FROM images WHERE file_name = ' + "'" + file_name + "'").fetchone()
            conn.close()
            if not image:
                conn = get_db_connection()
                conn.execute('INSERT INTO images (path, file_name) VALUES (?, ?)', (os.path.join('static/uploads' + '/', file_name), file_name))
                conn.commit()
                conn.close()
                flash('File already exists! Refreshing database.', 'warning')
            else:
                flash('File already exists!', 'danger')
        return redirect(url_for('gallery_manager'))

class AddOfficer(Form):
    username = StringField('Username', [validators.Length(min=1, max=30)])
    password = PasswordField('Password', [
            validators.DataRequired(),
            validators.EqualTo('confirm', message='Passwords do not match.')
        ])
    confirm = PasswordField('Confirm Password')
    add_member = SubmitField()

class EditOfficer(Form):
    id = HiddenField("ID")
    username = StringField('Username', [validators.Length(min=1, max=30)])
    password = PasswordField('Password', [
            validators.DataRequired(),
            validators.EqualTo('confirm', message='Passwords do not match.')
        ])
    confirm = PasswordField('Confirm Password')
    update_user = SubmitField()

class RemoveOfficer(Form):
    id = HiddenField("ID")
    remove_user = SubmitField()

@app.route("/officer_manager", methods=['GET', 'POST'])
def officer_manager():
    add = AddOfficer(request.form)
    edit = EditOfficer(request.form)
    remove = RemoveOfficer(request.form)
    conn = get_db_connection()
    officers = conn.execute("SELECT * FROM officers").fetchall()
    conn.close()
    try:
        if(session['loggedIn'] == False):
            return redirect(url_for('login'))
    except:
        session['loggedIn'] = False
        return redirect(url_for('login'))
    try:
        if request.method == 'POST' and add.add_member.data and add.validate():
            try:
                username = add.username.data
                password = bcrypt.hashpw(add.password.data.encode('utf-8'), bcrypt.gensalt())
                conn = get_db_connection()
                conn.execute("INSERT INTO officers(username, password) VALUES(?, ?)", (username, password))
                conn.commit()
                officers = conn.execute("SELECT * FROM officers").fetchall()
                conn.close()
                flash('Officer successfully added!', 'success')
                return render_template('officer_manager.html', officers=officers, add=add, edit=edit, remove=remove)
            except:
                flash('Officer add failed. Please try again.', 'danger')
                return render_template('officer_manager.html', officers=officers, add=add, edit=edit, remove=remove)
        elif request.method == 'POST' and edit.update_user.data and edit.validate():
            try:
                id = edit.id.data
                username = edit.username.data
                password = bcrypt.hashpw(edit.password.data.encode('utf-8'), bcrypt.gensalt())
                conn = get_db_connection()
                conn.execute('UPDATE officers SET username = ?, password = ? WHERE id = ?', (username, password, id))
                conn.commit()
                officers = conn.execute("SELECT * FROM officers").fetchall()
                conn.close()
                flash('Officer successfully edited!', 'success')
                return render_template('officer_manager.html', officers=officers, add=add, edit=edit, remove=remove)
            except:
                flash('Officer edit failed. Please try again.', 'danger')
                return render_template('officer_manager.html', officers=officers, add=add, edit=edit, remove=remove)
        elif request.method == 'POST' and remove.remove_user.data:
            try:
                id = remove.id.data
                conn = get_db_connection()
                conn.execute('DELETE FROM officers WHERE id = ?', (id,))
                conn.commit()
                officers = conn.execute("SELECT * FROM officers").fetchall()
                conn.close()
                flash('Officer successfully removed!', 'success')
                return render_template('officer_manager.html', officers=officers, add=add, edit=edit, remove=remove)
            except:
                flash('Officer remove failed. Please try again.', 'danger')
                return render_template('officer_manager.html', officers=officers, add=add, edit=edit, remove=remove)
    except:
        return render_template('officer_manager.html', officers=officers, add=add, edit=edit, remove=remove)
    return render_template('officer_manager.html', officers=officers, add=add, edit=edit, remove=remove)

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
                    check_password = form.password.data
                    conn = get_db_connection()
                    officer = conn.execute("SELECT * FROM officers WHERE username = '" + username + "'").fetchone()
                    dbPassword = officer[2]                    
                    conn.close()
                    if bcrypt.checkpw(check_password.encode('utf-8'), dbPassword):
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
                    check_password = form.password.data
                    conn = get_db_connection()
                    officer = conn.execute("SELECT * FROM officers WHERE username = '" + username + "'").fetchone()
                    dbPassword = officer[2]
                    conn.close()
                    if bcrypt.checkpw(check_password.encode('utf-8'), dbPassword):
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


@app.route('/logout')
def logout():
    try:
        if(session['loggedIn'] == False):
            return redirect(url_for('login'))
    except:
        session['loggedIn'] == False
        return redirect(url_for('login'))
    session.clear()
    flash('You have been logged out!', 'success')
    return redirect(url_for('login'))

class ContactForm(Form):
    firstname = StringField('First Name', [validators.Length(min=1, max=30)])
    lastname = StringField('Last Name', [validators.Length(min=1, max=30)])
    email = EmailField('Email Address')
    phone = IntegerField('Telephone Number')
    address = StringField('Street Address')
    city = StringField('City')
    state = SelectField('State', choices=["Alabama", "Alaska", "American Samoa", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "District of Columbia", "Florida", "Georgia", "Guam", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Minor Outlying Islands", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Northern Mariana Islands", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "U.S. Virgin Islands", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"])
    zipcode = IntegerField('Zip Code')
    contact_method = RadioField('How should we contact you?', choices=["Mail", "Phone", "Email"] )
    status = SelectField('I am', choices=["A Prospective Student", "A Current Student", "An Alumna/Alumnus"])
    interest = SelectField('I am interested in', choices=["BA in Physics", "BS in Physics", "3+2 Program", "2+2 Program",
    "BS in Physical Science",
    "BS in Physical Science and Teacher Education",
    "Minor in Physics",
    "Certificate Program in Physics",
    "Other" ])
    message = TextAreaField('Message')
    submit = SubmitField()

@app.route('/aboutus', methods=['GET', 'POST'])
def aboutus():
    contact = ContactForm(request.form)
    if request.method == 'POST' and contact.validate():
        try:
            msg = Message('FHSU Astronomy Club Inquiry', sender='fhsu.astronomy.inquiries@gmail.com', recipients=['fhsu.astronomy.inquiries@gmail.com'])
            msg.body = """
            First Name: %s
            Last Name: %s
            Email Address: %s
            Phone Number: %s
            Street Address: %s
            City: %s
            State: %s
            Zip Code: %s
            Preferred Contact Method: %s
            Student Status: %s
            Interest: %s
            Message: %s
            """ % (contact.firstname.data, contact.lastname.data, contact.email.data, contact.phone.data, contact.address.data, contact.city.data,
            contact.state.data, contact.zipcode.data, contact.contact_method.data, contact.status.data, contact.interest.data, contact.message.data)
            mail.send(msg)
            flash('Message submitted! We will get back to you shortly.', 'success')
            return redirect(url_for('aboutus'))
        except:
            flash('Message failed to send. Please try again.', 'danger')
            return render_template('aboutus.html', contact=contact)
    return render_template('aboutus.html', contact=contact)

    
@app.route('/events')
def events():
    date = datetime.today()
    today = date.strftime("%B %d, %Y")
    check = date.strftime("%Y-%m-%d")
    conn = get_db_connection()
    events = conn.execute("SELECT * FROM events ORDER BY date").fetchall()
    conn.close()
    event_array = []
    keys = ['title', 'start']
    for event in events:
        if (event[3] >= check):
            event_array.append(dict(zip(keys,(event[1], event[3]))))
        else:
            conn = get_db_connection()
            conn.execute("DELETE FROM events WHERE id = ?", (event[0],))
            conn.commit()
            conn.close()
    return render_template('events.html', today=today, check=check, events=events, event_array=event_array)

    
@app.route('/gallery')
def gallery():
    conn = get_db_connection()
    images = conn.execute("SELECT * FROM images").fetchall()
    conn.close()
    return render_template('gallery.html', images=images)

app.run(threaded=True, port = int(os.environ.get('PORT', 5000)))