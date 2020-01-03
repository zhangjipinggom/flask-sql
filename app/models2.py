encoding ='utf-8'
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from app import app

app = Flask(__name__)
db = SQLAlchemy(app, engine_options={"encoding": "utf-8"})

class Todo(db.Model):
    __tablename__ = "todo"
    id = db.Column('id', db.Integer, primary_key=True)
    student_id = db.Column("student_id", db.Integer, db.ForeignKey("student.id"))
    category_id = db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
    scoreweight_id = db.Column('scoreweight_id', db.Integer, db.ForeignKey('scoreweight.id'))
    description = db.Column('description', db.Unicode)
    creation_date = db.Column('creation_date', db.Date, default=datetime.utcnow)
    student = db.relationship('Student', foreign_keys=student_id)
    category = db.relationship('Category', foreign_keys=category_id)
    scoreweight = db.relationship('ScoreWeight', foreign_keys=scoreweight_id)


class ScoreWeight(db.Model):   # score
    __tablename__ = "scoreweight"
    id = db.Column('id', db.Integer, primary_key=True)
    value = db.Column('value', db.Integer)


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.Unicode)


class Student(db.Model):
    __tablename__ = "student"
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.Unicode)

