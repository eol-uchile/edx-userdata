#!/usr/bin/env python
# -- coding: utf-8 --

# Python Standard Libraries
import logging
import unicodecsv as csv

# Installed packages (via pip)
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.generic.base import View

# Internal project dependencies
from uchileedxlogin.views import EdxLoginStaff

logger = logging.getLogger(__name__)


class EdxUserDataStaff(View):
    def get(self, request):
        if self.validate_user(request):
            context = {'doc_ids': ''}
            return render(request, 'edxuserdata/staff.html', context)
        else:
            raise Http404()

    def post(self, request):
        """
        Returns a CSV with the data for the requested users.
        """
        if self.validate_user(request):
            doc_id_list = request.POST.get("doc_ids", "").split('\n')
            # doc_id clean up.
            doc_id_list = [doc_id.upper() for doc_id in doc_id_list]
            doc_id_list = [doc_id.replace("-", "") for doc_id in doc_id_list]
            doc_id_list = [doc_id.replace(".", "") for doc_id in doc_id_list]
            doc_id_list = [doc_id.strip() for doc_id in doc_id_list]
            doc_id_list = [doc_id for doc_id in doc_id_list if doc_id]

            context = {
                'doc_ids': request.POST.get('doc_ids')
            }
            # Data validation.
            context = self.validate_data(doc_id_list, context)
            # Returns if there is at least 1 error.
            if len(context) > 1:
                return render(request, 'edxuserdata/staff.html', context)
            return self.export_data(doc_id_list)
        else:
            raise Http404()

    def validate_user(self, request):
        """
        Validate if user have permission.
        """
        access = False
        if not request.user.is_anonymous:
            if request.user.has_perm('uchileedxlogin.uchile_instructor_staff'):
                access = True
        return access

    def validate_data(self, doc_id_list, context):
        """
        Validate if the data is valid.
        """
        invalid_doc_ids = ""
        # doc_id validation.
        for doc_id in doc_id_list:
            try:
                if doc_id[0] == 'P':
                    if 5 > len(doc_id[1:]) or len(doc_id[1:]) > 20:
                        invalid_doc_ids += doc_id + " - "
                elif doc_id[0:2] == 'CG':
                    if len(doc_id) != 10:
                        invalid_doc_ids += doc_id + " - "
                else:
                    if not EdxLoginStaff().validarRut(doc_id):
                        invalid_doc_ids += doc_id + " - "

            except Exception:
                invalid_doc_ids += doc_id + " - "

        invalid_doc_ids = invalid_doc_ids[:-3]

        # If there is an invalid doc_id.
        if invalid_doc_ids != "":
            context['invalid_doc_ids'] = invalid_doc_ids

        # If there is no doc_id.
        if not doc_id_list:
            context['no_doc_id'] = ''

        return context

    def get_userdata(self, doc_id):
        """
        Get username, fullname and email of the 'doc_id'.
        """
        user_data = {}
        try:
            user_data = EdxLoginStaff().get_user_data_by_rut(doc_id)            
        except Exception:
            user_data = {
                'doc_id': doc_id,
                'username': 'No Encontrado',
                'nombres': 'No Encontrado',
                'apellidoPaterno': 'No Encontrado',
                'apellidoMaterno': 'No Encontrado',
                'emails': ['No Encontrado']
            }
        return user_data

    def export_data(self, doc_id_list):
        """
        Create the CSV.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'

        writer = csv.writer(
            response,
            delimiter=';',
            dialect='excel',
            encoding='utf-8')
        headers = ['Documento_id', 'Username', 'Apellido Paterno', 'Apellido Materno', 'Nombre', 'Email']
        writer.writerow(headers)
        for doc_id in doc_id_list:
            while len(doc_id) < 10 and 'P' != doc_id[0] and 'CG' != doc_id[0:2]:
                doc_id = "0" + doc_id
            user_data = self.get_userdata(doc_id)
            data = [doc_id,
                    user_data['username'],
                    user_data['apellidoPaterno'],
                    user_data['apellidoMaterno'],
                    user_data['nombres']] + user_data['emails']
            writer.writerow(data)
        return response
