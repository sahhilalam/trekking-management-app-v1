from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

db = SQLAlchemy()

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    role = db.Column(Enum("Admin", "Staff", "User"), nullable=False)
    account_status = db.Column(Enum("Pending", "Approved", "Blacklisted"), nullable=False)
    
    manages = db.relationship("Trek", backref="manager")
    bookings = db.relationship("Booking", backref="user")

    def __repr__(self):
        return f"User: {self.user_id} {self.name} {self.email}"
    
class Trek(db.Model):
    trek_id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(Enum("Easy", "Moderate", "Hard"), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    status = db.Column(Enum("Open", "Closed", "Completed"), nullable=False)
    
    staff_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))

    bookings = db.relationship("Booking", backref="trek")

    def __repr__(self):
        return f"Trek: {self.trek_id} {self.trek_name} {self.staff_id}"
    

class Booking(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    booking_date = db.Column(db.Date, nullable=False)
    booking_status = db.Column(Enum("Booked", "Completed", "Cancelled"), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.trek_id"), nullable=False)

    def __repr__(self):
        return f"Booking: {self.booking_id} {self.user_id} {self.trek_id}"