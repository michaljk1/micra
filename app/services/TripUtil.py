# -*- coding: utf-8 -*-
from datetime import datetime

from app import db
from app.models.car import Trip


def add_trip(trip_date, update_balance):
    new_trip = Trip(trip_date = trip_date, update_balance = update_balance)
    print(trip_date)
    db.session.add(new_trip)
    db.session.commit()
    pass
