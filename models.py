from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    
    therapist_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

class HEP(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    therapist_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    title = db.Column(db.String(150), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    repetitions = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.String(50))





class ExerciseRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    hep_id = db.Column(
        db.Integer,
        db.ForeignKey("hep.id"),
        nullable=False
    )

    

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    status = db.Column(db.String(20), nullable=False)

    difficulty = db.Column(db.Integer, nullable=True)

    reason = db.Column(db.Text, nullable=True)

    date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )