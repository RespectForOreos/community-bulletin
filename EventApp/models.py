from flask import Flask
from app import db

class Event(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), unique = False, index = True)
    description = db.Column(db.String(250), unique = False, index = True)
    date = db.Column(db.String(40), unique = False, index = True)
    time = db.Column(db.String(40), unique = False, index = True)
