#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os
from typing import List
from app import db
from app.services.DateUtil import get_current_date
from app.models.solution import Solution
from app.models.export import Export
from app.models.statistics import Statistics
from app.models.usercourse import User
from app.services.PDFUtil import create_statistic_pdf, create_solutions_pdf


def get_csv_solution_export(solutions: List[Solution], current_user: User) -> Export:
    current_date = get_current_date()
    filename = ('rozwiazaniaCSV' + str(current_date) + '.csv').replace(" ", "_")
    with open(os.path.join(current_user.get_admin_directory(), filename), 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='|', quoting=csv.QUOTE_MINIMAL)
        for solution in solutions:
            csv_writer.writerow(
                [solution.author.index] + [solution.get_course().name] + [solution.get_lesson().name] +
                [solution.exercise.name] + [solution.send_date] + [solution.points] + [solution.status])
    export = Export(user_id=current_user.id, file_name=filename, generation_date=current_date, type=Export.types['CSV'], format=Export.formats['SOLUTION'])
    db.session.add(export)
    db.session.commit()
    return export


def get_csv_statistics_export(statistics_info, current_user: User) -> Export:
    current_date = get_current_date()
    filename = ('statystykiCSV' + str(current_date) + '.csv').replace(" ", "_")
    with open(os.path.join(current_user.get_admin_directory(), filename), 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='|', quoting=csv.QUOTE_MINIMAL)
        statistics: List[Statistics] = Statistics.get_statistics_by_ids(statistics_info)
        for statistic in statistics:
            csv_writer.writerow(
                [statistic.user_index] + [statistic.course_name] + [statistic.user_points] +
                [statistic.course_points] + [str(statistic.get_percent_value()) + '%'])
            for user_exercise in statistic.user_exercises:
                csv_writer.writerow(
                    [user_exercise.exercise.lesson.name] + [user_exercise.exercise.name] + [user_exercise.points] +
                    [user_exercise.max_points] + [str(user_exercise.get_percent_value()) + '%'])
            csv_writer.writerow('')
    export = Export(user_id=current_user.id, file_name=filename, generation_date=current_date, type=Export.types['CSV'],
                    format=Export.formats['STATISTICS'])
    db.session.add(export)
    db.session.commit()
    return export


def get_pdf_solution_export(solutions: List[Solution], current_user: User) -> Export:
    current_date = get_current_date()
    filename = ('rozwiazaniaPDF' + str(current_date) + '.pdf').replace(" ", "_")
    global_filename = os.path.join(current_user.get_admin_directory(), filename)
    create_solutions_pdf(solutions, global_filename)
    export = Export(user_id=current_user.id, file_name=filename, generation_date=current_date, type=Export.types['PDF'],
                    format=Export.formats['SOLUTION'])
    db.session.add(export)
    db.session.commit()
    return export


def get_pdf_statistics_export(statistics_info, current_user: User) -> Export:
    current_date = get_current_date()
    filename = ('statystykiPDF' + str(current_date) + '.pdf').replace(" ", "_")
    global_filename = os.path.join(current_user.get_admin_directory(), filename)
    create_statistic_pdf(statistics_info, global_filename)
    export = Export(user_id=current_user.id, file_name=filename, generation_date=current_date, type=Export.types['PDF'],
                    format=Export.formats['STATISTICS'])
    db.session.add(export)
    db.session.commit()
    return export