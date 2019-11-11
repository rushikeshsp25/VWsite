# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

YEAR_CHOICES = (
    ('FE', 'First Year'),
    ('SE', 'Second Year'),
    ('TE', 'Third Year'),
    ('BE', 'Fourth Year'),
    ('NA', 'Not Applicable')
)

RATING_CHOICES = (
    ('1','1'),
    ('2','2'),
    ('3','3'),
    ('4','4'),
    ('5','5')
)


LEVEL_CHOICES= (
    ('Beginner', 'Beginner'),
    ('Intermediate', 'Intermediate'),
    ('Advanced', 'Advanced')
)

class College(models.Model):
    name=models.CharField(max_length=70,unique=True)
    def __str__(self):
        return self.name

class Course(models.Model):
    course_name=models.CharField(max_length=70,unique=True)
    is_online=models.BooleanField(default=False)
    level=models.CharField(max_length=20,choices=LEVEL_CHOICES)
    course_icon=models.FileField()
    fees=models.IntegerField(default=0)
    outcomes=models.TextField()
    prerequisits=models.TextField()
    description=models.TextField()
    syllabus=models.FileField()
    date_time=models.DateTimeField(default=datetime.now, blank=True)
    def __str__(self):
        return self.course_name

class Student(models.Model):
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    name=models.CharField(max_length=30)
    email=models.EmailField()
    phone=models.CharField(max_length=10)
    college=models.ForeignKey(College,on_delete=models.SET('OTHER'))
    year=models.CharField(max_length=20,choices=YEAR_CHOICES)
    def __str__(self):
        return self.name

class StudentCourse(models.Model):
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,to_field='course_name',on_delete=models.CASCADE)
    admission = models.BooleanField(default=False)
    fees_paid = models.IntegerField(default=0)
    comments = models.TextField()
    rating = models.CharField(max_length=20, choices=RATING_CHOICES)
    def __str__(self):
        return self.name+" @ "+self.course.course_name

class StudentContact(models.Model):
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    message=models.TextField()
    def __str__(self):
        return self.name

class Review(models.Model):
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    course = models.ForeignKey(Course, to_field='course_name', on_delete=models.CASCADE)
    rating = models.CharField(max_length=20, choices=RATING_CHOICES)
    review = models.TextField()
    reviewer = models.ForeignKey(Student,on_delete=models.CASCADE)
    def __str__(self):
        return self.review

class StudyCourse(models.Model):
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    course_name= models.CharField(max_length=30)
    material_file=models.FileField()
    def __str__(self):
        return self.course_name