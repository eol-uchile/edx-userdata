#!/usr/bin/env python
# -- coding: utf-8 --

from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import View
from django.http import HttpResponse
from urllib import urlencode
from itertools import cycle
from uchileedxlogin.views import EdxLoginStaff

import json
import requests
import uuid
import unidecode
import logging
import sys
import unicodecsv as csv

logger = logging.getLogger(__name__)


class EdxUserDataStaff(View):

    def get(self, request):
        if self.validate_user(request):
            context = {'runs': ''}
            return render(request, 'edxuserdata/staff.html', context)
        else:
            raise Http404()

    def post(self, request):
        if self.validate_user(request):
            lista_run = request.POST.get("runs", "").split('\n')
            # limpieza de los run ingresados
            lista_run = [run.upper() for run in lista_run]
            lista_run = [run.replace("-", "") for run in lista_run]
            lista_run = [run.replace(".", "") for run in lista_run]
            lista_run = [run.strip() for run in lista_run]
            lista_run = [run for run in lista_run if run]

            context = {
                'runs': request.POST.get('runs')
            }
            # validacion de datos
            context = self.validate_data(request, lista_run, context)
            # retorna si hubo al menos un error
            if len(context) > 1:
                return render(request, 'edxuserdata/staff.html', context)
            return self.export_data(lista_run)
        else:
            raise Http404()

    def validate_user(self, request):
        access = False
        if not request.user.is_anonymous:
            if request.user.has_perm('uchileedxlogin.uchile_instructor_staff'):
                access = True
        return access

    def validate_data(self, request, lista_run, context):
        run_malos = ""
        # validacion de los run
        for run in lista_run:
            try:
                if run[0] == 'P':
                    if 5 > len(run[1:]) or len(run[1:]) > 20:
                        run_malos += run + " - "
                else:
                    if not EdxLoginStaff().validarRut(run):
                        run_malos += run + " - "

            except Exception:
                run_malos += run + " - "

        run_malos = run_malos[:-3]

        # si existe run malo
        if run_malos != "":
            context['run_malos'] = run_malos

        # si no se ingreso run
        if not lista_run:
            context['no_run'] = ''

        return context

    def get_userdata(self, run):
        user_data = {}
        try:
            username = EdxLoginStaff().get_username(run)
            user_data['username'] = username
        except Exception:
            user_data['username'] = 'No Encontrado'
        try:
            fullname = EdxLoginStaff().get_user_data(user_data['username'])
            user_data['name'] = fullname['nombreCompleto']
        except Exception:
            fullname = {'rut': ''}
            user_data['name'] = 'No Encontrado'
        try:
            email = self.get_user_email(fullname['rut'])
            if email == 'null':
                user_data['email'] = 'No Encontrado'
            else:
                user_data['email'] = email
        except Exception:
            user_data['email'] = 'No Encontrado'

        return user_data

    def get_user_email(self, rut):
        """
        Get the user email
        """
        parameters = {
            'rut': rut
        }
        result = requests.post(
            settings.EDXLOGIN_USER_EMAIL,
            data=json.dumps(parameters),
            headers={
                'content-type': 'application/json'})
        if result.status_code == 200:
            data = json.loads(result.text)
            if 'emails' in data:
                for mail in data['emails']:
                    if mail['nombreTipoEmail'] == 'PRINCIPAL':
                        if mail['email'] is not None:
                            return mail['email']
        return 'null'

    def export_data(self, lista_run):
        data = []
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'

        writer = csv.writer(
            response,
            delimiter=';',
            dialect='excel',
            encoding='utf-8')
        data.append([])
        data[0].extend(['Run', 'Username', 'Nombre', 'Email'])
        i = 1
        for run in lista_run:
            while len(run) < 10 and 'P' != run[0]:
                run = "0" + run
            data.append([])
            user_data = self.get_userdata(run)
            data[i].extend([run,
                            user_data['username'],
                            user_data['name'],
                            user_data['email']])
            i += 1
        writer.writerows(data)

        return response
