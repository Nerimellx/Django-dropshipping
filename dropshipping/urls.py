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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import reverse_lazy
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls import include
from django.conf.urls import url
from django.views.generic.base import TemplateView
from registration.backends.default.views import RegistrationView
from hellouser.forms import UpdatedRegistrationForm
from hellouser.views import group
from hellouser.views import dashboard


class RegistrationViewUniqueEmail(RegistrationView):
    form_class = UpdatedRegistrationForm


urlpatterns = [
    url(r'^admin/',
        admin.site.urls,
        name='admin'),

    url(r'^accounts/profile/group/',
        group,
        name='group'),

    url(r'^accounts/profile/dashboard/',
        dashboard,
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
        TemplateView.as_view(template_name='registration/profile.html'),
        name='profile'),

    url(r'^register/$', RegistrationViewUniqueEmail.as_view(),               name='registration_register'),

    url(r'', include('registration.backends.default.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
