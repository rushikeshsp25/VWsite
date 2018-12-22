# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

# Create your models here.
COLLEGE_CHOICES = (
    ( 'PCCOE','Pimpri Chinchwad College of Engineering,Pune'),
    ('DYAK','D.Y. Patil Akurdi'),
    ('DYAM','D.Y. Patil Ambi' ),
    ('DYPI','D.Y. Patil Pimpri'),
    ('JSPM','J.S.P.M. Tatawade'),
    ('Other', 'Other'),
)

YEAR_CHOICES = (
    ('FE', 'FE'),
    ('SE', 'SE'),
    ('TE', 'TE'),
    ('BE', 'BE'),
)

RATING_CHOICES = (
    ('1','1'),
('2','2'),
('3','3'),
('4','4'),
('5','5'),
)


LEVEL_CHOICES= (
    ('Beginner', 'Beginner'),
    ('Intermediate', 'Intermediate'),
    ('Advanced', 'Advanced'),
)

class course(models.Model):
    course_name=models.CharField(max_length=70,unique=True)
    level=models.CharField(max_length=20,choices=LEVEL_CHOICES)
    course_icon=models.FileField()
    fees=models.IntegerField(default=0)
    fees_description = models.TextField(null=True)
    outcomes=models.TextField()
    requirements=models.TextField()
    description=models.TextField()
    syllabus=models.FileField(null=True,blank=True)
    date_time=models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.course_name

class student(models.Model):
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    name=models.CharField(max_length=30)
    email=models.EmailField()
    phone=models.CharField(max_length=10)
    college=models.CharField(max_length=20,choices=COLLEGE_CHOICES)
    year=models.CharField(max_length=20,choices=YEAR_CHOICES)
    course = models.ForeignKey(course,to_field='course_name',on_delete=models.CASCADE)
    interest=models.CharField(max_length=50)
    admission=models.BooleanField(default=False)
    fees_paid=models.IntegerField(default=0)

class student_contact(models.Model):
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    message=models.TextField()
    def __str__(self):
        return self.name

class review(models.Model):
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    course = models.ForeignKey(course, to_field='course_name', on_delete=models.CASCADE)
    rating = models.CharField(max_length=20, choices=RATING_CHOICES)
    review=models.TextField()
    reviewer=models.ForeignKey(student,on_delete=models.CASCADE)
    def __str__(self):
        return self.review

