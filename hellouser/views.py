# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.shortcuts import render


def group(request):
    title = 'Profile group'
    return render(request,'registration/profile_group.html', {title: 'title'})


def dashboard(request):
    title = 'Profile dashboard'
    return render(request,'registration/dashboard.html', {title: 'title'})
# Create your views here.
