# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from app import db
from app.admin.car_forms import TripForm
from app.models.car import Trip, Tripuser, Period, Balance, Car
from app.models.settlementuser import SettlementUser
from app.models.tripsummary import TripSummary
from app.models.usercourse import User


def get_trip_users(form: TripForm):
    trip_users = []
    append_trip_user(form.first_trip_user.data, trip_users)
    append_trip_user(form.second_trip_user.data, trip_users)
    append_trip_user(form.third_trip_user.data, trip_users)
    return trip_users


def append_trip_user(trip_user_data, trip_users):
    name = trip_user_data['name']
    if name is not None and name != '':
        user = User.query.filter_by(name=name).first()
        trip_users.append(Tripuser(kilometers=trip_user_data['kilometers'], user=user))


def add_trip(trip_date, trip_users, update_balance):
    period = get_period_or_create_new(trip_date.year, trip_date.month)
    trip_summary: TripSummary = process_trip(trip_users, period, update_balance)
    new_trip = Trip(trip_date=trip_date, update_balance=update_balance, trip_users=trip_users,
                    total_kilometers=trip_summary.total_kilometers)
    for balance in trip_summary.balances:
        db.session.add(balance)
    car = Car.query.filter_by(name="micra").first()
    car.odometer += trip_summary.total_kilometers
    db.session.add(car)
    db.session.add(new_trip)
    db.session.commit()


def process_trip(trip_users: List[Tripuser], period, update_balance):
    total_kilometers = 0
    balances: List[Balance] = []
    for trip_user in trip_users:
        balance = get_user_balance(trip_user.user, period)
        user_kilometers = trip_user.kilometers
        total_kilometers += user_kilometers
        balance.add_kilometers(user_kilometers, update_balance)
        balances.append(balance)
    return TripSummary(balances=balances, total_kilometers=total_kilometers)


def get_user_balance(user, period):
    balance = user.get_balance(period.month, period.year)
    if balance is None:
        balance = Balance(user_id=user.id, period_id=period.id)
    return balance


def get_period_or_create_new(year, month):
    period = Period.query.filter_by(month=month, year=year).first()
    if period is None:
        period = Period(month=month, year=year)
        db.session.add(period)
        db.session.commit()
    return period



