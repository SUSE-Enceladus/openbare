from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^resource/(?P<item_subtype>\w+)/checkout$', views.checkout, name='checkout'),
    url(r'^instance/(?P<primary_key>\d+)/renew$', views.renew, name='renew'),
    url(r'^instance/(?P<primary_key>\d+)/checkin$', views.checkin, name='checkin'),
]

