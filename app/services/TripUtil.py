# -*- coding: utf-8 -*-
from typing import List



def create_statistic_pdf(statistics_info, global_filename):
    elements = []
    statistics_list: List[Statistics] = Statistics.get_statistics_by_ids(statistics_info)
    for statistics in statistics_list:
        data = get_pdf_statistics_data(statistics)
        table = Table(data, rowHeights=25, colWidths=[2.5 * inch, 2.5 * inch, 0.75 * inch, 0.75 * inch, 0.75 * inch])
        set_style_for_statistics_table(table, data)
        elements.append(table)
        # add one line free space
        elements.append(Paragraph('<font size=0>tinkering</font>', getSampleStyleSheet()['Normal']))
    pdf = SimpleDocTemplate(
        title='Statystyki',
        filename=global_filename,
        pagesize=letter
    )
    pdf.build(elements)


def set_style_for_statistics_table(table, data):
    for i in range(0, len(data)):
        if i == 0:
            bc = colors.khaki
        else:
            bc = colors.white
        table.setStyle(
            TableStyle([
                ('BACKGROUND', (0, i), (-1, i), bc)]
            )
        )
    table.setStyle(TableStyle(
        [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('LINEABOVE', (0, 2), (0, 2), 2, colors.black),
            ('GRID', (0, 0), (-1, -1), 2, colors.black),
        ]
    ))




def add_trip(solutions, global_filename):
    pass
