import os

from flask import current_app

from pointer import db
from pointer.models.usercourse import User


class Export(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    file_name = db.Column(db.String(100))
    type = db.Column(db.String(15))
    format = db.Column(db.String(10))
    generation_date = db.Column(db.DateTime)
    #TODO Rozwiązania
    formats = {
        'SOLUTION': 'Rozwiązani',
        'STATISTICS': 'Statystyki'
    }
    types = {
        'CSV': 'csv',
        'PDF': 'pdf'
    }

    def get_filename(self):
        return self.file_name

    def get_directory(self):
        user = User.query.filter_by(id=self.user_id).first()
        return os.path.join(current_app.instance_path, user.login)