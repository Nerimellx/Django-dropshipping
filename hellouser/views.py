# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from django.shortcuts import render
from .forms import SearchFilterForm
from django.db.models import Q
from django.db import connection


class GroupView(LoginRequiredMixin, View):
    title = 'Profile group'
    template_name = 'registration/profile_group.html'

    context = {
        'title': title
    }

    def get(self, request):
        return render(request, self.template_name, self.context)


class ProfileView(LoginRequiredMixin, View):
    template_name = 'registration/profile.html'

    def get(self, request):
        return render(request, self.template_name)


class WaybillView(LoginRequiredMixin, View):
    title = 'waybill'
    template_name = 'Documents.html'

    form = SearchFilterForm()

    waybill = WayBillDoc.objects.all()

    def get(self, request):

        paginator = Paginator(self.waybill, 7)

        page = request.GET.get('page')
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)

        content = {
            'title': self.title,
            'contacts': contacts,
            'form': self.form
        }

        return render(request, self.template_name, content)


class DashboardView(LoginRequiredMixin, View):
    title = 'Profile dashboard'
    template_name = 'registration/dashboard.html'

    context = {
        'title': title
    }

    def get(self, request):
        return render(request, self.template_name, self.context)


class ESearchView(LoginRequiredMixin, View):
    template_name = 'search.html'

    title = 'Search'

    def get(self, request, *args, **kwargs):
        number = request.GET.get('number')
        status = request.GET.get('status')
        editable = request.GET.get('editable')
        created = request.GET.get('created')
        updated = request.GET.get('updated')
        description = request.GET.get('description')

        form = SearchFilterForm()

        question = u"&number={0}&status={1}&editable={2}&created={3}&uploaded={4}&description={5}".format(number,
                                                                                                          status,
                                                                                                          editable,
                                                                                                          created,
                                                                                                          updated,
                                                                                                          description, )

        waybill = WayBillDoc.objects.filter(Q(status=status), Q(block=editable),
                                            Q(created_by=created), Q(number__startswith=number),
                                            Q(desc__startswith=description))

        paginator = Paginator(waybill, 7)

        page = request.GET.get('page')
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)

        content = {
            'title': self.title,
            'contacts': contacts,
            'question': question,
            'form': form
        }
        return render(request, self.template_name, content)
