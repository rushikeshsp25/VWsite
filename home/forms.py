from django import forms
from .models import student,course
from django.contrib.auth.models import User

class AdmissionForm(forms.ModelForm):
    interest = forms.CharField(required=False)

    class Meta:
        model = student
        fields = ['name', 'email', 'phone','college','year','course','interest']

class CourseForm(forms.ModelForm):
    class Meta:
        model = course
        fields = ['course_name','level','course_icon', 'fees','outcomes','requirements','description']

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']