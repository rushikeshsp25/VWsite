from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from .forms import UserForm,AdmissionForm,CourseForm,ReviewForm
from django.contrib.auth import authenticate, login,logout
from .models import student,course,student_contact
from datetime import datetime

# Create your views here.
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']

def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    all_courses = course.objects.all()
    context = {
        "form": form,
        'all_courses':all_courses,
    }
    return render(request, 'home/login.html', context)


def login_user(request):
    all_courses = course.objects.all()
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home:index')  # redirect() accepts a view name as parameter
            else:
                return render(request, 'home/login.html', {'error_message': 'Your account has been disabled','all_courses':
                                                           all_courses,})
        else:

            return render(request, 'home/login.html', {'error_message': 'Invalid login',
                                                        'all_courses': all_courses, })
    return render(request, 'home/login.html',{'all_courses': all_courses,})

def index(request):
    brand_new_courses=course.objects.order_by('-date_time')[:4]
    all_courses=course.objects.all()
    return render(request,'home/index.html',{'brand_new_courses':brand_new_courses,
                                             'all_courses':all_courses,})

def aboutus(request):
    all_courses = course.objects.all()
    return render(request,'home/aboutus.html',{'all_courses': all_courses,})

def admission(request):
    all_courses = course.objects.all()
    if request.method == "POST":
        form = AdmissionForm(request.POST)
        if form.is_valid():
            admission = form.save(commit=False)
            admission.date_time = timezone.now()
            admission.save()
            return redirect('home:success', 'admission_success')
    else:
        form = AdmissionForm()
        return render(request, 'home/admission.html', {'form': form,
                                                       'all_courses': all_courses,
                                                       })

def students(request):
    all_courses = course.objects.all()
    if request.user.is_authenticated():
        courses=course.objects.all()

        return render(request, 'home/students.html',{'courses':courses,
                                                     'all_courses': all_courses,})
    else:
        return redirect('home:login_user')

def students_all(request):
    all_courses = course.objects.all()
    if request.user.is_authenticated:
        s_objs = student.objects.all().order_by('-date_time')
        context = {
            "result_type": "All students ",
            "result_desc": "",
            "students": s_objs,
            'all_courses': all_courses,
        }
        return render(request, 'home/student_result.html', context)
    else:
        return redirect('home:login_user')

def students_result(request, type, subtype):
    all_courses = course.objects.all()
    if request.user.is_authenticated():
        today=datetime.today()
        if type=='ongoingcoursewise':
            result_type = "Ongoing Course Wise Students"
            s_objs = student.objects.filter(course=subtype, date_time__year=today.year).order_by('-date_time')
            context = {
            "result_type": result_type,
            "result_desc": subtype,
            "students": s_objs,
            'all_courses': all_courses,
            }

        elif type == 'coursewise':
            result_type = "Course Wise Students"
            s_objs = student.objects.filter(course=subtype).order_by('-date_time')

            context = {
            "result_type": result_type,
            "result_desc": subtype,
            "students": s_objs,
                'all_courses': all_courses,
            }
        elif type=="collegewise":
            result_type = "College Wise Students"
            result_desc="College "+subtype
            s_objs=student.objects.filter(college=subtype).order_by('-date_time')

            context = {
                "result_type": result_type,
                "result_desc": result_desc,
                "students": s_objs,
                'all_courses': all_courses,
            }
        return render(request, 'home/student_result.html', context)
    else:
        return redirect('home:login_user')

def student_detail(request,pk):
    all_courses = course.objects.all()
    if request.user.is_authenticated:
        s_obj = get_object_or_404(student, pk=pk)
        return render(request, 'home/student_detail.html', {'student': s_obj,
                                                            'all_courses': all_courses,})
    else:
        return redirect('home:login_user')

def search_student(request,search_by):
    all_courses = course.objects.all()
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                if search_by=='eno':
                    eno=request.POST.get('search_eno',False)
                    s_obj=get_object_or_404(student,pk=eno)
                    return render(request, 'home/student_detail.html', {'student': s_obj,'all_courses': all_courses,})
                if search_by=='name':
                    name=request.POST.get('search_name',False)
                    s_obj=get_object_or_404(student,name=name)
                    return render(request, 'home/student_detail.html', {'student': s_obj,'all_courses': all_courses,})
                if search_by=='email':
                    email=request.POST.get('search_email',False)
                    s_obj=get_object_or_404(student,email=email)
                    return render(request, 'home/student_detail.html', {'student': s_obj,'all_courses': all_courses,})
            except:
                courses = course.objects.all()
                return render(request, 'home/students.html',{'courses':courses,'error_message': 'No Student Found!','all_courses': all_courses,})
    else:
        return redirect('home:login_user')


def contactus(request):
    all_courses = course.objects.all()
    return render(request,'home/contactus.html',{'all_courses': all_courses,})

def create_new_course(request):
    all_courses = course.objects.all()
    if request.user.is_authenticated:
        form = CourseForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            new_course=form.save(commit=False)
            new_course.course_icon=request.FILES['course_icon']
            new_course.syllabus = request.FILES['syllabus']
            file_type = new_course.course_icon.url.split('.')[-1]
            file_type2 = new_course.syllabus.url.split('.')[-1]
            file_type = file_type.lower()
            file_type2 = file_type2.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                        'form': form,
                        'error_message': 'Image file must be PNG, JPG, or JPEG',
                    'all_courses': all_courses,
                }
                return render(request, 'home/create_new_course.html', context)
            if file_type2 !='pdf':
                context = {
                    'form': form,
                    'error_message': 'Syllabus file must be PDF',
                    'all_courses': all_courses,
                }
                return render(request, 'home/create_new_course.html', context)
            new_course.save()
            return redirect('home:success', 'course_success')
    else:
        return redirect(request, 'home:login_user')

    form=CourseForm()
    return render(request,'home/create_new_course.html',{'form':form,'all_courses': all_courses,})

def course_details(request,course_name):
    all_courses = course.objects.all()
    course_details=get_object_or_404(course,course_name=course_name)
    return render(request,'home/course_detail.html',{'course':course_details,'all_courses': all_courses,})

def user_options(request):
    all_courses = course.objects.all()
    if request.user.is_authenticated:
        return render(request, 'home/user_options.html',{'all_courses': all_courses,})
    else:
        return redirect('home:login_user')

def review(request):
    all_courses = course.objects.all()
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.save()
            return redirect('home:index')
    else:
        form = ReviewForm()
        return render(request, 'home/post_review.html', {'form': form,
                                                       'all_courses': all_courses,
                                                       })

def confirm_admission(request,pk):
    all_courses = course.objects.all()
    if request.user.is_authenticated():
        s_obj=get_object_or_404(student,pk=pk)
        s_obj.admission=True
        s_obj.date_time=datetime.now()
        s_obj.save()
        return redirect('home:student_detail', pk=pk)
    else:
        return redirect('home:login_user')


def pay_fees(request,pk):
    all_courses = course.objects.all()
    if request.method == "POST":
        fees_paying=request.POST.get('feesip',0)
        student_obj = get_object_or_404(student, pk=pk)
        fees_remaining = int(student_obj.course.fees) - int(student_obj.fees_paid)
        if int(fees_paying)>int(fees_remaining):
            return render(request, 'home/pay_fees.html', {'student': student_obj,
                                                          'fees_remaining': fees_remaining,
                                                          'all_courses': all_courses,
                                                          'error_message':'error',
                                                          })
        student_obj.fees_paid=int(student_obj.fees_paid)+int(fees_paying)
        student_obj.save()
        if int(student_obj.fees_paid)>=int(student_obj.course.fees)/2:
            return redirect('home:confirm_admission',student_obj.pk)
        return redirect('home:student_detail',student_obj.pk)
    else:
        student_obj = get_object_or_404(student, pk=pk)
        fees_remaining = int(student_obj.course.fees) - int(student_obj.fees_paid)
        return render(request,'home/pay_fees.html',{'student':student_obj,
                                                    'fees_remaining':fees_remaining,
                                                    'all_courses': all_courses,
                                                    })


def contact_student(request):
    if request.method == "POST":
        name=request.POST.get('name',False)
        email=request.POST.get('email',False)
        phone = request.POST.get('phone', False)
        message=request.POST.get('message',False)
        student=student_contact()
        student.name=name
        student.email=email
        student.phone=phone
        student.message=message
        student.save()
        return redirect('home:success','contact_success')

def contacted_students(request):
    all_courses = course.objects.all()
    s_objs=student_contact.objects.all()
    s_objs.order_by('-date_time')
    context = {
        "result_type": "List of contacted students",
        "result_desc": "",
        "students": s_objs,
        'all_courses': all_courses,
    }
    return render(request, 'home/contact_student_result.html', context)

def success(request,success_type):
    message1="Your response is recorded by Visionware , Our Team will contact you soon ! Thank You:))"
    message2="Course is Succesfully Created :))"
    message3 = "Your admission request is recorded by Visionware , Pay 50% fess @VisionWare office to confirm your Admission ! Thank You:))"
    if success_type=='course_success':
        return render(request, 'home/success.html',{'success_message':message2,})
    elif success_type=='contact_success':
        return render(request, 'home/success.html',{'success_message':message1,})
    elif success_type=='admission_success':
        return render(request, 'home/success.html',{'success_message':message3,})