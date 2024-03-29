#!/bin/dash
pip install -e git+https://github.com/eol-uchile/uchileedxlogin@d6bc551f2516aafd723b742dd9cd3dee103a17b5#egg=uchileedxlogin
pip install -e /openedx/requirements/edx-userdata

cd /openedx/requirements/edx-userdata
cp /openedx/edx-platform/setup.cfg .
mkdir test_root
cd test_root/
ln -s /openedx/staticfiles .

cd /openedx/requirements/edx-userdata

pip install pytest-cov genbadge[coverage]
sed -i '/--json-report/c addopts = --nomigrations --reuse-db --durations=20 --json-report --json-report-omit keywords streams collectors log traceback tests --json-report-file=none --cov=edxuserdata/ --cov-report term-missing --cov-report xml:reports/coverage/coverage.xml --cov-fail-under 70' setup.cfg

DJANGO_SETTINGS_MODULE=lms.envs.test EDXAPP_TEST_MONGO_HOST=mongodb pytest edxuserdata/tests.py

rm -rf test_root

genbadge coverage