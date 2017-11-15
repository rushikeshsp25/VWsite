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
    url(r'^students_result/(?P<type>[a-z]+)/(?P<subtype>[a-z]+)/$', views.students_result, name='students_result'),
]