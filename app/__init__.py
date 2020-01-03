from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config2 import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# from app import views, models
from app import models2, views2