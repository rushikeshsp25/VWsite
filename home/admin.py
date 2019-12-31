# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register([College,Course,Student,CourseBatch,StudyCourse,FeedbackQuestion,FeedbackBatch,FeedbackResponse,Recruiter,Attendance,CertificationDetail,StudentCertification,Service,PlacementInformation])
