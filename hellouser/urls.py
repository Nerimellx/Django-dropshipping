from django.conf.urls import url

from . import views

app_name = 'hellouser'
urlpatterns = [
    url(r'^$', views.ESearchView.as_view(), name='index'),
]