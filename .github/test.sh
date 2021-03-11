#!/bin/dash
pip install -e git+https://github.com/eol-uchile/uchileedxlogin@a11973e7625e1a3e66103ccad79c26103381988a#egg=uchileedxlogin
pip install -e /openedx/requirements/edx-userdata

cd /openedx/requirements/edx-userdata
cp /openedx/edx-platform/setup.cfg .
mkdir test_root
cd test_root/
ln -s /openedx/staticfiles .

cd /openedx/requirements/edx-userdata

DJANGO_SETTINGS_MODULE=lms.envs.test EDXAPP_TEST_MONGO_HOST=mongodb pytest edxuserdata/tests.py
