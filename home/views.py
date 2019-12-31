from django.shortcuts import render,redirect,get_object_or_404,render_to_response
from django.utils import timezone
from .forms import CourseForm,BatchForm, StudyCourseForm,FeedbackBatchForm, FeedbackForm,OnlineCampaignForm,CertificationDetailForm
from django.contrib.auth import authenticate, login,logout
from .models import *
from datetime import datetime
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.core import serializers
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.csrf import csrf_exempt
import os
import requests
import PyPDF2
import io
#for displaying messages
from django.contrib import messages
from django.template.loader import render_to_string



import requests
import json

from django.db.models import Subquery
from .helpers.linkCheck import getNotWorkingLinksHtml
from .helpers.feedbackQuestionsResponse import feedback_question_responses
from .helpers.onlineCampaignSMS import send_sms
from .helpers.attendance import get_attendance_dictionary
from .helpers.certification import generate_cert_id
import csv

from datetime import date
from django.forms.models import model_to_dict
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
    print(courses)
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
        batches = CourseBatch.objects.filter(course=course,registration_end_date__gte=today).order_by('start_date')
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

def feedback_init(request,feedback_batch_id):
    if request.method=="POST":
        email = request.POST['email']
        dob = request.POST['dob']
        try:
            sobj = Student.objects.get(email=email,dob=dob)
            feedback_batch = FeedbackBatch.objects.get(id=feedback_batch_id)
            try:
                fobjs = FeedbackResponse.objects.filter(feedback_batch=feedback_batch,student=sobj)
                print(fobjs)
                if(fobjs):
                    messages.error(request, 'You have already submitted the feedback')
                    return render(request,'home/feedback/feedback_init.html')
            except:
                pass
            feedback_questions=FeedbackQuestion.objects.all()
            today = datetime.today()
            feedback_batch = FeedbackBatch.objects.get(id=feedback_batch_id,start_date__gte = today, end_date__lte = today)
            if not (sobj.batch.id == feedback_batch.batch.id and sobj.admission):
                raise Exception("student not admitted")
            messages.success(request, 'Please give the proper feedback, It is very important to us!')
            return render(request,'home/feedback/feedback_proceed.html',{'feedback_batch':feedback_batch,'student':sobj,'feedback_questions':feedback_questions})
        except Exception as e:
            print(e)
            messages.error(request, 'You are not allowed to give this feedback')
            return render(request,'home/feedback/feedback_init.html')
    else:
        return render(request,'home/feedback/feedback_init.html')

@csrf_exempt
@login_required
def feedback_proceed(request,feedback_batch_id):
    userDetails = json.loads(request.POST.get("userDetails"))
    answers = json.loads(request.POST.get("answers"))
    sobj=None
    f_b=None
    try:
        # sobj = Student.objects.get(email=userDetails['userEmail'],dob=userDetails['userDob'])
        sobj = Student.objects.get(email=userDetails['userEmail'])
        f_b = FeedbackBatch.objects.get(id=feedback_batch_id)
    except Exception as e:
        print(e)
        messages.error(request,"Opps,something went wrong")
        return redirect('home:feedback_init',feedback_batch_id=feedback_batch_id )

    for key, value in answers.items():
        fq=FeedbackQuestion.objects.get(id = key)
        feed_res=FeedbackResponse(question=fq,feedback_batch=f_b,student=sobj,response=value)
        feed_res.save()
    # question=models.ForeignKey(FeedbackQuestion,on_delete=models.CASCADE)
    # feedback_batch=models.ForeignKey(FeedbackBatch,on_delete=models.CASCADE) 
    # response=models.TextField()
    messages.success(request,"Thank You! Feedback Submitted Successfully")
    return redirect('home:feedback_init',feedback_batch_id=feedback_batch_id )

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
            return redirect('home:feedback_questions')
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
    return HttpResponse("Permission Error")

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
@user_passes_test(lambda u: u.has_perm('home.view_student'),login_url='/permissionerror/')
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

@user_passes_test(lambda u: u.has_perm('home.change_student'),login_url='/permissionerror/')
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

@user_passes_test(lambda u: u.has_perm('home.change_student'),login_url='/permissionerror/')
def confirm_admission(request,pk):
    s_obj=get_object_or_404(Student,pk=pk)
    s_obj.admission=True
    s_obj.save()
    context_dict={
        "name":s_obj.first_name+" "+s_obj.last_name,
        "course_name":s_obj.batch.course.course_name,
        "batch_name":s_obj.batch.batch_name,
        "total_fees":s_obj.batch.fees,
        "paid_fees":s_obj.fees_paid
    }
    html_message = render_to_string('home/email_templates/admission_confirmed.html', context_dict)
    # try:
    #     email = EmailMessage('Admission Confirmation - VisionWare IT Training Institute', html_message, to=[str(s_obj.email),'dhapateashu.ad@gmail.com','rushikeshsp25@gmail.com'])
    #     email.content_subtype = "html" # this is the crucial part 
    #     email.send()
    # except Exception as e:
    #     messages.error(request,"Something Went Wrong !")
    #     return redirect('home:student_detail', pk=pk)
    messages.success(request,"Admission Confirmed !")
    return redirect('home:student_detail', pk=pk)

def services(request,name):
    if request.method=="POST":
        service_name = request.POST['service']
        full_name = request.POST['fullname']
        email = request.POST['email']
        mobile = request.POST['mobile']
        business_name = request.POST['company']
        company_des = request.POST['company_des']
        designation = request.POST['designation']
        message = request.POST['message']
        if not service_name or not full_name or not email or not mobile or not business_name or not designation or not message:
            return render(request, 'home/hire_with_us.html',{'error_message': '<li>Incomplete form is submitted</li>'})
        service = Service(service_name=service_name,full_name=full_name,email=email,mobile_no=mobile,business_name=business_name,designation=designation,work_description=message)
        service.save()
        messages.success(request,"Thank you for showing your interest in VisionWare, Our team will contact you soon")
        return redirect('home:index')
    else:
        service = name
        return render(request,'home/services.html',{'service':service})


    
@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def online_campaign(request):
    if request.method == "POST":
        form = OnlineCampaignForm(request.POST,request.FILES)
        if form.is_valid():
            new_online_campaign=form.save(commit=False)
            new_online_campaign.campaign_target_contacts_file=request.FILES['campaign_target_contacts_file']
            msg=request.POST.get('campaign_message')
            file_type = new_online_campaign.campaign_target_contacts_file.url.split('.')[-1].lower()
            if file_type != 'csv' :
                context = {
                    'form': form,
                    'error_message': '<li>Contacts file must be of type CSV</li>'
                }
                return render(request, 'home/online_campaign/online_campaign_form.html', context)
            file_contents=request.FILES['campaign_target_contacts_file'].read().decode('UTF-8')
            headings=file_contents.split('\r\n')[0].split(',')
            if headings[0].lower()!='name' or headings[1].lower()!='mobile' or headings[2].lower()!='email' or headings[3].lower()!='passout_year':
                context = {
                    'form': form,
                    'error_message': '<li>Table structure is not in the format of Name | Mobile | Email | Passout_Year</li>'
                }
                return render(request, 'home/online_campaign/online_campaign_form.html', context)
            new_online_campaign.save()
            status=send_sms(file_contents,msg)                      #this function is in helpers/onlineCampaignSMS.py
            if status==0:
                messages.error(request,'Sorry, something went wrong!')
                return redirect('home:dashboard')
            messages.success(request,'Online Campaign is successful!')
            return redirect('home:dashboard')
    else:
        form = OnlineCampaignForm()
        return render(request,'home/online_campaign/online_campaign_form.html',{'form':form})


@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def display_online_campaigns(request):
    campaigns=OnlineCampaign.objects.all().order_by('-id')
    return render(request,'home/online_campaign/display_online_campaigns.html',{'campaigns':campaigns})


@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def attendance_form(request):
    batches=CourseBatch.objects.all().order_by('-id')
    if request.method == "POST":
        if request.is_ajax():
            batch_id=request.POST.get('batch_id')
            students_queryset=Student.objects.filter(batch=batch_id)
            students=[]
            for i in students_queryset:
                l=[i.id,i.first_name,i.last_name]
                students.append(l)
            data={
            'students':students
            }
            return JsonResponse(data)
        else:
            if Attendance.objects.filter(batch=request.POST.get("batch"),lecture_date=datetime.now()).exists():
                messages.error(request,"Today's Attendance for entered batch has already been recorded!")
                return redirect('home:attendance_form')
                return render(request,'home/attendance/attendance_form.html',{'batches':batches,'error_message':"<li>Today's Attendance for entered batch has already been recorded!</li>"})
            att=Attendance()
            att.batch=CourseBatch.objects.get(id=request.POST.get("batch"))
            att.instructor=request.POST.get('lecture_taken_by')
            att.lecture_topics=request.POST.get('lecture_topics')
            att.start_time=request.POST.get('start_time')
            att.end_time=request.POST.get('end_time')
            att.remarks=request.POST.get('remarks')
            student_list=Student.objects.filter(batch=request.POST.get("batch"))
            att.attendance=get_attendance_dictionary(student_list,request.POST.getlist('students'))
            att.save()            
            
            messages.success(request,'Attendance added successfully!')
            return redirect('home:dashboard')
    else:
        return render(request,'home/attendance/attendance_form.html',{'batches':batches})


@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def view_attendance(request):
    batches=CourseBatch.objects.all().order_by('-id')
    if request.method=="POST":
        batch=request.POST.get('batch')
        att=Attendance.objects.filter(batch=batch).order_by('-id')
        return render(request,'home/attendance/view_attendance.html',{'batches':batches,'attendance':att})
    else:
        return render(request,'home/attendance/view_attendance.html',{'batches':batches})



@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def lecture_details(request,pk):
    a=Attendance.objects.get(id=pk)
    attendance=[]
    students=Student.objects.all()
    attendance_dict=json.loads(a.attendance)
    for s_id,att in attendance_dict.items():
        l=[s_id,students.get(id=int(s_id)).first_name,students.get(id=int(s_id)).last_name,att]
        attendance.append(l)   
    context={
        'batch':a.batch,
        'instructor':a.instructor,
        'lecture_date':a.lecture_date,
        'start_time':a.start_time,
        'end_time':a.end_time,
        'lecture_topics':a.lecture_topics,
        'remarks':a.remarks,
        'attendance':attendance
    }         
    return render(request,'home/attendance/view_lecture_details.html',context)

@login_required
@user_passes_test(lambda u: u.is_superuser,login_url='/permissionerror/')
def certification_form(request):
    if request.method == "POST":
        form = CertificationDetailForm(request.POST,request.FILES)
        if form.is_valid():
            certification=form.save(commit=False)
            certification.result_file=request.FILES['result_file']
            exam_name=request.POST.get('exam_name')
            exam_code=request.POST.get('exam_code')
            conducted_on=request.POST.get('conducted_on')
            file_type = certification.result_file.url.split('.')[-1].lower()
            if file_type != 'csv':
                context = {
                    'form': form,
                    'error_message': '<li>Result file must be of type CSV</li>'
                }
                return render(request, 'home/certification/certification_form.html', context)
            file_contents=request.FILES['result_file'].read().decode('UTF-8')
            headings=file_contents.split('\r\n')[0].split(',')
            if headings[0].lower()!='name' or headings[1].lower()!='email' or headings[2].lower()!='phone' or headings[3].lower()!='visionware_batch_name' or headings[4].lower()!='marks_out_of_100' or headings[5].lower()!='is_pass':
                context = {
                    'form': form,
                    'error_message': '<li>CSV Table structure is not in the format of name | email | phone | visionware_batch_name | marks_out_of_100 | is_pass </li>'
                }
                return render(request, 'home/certification/certification_form.html', context)
            certification.save()
            entry_no=0
            entries=file_contents.split('\r\n')[1:]
            for entry in entries:
                if entry!='':
                    entry_no+=1
                    line=entry.split(',')
                    cert=StudentCertification()
                    cert.certification_id=generate_cert_id(exam_code,conducted_on,str(entry_no))
                    cert.student_name=line[0]
                    cert.student_email=line[1]
                    cert.exam_name=exam_name
                    cert.visionware_batch_name=line[3]
                    cert.marks_out_of_100=line[4]
                    if line[5].lower() in('1','y','yes','true'):
                        cert.is_pass=True
                    elif line[5].lower() in('0','n','no','false'):
                        cert.is_pass=False
                    cert.save()
            messages.success(request,'Certification Details has been recorded!')
            return redirect('home:dashboard')
    else:
        form = CertificationDetailForm()
        return render(request, 'home/certification/certification_form.html',{'form':form})
    
def sat_check(request):
    if request.method=='POST':
        cert_id=request.POST.get('cert_id')
        print(cert_id)
        try:
            certification=StudentCertification.objects.get(certification_id=cert_id)
        except:
            messages.error(request,'Invalid Certificate ID')
            return redirect('home:sat_check')   
        return render(request, 'home/certification/SAT_check_display.html',{'certification':certification})     
    else:
        return render(request, 'home/certification/SAT_check_form.html')

    
