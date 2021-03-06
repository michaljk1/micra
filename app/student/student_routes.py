# -*- coding: utf-8 -*-
from flask import render_template, url_for, request, send_from_directory, flash
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from app import db
from app.models.exercise import Exercise
from app.models.lesson import Lesson
from app.models.solution import Solution
from app.models.statistics import Statistics
from app.models.usercourse import Course, User
from app.services.QueryUtil import get_filtered_by_status, exercise_student_query
from app.services.SolutionUtil import add_solution
from app.services.ValidationUtil import validate_role, validate_course, validate_solution_student, \
    validate_exercise_student, validate_lesson, validate_exists
from app.student import bp
from app.student.StudentUtil import can_send_solution
from app.student.student_forms import UploadForm, SolutionStudentSearchForm, StudentSolutionForm


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    validate_role(current_user, User.Roles['STUDENT'])
    return redirect(url_for('student.view_courses'))


@bp.route('/courses', methods=['GET'])
@login_required
def view_courses():
    validate_role(current_user, User.Roles['STUDENT'])
    return render_template('student/courses.html', courses=current_user.courses)


@bp.route('/course/<string:course_name>')
@login_required
def view_course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_course(current_user, User.Roles['STUDENT'], course)
    return render_template('student/course.html', course=course)


@bp.route('/lesson/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    lesson = Lesson.query.filter_by(id=lesson_id).first()
    validate_lesson(current_user, User.Roles['STUDENT'], lesson)
    return render_template('student/lesson.html', lesson=lesson)


@bp.route('/solution/<int:solution_id>')
@login_required
def view_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_solution_student(current_user, User.Roles['STUDENT'], solution)
    form = StudentSolutionForm(obj=solution, student_status=solution.get_student_status(),
                               student_points=solution.get_student_points())
    return render_template('student/solution.html', solution=solution, form=form)


@bp.route('/exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def view_exercise(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_exercise_student(current_user, User.Roles['STUDENT'], exercise)
    solutions = sorted(exercise.get_user_solutions(current_user.id), key=lambda sol: sol.send_date, reverse=True)
    send_solution = can_send_solution(exercise, solutions)
    form = UploadForm()
    if request.method == 'POST' and form.validate_on_submit():
        add_solution(exercise=exercise, member=current_user, file=request.files['file'],
                     ip_address=request.remote_addr, attempt_nr=(1+len(solutions)), os_info=str(request.user_agent))
        return redirect(url_for('student.view_exercise', exercise_id=exercise.id))
    return render_template('student/exercise.html', exercise=exercise, form=form, send_solution=send_solution,
                           solutions=solutions)


@bp.route('/solutions', methods=['GET', 'POST'])
@login_required
def view_solutions():
    validate_role(current_user, User.Roles['STUDENT'])
    form, solutions = SolutionStudentSearchForm(), []
    for course in current_user.courses:
        form.course.choices.append((course.name, course.name))
    if request.method == 'POST' and form.validate_on_submit():
        all_solutions = exercise_student_query(form=form, courses=current_user.get_course_names(),
                                               student_id=current_user.id).all()
        solutions = sorted(get_filtered_by_status(all_solutions, form.status.data), key=lambda sol: sol.send_date,
                           reverse=True)
    return render_template('student/solutions.html', form=form, solutions=solutions)


@bp.route('/statistics')
@login_required
def view_statistics():
    validate_role(current_user, User.Roles['STUDENT'])
    statistics_list = []
    for course in current_user.courses:
        statistics_list.append(Statistics(course=course, student=current_user))
    return render_template('student/statistics.html', statisticsList=statistics_list)


@bp.route('/uploads/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def download_content(lesson_id):
    lesson = Lesson.query.filter_by(id=lesson_id).first()
    validate_lesson(current_user, User.Roles['STUDENT'], lesson)
    return send_from_directory(directory=lesson.get_directory(), filename=lesson.content_pdf_path)


@bp.route('/mysolution/<int:solution_id>', methods=['GET', 'POST'])
@login_required
def download_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_solution_student(current_user, User.Roles['STUDENT'], solution)
    return send_from_directory(directory=solution.get_directory(), filename=solution.filename)


@bp.route('link/<string:link>')
@login_required
def append_course(link):
    course_by_link = Course.query.filter_by(link=link).first()
    validate_role(current_user, User.Roles['STUDENT'])
    validate_exists(course_by_link)
    if not course_by_link.is_open:
        flash('Przypisanie do kursu nie jest obecnie mo??liwe')
        return redirect(url_for('student.index'))
    elif course_by_link not in current_user.courses:
        current_user.courses.append(course_by_link)
        db.session.commit()
        flash('Przypisano do kursu')
    else:
        flash('U??ytkownik przypisany do kursu')
    return redirect(url_for('student.index'))
