# -*- coding: utf-8 -*-
import random
import string
from typing import List

from flask import render_template, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from app import db
from app.admin.car_forms import TripForm, TripUserForm
from app.models.car import Trip, Tripuser, Period
from app.admin import bp
from app.models.usercourse import User
from app.services import TripUtil, PaymentUtil
from app.services.TripUtil import get_trip_users


@bp.route('/trips', methods=['GET'])
def view_trips():
    return render_template('admin/trips.html', trips=Trip.query.all())

@bp.route('/periods', methods=['GET'])
def view_periods():
    return render_template('admin/periods.html', periods=Period.query.all())


@bp.route('/add_trip', methods=['GET', 'POST'])
def add_trip():
    form = TripForm()
    if request.method == 'POST':
        trip_date = form.trip_date.data
        update_balance = form.update_balance.data
        trip_users: List[Tripuser] = get_trip_users(form)
        TripUtil.add_trip(trip_date, trip_users, update_balance)

        flash('Dodano trip', 'message')
        return redirect(url_for('admin.view_trips'))
    return render_template('admin/add_trip.html', form=form)

@bp.route('/settle/<int:period_id>', methods=['GET'])
def settle(period_id):
    PaymentUtil.settle(period_id)
    return redirect(url_for('admin.view_period', period_id = period_id))

@bp.route('/trip/<int:trip_id>', methods=['GET'])
def view_trip(trip_id):
    trip = Trip.query.filter_by(id=trip_id).first()
    return render_template('admin/trip.html', trip=trip)

@bp.route('/period/<int:period_id>', methods=['GET'])
def view_period(period_id):
    period = Period.query.filter_by(id=period_id).first()
    return render_template('admin/period.html', period=period)


@bp.route('/add_tripuser/<int:trip_id>', methods=['GET', 'POST'])
def add_tripuser(trip_id):
    form = TripUserForm()
    trip = Trip.query.filter_by(id=trip_id).first()
    if request.method == 'POST' and form.validate_on_submit():
        kilometers = form.kilometers.data
        user = User.query.filter_by(name=form.name.data).first()
        trip.trip_users.append(Tripuser(user_id=user.id, kilometers=kilometers))
        trip.total_kilometers += kilometers
        db.session.commit()
        flash('Dodano trip', 'message')
        return redirect(url_for('admin.view_trip', trip_id=trip_id))
    return render_template('admin/add_trip.html', form=form)
