#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python Standard Libraries
from collections import namedtuple

# Installed packages (via pip)
from django.test import TestCase, Client
from django.urls import reverse
from mock import patch

# Edx dependencies
from common.djangoapps.student.tests.factories import UserFactory

class TestEdxUserDataStaff(TestCase):
    def setUp(self):
        with patch('common.djangoapps.student.models.cc.User.save'):
            # staff user
            self.client = Client()
            user = UserFactory(
                username='testuser3',
                password='12345',
                email='student2@edx.org',
                is_staff=True)
            self.client.login(username='testuser3', password='12345')
            
            # user with permission
            self.client_user = Client()
            user_wper = UserFactory(
                username='testuser4',
                password='12345',
                email='student4@edx.org')
            self.client_user.login(username='testuser4', password='12345')

            # user without permission
            self.client_no_per = Client()
            user_nper = UserFactory(
                username='testuser5',
                password='12345',
                email='student5@edx.org')
            self.client_no_per.login(username='testuser5', password='12345')

    @patch('edxuserdata.views.check_permission_instructor_staff')
    def test_staff_get(self, mock_permission_check):
        mock_permission_check.return_value = True
        response = self.client.get(reverse('edxuserdata-data:data'))
        request = response.request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request['PATH_INFO'], '/edxuserdata/data/')

    @patch('edxuserdata.views.check_permission_instructor_staff')
    def test_staff_get_user_anonymous(self, mock_permission_check):
        """
            Test if the user is anonymous
        """
        mock_permission_check.return_value = False
        self.client_anonymous = Client()
        response = self.client_anonymous.get(reverse('edxuserdata-data:data'))
        request = response.request
        self.assertEqual(response.status_code, 404)
        self.assertEqual(request['PATH_INFO'], '/edxuserdata/data/')
    
    @patch('edxuserdata.views.check_permission_instructor_staff')
    def test_staff_get_user_without_permission(self, mock_permission_check):
        """
            Test if the user does not have permission
        """
        mock_permission_check.return_value = False
        response = self.client_no_per.get(reverse('edxuserdata-data:data'))
        request = response.request
        self.assertEqual(response.status_code, 404)
        self.assertEqual(request['PATH_INFO'], '/edxuserdata/data/')

    @patch('edxuserdata.views.check_permission_instructor_staff')
    def test_staff_get_user_with_permission(self, mock_permission_check):       
        """
            Test if the user have permission
        """ 
        mock_permission_check.return_value = True
        response = self.client_user.get(reverse('edxuserdata-data:data'))
        request = response.request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request['PATH_INFO'], '/edxuserdata/data/')

    @patch('edxuserdata.views.check_permission_instructor_staff')
    @patch('requests.get')
    def test_staff_post(self, get, mock_permission_check):
        """
            Test normal process
        """
        mock_permission_check.return_value = True
        post_data = {
            'doc_ids': '10-8'
        }
        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "json"])(200,
                                                lambda:{'data':{'getRowsPersona':{'status_code':200,'persona':[
                                                            {"paterno": "TESTLASTNAME",
                                                            "materno": "TESTLASTNAME",
                                                            'pasaporte': [{'usuario':'avilio.perez'}],
                                                            "nombres": "TEST NAME",
                                                            'email': [{'email': 'test@test.test'}],
                                                            "indiv_id": "0000000108"}]}}})]
        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Documento_id;Username;Apellido Paterno;Apellido Materno;Nombre;Email")
        self.assertEqual(
            data[1],
            "0000000108;avilio.perez;TESTLASTNAME;TESTLASTNAME;TEST NAME;test@test.test")

    @patch('edxuserdata.views.check_permission_instructor_staff')
    @patch('requests.get')
    def test_staff_post_fail_data(self, get, mock_permission_check):
        """
            Test if get data fail
        """
        mock_permission_check.return_value = True
        post_data = {
            'doc_ids': '10-8'
        }
        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "json"])(400,
                                                lambda:{'data':{'getRowsPersona':{'status_code':200,'persona':[
                                                            {"paterno": "TESTLASTNAME",
                                                            "materno": "TESTLASTNAME",
                                                            'pasaporte': [{'usuario':'avilio.perez'}],
                                                            "nombres": "TEST NAME",
                                                            'email': [{'email': 'test@test.test'}],
                                                            "indiv_id": "0000000108"}]}}})]

        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Documento_id;Username;Apellido Paterno;Apellido Materno;Nombre;Email")
        self.assertEqual(
            data[1],
            "0000000108;No Encontrado;No Encontrado;No Encontrado;No Encontrado;No Encontrado")

    @patch('edxuserdata.views.check_permission_instructor_staff')
    @patch('requests.get')
    def test_staff_post_multiple_doc_id(self, get, mock_permission_check):
        """
            Test normal process with multiple 'r.u.n'
        """
        mock_permission_check.return_value = True
        post_data = {
            'doc_ids': '10-8\n9472337K'
        }
        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "json"])(200,
                                               lambda:{'data':{'getRowsPersona':{'status_code':200,'persona':[
                                                            {"paterno": "TESTLASTNAME",
                                                            "materno": "TESTLASTNAME",
                                                            'pasaporte': [{'usuario':'avilio.perez'}],
                                                            "nombres": "TEST NAME",
                                                            'email': [{'email': 'test@test.test'}],
                                                            "indiv_id": "0000000108"}]}}}),
                    namedtuple("Request",
                                      ["status_code",
                                       "json"])(200,
                                               lambda:{'data':{'getRowsPersona':{'status_code':200,'persona':[
                                                            {"paterno": "TESTLASTNAME2",
                                                            "materno": "TESTLASTNAME2",
                                                            'pasaporte': [{'usuario':'test.test'}],
                                                            "nombres": "TEST2 NAME2",
                                                            'email': [{'email': 'test2@test.test'}],
                                                            "indiv_id": "009472337K"}]}}})]

        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")

        self.assertEqual(data[0], "Documento_id;Username;Apellido Paterno;Apellido Materno;Nombre;Email")
        self.assertEqual(
            data[1],
            "0000000108;avilio.perez;TESTLASTNAME;TESTLASTNAME;TEST NAME;test@test.test")
        self.assertEqual(
            data[2],
            "009472337K;test.test;TESTLASTNAME2;TESTLASTNAME2;TEST2 NAME2;test2@test.test")

    @patch('edxuserdata.views.check_permission_instructor_staff')
    def test_staff_post_no_doc_id(self, mock_permission_check):
        """
            Test post if doc_ids is empty
        """
        mock_permission_check.return_value = True
        post_data = {
            'doc_ids': ''
        }
        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        self.assertTrue("id=\"no_doc_id\"" in response._container[0].decode())

    @patch('edxuserdata.views.check_permission_instructor_staff')
    def test_staff_post_wrong_doc_id(self, mock_permission_check):
        mock_permission_check.return_value = True
        post_data = {
            'doc_ids': '123456'
        }
        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        self.assertTrue("id=\"invalid_doc_ids\"" in response._container[0].decode())

    @patch('edxuserdata.views.check_permission_instructor_staff')
    def test_staff_post_wrong_passport(self, mock_permission_check):
        mock_permission_check.return_value = True
        post_data = {
            'doc_ids': 'P3456'
        }
        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        self.assertTrue("id=\"invalid_doc_ids\"" in response._container[0].decode())

    @patch('edxuserdata.views.check_permission_instructor_staff')
    def test_staff_post_wrong_CG(self, mock_permission_check):
        mock_permission_check.return_value = True
        post_data = {
            'doc_ids': 'CG123456'
        }
        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        self.assertTrue("id=\"invalid_doc_ids\"" in response._container[0].decode())

    @patch('edxuserdata.views.check_permission_instructor_staff')
    @patch('requests.get')
    def test_staff_post_passport(self, get, mock_permission_check):
        """
            Test normal process with passport
        """
        mock_permission_check.return_value = True
        post_data = {
            'doc_ids': 'p123456'
        }
        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "json"])(200,
                                                lambda:{'data':{'getRowsPersona':{'status_code':200,'persona':[
                                                            {"paterno": "TESTLASTNAME",
                                                            "materno": "TESTLASTNAME",
                                                            'pasaporte': [{'usuario':'avilio.perez'}],
                                                            "nombres": "TEST NAME",
                                                            'email': [{'email': 'test@test.test'}],
                                                            "indiv_id": "P123456"}]}}})]
        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Documento_id;Username;Apellido Paterno;Apellido Materno;Nombre;Email")
        self.assertEqual(
            data[1],
            "P123456;avilio.perez;TESTLASTNAME;TESTLASTNAME;TEST NAME;test@test.test")

    @patch('edxuserdata.views.check_permission_instructor_staff')
    @patch('requests.get')
    def test_staff_post_CG(self, get, mock_permission_check):
        """
            Test normal process with CG
        """
        mock_permission_check.return_value = True
        post_data = {
            'doc_ids': 'CG00123456'
        }
        get.side_effect = [namedtuple("Request",
                                      ["status_code",
                                       "json"])(200,
                                                lambda:{'data':{'getRowsPersona':{'status_code':200,'persona':[
                                                            {"paterno": "TESTLASTNAME",
                                                            "materno": "TESTLASTNAME",
                                                            'pasaporte': [{'usuario':'avilio.perez'}],
                                                            "nombres": "TEST NAME",
                                                            'email': [{'email': 'test@test.test'}],
                                                            "indiv_id": "CG00123456"}]}}})]
        response = self.client.post(
            reverse('edxuserdata-data:data'), post_data)
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Documento_id;Username;Apellido Paterno;Apellido Materno;Nombre;Email")
        self.assertEqual(
            data[1],
            "CG00123456;avilio.perez;TESTLASTNAME;TESTLASTNAME;TEST NAME;test@test.test")
