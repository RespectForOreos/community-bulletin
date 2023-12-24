from flask import Flask, render_template, redirect, url_for, request 
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'

db = SQLAlchemy(app)

class Event(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), unique = False, index = True)
    description = db.Column(db.String(250), unique = False, index = True)
    date = db.Column(db.String(40), unique = False, index = True)
    time = db.Column(db.String(40), unique = False, index = True)

class EventForm(FlaskForm): 
   name = StringField(label = "Event Name: ", validators = [DataRequired()])
   description = StringField(label = "Description: ", validators = [DataRequired()])
   time = StringField(label = "Time: ", validators = [DataRequired()])
   date = StringField(label = "Date: ", validators = [DataRequired()])
   submit = SubmitField(label = "Submit")


@app.route('/', methods = ["GET", "POST"])
@app.route('/home', methods = ["GET", "POST"])
def home(): 
    events = Event.query.all()
    return render_template('home.html', events = events)


@app.route('/add_event', methods = ["GET", "POST"])
def add_event():
    form = EventForm(csrf_enabled = False)
    if request.method == "POST" and form.validate(): 
        event = Event(name = form.name.data, description = form.description.data, 
                       date = form.date.data, time = form.time.data)
        try: 
            db.session.add(event)
            db.session.commit()
        except Exception as e: 
            print(e)
        return redirect(url_for('home'))
    return render_template('add_event.html', form = form)


@app.route('/about')
def about(): 
     return render_template('about.html')


@app.route('/event/<int:id>')
def event(id): 
    event = Event.query.get(id)
    return render_template('event.html', event = event)


if __name__ == '__main__':
    app.run(debug=True)