# -*- coding: utf-8 -*-

from app import db


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    odometer = db.Column(db.Integer, default=0)
    fuel_usage = db.Column(db.Float)


class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parking_kilometers = db.Column(db.Integer, default=0)
    parking_free_kilometers = db.Column(db.Integer, default=0)
    user_id = db.Column(db.ForeignKey('user.id'))
    period_id = db.Column(db.ForeignKey('period.id'))

    def add_kilometers(self, kilometers, update_balance):
        if update_balance:
            if self.parking_kilometers is None:
                self.parking_kilometers = 0
            self.parking_kilometers += kilometers
        else:
            if self.parking_free_kilometers is None:
                self.parking_free_kilometers = 0
            self.parking_free_kilometers += kilometers


class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)
    settled = db.Column(db.Boolean, default=False)
    balances = db.relationship('Balance', backref='period', lazy='dynamic')


class Tripuser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'))
    kilometers = db.Column(db.Integer)
    trip_id = db.Column(db.ForeignKey('trip.id'))
    user = None


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_date = db.Column(db.DateTime)
    total_kilometers = db.Column(db.Integer, default=0)
    update_balance = db.Column(db.Boolean, default=False)
    trip_users = db.relationship('Tripuser', backref='trip', lazy='dynamic')





