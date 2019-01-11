"""lab_safety_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path, include
# from django.conf.urls import handler404, handler500
from user.views import login, dashboard, logout, page_error, page_not_found
from data.views import operation_log

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', login),
    # path('/', login),
    path('dashboard/', dashboard),
    path('login/', login),
    path('logout/', logout),
    path('operation_log/', operation_log),
    path('data/', include('data.urls')),
    path('device/', include('device.urls')),
    path('user/', include('user.urls')),
]

handler404 = 'user.views.page_not_found'
handler500 = 'user.views.page_error'
