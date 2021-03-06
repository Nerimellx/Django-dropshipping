
"""dropshipping URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import reverse_lazy
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls import include
from django.conf.urls import url
from registration.backends.default.views import RegistrationView
from hellouser.forms import UpdatedRegistrationForm
from hellouser.views import GroupView
from hellouser.views import DashboardView
from hellouser.views import ProfileView
from hellouser.views import WaybillView


def i18n_javascript(request):
    return admin.site.i18n_javascript(request)


class RegistrationViewUniqueEmail(RegistrationView):
    form_class = UpdatedRegistrationForm


urlpatterns = [

    url(r'^admin/jsi18n', i18n_javascript),

    url(r'^accounts/profile/waybill/search/', include('hellouser.urls')),

    url(r'^accounts/profile/waybill/',
        WaybillView.as_view(),
        name='waybill'),

    url(r'^ckeditor/', include('ckeditor_uploader.urls')),

    url(r'^admin/',
        admin.site.urls,
        name='admin'),

    url(r'^accounts/profile/group/',
        GroupView.as_view(),
        name='group'),

    url(r'^accounts/profile/dashboard/',
        DashboardView.as_view(),
        name='dashboard'),

    url(r'^$',
        auth_views.LoginView.as_view(
            success_url=reverse_lazy('profile'),
            template_name='registration/login.html'),
        name='login'),


    url(r'^password-restore/$',
        auth_views.PasswordResetView.as_view(
            success_url=reverse_lazy('auth_password_reset_done'),
            html_email_template_name='registration/password_reset_email.html'
        ), name='auth_password_reset'),

    url(r'^accounts/profile/',
        ProfileView.as_view(),
        name='profile'),

    url(r'^register/$', RegistrationViewUniqueEmail.as_view(),               name='registration_register'),

    url(r'', include('registration.backends.default.urls')),
]
