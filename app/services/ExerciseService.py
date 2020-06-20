import os
import subprocess

from app import db
from app.models import Solution


def accept_best_solution(user_id, exercise):
    user_exercises = Solution.query.filter_by(user_id=user_id, exercise_id=exercise.id).all()
    points, best_solution = 0, None
    for user_exercise in user_exercises:
        if user_exercise.status != Solution.solutionStatus['REFUSED'] and user_exercise.points >= points:
            best_solution = user_exercise
            points = best_solution.points
    if best_solution is not None:
        best_solution.status = Solution.solutionStatus['ACTIVE']
        user_exercises.remove(best_solution)
    for user_exercise in user_exercises:
        if user_exercise.status != Solution.solutionStatus['REFUSED']:
            user_exercise.status = Solution.solutionStatus['SEND']
    db.session.commit()


def compile(solution):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    compile_command = solution.exercise.compile_command
    if len(compile_command.split()) > 0:
        bash_command = dir_path + '/compile.sh ' + solution.get_directory() + ' ' + compile_command
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)


def grade(solution):
    exercise = solution.exercise
    program_name = solution.file_path
    run_command = exercise.run_command
    dir_path = os.path.dirname(os.path.realpath(__file__))
    solution.points = 0
    for test in exercise.tests.all():
        test_dir = test.get_directory()
        input_name = test_dir + '/' + test.input_name
        output_name = test_dir + '/' + test.output_name
        bash_command = dir_path + '/run.sh ' + solution.get_directory() + ' ' + program_name + ' ' + input_name + ' ' + output_name + ' ' + run_command
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        if len(output) == 0:
            solution.points += test.points
    accept_best_solution(solution.user_id, exercise)
