from django import forms
from .models import Course, StudyCourse
from django.contrib.auth.models import User

# class AdmissionForm(forms.ModelForm):
#     interest = forms.CharField(required=False)

#     class Meta:
#         model = student
#         fields = ['name', 'email', 'phone','college','year','course','interest']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ['date_time']

class StudyCourseForm(forms.ModelForm):
    class Meta:
        model = StudyCourse
        exclude = ['date_time','course_slug']

# class UserForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password']

# class ReviewForm(forms.ModelForm):
#     class Meta:
#         model = review
#         fields = ['course', 'rating', 'review']