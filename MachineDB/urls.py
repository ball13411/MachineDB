"""MachineDB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from Machine_Management import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.signin,name='signin'),
    path('usermanage/', views.usermanage,name='usermanage'),
    path('resetpassword/', views.resetpassword,name='resetpassword'),
    path('adminmanage/', views.adminmanage,name='adminmanage'),
    path('rolemanage/', views.rolemanage,name='rolemanage'),
    path('screenmanage/', views.screenmanage,name='screenmanage'),
    path('rolescreen/',views.role_screen,name='role_screen_manage'),
    path('machinemanage/',views.machinemanage,name='machinemanage'),
    path('machinemanage/register/',views.machine_register,name='machineregister'),
    path('machinemanage/data/',views.machine_data,name='machinedata'),
    path('test/',views.test)

]
