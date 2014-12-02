from django.contrib.auth.models import Group

from cerc.models import (
    Family,
    Student,
)

student_group = Group.objects.get(name='Students')

students = Student.objects.all()

for student in students:
    student.user.groups.add(student_group)
    student.save()

family_group = Group.objects.get(name='Families')

families = Family.objects.all()

for family in families:
    family.user.groups.add(family_group)
    family.save()
