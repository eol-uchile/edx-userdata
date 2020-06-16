#!/bin/dash
pip install -e git+https://github.com/eol-uchile/uchileedxlogin@68b30d34df945360dbb630692cc5f31c610d6242#egg=uchileedxlogin
pip install -e /openedx/requirements/edx-userdata

cd /openedx/requirements/edx-userdata/edxuserdata
cp /openedx/edx-platform/setup.cfg .
mkdir test_root
cd test_root/
ln -s /openedx/staticfiles .

cd /openedx/requirements/edx-userdata/edxuserdata

DJANGO_SETTINGS_MODULE=lms.envs.test EDXAPP_TEST_MONGO_HOST=mongodb pytest tests.py