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
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, XMLConverter, HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO
import re


# Create your views here.
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']

def convert_pdf(path, format='html', codec='utf-8', password=''):
    ''' this function converts the pdf to html or text'''
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    laparams = LAParams()
    if format == 'text':
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'html':
        device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'xml':
        device = XMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    else:
        raise ValueError('provide format, either text, html or xml!')
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue().decode()
    fp.close()
    device.close()
    retstr.close()
    return text


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
@user_passes_test(lambda u: u.has_perm('home.add_course'),login_url='/permissionerror/')
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

def create_new_study_course(request):
    if request.method == "POST":
        form = StudyCourseForm(request.POST,request.FILES)
        if form.is_valid():
            new_study_course=form.save(commit=False)
            new_study_course.material_file=request.FILES['material_file']
            file_type = new_study_course.material_file.url.split('.')[-1].lower()
            if file_type !='pdf':
                context = {
                    'form': form,
                    'error_message': '<li>Syllabus file must be PDF</li>'
                }
                return render(request, 'home/create_edit_study_course.html', context)
            new_study_course.save()
            return HttpResponse('Study Course created successfully !')
    else:
        form = StudyCourseForm()
    return render(request,'home/create_edit_study_course.html',{'form':form})

def convert_pdf_to_html(request,pk):
    study_course = get_object_or_404(StudyCourse, pk=pk)
    material_filename=study_course.material_file
    material_filepath = os.path.abspath(os.path.dirname(__file__)+'/../media/'+str(material_filename))
    html_path=os.path.abspath(os.path.dirname(__file__)+'/templates/home/display_study_course_pdf.html')
    pdf_to_html=convert_pdf(material_filepath)              #convert pdf to html
    f=open(html_path,'w')
    f.write("<head><title>"+study_course.course_name+"</title></head>"+pdf_to_html)                 #write into template
    f.close()
    return render(request,'home/display_study_course_pdf.html')

def display_all_study_course(request):
    courses=StudyCourse.objects.all()
    return render(request,'home/display_study_courses_all.html',{'courses':courses})

def handler404(request,*args,**argv):
    return render(request,'home/page_not_found.html',status=404)

def handler500(request,*args,**argv):
    return HttpResponse("Resourse is deleted or moved")