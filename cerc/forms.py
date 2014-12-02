'''
Created on Aug 7, 2009

@author: dtamez
'''
from datetime import date
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from registration.forms import RegistrationForm
from registration.models import RegistrationProfile
from crispy_forms.helper import (
    FormHelper,
)
from crispy_forms.layout import Layout, Fieldset


from cerc.models import (
    Address,
    Assignment,
    ContactInfo,
    Course,
    Enrollment,
    Family,
    Semester,
    Student,
    StudentAssignment,
    StudentUnit,
    Teacher,
    TeacherRequest,
    Unit,
)


class ActiveSemesterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ActiveSemesterForm, self).__init__(*args, **kwargs)
        fall2011 = date(2011, 8, 1)
        choices = Semester.objects.filter(
            start_date__gte=fall2011).values_list('id', 'name')
        self.fields['active_semester'] = forms.ChoiceField(
            choices=choices, label='Choose a semester:',
            widget=forms.widgets.Select(attrs={
                'onchange': 'activateSemester(this.value);'}))


class CopyAssignmentsForm(forms.Form):
    def __init__(self, unit, teacher, *args, **kwargs):
        super(CopyAssignmentsForm, self).__init__(*args, **kwargs)
        self.fields['new_unit_name'] = forms.CharField()
        self.fields['original_unit'] = forms.IntegerField(
            widget=forms.widgets.HiddenInput(), initial=unit.id)
        self.fields['days_delta'] = forms.IntegerField()


class ChangeUnitAssignmentDatesForm(forms.Form):
    def __init__(self, unit, teacher, *args, **kwargs):
        super(ChangeUnitAssignmentDatesForm, self).__init__(*args, **kwargs)
        self.fields['original_unit'] = forms.IntegerField(
            widget=forms.widgets.HiddenInput(), initial=unit.id)
        self.fields['days_delta'] = forms.IntegerField()


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['family']


class CourseSubmissionForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'semester', 'min_slots', 'max_slots',
                  'materials_fee', 'materials_list', 'first_time_choice',
                  'second_time_choice', 'third_time_choice',
                  'schedule_considerations', 'teachers', 'length',
                  'days_per_week', 'age_level', 'grade_level',
                  'homework_hours', 'required_skills']

    def validate_min_slots(self):
        minslots = self.cleaned_data['min_slots']
        if minslots < 3:
            raise ValidationError('Please enter at least 3 for minimum slots',
                                  code='invalid')
        return minslots


class CourseDetailsForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'semester', 'min_slots', 'max_slots',
                  'materials_fee', 'materials_list', 'first_time_choice',
                  'second_time_choice', 'third_time_choice',
                  'schedule_considerations', 'teachers', 'length',
                  'days_per_week', 'age_level', 'grade_level',
                  'homework_hours', 'required_skills']
        widgets = {'description':  forms.widgets.Textarea(
            attrs={'cols': 980, 'rows': 20,
                   'style': 'width: 900px'}), }

    def validate_min_slots(self):
        minslots = self.cleaned_data['min_slots']
        if minslots < 3:
            raise ValidationError('Please enter at least 3 for minimum slots',
                                  code='invalid')
        return minslots


class TeacherBioForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['bio']


class ContactInfoForm(forms.ModelForm):
    class Meta:
        model = ContactInfo


class AddressForm(forms.ModelForm):

    class Meta:
        model = Address


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment


class StudentAssignmentForm(forms.ModelForm):
    class Meta:
        model = StudentAssignment
        fields = ['grade', 'turn_in_date']

    def __init__(self, *args, **kwargs):
        super(StudentAssignmentForm, self).__init__(*args, **kwargs)
        self.index = '_%s_%s' % (self.instance.student.id,
                                 self.instance.assignment.id)
        cal = self.fields['turn_in_date']
        cal.widget.attrs['id'] = 'id_turn_in_date_%s' % self.index


class TeacherRequestForm(forms.ModelForm):
    class Meta:
        model = TeacherRequest
        exclude = ['approved']


class CercRegistrationForm(RegistrationForm):
    family_name = forms.CharField(max_length=30,
                                  widget=forms.TextInput(attrs={'class':
                                                                'required'}))

    def save(self, profile_callback=None):
        new_user = RegistrationProfile.objects.create_inactive_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email'])
        family = Family()
        family.user = new_user
        family.family_name = self.cleaned_data['family_name']
        family.save()
        return new_user


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        exclude = ['unit']


class UnitForm(forms.ModelForm):

    class Meta:
        model = Unit
        exclude = ['course']


class UnitGradeForm(forms.ModelForm):

    class Meta:
        model = StudentUnit
        exclude = ['unit', 'student']


class EmailChoicField(forms.MultipleChoiceField):
    def __init__(self, choices=(), required=True,
                 widget=forms.CheckboxSelectMultiple(), label=None,
                 initial=None, help_text=None, *args, **kwargs):
        super(EmailChoicField, self).__init__(required=required, widget=widget,
                                              label=label, choices=choices,
                                              initial=initial,
                                              help_text=help_text, *args,
                                              **kwargs)
        self.choices = choices

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])


class EmailForm(forms.Form):
    def __init__(self, recipients, show_cc=True, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        recipient_choices = tuple([(recipient.id, recipient.full_name)
                                   for recipient in recipients])
        self.fields['recipient_id'] = EmailChoicField(
            choices=recipient_choices, label="Recipients",
            widget=forms.CheckboxSelectMultiple())
        if show_cc:
            self.fields['include_parents'] = forms.BooleanField(
                label='CC Parents?', required=False)
        self.fields['subject'] = forms.CharField(
            label='Subject', widget=forms.widgets.TextInput(
                attrs={"size": 84}))
        self.fields['body'] = forms.CharField(
            label='Body', widget=forms.widgets.Textarea(
                attrs={'cols': 980, 'rows': 20, 'style': 'width: 600px'}))


class FamilyForm(forms.ModelForm):

    class Meta:
        model = Family
        exclude = ['user', 'approved', 'fee_paid_date', 'father',
                   'address', 'mother']


class MotherForm(ContactInfoForm):
    def __init__(self, *args, **kwargs):
        super(MotherForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset('Mother', 'first_name', 'last_name', 'email',
                     'email_secondary', 'phone', 'phone_secondary',
                     'birthdate',)
        )
        self.helper.form_tag = False


class FatherForm(ContactInfoForm):
    def __init__(self, *args, **kwargs):
        super(FatherForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Father', 'first_name', 'last_name', 'email',
                'email_secondary', 'phone', 'phone_secondary', 'birthdate'
            )
        )
        self.helper.form_tag = False


class UserForm(forms.ModelForm):
    class Meta:
        model = User
