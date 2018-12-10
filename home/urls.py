from django.conf.urls import url
from . import views

from django.conf import settings                #imp to add for dealing with image
from django.conf.urls.static import static      #imp to add for dealing with image

app_name='home'
urlpatterns = [
    url(r'^$', views.index,name='index'),
    url(r'^aboutus/', views.aboutus,name='aboutus'),
    url(r'^lbwithcpp/', views.lbwithcpp,name='lbwithcpp'),
    url(r'^admission/', views.admission,name='admission'),
    url(r'^contactus/', views.contactus,name='contactus'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^create_new_course/$', views.create_new_course, name='create_new_course'),
    url(r'^students/$', views.students, name='students'),
    url(r'^students/all/$', views.students_all, name='students_all'),
    url(r'^user_options/$', views.user_options, name='user_options'),
    url(r'^students_result/(?P<type>[a-zA-Z]+)/(?P<subtype>[^~,]+)/$', views.students_result, name='students_result'),
    url(r'^confirm_admission/(?P<pk>\d+)/$', views.confirm_admission,name='confirm_admission'),
    url(r'^student_detail/(?P<pk>\d+)/$', views.student_detail,name='student_detail'),
    url(r'^search_student/(?P<search_by>[a-z]+)/$', views.search_student,name='search_student'),
    url(r'^course_details/(?P<course_name>[^~,]+)/$', views.course_details, name='course_details'),
    url(r'^review/$', views.review, name='review'),
    url(r'^pay_fees/(?P<pk>\d+)/$', views.pay_fees, name='pay_fees'),
    url(r'^contact_visionware/$', views.contact_student, name='contact_student'),
    url(r'^contacted_students/$', views.contacted_students, name='contacted_students'),
    url(r'^success/(?P<success_type>[^~,]+)/$', views.success, name='success'),
    url(r'^satcheck/', views.satcheck, name='satcheck'),
]
if settings.Debug:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)