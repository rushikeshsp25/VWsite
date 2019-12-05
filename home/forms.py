from django import forms
from .models import Course,CourseBatch, StudyCourse,FeedbackBatch,FeedbackQuestion
from django.contrib.auth.models import User

# class AdmissionForm(forms.ModelForm):
#     interest = forms.CharField(required=False)

#     class Meta:
#         model = student
#         fields = ['name', 'email', 'phone','college','year','course','interest']
class DateInput(forms.DateInput):
    input_type='date'

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ['date_time','course_slug']

class BatchForm(forms.ModelForm):
    class Meta:
        model = CourseBatch   
        exclude = ['date_time']
        widgets={'start_date':DateInput()}

class FeedbackForm(forms.ModelForm):
    class Meta:
        model=FeedbackQuestion
        exlude=['']
        fields=['question','question_type']

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

class FeedbackBatchForm(forms.ModelForm):
    class Meta:
        model = FeedbackBatch
        exclude = ['date_time']
        widgets={'start_date':DateInput(),'end_date':DateInput()}