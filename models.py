from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    username = db.Column(db.String(50), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)

    is_active = db.Column(db.Boolean, default=True)

    bookings = db.relationship("Booking", backref="user", lazy=True)

class Trek(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    trek_name = db.Column(db.String(100), nullable=False)

    location = db.Column(db.String(100), nullable=False)

    difficulty = db.Column(db.String(20), nullable=False)

    duration = db.Column(db.String(30), nullable=False)

    available_slots = db.Column(db.Integer, nullable=False)

    assigned_staff = db.Column(db.Integer)

    status = db.Column(db.String(20), default="Open")

    description = db.Column(db.String(300))

    bookings = db.relationship("Booking", backref="trek", lazy=True)

class Booking(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)

    booking_status = db.Column(db.String(20), default="Booked")

    booking_date = db.Column(db.String(30))

    payment_status = db.Column(db.String(20), default="Pending")


class StaffProfile(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        unique=True,
        nullable=False
    )

    phone = db.Column(db.String(15))

    experience = db.Column(db.Integer)

    specialization = db.Column(db.String(100))

    user = db.relationship(
        "User",
        backref=db.backref("staff_profile", uselist=False)
    )