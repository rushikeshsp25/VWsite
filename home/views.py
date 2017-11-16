from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from .forms import UserForm,AdmissionForm,CourseForm
from django.contrib.auth import authenticate, login,logout
from .models import student,course
from datetime import datetime

# Create your views here.
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']

def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'home/login.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home:index')  # redirect() accepts a view name as parameter
            else:
                return render(request, 'home/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'home/login.html', {'error_message': 'Invalid login'})
    return render(request, 'home/login.html')

def index(request):
    return render(request,'home/index.html')

def aboutus(request):
    return render(request,'home/aboutus.html')

def admission(request):
    if request.method == "POST":
        form = AdmissionForm(request.POST)
        if form.is_valid():
            admission = form.save(commit=False)
            admission.date_time = timezone.now()
            admission.save()
            return redirect('home:index')
    else:
        form = AdmissionForm()
        return render(request, 'home/admission.html', {'form': form})

def students(request):
    if request.user.is_authenticated():
        courses=course.objects.all()
        return render(request, 'home/students.html',{'courses':courses})
    else:
        return render(request, 'home/login.html')

def students_result(request, type, subtype):
    if request.user.is_authenticated():
        s_objs = student()
        result_type=""
        result_desc=""
        if type=='ongoingcoursewise':
            result_type = "Ongoing Course Wise Students"
            s_objs = student.objects.filter(course=subtype, date_time__year=2017).order_by('-date_time')
            context = {
            "result_type": result_type,
            "result_desc": subtype,
            "students": s_objs,
            }

        elif type == 'coursewise':
            result_type = "Course Wise Students"
            s_objs = student.objects.filter(course=subtype).order_by('-date_time')

            context = {
            "result_type": result_type,
            "result_desc": subtype,
            "students": s_objs,
            }
        elif type=="collegewise":
            result_type = "College Wise Students"
            result_desc="College "+subtype
            s_objs=student.objects.filter(college=subtype).order_by('-date_time')

            context = {
                "result_type": result_type,
                "result_desc": result_desc,
                "students": s_objs,
            }
        return render(request, 'home/student_result.html', context)
    else:
        return render(request, 'home/login.html')

def confirm_admission(request,pk):
    if request.user.is_authenticated():
        s_obj=get_object_or_404(student,pk=pk)
        s_obj.admission=True
        s_obj.save()
        return redirect('home:student_detail', pk=pk)
    else:
        return render(request, 'home/login.html')

def student_detail(request,pk):
    s_obj = get_object_or_404(student, pk=pk)
    return render(request, 'home/student_detail.html', {'student': s_obj})

def search_student(request,search_by):
    if request.method == "POST":
        try:
            if search_by=='eno':
                eno=request.POST.get('search_eno',False)
                s_obj=get_object_or_404(student,pk=eno)
                return render(request, 'home/student_detail.html', {'student': s_obj})
            if search_by=='name':
                name=request.POST.get('search_name',False)
                s_obj=get_object_or_404(student,name=name)
                return render(request, 'home/student_detail.html', {'student': s_obj})
            if search_by=='email':
                email=request.POST.get('search_email',False)
                s_obj=get_object_or_404(student,email=email)
                return render(request, 'home/student_detail.html', {'student': s_obj})
        except:
            courses = course.objects.all()
            return render(request, 'home/students.html',{'courses':courses,'error_message': 'No Student Found!'})



def contactus(request):
    return render(request,'home/contactus.html')

def create_new_course(request):
    form = CourseForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        course=form.save(commit=False)
        course.course_icon=request.FILES['course_icon']
        file_type = course.course_icon.url.split('.')[-1]
        file_type = file_type.lower()
        if file_type not in IMAGE_FILE_TYPES:
            context = {
                    'form': form,
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
            }
            return render(request, 'home/create_new_course.html', context)
        course.save()
        return redirect('home:index')

    form=CourseForm()
    return render(request,'home/create_new_course.html',{'form':form})