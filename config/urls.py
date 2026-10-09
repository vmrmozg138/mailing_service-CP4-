
from django.contrib import admin
from django.urls import path, include

import mailing_service

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("mailing_service.urls")),
    path("users/", include("users.urls"))

]
