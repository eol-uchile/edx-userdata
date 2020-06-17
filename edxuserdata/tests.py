#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mock import patch, Mock, MagicMock
from collections import namedtuple
from django.urls import reverse
from django.test import TestCase, Client
from django.test import Client
from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from urllib.parse import parse_qs
from opaque_keys.edx.locator import CourseLocator
from student.tests.factories import CourseEnrollmentAllowedFactory, UserFactory, CourseEnrollmentFactory
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from uchileedxlogin.models import EdxLoginUser
import re
import json
import urllib.parse
# Create your tests here.


class TestEdxUserDataStaff(TestCase):

    def setUp(self):
        with patch('student.models.cc.User.save'):
            content_type = ContentType.objects.get_for_model(EdxLoginUser)
            permission = Permission.objects.get(
                codename='uchile_instructor_staff',
                content_type=content_type,
            )
            # staff user
            self.client = Client()
            user = UserFactory(
                username='testuser3',
                password='12345',
                email='student2@edx.org',
                is_staff=True)
            user.user_permissions.add(permission)
            self.client.login(username='testuser3', password='12345')

    def test_staff_get(self):
        response = self.client.get(reverse('edxuserdata-data:data'))
        request = response.request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request['PATH_INFO'], '/edxuserdata/data/')

    @patch('requests.post')
    @patch('requests.get')
    def test_staff_post(self, get, post):
        post_data = {
            'runs': '10-8'
        }
        data = {"cuentascorp": [{"cuentaCorp": "avilio.perez@ug.uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "ug.uchile.cl"},
                                {"cuentaCorp": "avilio.perez@uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "uchile.cl"},
                                {"cuentaCorp": "avilio.perez@u.uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "u.uchile.cl"},
                                {"cuentaCorp": "avilio.perez",
                                 "tipoCuenta": "CUENTA PASAPORTE",
                                 "organismoDominio": "Universidad de Chile"}]}

        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "text"])(200,
                                                json.dumps({"apellidoPaterno": "TESTLASTNAME",
                                                            "apellidoMaterno": "TESTLASTNAME",
                                                            "nombres": "TEST NAME",
                                                            "nombreCompleto": "TEST NAME TESTLASTNAME TESTLASTNAME",
                                                            "rut": "0000000108"}))]
        post.side_effect = [namedtuple("Request",
                                       ["status_code",
                                        "text"])(200,
                                                 json.dumps(data)),
                            namedtuple("Request",
                                       ["status_code",
                                        "text"])(200,
                                                 json.dumps({"emails": [{"rut": "0000000108",
                                                                         "email": "test@test.test",
                                                                         "codigoTipoEmail": "1",
                                                                         "nombreTipoEmail": "PRINCIPAL"}]}))]

        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Run;Username;Nombre;Email")
        self.assertEqual(
            data[1],
            "0000000108;avilio.perez;TEST NAME TESTLASTNAME TESTLASTNAME;test@test.test")

    @patch('requests.post')
    @patch('requests.get')
    def test_staff_post_fail_username(self, get, post):
        post_data = {
            'runs': '10-8'
        }
        data = {"cuentascorp": [{"cuentaCorp": "avilio.perez@ug.uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "ug.uchile.cl"},
                                {"cuentaCorp": "avilio.perez@uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "uchile.cl"},
                                {"cuentaCorp": "avilio.perez@u.uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "u.uchile.cl"},
                                {"cuentaCorp": "avilio.perez",
                                 "tipoCuenta": "CUENTA PASAPORTE",
                                 "organismoDominio": "Universidad de Chile"}]}

        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "text"])(404,
                                                json.dumps({"apellidoPaterno": "TESTLASTNAME",
                                                            "apellidoMaterno": "TESTLASTNAME",
                                                            "nombres": "TEST NAME",
                                                            "nombreCompleto": "TEST NAME TESTLASTNAME TESTLASTNAME",
                                                            "rut": "0000000108"}))]
        post.side_effect = [namedtuple("Request",
                                       ["status_code",
                                        "text"])(404,
                                                 json.dumps(data)),
                            namedtuple("Request",
                                       ["status_code",
                                        "text"])(404,
                                                 json.dumps({"emails": [{"rut": "0000000108",
                                                                         "email": "test@test.test",
                                                                         "codigoTipoEmail": "1",
                                                                         "nombreTipoEmail": "PRINCIPAL"}]}))]

        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Run;Username;Nombre;Email")
        self.assertEqual(
            data[1],
            "0000000108;No Encontrado;No Encontrado;No Encontrado")

    @patch('requests.post')
    @patch('requests.get')
    def test_staff_post_fail_fullname(self, get, post):
        post_data = {
            'runs': '10-8'
        }
        data = {"cuentascorp": [{"cuentaCorp": "avilio.perez@ug.uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "ug.uchile.cl"},
                                {"cuentaCorp": "avilio.perez@uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "uchile.cl"},
                                {"cuentaCorp": "avilio.perez@u.uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "u.uchile.cl"},
                                {"cuentaCorp": "avilio.perez",
                                 "tipoCuenta": "CUENTA PASAPORTE",
                                 "organismoDominio": "Universidad de Chile"}]}

        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "text"])(404,
                                                json.dumps({"apellidoPaterno": "TESTLASTNAME",
                                                            "apellidoMaterno": "TESTLASTNAME",
                                                            "nombres": "TEST NAME",
                                                            "nombreCompleto": "TEST NAME TESTLASTNAME TESTLASTNAME",
                                                            "rut": "0000000108"}))]
        post.side_effect = [namedtuple("Request",
                                       ["status_code",
                                        "text"])(200,
                                                 json.dumps(data)),
                            namedtuple("Request",
                                       ["status_code",
                                        "text"])(404,
                                                 json.dumps({"emails": [{"rut": "0000000108",
                                                                         "email": "test@test.test",
                                                                         "codigoTipoEmail": "1",
                                                                         "nombreTipoEmail": "PRINCIPAL"}]}))]

        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Run;Username;Nombre;Email")
        self.assertEqual(
            data[1],
            "0000000108;avilio.perez;No Encontrado;No Encontrado")

    @patch('requests.post')
    @patch('requests.get')
    def test_staff_post_fail_email(self, get, post):
        post_data = {
            'runs': '10-8'
        }
        data = {"cuentascorp": [{"cuentaCorp": "avilio.perez@ug.uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "ug.uchile.cl"},
                                {"cuentaCorp": "avilio.perez@uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "uchile.cl"},
                                {"cuentaCorp": "avilio.perez@u.uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "u.uchile.cl"},
                                {"cuentaCorp": "avilio.perez",
                                 "tipoCuenta": "CUENTA PASAPORTE",
                                 "organismoDominio": "Universidad de Chile"}]}

        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "text"])(200,
                                                json.dumps({"apellidoPaterno": "TESTLASTNAME",
                                                            "apellidoMaterno": "TESTLASTNAME",
                                                            "nombres": "TEST NAME",
                                                            "nombreCompleto": "TEST NAME TESTLASTNAME TESTLASTNAME",
                                                            "rut": "0000000108"}))]
        post.side_effect = [namedtuple("Request",
                                       ["status_code",
                                        "text"])(200,
                                                 json.dumps(data)),
                            namedtuple("Request",
                                       ["status_code",
                                        "text"])(404,
                                                 json.dumps({"emails": [{"rut": "0000000108",
                                                                         "email": "test@test.test",
                                                                         "codigoTipoEmail": "1",
                                                                         "nombreTipoEmail": "PRINCIPAL"}]}))]

        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Run;Username;Nombre;Email")
        self.assertEqual(
            data[1],
            "0000000108;avilio.perez;TEST NAME TESTLASTNAME TESTLASTNAME;No Encontrado")

    @patch('requests.post')
    @patch('requests.get')
    def test_staff_post_null_email(self, get, post):
        post_data = {
            'runs': '10-8'
        }
        data = {"cuentascorp": [{"cuentaCorp": "avilio.perez@ug.uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "ug.uchile.cl"},
                                {"cuentaCorp": "avilio.perez@uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "uchile.cl"},
                                {"cuentaCorp": "avilio.perez@u.uchile.cl",
                                 "tipoCuenta": "EMAIL",
                                 "organismoDominio": "u.uchile.cl"},
                                {"cuentaCorp": "avilio.perez",
                                 "tipoCuenta": "CUENTA PASAPORTE",
                                 "organismoDominio": "Universidad de Chile"}]}

        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "text"])(200,
                                                json.dumps({"apellidoPaterno": "TESTLASTNAME",
                                                            "apellidoMaterno": "TESTLASTNAME",
                                                            "nombres": "TEST NAME",
                                                            "nombreCompleto": "TEST NAME TESTLASTNAME TESTLASTNAME",
                                                            "rut": "0000000108"}))]
        post.side_effect = [namedtuple("Request",
                                       ["status_code",
                                        "text"])(200,
                                                 json.dumps(data)),
                            namedtuple("Request",
                                       ["status_code",
                                        "text"])(200,
                                                 json.dumps({"emails": [{}]}))]

        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Run;Username;Nombre;Email")
        self.assertEqual(
            data[1],
            "0000000108;avilio.perez;TEST NAME TESTLASTNAME TESTLASTNAME;No Encontrado")

    @patch('requests.post')
    @patch('requests.get')
    def test_staff_post_multiple_run(self, get, post):
        post_data = {
            'runs': '10-8\n9472337K'
        }
        user_data_1 = {"cuentascorp": [{"cuentaCorp": "avilio.perez@ug.uchile.cl",
                                        "tipoCuenta": "EMAIL",
                                        "organismoDominio": "ug.uchile.cl"},
                                       {"cuentaCorp": "avilio.perez@uchile.cl",
                                        "tipoCuenta": "EMAIL",
                                        "organismoDominio": "uchile.cl"},
                                       {"cuentaCorp": "avilio.perez@u.uchile.cl",
                                        "tipoCuenta": "EMAIL",
                                        "organismoDominio": "u.uchile.cl"},
                                       {"cuentaCorp": "avilio.perez",
                                        "tipoCuenta": "CUENTA PASAPORTE",
                                        "organismoDominio": "Universidad de Chile"}]}

        user_data_2 = {
            "cuentascorp": [
                {
                    "cuentaCorp": "test.test",
                    "tipoCuenta": "CUENTA PASAPORTE",
                    "organismoDominio": "Universidad de Chile"}]}

        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "text"])(200,
                                                json.dumps({"apellidoPaterno": "TESTLASTNAME",
                                                            "apellidoMaterno": "TESTLASTNAME",
                                                            "nombres": "TEST NAME",
                                                            "nombreCompleto": "TEST NAME TESTLASTNAME TESTLASTNAME",
                                                            "rut": "0000000108"})),
                           namedtuple("Request",
                                      ["status_code",
                                       "text"])(200,
                                                json.dumps({"apellidoPaterno": "TESTLASTNAME",
                                                            "apellidoMaterno": "TESTLASTNAME",
                                                            "nombres": "TEST NAME",
                                                            "nombreCompleto": "TEST2 NAME2 TESTLASTNAME2 TESTLASTNAME2",
                                                            "rut": "009472337K"}))]
        post.side_effect = [namedtuple("Request",
                                       ["status_code",
                                        "text"])(200,
                                                 json.dumps(user_data_1)),
                            namedtuple("Request",
                                       ["status_code",
                                        "text"])(200,
                                                 json.dumps({"emails": [{"rut": "0000000108",
                                                                         "email": "test@test.test",
                                                                         "codigoTipoEmail": "1",
                                                                         "nombreTipoEmail": "PRINCIPAL"}]})),
                            namedtuple("Request",
                                       ["status_code",
                                        "text"])(200,
                                                 json.dumps(user_data_2)),
                            namedtuple("Request",
                                       ["status_code",
                                        "text"])(200,
                                                 json.dumps({"emails": [{"rut": "009472337K",
                                                                         "email": "test2@test.test",
                                                                         "codigoTipoEmail": "1",
                                                                         "nombreTipoEmail": "PRINCIPAL"}]}))]

        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Run;Username;Nombre;Email")
        self.assertEqual(
            data[1],
            "0000000108;avilio.perez;TEST NAME TESTLASTNAME TESTLASTNAME;test@test.test")
        self.assertEqual(
            data[2],
            "009472337K;test.test;TEST2 NAME2 TESTLASTNAME2 TESTLASTNAME2;test2@test.test")

    def test_staff_post_no_run(self):
        post_data = {
            'runs': ''
        }
        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        self.assertTrue("id=\"no_run\"" in response._container[0].decode())

    def test_staff_post_wrong_run(self):
        post_data = {
            'runs': '123456'
        }
        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        self.assertTrue("id=\"run_malos\"" in response._container[0].decode())
