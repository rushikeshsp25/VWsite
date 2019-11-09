from django.conf.urls import url
from . import views
from django.urls import path



app_name='home'
urlpatterns = [
    path('', views.index,name='index'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('course/new/', views.create_new_course, name='create_new_course'),
    path('course/edit/<int:pk>/', views.edit_course, name='edit_course'),
    path('course/all/', views.display_all_courses, name='display_all_courses'),
    path('student/admission/', views.student_admission, name='student_admission'),
    path('study-course/get/<int:pk>/', views.convert_pdf_to_html, name='convert_pdf_to_html'),
    path('study-course/new/', views.create_new_study_course, name='create_new_study_course'),
]

