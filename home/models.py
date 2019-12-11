# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
from django.utils.text import slugify
import itertools

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

FEEDBACK_TYPE_CHOICES=(
    ('comment', 'comment'),
    ('rating', 'rating'),
)


LEVEL_CHOICES= (
    ('Beginner', 'Beginner'),
    ('Intermediate', 'Intermediate'),
    ('Advanced', 'Advanced')
)

FEEDBACK_TYPE_CHOICES=(
    ('comment', 'comment'),
    ('rating', 'rating'),
)


class College(models.Model):
    name=models.CharField(max_length=70,unique=True)
    shortname_without_space=models.CharField(max_length=70,unique=True)
    def __str__(self):
        return self.name

class Course(models.Model):
    date_time=models.DateTimeField(default=datetime.now, blank=True)
    course_name=models.CharField(max_length=70,unique=True)
    is_online=models.BooleanField(default=False)
    level=models.CharField(max_length=20,choices=LEVEL_CHOICES)
    course_icon=models.FileField(upload_to='courseIcons')
    # fees=models.IntegerField(default=0)
    outcomes=models.TextField()
    prerequisits=models.TextField()
    description=models.TextField()
    syllabus=models.FileField(upload_to='syllabus')
    course_slug = models.SlugField(unique=True,blank=True)
    def _generate_slug(self):
        generated_slug = slug_original = slugify(self.course_name, allow_unicode=True)
        for i in itertools.count(1):
            if not StudyCourse.objects.filter(course_slug=generated_slug).exists():
                break
            generated_slug = '{}-{}'.format(slug_original, i)
        self.course_slug = generated_slug

    def save(self, *args, **kwargs):
        if not self.pk:
            self._generate_slug()
        super().save(*args, **kwargs)
    def __str__(self):
        return self.course_name

class CourseBatch(models.Model):
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    batch_name=models.CharField(max_length=30)
    start_date=models.DateField()
    registration_end_date=models.DateField()
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    fees=models.IntegerField()
    def __str__(self):
        return self.batch_name

class Student(models.Model):
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    first_name=models.CharField(max_length=70)
    last_name=models.CharField(max_length=70)
    email = models.EmailField()
    phone=models.CharField(max_length=10)
    college=models.ForeignKey(College,on_delete=models.SET('OTHER'))
    year=models.CharField(max_length=20,choices=YEAR_CHOICES)
    dob = models.DateField()
    batch = models.ForeignKey(CourseBatch,on_delete=models.CASCADE)
    admission = models.BooleanField(default=False)
    fees_paid = models.IntegerField(default=0)
    comments = models.TextField(blank=True)
    rating = models.CharField(max_length=20, choices=RATING_CHOICES,blank=True)
    def __str__(self):
        return self.first_name+' @ '+self.batch.batch_name
        
class StudyCourse(models.Model):
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    course_name= models.CharField(max_length=70)
    description = models.TextField(blank=True,null=True)
    material_file=models.FileField(upload_to='StudyCourse')
    course_slug = models.SlugField(unique=True,blank=True)
    def _generate_slug(self):
        generated_slug = slug_original = slugify(self.course_name, allow_unicode=True)
        for i in itertools.count(1):
            if not StudyCourse.objects.filter(course_slug=generated_slug).exists():
                break
            generated_slug = '{}-{}'.format(slug_original, i)
        self.course_slug = generated_slug

    def save(self, *args, **kwargs):
        if not self.pk:
            self._generate_slug()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.course_name

class FeedbackQuestion(models.Model):
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    question=models.TextField()
    question_type=models.CharField(max_length=10,choices=FEEDBACK_TYPE_CHOICES)
    def __str__(self):
        return self.question

class FeedbackBatch(models.Model):
    date_time=models.DateTimeField(default=datetime.now)
    batch=models.ForeignKey(CourseBatch,on_delete=models.CASCADE)
    feedback_title=models.CharField(max_length=50,default='')
    start_date=models.DateField()    
    end_date=models.DateField()
    def __str__(self):
        return self.feedback_title

class FeedbackResponse(models.Model):
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    question=models.ForeignKey(FeedbackQuestion,on_delete=models.CASCADE)
    feedback_batch=models.ForeignKey(FeedbackBatch,on_delete=models.CASCADE)
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    response=models.TextField()
    def __str__(self):
        return self.feedback_batch.feedback_title+" : "+self.question.question+" : "+self.student.user.email

class Recruiter(models.Model):
    full_name = models.CharField(max_length=70)
    email = models.EmailField()
    mobile_no=models.CharField(max_length=10)
    company_name = models.CharField(max_length=70)
    designation = models.CharField(max_length=70)
    message = models.TextField()
    def __str__(self):
        return self.full_name+"@"+self.company_name


class Service(models.Model):
    service_name = models.CharField(max_length=70)
    full_name = models.CharField(max_length=70)
    email = models.EmailField()
    mobile_no=models.CharField(max_length=10)
    business_name = models.CharField(max_length=70)
    business_description = models.TextField()
    designation = models.CharField(max_length=70)
    work_description = models.TextField()
    def __str__(self):
        return self.full_name+"@"+self.service_name