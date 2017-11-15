# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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

COURSE_CHOICES= (
    ('C', 'C'),
    ('C++', 'C++'),
    ('Python', 'Python'),
    ('Django', 'Django'),
)

class student(models.Model):
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    name=models.CharField(max_length=30)
    email=models.EmailField()
    phone=models.CharField(max_length=10)
    college=models.CharField(max_length=20,choices=COLLEGE_CHOICES)
    year=models.CharField(max_length=20,choices=YEAR_CHOICES)
    course=models.CharField(max_length=20,choices=COURSE_CHOICES)
    interest=models.CharField(max_length=50)

