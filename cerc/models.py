'''
Created on Aug 1, 2009

@author: dtamez
'''
from datetime import date

from django.contrib.auth.models import Group, User
from django.db import models
from localflavor.us.models import USStateField
from registration.signals import user_registered
from south.modelsinspector import add_introspection_rules

add_introspection_rules([], ["^localflavor\.us\.models\.USStateField"])


def cerc_user_registered(sender, **kwargs):
    user = kwargs['user']
    group = Group.objects.get(name='Families')
    user.groups.add(group)
    user.save()
    f = Family(user=user)
    f.save()

user_registered.connect(cerc_user_registered)


class Semester(models.Model):
    """There are at least two semesters (Fall and Spring) but
    sometimes there are smaller mini mesters as well"""
    name = models.CharField(max_length=20)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'semester'
        ordering = ['start_date', 'name']

    def __str__(self):
        return self.name


class Family(models.Model):
    """The family of a CERC student"""
    user = models.OneToOneField(User, unique=True)
    family_name = models.CharField(max_length=30, blank=True,
                                   help_text='A name or phrase by which to '
                                   'identify this family')
    fee_paid_date = models.DateField(editable=False, null=True,
                                     help_text='Date this year on which the '
                                     'family fee was paid')
    address = models.OneToOneField('Address', null=True)
    mother = models.OneToOneField('ContactInfo', related_name='mother',
                                  null=True)
    father = models.OneToOneField('ContactInfo', related_name='father',
                                  null=True)
    emergency_number = models.CharField(max_length=10, blank=True)
    emergency_name = models.CharField(max_length=20, blank=True)
    emergency_relationship = models.CharField(max_length=20, blank=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return '%s family' % self.family_name

    def save(self, *args, **kwargs):
        group = Group.objects.get(name='Families')
        self.user.groups.add(group)
        super(Family, self).save(*args, **kwargs)

    class Meta:
        db_table = 'family'
        verbose_name_plural = 'Families'
        ordering = ['family_name']


class Address(models.Model):
    street = models.CharField(max_length=60)
    city = models.CharField(max_length=60, default="Rowlett")
    state = USStateField(default='TX')
    zip = models.CharField(max_length=5, default='75089')

    def __str__(self):
        return self.street

    class Meta:
        db_table = 'address'
        verbose_name_plural = 'Addresses'
        ordering = ['street', 'city']


class ContactInfo(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField()
    email_secondary = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=10, verbose_name='Home Phone')
    phone_secondary = models.CharField(max_length=10, null=True, blank=True,
                                       verbose_name='Cell Phone')
    birthdate = models.DateField(null=True, blank=True)

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'contact_info'
        verbose_name_plural = 'Contact Info'
        ordering = ['last_name', 'first_name']


class Teacher(models.Model):
    user = models.OneToOneField(User, unique=True, null=True)
    address = models.ForeignKey(Address)
    contact_info = models.ForeignKey(ContactInfo)
    bio = models.TextField(default='')

    def __str__(self):
        return self.contact_info.__str__()

    class Meta:

        db_table = 'teacher'
        ordering = ['contact_info']

    @property
    def full_name(self):
        return self.contact_info.full_name

    @property
    def email(self):
        return self.contact_info.email or self.user.email

    def save(self, *args, **kwargs):
        group = Group.objects.get(name='Teachers')
        self.user.groups.add(group)
        super(Teacher, self).save(*args, **kwargs)


class TeacherRequest(models.Model):
    """A request from a non teacher that would like to teach at CERC"""
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField()
    courses = models.TextField(verbose_name='Courses taught')
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Student(models.Model):
    user = models.OneToOneField(User, unique=True, null=True)
    student = models.OneToOneField(ContactInfo, related_name='student')
    family = models.ForeignKey(Family)
    special_needs = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.student.__str__()

    class Meta:
        db_table = 'student'
        ordering = ['student']

    @property
    def full_name(self):
        return self.student.full_name

    @property
    def email(self):
        return self.student.email or self.user.email

    def save(self, *args, **kwargs):
        group = Group.objects.get(name='Students')
        self.user.groups.add(group)
        super(Student, self).save(*args, **kwargs)


class Enrollment(models.Model):
    """Enrollment in a particular course for one student"""
    course = models.ForeignKey('Course')
    student = models.ForeignKey(Student)
    entroll_date = models.DateField()
    drop_date = models.DateField(null=True, blank=True)

    def is_active(self):
        today = date.today()
        return ((not self.drop_date) and
                (self.course.semester.start_date < today <
                 self.course.semester.end_date))

    def __str__(self):
        return "%s - %s" % (self.course.__str__(), self.student.__str__())

    class Meta:
        db_table = "enrollment"
        ordering = ['course', 'student']


class Course(models.Model):
    """A particular instance of a class taught at CERC"""
    DAYS = (('Mo', 'Monday'),
            ('Tu', 'Tuesday'),
            ('We', 'Wednesday'),
            ('Th', 'Thursday'),
            ('TuTh', 'Tuesday and Thursday'),
            ('MoWe', 'Monday and Wednesday'),
            ('MoTh', 'Monday and Thursday'))
    LENGTH = ((1.0, '1 hour'), (1.5, '1.5 hours'), (2.0, '2 hours'))
    DAYS_PER_WEEK = ((1, "One day per week"), (2, "Two days per week"),
                     (3, "Three days per week"), (4, "Four days per week"))
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    semester = models.ForeignKey(Semester)
    days_per_week = models.IntegerField(choices=DAYS_PER_WEEK, default=0)
    homework_hours = models.CharField(max_length=10)
    min_slots = models.IntegerField(default=1)
    max_slots = models.IntegerField()
    length = models.DecimalField(choices=LENGTH, decimal_places=1,
                                 max_digits=2)
    materials_fee = models.DecimalField(decimal_places=2, max_digits=4)
    materials_list = models.TextField()
    first_time_choice = models.CharField(max_length=50, default='')
    second_time_choice = models.CharField(max_length=50, default='')
    third_time_choice = models.CharField(max_length=50, default='')
    schedule_considerations = models.CharField(max_length=100, null=True,
                                               blank=True)
    required_skills = models.CharField(max_length=100, null=True, blank=True)
    age_level = models.CharField(max_length=10)
    grade_level = models.CharField(max_length=10)
    teachers = models.ManyToManyField(Teacher)

    # Fields to be filled in by the admin
    code = models.CharField(max_length=10)
    approved = models.BooleanField(default=False)
    tuition = models.IntegerField(blank=True, null=True)
    day = models.CharField(max_length=4, choices=DAYS, blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    students = models.ManyToManyField(Student, through=Enrollment, blank=True,
                                      null=True)

    def __str__(self):
        return "%s (%s) %s" % (self.title, self.code, self.semester.name)

    class Meta:
        db_table = 'course'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['title', 'code']


class Unit(models.Model):
    """Top level division of a course"""
    name = models.CharField(max_length=30)
    course = models.ForeignKey(Course)
    date = models.DateField()

    def __str__(self):
        return "%s for %s, due %s" % (self.name, self.course, self.date)


class StudentUnit(models.Model):
    """Ties a unit a student and a grade together"""
    student = models.ForeignKey(Student)
    unit = models.ForeignKey(Unit)
    grade = models.DecimalField(blank=True, null=True,
                                max_digits=5, decimal_places=2,
                                help_text='The grade the student recieved for'
                                'this module')


class Attendance(models.Model):
    """Attendance for one student for one course on one date"""
    course = models.ForeignKey(Course)
    student = models.ForeignKey(Student)
    date = models.DateField()

    def __str__(self):
        return "%s - %s - %s" % (self.date, self.course, self.student)

    class Meta:
        db_table = 'attendance'
        verbose_name_plural = 'Attendance'
        ordering = ['date', 'course', 'student']


class Assignment(models.Model):
    """A gradeable unit of work that is part of a particular course"""

    name = models.CharField(max_length=80, blank=False,
                            help_text='A short name by which you can reference'
                            'this assignment')
    instructions = models.TextField(help_text="Any instructions necessary for "
                                    "the student to complete the assignment")
    unit = models.ForeignKey(Unit)
    due_date = models.DateField(blank=False, null=False,
                                help_text='The latest date at which this'
                                ' assignment may be turned in without penalty')
    weight = models.IntegerField(help_text='A number between 0 and 100 '
                                 'specifying the percentage of the final grade'
                                 'that this assignment is worth')

    def __str__(self):
        return "%s - %s - %s" % (self.unit.course, self.name, self.due_date)


class StudentAssignment(models.Model):
    """These should be generated for each student when he is added to a
    course"""
    assignment = models.ForeignKey(Assignment, help_text='The course '
                                   'assignment the student has been assigned.')
    student = models.ForeignKey(Student, help_text='The student that was '
                                'assigned this assignment')
    grade = models.DecimalField(blank=True, null=True,
                                max_digits=5, decimal_places=2,
                                help_text='The grade the student recieved for'
                                ' this assignment')
    turn_in_date = models.DateField(blank=True, null=True, help_text='The date'
                                    ' this assignment was turned in')

    def __str__(self):
        return "%s - %s - %s - %s" % (self.assignment.unit.course.title,
                                      self.assignment.unit.name,
                                      self.assignment.name, self.student)

    def get_absolute_url(self):
        return '/student_assignment/%i/' % self.id


class Conduct(models.Model):
    """Comments on a student's behavior"""
    date = models.DateField(blank=False, null=False,
                            help_text="When the conduct event occurred")
    comments = models.TextField(blank=False,
                                help_text="Comments on the student's conduct")
    student = models.ForeignKey(Student, help_text="Student for which this "
                                "conduct comment is being made.")

    def __str__(self):
        return "%s - %s - %s" % (self.date, self.student, self.comments)

    class Meta:
        db_table = 'conduct'
        verbose_name_plural = 'Conduct'
        ordering = ['date', 'student', 'comments']


class Message(models.Model):
    """Represents communcation betwee a teacher and student"""
    email_group_id = models.CharField(max_length=50)
    subject = models.CharField(max_length=50, blank=False,
                               help_text="The subject of this message")
    body = models.TextField(help_text="The body of this message")
    date = models.DateTimeField(help_text="When the message was sent")
    sender = models.ForeignKey(User, related_name='sender')
    recipient = models.ForeignKey(User, related_name='recipient')

    def __str__(self):
        return "From: %s To:%s -  %s" % (self.sender.get_full_name(),
                                         self.recipient.get_full_name(),
                                         self.subject[:25])
