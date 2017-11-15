from django.shortcuts import render,redirect
from django.utils import timezone
from .forms import UserForm,AdmissionForm
from django.contrib.auth import authenticate, login,logout
from .models import student

# Create your views here.

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
        return render(request, 'home/students.html')
    else:
        return render(request, 'home/login.html')

def students_result(request, type, subtype):
    if request.user.is_authenticated():
        s_objs = student()
        result_type=""
        result_desc=""
        if type == 'coursewise':
            result_type = "Course Wise Students"
            if subtype == 'c':
                result_desc = "Course - C"
                s_objs = student.objects.filter(course='C').order_by('-date_time')
            elif subtype == 'cpp':
                result_desc = "Course - C++"
                s_objs = student.objects.filter(course='C++').order_by('-date_time')
            elif subtype == 'python':
                result_desc = "Course - Python"
                s_objs = student.objects.filter(course='Python').order_by('-date_time')
            elif subtype == 'django':
                result_desc = "Course - Django"
                s_objs = student.objects.filter(course='Django').order_by('-date_time')
            context = {
            "result_type": result_type,
            "result_desc": result_desc,
            "students": s_objs,
        }
        return render(request, 'home/student_result.html', context)
    else:
        return render(request, 'home/login.html')

def contactus(request):
    return render(request,'home/contactus.html')
