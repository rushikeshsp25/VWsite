from django.conf.urls import url
from . import views

app_name='home'
urlpatterns = [
    url(r'^$', views.index,name='index'),
    url(r'^aboutus/', views.aboutus,name='aboutus'),
    url(r'^admission/', views.admission,name='admission'),
    url(r'^contactus/', views.contactus,name='contactus'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^students/$', views.students, name='students'),
    url(r'^students_result/(?P<type>[a-z]+)/(?P<subtype>[a-zA-Z]+)/$', views.students_result, name='students_result'),
    url(r'^confirm_admission/(?P<pk>\d+)/$', views.confirm_admission,name='confirm_admission'),
    url(r'^student_detail/(?P<pk>\d+)/$', views.student_detail,name='student_detail'),
    url(r'^search_student/(?P<search_by>[a-z]+)/$', views.search_student,name='search_student'),
]