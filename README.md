# Eol User Data

![https://github.com/eol-uchile/edx-userdata/actions](https://github.com/eol-uchile/edx-userdata/workflows/Python%20application/badge.svg)

Return CSV with user data from api

# Install App

    docker-compose exec lms pip install -e /openedx/requirements/edx-userdata

## TESTS
**Prepare tests:**

    > cd .github/
    > docker-compose run lms /openedx/requirements/edx-userdata/.github/test.sh

## Notes

- Need Uchileedxlogin