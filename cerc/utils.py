from calendar import HTMLCalendar
from datetime import date
from itertools import groupby

from django.utils.html import conditional_escape as esc


class AssignmentCalendar(HTMLCalendar):
    """HTML representation of a students assignments in a calendar format"""
    def __init__(self, firstweekday,  assignments):
        super(AssignmentCalendar, self).__init__(firstweekday)
        self.assignments = self.group_by_day(assignments)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.assignments:
                cssclass += ' filled'
                body = ['<ul>']
                for assignment in self.assignments[day]:
                    body.append('<li>')
                    body.append('<a href="javascript: loadInfo(%s);">' %
                                assignment.id)
                    body.append('%s' % esc(assignment.assignment.name))
                    body.append('</a></li>')
                body.append('</ul>')
                return self.day_cell(cssclass, '%d %s' % (day, ''.join(body)))
            return self.day_cell(cssclass, day)
        return self.day_cell(' noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(AssignmentCalendar, self).formatmonth(year, month)

    def group_by_day(self, assignments):
        field = lambda assignment: assignment.assignment.due_date.day
        return dict(
            [(day, list(items)) for day, items in groupby(assignments, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)
