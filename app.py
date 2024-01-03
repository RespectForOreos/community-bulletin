from flask import Flask, render_template, redirect, url_for, request, flash 
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user,\
      logout_user

#use PythonAnywhere to deploy when done

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@login_manager.unauthorized_handler
def unauthorized(): 
    return redirect(url_for('login'))

class Event(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), unique = False, index = True)
    description = db.Column(db.String(250), unique = False, index = True)
    date = db.Column(db.String(40), unique = False, index = True)
    time = db.Column(db.String(40), unique = False, index = True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True) 
    username = db.Column(db.String(100), unique = True, index = True)
    password_hash = db.Column(db.String(128), unique = False, index = True)
    events = db.relationship('Event', backref = 'user', laxy = 'dynamic')

    def __repr__(self): 
        return '<User {}>'.format(self.username)
    
    def generate_password(self, password): 
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password): 
        return check_password_hash(self.password_hash, password)


class EventForm(FlaskForm): 
   name = StringField(label = "Event Name: ", validators = [DataRequired()])
   description = StringField(label = "Description: ", validators = [DataRequired()])
   time = StringField(label = "Time: ", validators = [DataRequired()])
   date = StringField(label = "Date: ", validators = [DataRequired()])
   submit = SubmitField(label = "Submit")

class LoginForm(FlaskForm): 
    username = StringField(label = "Username: ", validators = [DataRequired()])
    password = PasswordField(label = "Password: ", validators = [DataRequired()])
    submit = SubmitField(label = "Login")

class RegisterForm(FlaskForm): 
    username = StringField(label = "Username: ", validators = [DataRequired()])
    password = PasswordField(label = "Password: ", validators = [DataRequired()])
    confirm_password = PasswordField(label = "Confirm Password: ", validators = [DataRequired()])
    submit = SubmitField(label = "Register")

@app.route('/')
@app.route('/home')
def home(): 
    events = Event.query.all()
    return render_template('home.html', events = events)


@app.route('/add_event', methods = ["GET", "POST"])
@login_required
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

@app.route('/profile')
@login_required
def profile(): 
    user = user = User.query.get(current_user.get_id())
    return render_template('profile.html')


@app.route('/login', methods = ["GET", "POST"])
def login(): 
    form = LoginForm()
    if form.method == "POST" and form.validate(): 
        user = User.query.filter_by(username = form.username.data).first()
        if user == None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('login'))
        login_user(user)
        return redirect(request.args.get('next'))
    return redirect(url_for('home'))

@app.route('/register', methods = ["GET", "POST"])
def register():
    if current_user.is_authenticated: 
        return redirect(url_for('home'))
    else: 
        form = RegisterForm()
        if form.method == "POST" and form.validate(): 
            try: 
                user = User(username = form.username.data)
                user.generate_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                flash("Congratualtions, you are now a registered user!")
            except Exception as e:
                return "{e}"
            return redirect(url_for('home'))

        return render_template('register.html', form = form)

@app.route('/logout')
@login_required
def logout(): 
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)