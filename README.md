# Eol User Data

![Coverage Status](/coverage-badge.svg)

![https://github.com/eol-uchile/edx-userdata/actions](https://github.com/eol-uchile/edx-userdata/workflows/Python%20application/badge.svg) 

Return CSV with user data from api

# Install App

    docker-compose exec lms pip install -e /openedx/requirements/edx-userdata

## TESTS
**Prepare tests:**

- Install **act** following the instructions in [https://nektosact.com/installation/index.html](https://nektosact.com/installation/index.html)

**Run tests:**
- In a terminal at the root of the project
    ```
    act -W .github/workflows/pythonapp.yml
    ```

## Notes

- Need Uchileedxlogin
