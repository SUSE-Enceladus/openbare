
from django.conf.urls import include, url
from django.contrib import admin
from library import views

urlpatterns = [
    url('', include('django.contrib.auth.urls', namespace='auth')),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^library/', include('library.urls', namespace='library')),
    url(r'^$', views.index, name='home'),
]
