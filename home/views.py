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
#for displaying messages
from django.contrib import messages

import requests
import json

from .helpers.linkCheck import getNotWorkingLinksHtml

# Create your views here.
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']

def dictionarify_the_response_queryset(response):
    d={}
    for i in response:
        print(i.id)
        d[i.response]=d.get(i,0)+1
    return d


def login_user(request):
    if(request.user.is_authenticated):
        return redirect('home:index')
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
                return render(request, 'home/auth/login.html', {'error_message': '<li>Your account has been disabled</li>'})
        else:
            return render(request, 'home/auth/login.html', {'error_message': '<li>Invalid Username or Password</li>'})
    return render(request, 'home/auth/login.html')

def signup_user(request):
    colleges = College.objects.all()
    if(request.user.is_authenticated):
        return redirect('home:index')
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        mobile = request.POST['mobile']
        college = request.POST['college']
        year = request.POST['year']
        password = request.POST['password']
        college_obj = College.objects.get(shortname_without_space = college)
        print(fname,lname,email,mobile,college,year,password)
        if not fname or not lname or not email or not mobile or not college or not year or not password:
            return render(request, 'home/auth/signup.html',{'colleges':colleges,
                    'error_message': '<li>Incomplete form is submitted</li>'
            })
        if User.objects.filter(email=email).exists():
            messages.error(request,'Signup failed! There is existing account with this email')
            return render(request, 'home/auth/signup.html',{'colleges':colleges})
        
        user = User.objects.create_user(username = email, 
                            email= email,
                            first_name = fname,
                            last_name = lname,
                            password=password)
        
        student = Student(phone = mobile,user=user,college=college_obj,year=year)
        student.save()

        if user:
            messages.success(request,'Account created successfully ! Please login')
            return redirect('home:login_user')
        else:
            messages.error(request,'Signup failed! Please try agin')
            return render(request, 'home/auth/signup.html',{'colleges':colleges})
    else:
        colleges = College.objects.all()
        return render(request, 'home/auth/signup.html',{'colleges':colleges})

def logout_user(request):
    logout(request)
    return redirect('home:login_user')

def index(request):
    courses = Course.objects.all().order_by('date_time')[:5]
    return render(request,'home/index.html',{'courses':courses})

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
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
                return render(request, 'home/course/create_edit_course.html', context)
            new_course.save()
            messages.success(request,'Course Saved successfully !')
            return redirect('home:dashboard')
    else:
        form = CourseForm()
    return render(request,'home/course/create_edit_course.html',{'form':form})

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
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
            messages.success(request,'Course Saved successfully !')
            return redirect('home:dashboard')
    else:
        form = CourseForm(instance=course)
    return render(request,'home/course/create_edit_course.html',{'form':form})

def display_all_courses(request):
    offline_courses = Course.objects.filter(is_online = False).order_by('date_time')
    online_courses = Course.objects.filter(is_online = True).order_by('date_time')
    return render(request,'home/course/courses.html',{'offline_courses':offline_courses,'online_courses':online_courses})

def course_details(request,course_slug):
    course = Course.objects.get(course_slug=course_slug)
    if course.is_online:
        return render(request,'home/course/course_detail.html',{'course':course})
    else:    
        today = datetime.today()
        batches = CourseBatch.objects.filter(course=course,start_date__gte=today).order_by('start_date')
        return render(request,'home/course/course_detail.html',{'course':course,'upcoming_batches':batches})

@login_required
def student_admission_batch(request,course_batch_pk):
    try:
        course_batch = CourseBatch.objects.get(pk = course_batch_pk)
    except:
        messages.error(request,"Selected course batch doesn't exists !")
        return redirect('home:display_all_courses')
    try:
        student = Student.objects.get(user = request.user)
    except:
        messages.error(request,'Invalid attempt !')
        return redirect('home:display_all_courses')
    
    student_batch = StudentBatch(student=student,
                            batch=course_batch
                     )
    student_batch.save()
    messages.success(request,"Please make the payment to confirm your admission !")
    return render(request,'home/student/admission.html')

@login_required
def student_admission_online_course(request,course_pk):
    try:
        course = Course.objects.get(pk = course_pk)
    except:
        messages.error(request,"Selected online course doesn't exists !")
        return redirect('home:display_all_courses')
    try:
        student = Student.objects.get(user = request.user)
    except:
        messages.error('Invalid attempt !')
        return redirect('home:display_all_courses')
    
    student_course = StudentOnlineCourse(student=student,
                            batch=batch
                     )
    student_course.save()
    messages.success(request,"Please make the payment to confirm your admission !")
    return render(request,'home/admission.html')

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
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
                return render(request, 'home/study_material/create_edit_study_course.html', context)
            new_study_course.save()
            messages.success(request,'Study Material created successfully !')
            return redirect('home:dashboard')
    else:
        form = StudyCourseForm()
    return render(request,'home/study_material/create_edit_study_course.html',{'form':form})

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
        return render(request,'home/study_material/display_study_course.html',{'course_name':study_course.course_name,'description':study_course.description,'content':contents})

def display_all_study_material(request):
    courses=StudyCourse.objects.all()
    return render(request,'home/study_material/display_study_courses_all.html',{'courses':courses})

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
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
        #also add for pdf
        #else:
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
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def dashboard(request):
    all_courses = Course.objects.all()
    all_batches = CourseBatch.objects.all()
    return render(request,'home/dashboard.html',{
        'all_courses':all_courses,
        'all_batches':all_batches
    })

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def display_feedback_enabled_batches(request):
    feedback_enabled_batches=CourseBatch.objects.filter(feedback_enable=True).order_by('-start_date')
    return render(request,'home/feedback/display_feedback_enabled_batches.html',{'feedback_enabled_batches':feedback_enabled_batches})

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def display_feedback_questions(request,batch_id):
    batch=CourseBatch.objects.get(id=batch_id)
    feedback_questions=FeedbackQuestion.objects.all()
    return render(request,'home/feedback/display_feedback_questions.html',{'feedback_questions':feedback_questions,'batch':batch})

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def display_feedback_response(request,batch_id,question_id):
    question=FeedbackQuestion.objects.get(id=question_id)
    batch=CourseBatch.objects.get(id=batch_id)
    if question.question_type=='rating':
        response=FeedbackResponse.objects.filter(question_id=question_id,batch_id=batch_id)
        data={'1':0,'2':0,'3':0,'4':0,'5':0}
        for i in response:
            if i.response in data.keys():                                     #convert ratings into dictionary format{'rate':'No of students'}
                data[i.response]=data[i.response]+1        
        return render(request,'home/feedback/display_feedback_response.html',{'data':data,'batch':batch,'question':question})
    else:
         response=FeedbackResponse.objects.filter(question_id=question_id,batch_id=batch_id)
         return render(request,'home/feedback/display_feedback_response.html',{'response':response,'batch':batch,'question':question})

def contact_us(request):
    return render(request,'home/contactus.html')

def hire_with_us(request):
    if request.method == "POST":
        full_name = request.POST['fullname']
        email = request.POST['email']
        mobile = request.POST['mobile']
        company = request.POST['company']
        designation = request.POST['designation']
        message = request.POST['message']
        if not full_name or not email or not mobile or not company or not designation or not message:
            return render(request, 'home/hire_with_us.html',{'error_message': '<li>Incomplete form is submitted</li>'})
        recruiter = Recruiter(full_name=full_name,email=email,mobile_no=mobile,company_name=company,designation=designation,message=message)
        recruiter.save()
        messages.success(request,'Your Request Submitted Successfully ! Our Team will contact you soon !')
        return redirect('home:hire_with_us')
    else:
        return render(request,'home/hire_with_us.html')

def student_dashboard(request):
    return render(request,'home/student/dashboard_student.html')

def handler404(request,*args,**argv):
    return render(request,'home/page_not_found.html',status=404)

def handler500(request,*args,**argv):
    return HttpResponse("Resourse is deleted or moved")

def permissionerror(request):
    return render(request,'home/page_not_found.html')


#student search related views
@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def admit_student(request):
    return HttpResponse('admitting a student')

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def students(request):
    all_batches = CourseBatch.objects.all()
    all_colleges = College.objects.all()
    return render(request, 'home/admin/students.html',{'all_batches':all_batches,'all_colleges':all_colleges})

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def students_all(request):
    s_objs = Student.objects.all().order_by('-date_time')
    context = {
        "result_type": "All students ",
        "result_desc": "",
        "students": s_objs
    }
    return render(request, 'home/admin/student_college_all.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def batchwise_students(request,pk):
    try:
        batch=CourseBatch.objects.get(pk=pk)
    except:
        messages.error(request,'Invalid Batch')
        return redirect('home:students')

    s_objs = StudentBatch.objects.filter(batch=batch).order_by('-date_time')
    context = {
    "result_type": "Batch Wise Students",
    "result_desc": batch.batch_name,
    "students": s_objs,
    }
    return render(request, 'home/admin/student_batch.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def collegewise_students(request,pk):
    try:
        college=College.objects.get(pk=pk)
    except:
        messages.error(request,'Invalid College Name')
        return redirect('home:students')
    s_objs=Student.objects.filter(college=college).order_by('-date_time')
    context = {
        "result_type": "College Wise Students",
        "result_desc": college.name,
        "students": s_objs,
    }
    return render(request, 'home/admin/student_college_all.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def student_detail(request,pk):
    try:
        s_obj = Student.objects.get(pk=pk)
    except:
        messages.error(request,'Invalid Student ID')
        return redirect('home:students')
    try:
        s_batches = StudentBatch.objects.filter(student=s_obj)
    except:
        s_batches=None
    print(s_batches)
    return render(request, 'home/student_detail.html', {'student': s_obj,'student_batches':s_batches})

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def search_student(request,search_by):
    if request.method == "POST":
        try:
            s_objs=None
            if search_by=='eno':
                eno=request.POST.get('search_eno',False)
                s_objs=Student.objects.filter(pk=eno)
            if search_by=='name':
                name=request.POST.get('search_name',False)
                s_objs=Student.objects.filter(user__first_name__contains=name)
            if search_by=='email':
                email=request.POST.get('search_email',False)
                s_objs=Student.objects.filter(user__email=email)
            context = {
                "result_type": "Students Result",
                "result_desc": "",
                "students": s_objs,
            }
            return render(request, 'home/admin/student_college_all.html', context)
        except Exception as err:
            print(err)
            messages.error(request,'No Student Found!')
            return redirect('home:students')

