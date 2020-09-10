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

    # General Path
    path('admin/', admin.site.urls),
    path('', views.signin, name='signin'),
    path('resetpassword/', views.resetpassword,name='resetpassword'),

    # User Management
    path('usermanage/user', views.usermanage,name='usermanage'),
    path('usermanage/role/', views.rolemanage,name='rolemanage'),
    path('usermanage/screen/', views.screenmanage,name='screenmanage'),
    path('usermanage/rolescreen/', views.role_screen,name='role_screen_manage'),
    path('usermanage/menu/', views.menumanage, name='menumanage'),

    # Organization Management
    path('organizemanage/organization', views.organizemanage,name='organization'),
    path('organizemanage/line', views.production_line,name='productionline'),
    path('organizemanage/location', views.location,name='location'),
    path('organziemanage/orgline', views.org_productline,name='org_prodline'),
    path('organziemanage/productmanage',views.productmanage,name='productmanage'),

    # Machine Management
    path('machinemanage/machine/',views.machine_manage,name='machine_manage'),
    path('machinemanage/machinetype/',views.machine_type,name='machine_type'),
    path('machinemanage/machinesubtype/',views.machine_subtype,name='machine_subtype'),

    # Spare part Management
    path('sparepartmanage/sparepart/',views.spare_part_manage, name='spare_part_manage'),
    path('sparepartmanage/subtype/', views.spare_part_subtype, name='spare_part_subtype'),
    path('sparepartmanage/type/', views.spare_part_type, name='spare_part_type'),

    # Home
    path('home/', views.home, name='home'),
    path('machine/data/', views.machine_data, name='machinedata'),
    path('machine/data/line-<int:line>', views.machine_data_machine, name='machine_data_line'),
    path('machine/data/line-<int:line>/machine-<int:machine>', views.machine_details, name='machine_data_machine'),
    path('machine/register/', views.machine_register, name='machineregister'),
    path('machine/search', views.machine_search, name='machinesearch'),
    path('machine/update', views.machine_update, name='machineupdate'),
    path('machine/update/edit', views.machine_edit, name='machineedit'),
    path('machine/searching/', views.machine_searching, name='machine_searching'),

    # AJAX Script
    path('check_username', views.check_username, name='check_username'),                                        # check user exists
    path('check_email', views.check_email, name='check_email'),                                                 # check email exists
    path('ajax/load-building/', views.load_building, name='ajax_load_building'),                                # select building of site (Dropdown)
    path('ajax/load-floor/', views.load_floor, name='ajax_load_floor'),                                         # select floor of building (Dropdown)
    path('check_role', views.check_role, name='check_role'),                                                    # check role exists
    path('ajax/load-machine-type/', views.load_machine_type, name='ajax_machine_type'),                         # select mch_type of line (Dropdown)
    path('ajax/load-machine-subtype/', views.load_machine_subtype, name='ajax_machine_subtype'),                # select sub_type of mch_type (Dropdown)
    path('check_serial', views.check_serial, name='check_serial'),                                              # machinemanage/machine/
    path('check_machine_type_code', views.check_machine_type_code, name='check_machine_type_code'),             # machinemanage/machinetype/
    path('check_machine_subtype_code', views.check_machine_subtype_code, name='check_machine_subtype_code'),    # machinemanage/machinesubtype/
    path('check_screen_id', views.check_screen_id, name='check_screen_id'),
    path('check_menu_id', views.check_menu_id, name='check_menu_id'),
    path('check_org_code', views.check_org_code, name='check_org_code'),
    path('ajax/load-spare-part-subtype/', views.load_spare_part_subtype, name='ajax_spare_part_subtype'),
    path('check_spare_part_type_code', views.check_spare_part_type_code, name='check_spare_part_type_code'),
    path('check_spare_part_subtype_code', views.check_spare_part_subtype_code, name='check_spare_part_subtype_code'),
    path('check_spare_part_code', views.check_spare_part_code, name='check_spare_part_code'),

    # Test File
    path('productionline/create', views.production_line_create, name='linecreate'),
    path('test/', views.test)

]
