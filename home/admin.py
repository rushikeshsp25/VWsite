# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import student,course,student_contact
# Register your models here.

admin.site.register(student)
admin.site.register(course)
admin.site.register(student_contact)