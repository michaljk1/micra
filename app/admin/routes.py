import os
import string
import random
# TODO
# obsluga maili
# sqllite
# wyniki do csv i pdfa
# paginacja + order by przy wynikach
# informacja dla usera na jakim etapie jest program, jesli nie przejdzie testów ot przerwac wykonywanie kolejnych, testy od najprostszych
# data+time, przerwa miedzy wysylaniem zadan
# modyfikacja istniejacych obiektow
from flask import render_template, url_for, flash, request, send_from_directory
from flask_login import logout_user, login_required, current_user
from sqlalchemy import desc

from app.admin import bp
from app.admin.forms import CourseForm, ExerciseForm, LessonForm, AssigneUserForm, SolutionForm, \
    SolutionAdminSearchForm, EnableAssingmentLink, TestForm
from werkzeug.utils import redirect, secure_filename

from app.mod.forms import LoginInfoForm
from app.models import Course, Exercise, Lesson, User, Solution, role
from app import db
from app.services.ExerciseService import accept_best_solution
from app.services.QueryService import exercise_query, login_query
from app.services.RouteService import validate_exists, validate_role_course, validate_role


@bp.route('/logout')
def logout():
    validate_role(current_user, role['ADMIN'])
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/<string:course_name>/add_student', methods=['GET', 'POST'])
def add_student(course_name):
    validate_role(current_user, role['ADMIN'])
    form = AssigneUserForm()
    course = Course.query.filter_by(name=course_name).first()
    users = []
    for user in User.query.filter(~User.courses.any(name=course.name)).all():
        data = (user.email, user.email)
        users.append(data)
    form.email.choices = users
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.courses.append(course)
        db.session.commit()
        flash('Dodano studenta')
    return render_template('admin/add_student.html', form=form, course=course)


@bp.route('/')
@bp.route('/index')
@bp.route('/courses', methods=['GET'])
def view_courses():
    validate_role(current_user, role['ADMIN'])
    return render_template('admin/courses.html', courses=current_user.courses)


@bp.route('/course/<string:course_name>', methods=['GET', 'POST'])
def view_course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_role_course(current_user, role['ADMIN'], course)
    form = EnableAssingmentLink(activate=course.is_open)
    if request.method == 'POST' and form.validate_on_submit():
        if form.activate.data:
            course.is_open = True
        else:
            course.is_open = False
        db.session.commit()
        flash('Zapisano zmiany')
        return render_template('admin/course.html', form=form, course=course)
    return render_template('admin/course.html', form=form, course=course)


@bp.route('/add_course', methods=['GET', 'POST'])
def add_course():
    validate_role(current_user, role['ADMIN'])
    form = CourseForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_course = Course(name=form.name.data, is_open=True,
                            link=''.join(random.choice(string.ascii_lowercase) for i in range(25)))
        current_user.courses.append(new_course)
        os.makedirs(new_course.get_directory())
        db.session.commit()
        flash('Dodano kurs')
        return redirect(url_for('admin.view_courses'))
    return render_template('admin/add_course.html', form=form)


@bp.route('/<string:course_name>/<int:lesson_id>')
def view_lesson(course_name, lesson_id):
    lesson = Lesson.query.filter_by(id=lesson_id).first()
    validate_role_course(current_user, role['ADMIN'], lesson.course)
    return render_template('admin/lesson.html', lesson=lesson, course=lesson.course)


@bp.route('/<string:course_name>/add_lesson', methods=['GET', 'POST'])
def add_lesson(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_role_course(current_user, role['ADMIN'], course)
    form = LessonForm()
    if request.method == 'POST' and form.validate_on_submit():
        file = request.files['pdf_content']
        filename = secure_filename(file.filename)
        if filename == '':
            filename = None
        lesson_name = form.name.data
        new_lesson = Lesson(name=lesson_name, content_pdf_path=filename, content_url=form.content_url.data,
                            raw_text=form.text_content.data)
        course.lessons.append(new_lesson)
        lesson_directory = new_lesson.get_directory()
        os.makedirs(lesson_directory)
        if filename is not None:
            file.save(os.path.join(lesson_directory, filename))
        db.session.commit()
        return redirect(url_for('admin.view_lesson', lesson_id=new_lesson.id, course_name=course.name))
    return render_template('admin/add_lesson.html', form=form, course=course)


@bp.route('/exercise/<int:exercise_id>', methods=['GET', 'POST'])
def view_exercise(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_role_course(current_user, role['ADMIN'], exercise.lesson.course)
    solutions = Solution.query.filter_by(exercise_id=exercise_id, is_active=True).all()
    return render_template('admin/exercise.html', exercise=exercise, solutions=solutions)


@bp.route('/test/<int:exercise_id>', methods=['GET', 'POST'])
def add_test(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_role_course(current_user, role['ADMIN'], exercise.lesson.course)
    form = TestForm()
    if request.method == 'POST' and form.validate_on_submit():
        exercise.create_test(request.files['input'], request.files['output'], form.max_points.data)
        db.session.commit()
    return render_template('admin/add_test.html', exercise=exercise, form=form)


@bp.route('/<string:course_name>/<string:lesson_name>/add_exercise', methods=['GET', 'POST'])
def add_exercise(course_name, lesson_name):
    course = Course.query.filter_by(name=course_name).first()
    lesson = course.get_lesson_by_name(lesson_name)
    validate_exists(lesson)
    validate_role_course(current_user, role['ADMIN'], course)
    form = ExerciseForm()
    if form.validate_on_submit():
        exercise_name = form.name.data
        exercise = Exercise(name=exercise_name, content=form.content.data, lesson_id=lesson.id,
                            max_attempts=form.max_attempts.data, compile_command=form.compile_command.data,
                            end_date=form.end_date.data, run_command=form.run_command.data,
                            program_name=form.program_name.data)
        lesson.exercises.append(exercise)
        os.makedirs(exercise.get_directory())
        exercise.create_test(request.files['input'], request.files['output'], form.max_points.data)
        db.session.commit()
        return redirect(url_for('admin.view_lesson', course_name=lesson.course.name, lesson_id=lesson.id))
    return render_template('admin/add_template.html', form=form, lesson=lesson)


@bp.route('/solutions', methods=['GET', 'POST'])
def view_solutions():
    validate_role(current_user, role['ADMIN'])
    course = request.args.get('course')
    lesson = request.args.get('lesson')
    exercise = request.args.get('exercise')
    course_db = Course.query.filter_by(name=course).first()
    if course is None or lesson is None or exercise is None or course_db is None or course_db not in current_user.courses:
        form = SolutionAdminSearchForm()
    else:
        form = SolutionAdminSearchForm(course=course, lesson=lesson, exercise=exercise)
    for course in current_user.courses:
        form.course.choices.append((course.name, course.name))
    if request.method == 'POST' and form.validate_on_submit():
        solutions = exercise_query(form=form, courses=current_user.get_course_names()).all()
        return render_template('admin/solutions.html', form=form, solutions=solutions)
    return render_template('admin/solutions.html', form=form, solutions=[])


@bp.route('/solution/<int:solution_id>', methods=['GET', 'POST'])
def view_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_exists(solution)
    validate_role_course(current_user, role['ADMIN'], solution.exercise.lesson.course)
    solution_form = SolutionForm(obj=solution, email=solution.author.email)
    if request.method == 'POST':
        if solution_form.admin_refused.data:
            solution.status = Solution.solutionStatus['REFUSED']
        else:
            solution.status = Solution.solutionStatus['SEND']
        solution.points = solution_form.points.data
        db.session.commit()
        accept_best_solution(solution.user_id, solution.exercise)
        flash('Zapisano zmiany')
        return render_template('admin/solution.html', form=solution_form, solution=solution)
    return render_template('admin/solution.html', form=solution_form, solution=solution)


@bp.route('/logins', methods=['GET', 'POST'])
@login_required
def view_logins():
    validate_role(current_user, role['ADMIN'])
    form = LoginInfoForm()
    user_ids = []
    for course in current_user.courses:
        for member in course.members:
            if member.role == role['STUDENT'] and member.id not in user_ids:
                user_ids.append(member.id)
                form.email.choices.append((member.email, member.email))
    if form.validate_on_submit():
        logins = login_query(form, current_user.role, ids=user_ids).order_by(desc(User.email)).all()
        return render_template('mod/logins.html', form=form, logins=logins)
    return render_template('mod/logins.html', form=form, logins=[])


@bp.route('/uploads/<int:solution_id>/', methods=['GET', 'POST'])
@login_required
def download_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_role_course(current_user, role['ADMIN'], solution.exercise.lesson.course)
    return send_from_directory(directory=solution.get_directory(),
                               filename=solution.file_path)
