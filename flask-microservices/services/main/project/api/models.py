# services/main/project/api/models.py


from project import db


class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, name):
        self.name = name
