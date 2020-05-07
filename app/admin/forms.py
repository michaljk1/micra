from flask_wtf.file import FileField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField, FieldList, \
    SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email


class UploadForm(FlaskForm):
    file = FileField('Select File')
    submit_button = SubmitField('Submit Form')


class CourseForm(FlaskForm):
    name = StringField('Course name')
    submit_button = SubmitField('Add course')


class LessonForm(FlaskForm):
    name = StringField('Lesson name')
    text_content = StringField('Content')
    pdf_content = FileField('Select File')
    content_url = StringField('Url')
    submit_button = SubmitField('Add Lesson')


class TemplateForm(FlaskForm):
    name = StringField('Nazwa')
    content = StringField('content')
    max_attempts = IntegerField('Liczba prób', default=3)
    points = FloatField('Liczba punktów')
    end_date = DateField('End date', format='%Y-%m-%d')
    submit_button = SubmitField('Add template')


class CreateAccountRequestForm(FlaskForm):
    email = SelectField('User', choices=[])
    submit_button = SubmitField('Request Password Reset')
