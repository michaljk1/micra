# -*- coding: utf-8 -*-
import random
import string

from flask import render_template, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from app import db
from app.teacher import bp
from app.teacher.teacher_forms import CourseForm, DeleteStudentForm, AddStudentForm
from app.models.usercourse import Course, User, Student
from app.services.FileUtil import create_directory
from app.services.ValidationUtil import validate_course, validate_role


@bp.route('/')
@bp.route('/index')
@bp.route('/courses', methods=['GET'])
@login_required
def view_courses():
    validate_role(current_user, User.Roles['TEACHER'])
    return render_template('teacher/courses.html', courses=current_user.courses)


@bp.route('/course/<string:course_name>', methods=['GET'])
@login_required
def view_course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_course(current_user, User.Roles['TEACHER'], course)
    return render_template('teacher/course.html', course=course)


@bp.route('/<string:course_name>/add_student', methods=['GET', 'POST'])
@login_required
def add_student(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_course(current_user, User.Roles['TEACHER'], course)
    form = AddStudentForm()
    for student in Student.query.filter(~Student.courses.any(name=course.name)).all():
        form.email.choices.append((student.email, student.email))
    if form.validate_on_submit():
        student = Student.query.filter_by(email=form.email.data).first()
        student.courses.append(course)
        student.launch_course_email(course_name)
        db.session.commit()
        flash('Dodano studenta', 'message')
        return redirect(url_for('teacher.add_student', course_name=course.name))
    return render_template('teacher/add_student.html', form=form, course=course)


@bp.route('/<string:course_name>/delete_student', methods=['GET', 'POST'])
@login_required
def delete_student(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_course(current_user, User.Roles['TEACHER'], course)
    form = DeleteStudentForm()
    for student in course.get_students():
        form.email.choices.append((student.email, student.email))
    if form.validate_on_submit():
        student = Student.query.filter_by(email=form.email.data).first()
        student.courses.remove(course)
        db.session.commit()
        flash('Usuni??to studenta', 'message')
        return redirect(url_for('teacher.delete_student', course_name=course.name))
    return render_template('teacher/delete_student.html', form=form, course=course)


@bp.route('/change_open/<int:course_id>', methods=['GET', 'POST'])
@login_required
def change_open_course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    validate_course(current_user, User.Roles['TEACHER'], course)
    course.is_open = not course.is_open
    db.session.commit()
    flash('Zapisano zmiany', 'message')
    return redirect(url_for('teacher.view_course', course_name=course.name))


@bp.route('/add_course', methods=['GET', 'POST'])
@login_required
def add_course():
    validate_role(current_user, User.Roles['TEACHER'])
    form = CourseForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_course = Course(name=form.name.data, is_open=True,
                            link=''.join(random.choice(string.ascii_lowercase) for i in range(25)))
        current_user.courses.append(new_course)
        create_directory(new_course.get_directory())
        db.session.commit()
        flash('Dodano kurs', 'message')
        return redirect(url_for('teacher.view_courses'))
    return render_template('teacher/add_course.html', form=form)
