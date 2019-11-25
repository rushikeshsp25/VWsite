from django.conf.urls import url
from . import views
from django.urls import path

app_name='home'
urlpatterns = [
    path('', views.index,name='index'),
    path('login/', views.login_user, name='login_user'),
    path('signup/', views.signup_user, name='signup_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('course/', views.display_all_courses, name='display_all_courses'),
    path('course/details/<slug:course_slug>/', views.course_details, name='course_details'),
    path('permissionerror/', views.permissionerror, name='permissionerror'),
    path('hire-with-us/',views.hire_with_us,name='hire_with_us'),
    path('student/admission/offline/batch/<int:course_batch_pk>/', views.student_admission_batch, name='student_admission_batch'),
    path('student/admission/online/course/<int:course_pk>/', views.student_admission_online_course, name='student_admission_online_course'),
    path('su/course/new/', views.create_new_course, name='create_new_course'),
    path('su/course/edit/<int:pk>/', views.edit_course, name='edit_course'),
    path('su/study-material/', views.display_all_study_material, name='display_all_study_material'),
    path('su/study-material/get/<slug:course_slug>/', views.display_study_material, name='display_study_material'),
    path('su/study-material/new/', views.create_new_study_material, name='create_new_study_material'),
    path('su/study-material/not-working-links/get/', views.notWorkingLinks, name='notWorkingLinks'),
    path('su/dashboard/',views.dashboard,name='dashboard'),
    path('su/feedback-analysis/batches/',views.display_feedback_enabled_batches,name='feedback_analysis_batches'),
    path('su/feedback-analysis/questions/<int:batch_id>/',views.display_feedback_questions,name='feedback_analysis_questions'),
    path('su/feedback-analysis/response/<int:batch_id>/<int:question_id>/',views.display_feedback_response,name='feedback_analysis_response'),
    path('su/admit_student/',views.admit_student,name='admit_student'),
    path('su/student/',views.students,name='students'),
    path('su/student/detail/<int:pk>',views.student_detail,name='student_detail'),
    path('su/student/search/<str:search_by>/',views.search_student,name='search_student'),
    path('su/student/result/batchwise/<int:pk>/',views.batchwise_students,name='batchwise_students'),
    path('su/student/result/collegewise/<int:pk>/',views.collegewise_students,name='collegewise_students'),
    path('su/student/result/all/',views.students_all,name='students_all'),

]

