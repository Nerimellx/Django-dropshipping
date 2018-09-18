# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from django.shortcuts import render
from .forms import SearchFilterForm
from django.db.models import Q
import datetime


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
    template_name = 'Documents.html'

    title = 'Search'

    def get(self, request, *args, **kwargs):
        number = request.GET.get('number', None)
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        status = request.GET.get('status')
        editable = request.GET.get('editable')
        created = request.GET.get('created')
        updated = request.GET.get('updated')
        description = request.GET.get('description')

        form = SearchFilterForm()

        if not from_date:
            from_date = datetime.date(1900, 1, 1)

        if not to_date:
            to_date = datetime.date(2600, 1, 1)

        query_list = [Q(updated__range=(from_date, to_date))]

        if number:
            query_list.append(Q(number__contains=number))

        if status:
            query_list.append(Q(status__startswith=status))

        if editable:
            query_list.append(Q(block__startswith=editable))

        if created:
            query_list.append(Q(created_by__startswith=created))

        if updated:
            query_list.append(Q(source__startswith=updated))

        if description:
            query_list.append(Q(desc__startswith=description))

        question = u"&number={0}&from_date={1}&to_date={2}&status={3}" \
                   u"&editable={4}&created={5}&updated={6}&description={7}".format(
            number,
            from_date,
            to_date,
            status,
            editable,
            created,
            updated,
            description, )

        waybill = WayBillDoc.objects.filter(*query_list)

        paginator = Paginator(waybill, 2)

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
