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
from common.djangoapps.student.tests.factories import CourseEnrollmentAllowedFactory, UserFactory, CourseEnrollmentFactory
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
        with patch('common.djangoapps.student.models.cc.User.save'):
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
            
            # user with permision
            self.client_user = Client()
            user_wper = UserFactory(
                username='testuser4',
                password='12345',
                email='student4@edx.org')
            user_wper.user_permissions.add(permission)
            self.client_user.login(username='testuser4', password='12345')

            # user without permision
            self.client_no_per = Client()
            user_nper = UserFactory(
                username='testuser5',
                password='12345',
                email='student5@edx.org')
            self.client_no_per.login(username='testuser5', password='12345')

            # user with permision
            self.client_user = Client()
            user_wper = UserFactory(
                username='testuser4',
                password='12345',
                email='student4@edx.org')
            user_wper.user_permissions.add(permission)
            self.client_user.login(username='testuser4', password='12345')

            # user without permision
            self.client_no_per = Client()
            user_nper = UserFactory(
                username='testuser5',
                password='12345',
                email='student5@edx.org')
            self.client_no_per.login(username='testuser5', password='12345')

    def test_staff_get(self):
        response = self.client.get(reverse('edxuserdata-data:data'))
        request = response.request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request['PATH_INFO'], '/edxuserdata/data/')

    def test_staff_get_user_anonymous(self):
        """
            Test if the user is anonymous
        """
        self.client_anonymous = Client()
        response = self.client_anonymous.get(reverse('edxuserdata-data:data'))
        request = response.request
        self.assertEqual(response.status_code, 404)
        self.assertEqual(request['PATH_INFO'], '/edxuserdata/data/')
    
    def test_staff_get_user_without_permission(self):
        """
            Test if the user does not have permission
        """
        response = self.client_no_per.get(reverse('edxuserdata-data:data'))
        request = response.request
        self.assertEqual(response.status_code, 404)
        self.assertEqual(request['PATH_INFO'], '/edxuserdata/data/')

    def test_staff_get_user_with_permission(self):       
        """
            Test if the user have permission
        """ 
        response = self.client_user.get(reverse('edxuserdata-data:data'))
        request = response.request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request['PATH_INFO'], '/edxuserdata/data/')

    def test_staff_get_user_anonymous(self):
        """
            Test if the user is anonymous
        """
        self.client_anonymous = Client()
        response = self.client_anonymous.get(reverse('edxuserdata-data:data'))
        request = response.request
        self.assertEqual(response.status_code, 404)
        self.assertEqual(request['PATH_INFO'], '/edxuserdata/data/')

    def test_staff_get_user_without_permission(self):
        """
            Test if the user does not have permission
        """
        response = self.client_no_per.get(reverse('edxuserdata-data:data'))
        request = response.request
        self.assertEqual(response.status_code, 404)
        self.assertEqual(request['PATH_INFO'], '/edxuserdata/data/')

    def test_staff_get_user_with_permission(self):       
        """
            Test if the user have permission
        """ 
        response = self.client_user.get(reverse('edxuserdata-data:data'))
        request = response.request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request['PATH_INFO'], '/edxuserdata/data/')

    @patch('requests.get')
    def test_staff_post(self, get):
        """
            Test normal process
        """
        post_data = {
            'runs': '10-8'
        }
        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "text"])(200,
                                                json.dumps({'data':{'getRowsPersona':{'status_code':200,'persona':[
                                                            {"paterno": "TESTLASTNAME",
                                                            "materno": "TESTLASTNAME",
                                                            'pasaporte': [{'usuario':'avilio.perez'}],
                                                            "nombres": "TEST NAME",
                                                            'email': [{'email': 'test@test.test'}],
                                                            "indiv_id": "0000000108"}]}}}))]
        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Run;Username;Apellido Paterno;Apellido Materno;Nombre;Email")
        self.assertEqual(
            data[1],
            "0000000108;avilio.perez;TESTLASTNAME;TESTLASTNAME;TEST NAME;test@test.test")

    @patch('requests.get')
    def test_staff_post_fail_data(self, get):
        """
            Test if get data fail
        """
        post_data = {
            'runs': '10-8'
        }
        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "text"])(400,
                                                json.dumps({'data':{'getRowsPersona':{'status_code':200,'persona':[
                                                            {"paterno": "TESTLASTNAME",
                                                            "materno": "TESTLASTNAME",
                                                            'pasaporte': [{'usuario':'avilio.perez'}],
                                                            "nombres": "TEST NAME",
                                                            'email': [{'email': 'test@test.test'}],
                                                            "indiv_id": "0000000108"}]}}}))]

        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Run;Username;Apellido Paterno;Apellido Materno;Nombre;Email")
        self.assertEqual(
            data[1],
            "0000000108;No Encontrado;No Encontrado;No Encontrado;No Encontrado;No Encontrado")

    @patch('requests.get')
    def test_staff_post_multiple_run(self, get):
        """
            Test normal process with multiple 'r.u.n'
        """
        post_data = {
            'runs': '10-8\n9472337K'
        }
        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "text"])(200,
                                                json.dumps({'data':{'getRowsPersona':{'status_code':200,'persona':[
                                                            {"paterno": "TESTLASTNAME",
                                                            "materno": "TESTLASTNAME",
                                                            'pasaporte': [{'usuario':'avilio.perez'}],
                                                            "nombres": "TEST NAME",
                                                            'email': [{'email': 'test@test.test'}],
                                                            "indiv_id": "0000000108"}]}}})),
                    namedtuple("Request",
                                      ["status_code",
                                       "text"])(200,
                                                json.dumps({'data':{'getRowsPersona':{'status_code':200,'persona':[
                                                            {"paterno": "TESTLASTNAME2",
                                                            "materno": "TESTLASTNAME2",
                                                            'pasaporte': [{'usuario':'test.test'}],
                                                            "nombres": "TEST2 NAME2",
                                                            'email': [{'email': 'test2@test.test'}],
                                                            "indiv_id": "009472337K"}]}}}))]

        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")

        self.assertEqual(data[0], "Run;Username;Apellido Paterno;Apellido Materno;Nombre;Email")
        self.assertEqual(
            data[1],
            "0000000108;avilio.perez;TESTLASTNAME;TESTLASTNAME;TEST NAME;test@test.test")
        self.assertEqual(
            data[2],
            "009472337K;test.test;TESTLASTNAME2;TESTLASTNAME2;TEST2 NAME2;test2@test.test")

    def test_staff_post_no_run(self):
        """
            Test post if runs is empty
        """
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

    def test_staff_post_wrong_passport(self):
        post_data = {
            'runs': 'P3456'
        }
        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        self.assertTrue("id=\"run_malos\"" in response._container[0].decode())

    def test_staff_post_wrong_CG(self):
        post_data = {
            'runs': 'CG123456'
        }
        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        self.assertTrue("id=\"run_malos\"" in response._container[0].decode())

    @patch('requests.get')
    def test_staff_post_passport(self, get):
        """
            Test normal process with passport
        """
        post_data = {
            'runs': 'p123456'
        }
        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "text"])(200,
                                                json.dumps({'data':{'getRowsPersona':{'status_code':200,'persona':[
                                                            {"paterno": "TESTLASTNAME",
                                                            "materno": "TESTLASTNAME",
                                                            'pasaporte': [{'usuario':'avilio.perez'}],
                                                            "nombres": "TEST NAME",
                                                            'email': [{'email': 'test@test.test'}],
                                                            "indiv_id": "P123456"}]}}}))]
        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Run;Username;Apellido Paterno;Apellido Materno;Nombre;Email")
        self.assertEqual(
            data[1],
            "P123456;avilio.perez;TESTLASTNAME;TESTLASTNAME;TEST NAME;test@test.test")

    @patch('requests.get')
    def test_staff_post_CG(self, get):
        """
            Test normal process with CG
        """
        post_data = {
            'runs': 'CG00123456'
        }
        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "text"])(200,
                                                json.dumps({'data':{'getRowsPersona':{'status_code':200,'persona':[
                                                            {"paterno": "TESTLASTNAME",
                                                            "materno": "TESTLASTNAME",
                                                            'pasaporte': [{'usuario':'avilio.perez'}],
                                                            "nombres": "TEST NAME",
                                                            'email': [{'email': 'test@test.test'}],
                                                            "indiv_id": "CG00123456"}]}}}))]
        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Run;Username;Apellido Paterno;Apellido Materno;Nombre;Email")
        self.assertEqual(
            data[1],
            "CG00123456;avilio.perez;TESTLASTNAME;TESTLASTNAME;TEST NAME;test@test.test")
