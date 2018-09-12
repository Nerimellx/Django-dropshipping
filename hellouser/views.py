# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

class GroupView(LoginRequiredMixin, View):
    title = 'Profile group'
    template_name = 'registration/profile_group.html'

    context = {
        'title' : title
    }

    def get(self, request):
        return render(request,self.template_name, self.context)


class ProfileView(LoginRequiredMixin, View):
    template_name = 'registration/profile.html'

    def get(self, request):
        return render(request,self.template_name)

class DashboardView(LoginRequiredMixin, View):
    title = 'Profile dashboard'
    template_name = 'registration/dashboard.html'

    context = {
        'title' : title
    }

    def get(self, request):
        return render(request,self.template_name, self.context)