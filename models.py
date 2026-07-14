from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    username = db.Column(db.String(50), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)

class Trek(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    trek_name = db.Column(db.String(100), nullable=False)

    location = db.Column(db.String(100), nullable=False)

    date = db.Column(db.String(30), nullable=False)

    difficulty = db.Column(db.String(20), nullable=False)

    slots = db.Column(db.Integer, nullable=False)

    description = db.Column(db.String(300))

class Booking(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    trek_id = db.Column(db.Integer, nullable=False)

    booking_status = db.Column(db.String(20), default="Pending")