# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, FieldList, FormField, HiddenField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired





class TripUserForm(FlaskForm):
    name = StringField('Użytkownik')
    kilometers = IntegerField('Kilometry', default=0)

class TripForm(FlaskForm):
    update_balance = BooleanField('Zaktualizuj balans')
    trip_date = DateField('Data', format='%Y-%m-%d', validators=[DataRequired()])
    first_trip_user = FormField(TripUserForm)
    second_trip_user =FormField(TripUserForm)
    third_trip_user = FormField(TripUserForm)
    submit_button = SubmitField('Dodaj trip')
