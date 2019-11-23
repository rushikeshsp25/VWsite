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

class College(models.Model):
    name=models.CharField(max_length=70,unique=True)
    def __str__(self):
        return self.name

class Course(models.Model):
    date_time=models.DateTimeField(default=datetime.now, blank=True)
    course_name=models.CharField(max_length=70,unique=True)
    is_online=models.BooleanField(default=False)
    level=models.CharField(max_length=20,choices=LEVEL_CHOICES)
    course_icon=models.FileField()
    fees=models.IntegerField(default=0)
    outcomes=models.TextField()
    prerequisits=models.TextField()
    description=models.TextField()
    syllabus=models.FileField()

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


class CourseBatch(models.Model):
    start_date=models.DateField(blank=True)
    course=models.ForeignKey(Course,to_field='course_name',on_delete=models.CASCADE)
    batch_name=models.CharField(max_length=30)
    fees=models.IntegerField()
    feedback_enable=models.BooleanField()
    def __str__(self):
       return self.batch_name


class FeedbackQuestion(models.Model):
    question_name=models.TextField()
    question_type=models.CharField(max_length=10,choices=FEEDBACK_TYPE_CHOICES)
    def __str__(self):
        return self.question_name

class FeedbackBatch(models.Model):
    batch_id=models.ForeignKey(CourseBatch,on_delete=models.CASCADE)
    start_date=models.DateTimeField()
    end_date=models.DateTimeField()

class FeedbackResponse(models.Model):
    question_id=models.ForeignKey(FeedbackQuestion,on_delete=models.CASCADE)
    feedback_batch_id=models.ForeignKey(FeedbackBatch,on_delete=models.CASCADE)
    student_id=models.ForeignKey(Student,to_field='id',on_delete=models.CASCADE)
    response=models.TextField()

