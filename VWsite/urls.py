from django.conf.urls import include,url
from django.contrib import admin
from django.conf import settings               
from django.conf.urls.static import static   
  
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^',include('home.urls')),
]

handler404 = 'home.views.handler404'
handler500 = 'home.views.handler500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
