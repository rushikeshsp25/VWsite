from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from .forms import CourseForm, StudyCourseForm
from django.contrib.auth import authenticate, login,logout
from .models import *
from datetime import datetime
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
import os
import requests
import PyPDF2
import io
#for displaying messages
from django.contrib import messages

from .helpers.linkCheck import getNotWorkingLinksHtml

# Create your views here.
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if 'next' in request.GET:
                    return redirect(request.GET['next'])
                else:
                    return redirect('home:index')
            else:
                return render(request, 'home/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'home/login.html', {'error_message': 'Invalid login'})
    return render(request, 'home/login.html')

def logout_user(request):
    logout(request)
    return redirect('home:login_user')

def index(request):
    return render(request,'home/index.html')

@login_required
@user_passes_test(lambda u: u.has_perm('home.add_course'),login_url='/permissionerror/')
def create_new_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            new_course=form.save(commit=False)
            new_course.course_icon=request.FILES['course_icon']
            new_course.syllabus = request.FILES['syllabus']
            file_type = new_course.course_icon.url.split('.')[-1].lower()
            file_type2 = new_course.syllabus.url.split('.')[-1].lower()
            context = {
                'form': form
            }
            is_error=False
            if file_type not in IMAGE_FILE_TYPES:
                is_error=True
                context['error_message'] = '<li>Course Icon file must be PNG, JPG, or JPEG</li>'
            if file_type2 !='pdf':
                is_error=True
                if 'error_message' in context:
                    context['error_message'] = context['error_message']+'<li>Syllabus file must be PDF</li>'
                else:
                    context['error_message'] = '<li>Syllabus file must be PDF</li>'
            if is_error:
                return render(request, 'home/create_edit_course.html', context)
            new_course.save()
            return HttpResponse('Course created successfully !')
    else:
        form = CourseForm()
    return render(request,'home/create_edit_course.html',{'form':form})

@login_required
@user_passes_test(lambda u: u.has_perm('home.edit_course'),login_url='/permissionerror/')
def edit_course(request,pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        form = CourseForm(request.POST,request.FILES,instance=course)
        if form.is_valid():
            new_course=form.save(commit=False)
            new_course.course_icon=request.FILES['course_icon']
            new_course.syllabus = request.FILES['syllabus']
            file_type = new_course.course_icon.url.split('.')[-1].lower()
            file_type2 = new_course.syllabus.url.split('.')[-1].lower()
            context = {
                'form': form
            }
            is_error=False
            if file_type not in IMAGE_FILE_TYPES:
                is_error=True
                context['error_message'] = '<li>Course Icon file must be PNG, JPG, or JPEG</li>'
            if file_type2 !='pdf':
                is_error=True
                if 'error_message' in context:
                    context['error_message'] = context['error_message']+'<li>Syllabus file must be PDF</li>'
                else:
                    context['error_message'] = '<li>Syllabus file must be PDF</li>'
            if is_error:
                return render(request, 'home/create_edit_course.html', context)
            new_course.save()
            return HttpResponse('Course created successfully !')
    else:
        form = CourseForm(instance=course)
    return render(request,'home/create_edit_course.html',{'form':form})

def display_all_courses(request):
    return render(request,'home/courses.html')

def student_admission(request):
    return render(request,'home/admission.html')

@login_required
@user_passes_test(lambda u: u.has_perm('home.create_studycourse'),login_url='/permissionerror/')
def create_new_study_material(request):
    if request.method == "POST":
        form = StudyCourseForm(request.POST,request.FILES)
        if form.is_valid():
            new_study_course=form.save(commit=False)
            new_study_course.material_file=request.FILES['material_file']
            file_type = new_study_course.material_file.url.split('.')[-1].lower()
            if file_type not in ['html','pdf'] :
                context = {
                    'form': form,
                    'error_message': '<li>Syllabus file must be of type HTML or PDF</li>'
                }
                return render(request, 'home/create_edit_study_course.html', context)
            new_study_course.save()
            messages.success(request,'Study Material created successfully !')
            return redirect('home:dashboard')
    else:
        form = StudyCourseForm()
    return render(request,'home/create_edit_study_course.html',{'form':form})

def display_study_material(request,course_slug):
    study_course = get_object_or_404(StudyCourse, course_slug=course_slug)
    material_filename=study_course.material_file
    file_type = material_filename.url.split('.')[-1].lower()
    material_filepath = os.path.abspath(os.path.dirname(__file__)+'/../media/'+str(material_filename))
    if file_type == 'pdf':
        f=open(material_filepath, "rb")     #readin in binary mode is necessary for a pdf file
        contents =f.read()
        f.close()
        return HttpResponse(contents, content_type='application/pdf')
    else:
        f=open(material_filepath, "r")
        contents =f.read()
        f.close()
        return render(request,'home/display_study_course.html',{'course_name':study_course.course_name,'content':contents})

def display_all_study_material(request):
    courses=StudyCourse.objects.all()
    return render(request,'home/display_study_courses_all.html',{'courses':courses})

@login_required
@user_passes_test(lambda u: u.has_perm('home.view_studycourse'),login_url='/permissionerror/')
def notWorkingLinks(request):
    study_courses = StudyCourse.objects.all()
    not_working_links_all = []
    for course in study_courses:
        course_name = course.course_name
        material_filename = course.material_file
        file_type = material_filename.url.split('.')[-1].lower()
        material_filepath = os.path.abspath(os.path.dirname(__file__)+'/../media/'+str(material_filename))
        if file_type == 'html':
            f = open(material_filepath,"r")
            html_content = f.read()
            not_working_links = getNotWorkingLinksHtml(html_content)
            not_working_links_all.append({course_name : not_working_links})
        elif file_type=='PDF':
            pdf_content = io.BytesIO()
            pdf_content.seek(0)
            pdf_content =PyPDF2.PdfFileReader(open(material_filepath,mode='rb'))
            not_working_links_pdf=get_not_working_links_pdf(pdf_content)
            not_working_links_all.append({course_name :not_working_links_pdf })
        else:
            return HttpResponse("Please Choose Either Html or Pdf file correctly")
    #sending emails
    admin_emails =  User.objects.filter(is_superuser=True).values_list('email', flat=True)
    try:
        send_mail('Unreachable Links Report',
                'Hi Admin,\n' + 
                'Following are unreachable links please take action : \n'+
                str(not_working_links_all),
                'admin@visionware.in', admin_emails)
        return HttpResponse("not working links mails sent successfully")
    except Exception as e:
        print("Exception is : ",e)
        return HttpResponse("Something went wrong while sending not working links emails")
    return HttpResponse(not_working_links_all)

@login_required
def feedback_questions(request):
    feedback_questions=FeedbackQuestion.objects.all()
    return render(request,'home/feedback.html',{'feedback_questions':feedback_questions})








@login_required
@user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    return render(request,'home/dashboard.html')
    
def handler404(request,*args,**argv):
    return render(request,'home/page_not_found.html',status=404)

def handler500(request,*args,**argv):
    return HttpResponse("Resourse is deleted or moved")