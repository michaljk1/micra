# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, FieldList, FormField, HiddenField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired





class TripUserForm(FlaskForm):
    name = StringField('Użytkownik', validators=[DataRequired()])
    kilometers = IntegerField('Kilometry', default=0, validators=[DataRequired()])
    submit_button = SubmitField('Dodaj usera')

class TripForm(FlaskForm):
    update_balance = BooleanField('Zaktualizuj balans')
    trip_date = DateField('Data', format='%Y-%m-%d', validators=[DataRequired()])
    # trip_users = FieldList(FormField(TripUserForm))
    submit_button = SubmitField('Dodaj trip')