import hashlib
from datetime import date, datetime
current_date = date.today()
now = current_date.strftime("%B %d, %Y")

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)

