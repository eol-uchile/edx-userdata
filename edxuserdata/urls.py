from django.conf.urls import url
from .views import *


urlpatterns = [
    url('data/', EdxUserDataStaff.as_view(), name='data'),
]
