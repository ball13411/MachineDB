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
    path('usermanage/user', views.usermanage,name='usermanage'),
    path('resetpassword/', views.resetpassword,name='resetpassword'),
    path('adminmanage/', views.adminmanage,name='adminmanage'),
    path('usermanage/role/', views.rolemanage,name='rolemanage'),
    path('usermanage/screen/', views.screenmanage,name='screenmanage'),
    path('usermanage/rolescreen/',views.role_screen,name='role_screen_manage'),
    path('home/',views.home,name='home'),
    path('machine/register/',views.machine_register,name='machineregister'),
    path('machine/data/',views.machine_data,name='machinedata'),
    path('usermanage/menu/',views.menumanage,name='menumanage'),
    path('organizemanage/organization',views.organizemanage,name='organization'),
    path('machine/search',views.machine_search,name='machinesearch'),
    path('machine/update',views.machine_update,name='machineupdate'),
    path('machine/update/edit',views.machine_edit,name='machineedit'),
    path('check_username', views.check_username, name='check_username'),
    path('check_email', views.check_email, name='check_email'),
    path('productionline/create',views.production_line_create,name='linecreate'),
    path('ajax/load-building/', views.load_building, name='ajax_load_building'),
    path('ajax/load-floor/', views.load_floor, name='ajax_load_floor'),
    path('organizemanage/line',views.production_line,name='productionline'),
    path('organizemanage/location',views.location,name='location'),
    path('organziemanage/orgline',views.org_productline,name='org_prodline'),
    path('organziemanage/productmanage',views.productmanage,name='productmanage'),
    path('machinemanage/machine',views.machine_manage,name='machine_manage'),
    path('check_role', views.check_role, name='check_role'),

    # path('machinemanage/sparepart/',views.sparepart,name='sparepart'),
    path('test/',views.test)

]
