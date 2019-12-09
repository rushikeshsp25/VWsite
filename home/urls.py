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
    path('study-material/', views.display_all_study_material, name='display_all_study_material'),
    path('study-material/get/<slug:course_slug>/', views.display_study_material, name='display_study_material'),
    path('student/admission/classroom/batch/<int:course_batch_pk>/', views.student_admission_batch, name='student_admission_batch'),
    path('student/pay-fees/<int:pk>/', views.pay_fees, name='pay_fees'),
    path('student/confirm-admission/<int:pk>/', views.confirm_admission,name='confirm_admission'),
    path('student/feedback/init/<int:feedback_batch_id>/',views.feedback_init,name='feedback_init'),
    path('student/feedback/proceed/<int:feedback_batch_id>/',views.feedback_proceed,name='feedback_proceed'),
    path('su/course/new/', views.create_new_course, name='create_new_course'),
    path('su/course/edit/<int:pk>/', views.edit_course, name='edit_course'),
    path('su/batch/new/', views.create_new_batch, name='create_new_batch'),
    path('su/study-material/new/', views.create_new_study_material, name='create_new_study_material'),
    path('su/study-material/not-working-links/get/', views.notWorkingLinks, name='notWorkingLinks'),
    path('su/dashboard/',views.dashboard,name='dashboard'),
    path('su/feedback-batch/new/',views.create_new_feedback,name='create_new_feedback'),
    path('su/feedback/feedback_question/',views.feedback_questions,name='feedback_questions'),
    path('su/feedback/feedback_question/delete/<int:pk>/',views.delete_feedback_question,name='delete_feedback_question'),
    path('su/feedback/feedback_question/edit/<int:pk>/',views.edit_feedback_question,name='edit_feedback_question'),
    path('su/feedback/feedback_question/new/',views.feedback_questions_new,name='feedback_questions_new'),
    path('su/feedback-analysis/batches/all/',views.display_feedback_enabled_batches,name='display_feedback_enabled_batches'),
    path('su/feedback-analysis/batches/<int:feedback_batch_id>/',views.feedback_batch_response,name='feedback_batch_response'),
    path('su/student/',views.students,name='students'),
    path('su/student/detail/<int:pk>',views.student_detail,name='student_detail'),
    path('su/student/search/<str:search_by>/',views.search_student,name='search_student'),
    path('su/student/result/batchwise/<int:pk>/',views.batchwise_students,name='batchwise_students'),
    path('su/student/result/collegewise/<int:pk>/',views.collegewise_students,name='collegewise_students'),
    path('su/student/result/all/',views.students_all,name='students_all'),
    path('services/<str:name>/',views.services,name='services'),

]

