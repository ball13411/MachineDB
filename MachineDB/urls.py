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
from Machine_Management import views, views_ajax
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # General Path
    # path('admin/', admin.site.urls),

    # Sign In
    path('', views.signin, name='signin'),
    path('sign-in/department/', views.signIn_department, name='signIn_department'),
    path('resetpassword/', views.reset_password, name='resetpassword'),

    # User Management
    path('usermanage/user-management', views.usermanage, name='usermanage'),
    path('usermanage/role-management', views.rolemanage, name='rolemanage'),
    path('usermanage/screen-management', views.screenmanage, name='screenmanage'),
    path('usermanage/role-screen-management', views.role_screen, name='role_screen_manage'),
    path('usermanage/menu-management', views.menumanage, name='menumanage'),
    path('usermanage/department-management', views.department_manage, name='department_manage'),
    path('usermanage/user-department', views.user_department, name='user_department'),

    # Organization Management
    path('organizemanage/organization-management', views.organizemanage, name='organization'),
    path('organizemanage/production-line-management', views.production_line, name='productionline'),
    path('organizemanage/location-management', views.location, name='location'),
    path('organizemanage/organize-production-line', views.org_productline, name='org_prodline'),
    path('organizemanage/product-management', views.productmanage, name='productmanage'),

    # Machine Management
    path('machinemanage/machine-management', views.machine_manage, name='machine_manage'),
    path('machinemanage/machine-type/', views.machine_type, name='machine_type'),
    path('machinemanage/machine-subtype/', views.machine_subtype, name='machine_subtype'),
    path('machinemanage/capacity/', views.machine_capacity, name='machine_capacity'),
    path('machinemanage/machine-spare-part/', views.machine_and_spare_part, name='machine_and_spare_part'),

    # Spare part Management
    path('sparepartmanage/spare-part/', views.spare_part_manage, name='spare_part_manage'),
    path('sparepartmanage/subtype/', views.spare_part_subtype, name='spare_part_subtype'),
    path('sparepartmanage/type/', views.spare_part_type, name='spare_part_type'),
    path('sparepartmanage/group/', views.spare_part_group, name='spare_part_group'),
    path('sparepartmanage/spare-pare-machine/', views.spare_part_and_machine, name='spare_part_and_machine'),

    # Repair Inform
    path('repair/inform', views.repair_notice, name='repair_notice'),
    path('repair/inspect', views.repair_inspect, name='repair_inspect'),
    path('repair/approve', views.repair_approve, name='repair_approve'),

    # Preventive Data
    path('preventive/maintenance-receive', views.maintenance_receive, name='maintenance_receive'),
    path('preventive/maintenance-inspect', views.maintenance_inspect, name='maintenance_inspect'),
    path('preventive/maintenance-data', views.maintenance_data, name='maintenance_data'),
    path('preventive/maintenance-assign', views.maintenance_assign, name='maintenance_assign'),
    path('preventive/maintenance-report', views.maintenance_report, name='maintenance_report'),
    path('preventive/maintenance-machine', views.machine_hour_update, name='machine_hour_update'),

    # Home
    path('home/', views.home, name='home'),
    path('home/line-<int:line>', views.home_machine, name='machine_data_line'),
    path('home/line-<int:line>/machine-<int:machine>', views.machine_details, name='machine_data_machine'),

    # AJAX Script
    path('check_username', views_ajax.check_username, name='check_username'),                                        # check user exists
    path('check_email', views_ajax.check_email, name='check_email'),                                                 # check email exists
    path('ajax/load-building/', views_ajax.load_building, name='ajax_load_building'),                                # select building of site (Dropdown)
    path('ajax/load-floor/', views_ajax.load_floor, name='ajax_load_floor'),                                         # select floor of building (Dropdown)
    path('check_role', views_ajax.check_role, name='check_role'),                                                    # check role exists
    # path('ajax/load-machine-type/', views.load_machine_type, name='ajax_machine_type'),                         # select mch_type of line (Dropdown)
    path('ajax/load-machine-subtype/', views_ajax.load_machine_subtype, name='ajax_machine_subtype'),                # select sub_type of mch_type (Dropdown)
    path('check_serial', views_ajax.check_serial, name='check_serial'),                                              # machine_manage/machine/
    path('check_machine_type_code', views_ajax.check_machine_type_code, name='check_machine_type_code'),             # machine_manage/machine_type/
    path('check_machine_subtype_code', views_ajax.check_machine_subtype_code, name='check_machine_subtype_code'),    # machine_manage/machine_subtype/
    path('check_screen_id', views_ajax.check_screen_id, name='check_screen_id'),
    path('check_menu_id', views_ajax.check_menu_id, name='check_menu_id'),
    path('check_org_code', views_ajax.check_org_code, name='check_org_code'),
    path('ajax/load-spare-part-subtype/', views_ajax.load_spare_part_subtype, name='ajax_spare_part_subtype'),
    path('ajax/load-spare-part-subtype2/', views_ajax.load_spare_part_subtype2, name='ajax_spare_part_subtype2'),
    path('check_spare_part_type_code', views_ajax.check_spare_part_type_code, name='check_spare_part_type_code'),
    path('check_spare_part_subtype_code', views_ajax.check_spare_part_subtype_code, name='check_spare_part_subtype_code'),
    # path('check_spare_part_code', views_ajax.check_spare_part_code, name='check_spare_part_code'),
    path('ajax/load_spare_part/', views_ajax.load_spare_part, name='load_spare_part'),
    path('ajax/load_machine/', views_ajax.load_machine_from_line, name='ajax_load_machine'),
    path('ajax/load_product/', views_ajax.load_product, name='ajax_load_product'),
    path('check_machine_product', views_ajax.check_machine_product, name='check_machine_product'),
    path('check_spare_part_group_code/', views_ajax.check_spare_part_group_code, name='check_spare_part_group_code'),
    path('ajax_dropdown_sp_type/', views_ajax.ajax_dropdown_sp_type, name='ajax_dropdown_sp_type'),
    path('ajax_dropdown_sp_subtype/', views_ajax.ajax_dropdown_sp_subtype, name='ajax_dropdown_sp_subtype'),
    path('ajax_dropdown_sp/', views_ajax.ajax_dropdown_sp, name='ajax_dropdown_sp'),
    path('ajax/load_selected_lines/', views_ajax.load_selected_lines, name='ajax_selected_lines'),
    path('ajax/load_role_screen/', views_ajax.load_role_screen, name='load_role_screen'),
    path('ajax/load_machine', views_ajax.load_machine, name='load_machine'),
    path('ajax/load_machine_sparepart', views_ajax.load_machine_sparepart, name='load_machine_sparepart'),
    path('check_department_code', views_ajax.check_department_code, name='check_dep_code'),
    path('ajax/load_username/', views_ajax.load_username, name='load_username'),
    path('ajax/load_userInOrg', views_ajax.load_userInOrg, name='load_userInOrg'),
    path('ajax/load_department_name', views_ajax.load_department_name, name='load_department_name'),
    path('ajax/load_round_username', views_ajax.load_round_username, name='load_round_username'),


]

handler404 = views.error404

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
