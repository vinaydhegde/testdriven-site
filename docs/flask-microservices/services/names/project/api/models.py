# services/names/project/api/models.py


import datetime

from project import db


class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)


    def __init__(self, text):
        self.text = text
        self.created_date = datetime.datetime.now()
