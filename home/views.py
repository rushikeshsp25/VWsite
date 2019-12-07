from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from .forms import CourseForm,BatchForm, StudyCourseForm,FeedbackBatchForm, FeedbackForm
from django.contrib.auth import authenticate, login,logout
from .models import *
from datetime import datetime
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.csrf import csrf_exempt
import os
import requests
import PyPDF2
import io
#for displaying messages
from django.contrib import messages

import requests
import json

from django.db.models import Subquery
from .helpers.linkCheck import getNotWorkingLinksHtml
from .helpers.feedbackQuestionsResponse import feedback_question_responses

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
    courses = Course.objects.all().order_by('date_time')[:4]
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

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def create_new_batch(request):
    if request.method == "POST":
        form = BatchForm(request.POST)
        if form.is_valid():
            new_batch=form.save(commit=False)
            new_batch.save()
            messages.success(request,'Batch Saved successfully !')
            return redirect('home:dashboard')
        else:
            messages.error(request,'Invalid Form Submitted !')
            return redirect('home:create_new_batch')
    else:
        form = BatchForm()
    return render(request,'home/course/create_edit_batch.html',{'form':form})

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

def student_admission_batch(request,course_batch_pk):
    try:
        course_batch = CourseBatch.objects.get(pk = course_batch_pk)
    except:
        messages.error(request,"Selected course batch doesn't exists !")
        return redirect('home:display_all_courses')
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        mobile = request.POST['mobile']
        college = request.POST['college']
        year = request.POST['year']
        dob = request.POST['dob']
        college_obj = College.objects.get(shortname_without_space = college)
        batch = CourseBatch.objects.get(pk=course_batch_pk)
        student = Student(first_name=fname,last_name=lname,email=email,phone = mobile,college=college_obj,year=year,dob=dob,batch=batch)
        student.save()
        messages.success(request,'You have successfully enrolled for the batch !')
        return redirect('home:display_all_courses')
    else:
        all_colleges = College.objects.all()
        return render(request,'home/student/admission.html',{'colleges':all_colleges})


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
def feedback_init(request,feedback_batch_id):
    if request.method=="POST":
        email = request.POST['email']
        dob = request.POST['dob']
        try:
            sobj = Student.objects.get(email=email,dob=dob)
            print(sobj)
            messages.success(request, 'Please give the proper feedback, It is very important to us!')
            feedback_questions=FeedbackQuestion.objects.all()
            feedback_batch = FeedbackBatch.objects.get(id=feedback_batch_id)
            return render(request,'home/feedback/feedback_proceed.html',{'feedback_batch':feedback_batch,'student':sobj,'feedback_questions':feedback_questions})
        except:
            messages.error(request, 'You are not allowed to give this feedback')
            return HttpResponse("Something went wrong")
            # return redirect('home:feedback_init')
        return HttpResponse("Your Feedback is successfully submitted")
    else:
        return render(request,'home/feedback/feedback_init.html')

@csrf_exempt
@login_required
def feedback_proceed(request,feedback_batch_id):
    print(request.POST)
    return HttpResponse("Feedback next steps")
    # feedback_questions=FeedbackQuestion.objects.all()
    # response=FeedbackResponse()
    # response.response=request.POST.get("comment")
    # response.save()
    # return render(request,'home/feedback/feedback.html',{'feedback_questions':feedback_questions})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_feedback_question(request,pk):
    FeedbackQuestion.objects.filter(id=pk).delete()
    display_all_questions=FeedbackQuestion.objects.all()
    return render(request,'home/feedback/feedback_question.html',{'display_all_questions':display_all_questions})

@login_required
def feedback_questions(request):
    display_all_questions=FeedbackQuestion.objects.all()
    return render(request,'home/feedback/feedback_question.html',{'display_all_questions':display_all_questions})

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def feedback_questions_new(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            new_question=form.save()
            new_question.save()
            messages.success(request, 'Question Created Successfully!')
            return render(request,'home/dashboard.html')
    else:
        form = FeedbackForm()
    return render(request,'home/feedback/create_edit_feedback_question.html',{'form':form})

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def edit_feedback_question(request,pk):
    course = get_object_or_404(FeedbackQuestion, pk=pk)
    if request.method=='POST':
        form = FeedbackForm(request.POST,instance=course)
        if form.is_valid():
            new_question=form.save()
            new_question.save()
            messages.success(request, 'Question Edited successfully!')
            return render(request,'home/dashboard.html')
    else:
        form = FeedbackForm(instance=course)
    return render(request,'home/feedback/create_edit_feedback_question.html',{'form':form})

@login_required
# @user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def dashboard(request):
    if request.user.is_superuser:
        all_courses = Course.objects.all()
        all_batches = CourseBatch.objects.all()
        return render(request,'home/dashboard.html',{
            'all_courses':all_courses,
            'all_batches':all_batches
        })
    else:
        return redirect('home:student_dashboard')

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

@login_required
@user_passes_test(lambda u: u.is_superuser)
def display_feedback_enabled_batches(request):
    feedback_batches=FeedbackBatch.objects.all().order_by('-start_date')
    return render(request,'home/feedback/display_feedback_batches.html',{'feedback_batches':feedback_batches})

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def feedback_batch_response(request,feedback_batch_id):
    feedback_batch=FeedbackBatch.objects.get(id=feedback_batch_id)
    feedback_questions=FeedbackQuestion.objects.all()
    rating_question_ids=FeedbackQuestion.objects.filter(question_type='rating').values_list('id')
    response=FeedbackResponse.objects.filter(feedback_batch_id=feedback_batch_id,question_id__in=Subquery(rating_question_ids))           #selecting response of a batch and only response type questions
    data={'1':0,'2':0,'3':0,'4':0,'5':0}
    for i in response:
        if i.response in data.keys():                                     #convert ratings into dictionary format{'rate':'No of students'}
            data[i.response]=data[i.response]+1
    feedback_batch = FeedbackBatch.objects.get(id=feedback_batch_id)
    batch_responses= FeedbackResponse.objects.filter(feedback_batch=feedback_batch)
    rating_response,comment_response=feedback_question_responses(feedback_questions,batch_responses)  
    print(rating_response,comment_response)  
    return render(request,'home/feedback/feedback_batch_response.html',{'feedback_questions':feedback_questions,'overall':data,'rating_response':rating_response,'comment_response':comment_response,'feedback_batch':feedback_batch})

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def create_new_feedback(request):
    if request.method == "POST":
        form = FeedbackBatchForm(request.POST,request.FILES)
        if form.is_valid():
            feedback=form.save(commit=False)
            if (feedback.end_date-feedback.start_date).days >= 0:
                print(feedback.end_date-feedback.start_date)
                feedback.save()
                messages.success(request,'Feedback for Batch is created successfully !')
                return redirect('home:dashboard')
            else:
                context = {
                    'form': form,
                    'error_message': '<li>End date cannot be before Start date</li>'
                }
                return render(request,'home/feedback/feedback_batch_form.html',context)
    else:
        form = FeedbackBatchForm()
    return render(request,'home/feedback/feedback_batch_form.html',{'form':form})

def handler404(request,*args,**argv):
    return render(request,'home/page_not_found.html',status=404)

def handler500(request,*args,**argv):
    return HttpResponse("Resourse is deleted or moved")

def permissionerror(request):
    return render(request,'home/page_not_found.html')

#student search related views
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

    s_objs = Student.objects.filter(batch=batch).order_by('-date_time')
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
    return render(request, 'home/student_detail.html', {'student': s_obj})

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
                s_objs=Student.objects.filter(first_name__contains=name)
            if search_by=='email':
                email=request.POST.get('search_email',False)
                s_objs=Student.objects.filter(email=email)
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

@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def pay_fees(request,pk):
    if request.method == "POST":
        fees_paying=request.POST.get('feesip',0)
        student_obj = get_object_or_404(Student, pk=pk)
        fees_remaining = int(student_obj.batch.fees) - int(student_obj.fees_paid)
        if int(fees_paying)>int(fees_remaining):
            return render(request, 'home/pay_fees.html', {'student': student_obj,
                                                          'fees_remaining': fees_remaining,
                                                          'error_message':'invalid fees amount entered',
                                                          })
        student_obj.fees_paid=int(student_obj.fees_paid)+int(fees_paying)
        student_obj.save()
        if int(student_obj.fees_paid)>=int(student_obj.batch.fees)/2:
            return redirect('home:confirm_admission',student_obj.pk)
        messages.success(request,'Rs'+str(fees_paying)+' fees is received successfully')
        return redirect('home:student_detail',student_obj.pk)
    else:
        student_obj = get_object_or_404(Student, pk=pk)
        fees_remaining = int(student_obj.batch.fees) - int(student_obj.fees_paid)
        return render(request,'home/pay_fees.html',{'student':student_obj,
                                                    'fees_remaining':fees_remaining,
                                                    })

@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def confirm_admission(request,pk):
    s_obj=get_object_or_404(Student,pk=pk)
    s_obj.admission=True
    s_obj.save()
    # try:
    #     send_mail('Your Admission @ VisionWare IT Training Institute',
    #               'Hi ' + s_obj.name + ',\n' + 'Your admission is confirmed for ' + str(
    #                   s_obj.course.course_name) +
    #               ' course.\nTotal course Fees is : ' + str(s_obj.course.fees) + '\nYou have Paid : ' + str(
    #                   s_obj.fees_paid) +
    #               '\nYour Enrollment Number is : ' + str(
    #                   s_obj.pk) + '\nThanks for Being part of Visionware :))'
    #               , 'admin@visionware.in', [str(s_obj.email),'rushikeshsp25@gmail.com'])
    # except Exception as e:
    #     return redirect('home:student_detail', pk=pk)
    return redirect('home:student_detail', pk=pk)