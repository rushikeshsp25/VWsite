from django.conf.urls import url
from . import views
from django.urls import path

app_name='home'
urlpatterns = [
    path('', views.index,name='index'),
    path('login/', views.login_user, name='login_user'),
    path('signup/', views.signup_user, name='signup_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('course/', views.display_all_courses, name='display_all_courses'),
    path('course/new/', views.create_new_course, name='create_new_course'),
    path('course/edit/<int:pk>/', views.edit_course, name='edit_course'),
    path('student/admission/', views.student_admission, name='student_admission'),
    path('study-material/', views.display_all_study_material, name='display_all_study_material'),
    path('study-material/get/<slug:course_slug>/', views.display_study_material, name='display_study_material'),
    path('study-material/new/', views.create_new_study_material, name='create_new_study_material'),
    path('study-material/not-working-links/get/', views.notWorkingLinks, name='notWorkingLinks'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('feedback-analysis/batches/',views.display_feedback_enabled_batches,name='feedback_analysis_batches'),
    path('feedback-analysis/questions/<int:batch_id>/',views.display_feedback_questions,name='feedback_analysis_questions'),
    path('feedback-analysis/response/<int:batch_id>/<int:question_id>/',views.display_feedback_response,name='feedback_analysis_response'),
]

