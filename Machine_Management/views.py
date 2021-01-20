from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import *
import Machine_Management
import datetime
import django
from .forms import *
from .filters import MachineFilter
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.http import HttpResponse
from django.core import serializers
import xlwt
import ast
from docx import Document
from docx.shared import Inches
from collections import Counter
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Create your views here.

# GLOBAL var
User_login, UserRole, List_user_Screen, dict_menu_level, User_org_machine_line, List_user_Screen = None, None, [], {}, None, None  # User Login for use all pages


def signin(request):
    # Functions for Sign In to webapp
    # Templates/signin.html
    global User_login, UserRole
    User_login, UserRole = None, None
    if request.method == "POST":
        # Form Sign In
        if 'signin' in request.POST:
            username = request.POST['inputUser']  # Get var('username') from HTML
            password = request.POST['inputPassword']  # Get var('password') from HTML
            try:                                                                                    # Try connect username and passwd on Model
                user = User.objects.get(username=username, password=password)
                now = datetime.datetime.now()  # Call Datetime now
                datenow = datetime.date.today()                                                                         # Call Date now
                user.last_login_date = now                                                                              # Update last_login to now
                user.save()                                                                                             # Save Update
                if user.start_date > datenow:                                                                           # Check StartDate and DateNow
                    messages.error(request, f'ชื่อผู้ใช้นี้ยังไม่สามารถเข้าสู่ระบบได้ สามารถเข้าได้ในวันที่ {user.start_date}')
                    return redirect('/')
                elif datenow > user.expired_date:                                                   # Check Expired Date if expired link to resetpassword
                    messages.info(request, 'รหัสผ่านหมดอายุแล้ว กรุณาทำการ Reset Password')
                    return redirect('/')
                if user is not None:                                                                # Check login User   # Set user login
                    User_login = user
                    UserRole = str(User_login.role)
                    return redirect('/home')
            except Machine_Management.models.User.DoesNotExist:  # Message Wrong username or password
                messages.error(request, "username หรือ password ไม่ถูกต้อง")

    return render(request, 'signin.html')


def usermanage(request):
    # Functions for User Management
    # Templates/usermanage.html
    global User_login, List_user_Screen  # Call User sign in
    if not Role_Screen.objects.filter(role=UserRole, screen_id='usermanage').exists():
        return redirect('/')
    if request.method == "POST":
        # Form Edituser (Settings of user)
        if 'Edituser' in request.POST:
            username = request.POST['set_username']  # Get var('username') from HTML
            update_role = request.POST['select_role']  # Get var('role') from HTML
            update_org = request.POST['select_org']
            now = datetime.datetime.now()  # Call Datetime now
            user = User.objects.get(username=username)  # Query user
            user.user_active = request.POST.get('set_user_status', False)
            user.update_date = now  # Update UpdateDate to now
            user.update_by = str(User_login.username)  # Update UserUpdate of UserSelect
            org = Organization.objects.get(org_id=update_org)
            user.org = org
            role = Role.objects.get(role_id=update_role)  # Get RoleID of UserSelect
            user.role = role  # Update Role of UserSelect
            user.save()  # Save all Update
            messages.success(request, "แก้ไขและบันทึกรายการสำเร็จ")
        # Form Add User (Add New User)
        elif 'Adduser' in request.POST:
            username = request.POST['add_username']  # Get var('username') form HTML
            fname = request.POST['add_fname']
            lname = request.POST['add_lname']
            email = request.POST['add_email']
            startdate = request.POST['add_startdate']
            create_role = request.POST['select_role']
            passwd = request.POST['add_password']
            conpasswd = request.POST['add_cfpassword']
            add_org = request.POST['add_select_org']
            now = datetime.datetime.now()
            org = Organization.objects.get(org_id=add_org)
            role = Role.objects.get(role_id=create_role)
            if passwd == conpasswd:  # Check password and confirm password
                if User.objects.filter(username=username).exists():  # Query username is exists in model(DB)
                    messages.error(request, "มีผู้ใช้ชื่อ Username นี้แล้ว")  # Show Message Username is exists
                elif User.objects.filter(email=email).exists():  # Query email is exists in model(DB)
                    messages.error(request, "มีผู้ใช้ Email นี้แล้ว")  # Show Message Email is exists
                else:
                    user = User.objects.create(
                        username=username,
                        email=email,
                        firstname=fname.capitalize(),
                        lastname=lname.capitalize(),
                        password=passwd,
                        create_by=str(User_login.username),
                        create_date=now,
                        expired_date=now - datetime.timedelta(1),
                        expired_day=90,
                        start_date=startdate,
                        update_by=None,
                        update_date=None,
                        last_login_date=None,
                        role=role,
                        org=org,
                        user_active=True
                    )
                    user.save()                                                                 # Save User
                    messages.success(request, "สร้างรายการสำเร็จ")
                    # return redirect('/usermanage')
            else:
                messages.error(request, "รหัสผ่านไม่ตรงกัน กรุณาตรวจสอบใหม่")  # Show Message Password != ConPassword

        # Button Sign Out
        elif 'signout' in request.POST:
            User_login = None  # Set User_login is None

        # Form DeleteUser (icon delete)
        elif 'deleteuser' in request.POST:
            username = request.POST['deleteuser']                               # get var('username') from HTML
            user = User.objects.get(username=username)                          # Query Username
            user.delete()                                                       # Delete User from Model(DB)
            messages.success(request, "ลบรายการสำเร็จ")

        return redirect('/usermanage/user')

    # return var to HTML
    roles = Role.objects.all()
    users = User.objects.all()
    orgs = Organization.objects.all()
    context = {'users': users,
               'roles': roles,
               'User_login': User_login,
               'orgs': orgs}
    return render(request, 'usermanage.html', context)


@csrf_exempt
def check_username(request):
    if request.method == 'POST':
        response_data = {}
        add_username = request.POST["add_username"]
        userid = User.objects.filter(username=add_username)
        user = None
        try:
            try:
                # we are matching the input again hardcoded value to avoid use of DB.
                # You can use DB and fetch value from table and proceed accordingly.
                if userid.count():
                    user = True

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e

            if not user:
                response_data["username_success"] = True
            else:
                response_data["username_success"] = False

        except Exception:
            response_data["username_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."

        return JsonResponse(response_data)


@csrf_exempt
def check_email(request):
    if request.method == 'POST':
        response_data = {}
        add_email = request.POST["add_email"]
        mail = User.objects.filter(email=add_email)
        email = None

        try:
            # we are matching the input again hardcoded value to avoid use of DB.
            # You can use DB and fetch value from table and proceed accordingly.
            if mail.count():
                email = True

        except ObjectDoesNotExist:
            pass
        except Exception as e:
            raise e

        if not email:
            response_data["email_success"] = True
        else:
            response_data["email_success"] = False

        return JsonResponse(response_data)


def reset_password(request):
    # Form Reset Password
    # Get variables from Input HTML
    if request.method == "POST":
        username = request.POST['inputUser']
        old_password = request.POST['oldPassword']
        new_password = request.POST['newPassword']
        con_new_password = request.POST['conPassword']
        try:  # Test connect User in modals(DB)
            user = User.objects.get(username=username, password=old_password)
            if old_password != new_password:
                if new_password == con_new_password:  # Check new_pass and con_pass
                    user.password = new_password
                    now = datetime.date.today()
                    user.expired_date = now + datetime.timedelta(90)
                    user.save()
                    messages.success(request, "สร้างรายการสำเร็จ")
                    return redirect('/')
                else:  # NewPassword != ConPassword
                    messages.error(request, 'รหัสผ่านใหม่และรหัสผ่านยืนยันไม่ตรงกัน')
            else:  # OldPassword != NewPassword
                messages.error(request, 'รหัสผ่านเก่าต้องไม่ตรงกับรหัสผ่านใหม่')
        except Machine_Management.models.User.DoesNotExist:  # Failed Connect User in model(DB)
            messages.error(request, 'ชื่อผู้ใช้และรหัสผ่านเก่าไม่ถูกต้อง')
    return render(request, 'resetpassword.html')


def rolemanage(request):
    global User_login  # Call User sign in
    if not Role_Screen.objects.filter(role=UserRole, screen_id='rolemanage').exists():
        return redirect('/')
    if request.method == "POST":
        if 'Editrole' in request.POST:
            role_id = request.POST['set_roleid']  # Get var('role id') from HTML
            role_name = request.POST['set_rolename']  # Get var('role name') from HTML
            role = Role.objects.get(role_id=role_id)
            role.role_name = role_name
            role.save()
            messages.success(request, "แก้ไขและบันทึกรายการสำเร็จ")
        elif 'Addrole' in request.POST:
            role_id = request.POST['add_roleid']  # Get var('role id') from HTML
            role_name = request.POST['add_rolename']  # Get var('role name') from HTML
            try:
                role = Role.objects.create(role_id=role_id, role_name=role_name)
                role.save()
                messages.success(request, "สร้างรายการสำเร็จ")
            except django.db.utils.IntegrityError:
                messages.error(request, "มีชื่อ Role ID นี้แล้ว กรุณาตั้งใหม่")
        elif 'deleterole' in request.POST:
            role_id = request.POST['deleterole']  # Get var('role id') from HTML
            role = Role.objects.get(role_id=role_id)
            role.delete()
            messages.success(request, "ลบรายการสำเร็จ")
        elif 'signout' in request.POST:
            User_login = None  # Set User_login is None

        return redirect('/usermanage/role/')

    roles = Role.objects.all()
    context = {'roles': roles,
               'User_login': User_login}
    return render(request, 'rolemanage.html', context)


def screenmanage(request):
    global User_login
    if not Role_Screen.objects.filter(role=UserRole, screen_id='screenmanage').exists():
        return redirect('/')
    if request.method == "POST":
        if 'Addscreen' in request.POST:
            if not Screen.objects.filter(screen_id=request.POST['screen_id']).exists():
                screen_id = request.POST['screen_id']
                screen_name = request.POST['screen_name']
                file_py = request.POST['file_py']
                file_html = request.POST['file_html']
                screen = Screen.objects.create(
                    screen_id=screen_id,
                    screen_name=screen_name,
                    file_py=file_py,
                    file_html=file_html
                )
                screen.save()
                messages.success(request, "สร้างรายการสำเร็จ")
            else:
                messages.info(request, "มีชื่อ Screen ID นี้แล้ว กรุณาตั้งใหม่")
        elif 'deletescreen' in request.POST:
            del_screen_id = request.POST['deletescreen']
            screen = Screen.objects.get(screen_id=del_screen_id)
            screen.delete()
            messages.success(request, "ลบรายการสำเร็จ")
        elif 'Editscreen' in request.POST:
            set_screen_id = request.POST['set_screenid']
            set_screen_name = request.POST['set_screenname']
            set_file_py = request.POST['set_filepy']
            set_file_html = request.POST['set_filehtml']
            screen = Screen.objects.get(screen_id=request.POST['Editscreen'])
            screen.screen_id = set_screen_id
            screen.screen_name = set_screen_name
            screen.file_py = set_file_py
            screen.file_html = set_file_html
            screen.save()
            messages.success(request, "แก้ไขและบันทึกรายการสำเร็จ")

        return redirect('/usermanage/screen/')

    screens = Screen.objects.all()
    context = {'User_logined': User_login,
               'screens': screens}
    return render(request, 'screenmanage.html', context)


def role_screen(request):
    global User_login
    if not Role_Screen.objects.filter(role=UserRole, screen_id='role_screen').exists():
        return redirect('/')
    if request.method == "POST":
        if 'delete_rs' in request.POST:
            rs_id = request.POST['delete_rs']
            role_screen = Role_Screen.objects.get(id=rs_id)
            role_screen.delete()
            messages.success(request, "ลบรายการสำเร็จ")
        elif 'Edit_rs' in request.POST:
            rs = Role_Screen.objects.get(id=request.POST['Edit_rs'])
            if rs.role_id == request.POST['set_rs_role'] and rs.screen_id == request.POST['set_rs_screen']:
                rs_id = request.POST['Edit_rs']
                rs_role_id = request.POST['set_rs_role']
                rs_screen_id = request.POST['set_rs_screen']
                rs_insert = request.POST.get('set_rs_insert', "N")
                rs_update = request.POST.get('set_rs_update', "N")
                rs_delete = request.POST.get('set_rs_delete', "N")
                role_screen = Role_Screen.objects.get(id=rs_id)
                role_screen.role_id = rs_role_id
                role_screen.screen_id = rs_screen_id
                role_screen.permission_insert = rs_insert
                role_screen.permission_update = rs_update
                role_screen.permission_delete = rs_delete
                role_screen.save()
                messages.success(request, "แก้ไขและบันทึกรายการสำเร็จ")
            elif not Role_Screen.objects.filter(role_id=request.POST['set_rs_role'],
                                                screen_id=request.POST['set_rs_screen']).exists():
                rs_id = request.POST['Edit_rs']
                rs_role_id = request.POST['set_rs_role']
                rs_screen_id = request.POST['set_rs_screen']
                rs_insert = request.POST.get('set_rs_insert', "N")
                rs_update = request.POST.get('set_rs_update', "N")
                rs_delete = request.POST.get('set_rs_delete', "N")
                role_screen = Role_Screen.objects.get(id=rs_id)
                role_screen.role_id = rs_role_id
                role_screen.screen_id = rs_screen_id
                role_screen.permission_insert = rs_insert
                role_screen.permission_update = rs_update
                role_screen.permission_delete = rs_delete
                role_screen.save()
                messages.success(request, "แก้ไขและบันทึกรายการสำเร็จ")
            else:
                messages.error(request, 'Role และ Screen นี้มีแล้ว!! ไม่สามารถสร้างซ้ำได้')
        elif 'Addrolescreen' in request.POST:
            if not Role_Screen.objects.filter(role_id=request.POST['add_rs_role'],
                                              screen_id=request.POST['add_rs_screen']).exists():
                rs_role_id = request.POST['add_rs_role']
                rs_screen_id = request.POST['add_rs_screen']
                rs_insert = request.POST.get('add_rs_insert', "N")
                rs_update = request.POST.get('add_rs_update', "N")
                rs_delete = request.POST.get('add_rs_delete', "N")
                role_screen = Role_Screen.objects.create(
                    role_id=rs_role_id,
                    screen_id=rs_screen_id,
                    permission_insert=rs_insert,
                    permission_update=rs_update,
                    permission_delete=rs_delete
                )
                role_screen.save()
                messages.success(request, "สร้างรายการสำเร็จ")
            else:
                messages.error(request, 'Role และ Screen นี้มีแล้ว!! ไม่สามารถสร้างซ้ำได้')

        return redirect('/usermanage/rolescreen/')

    list_role_screen = Role_Screen.objects.all()
    roles = Role.objects.all()
    screens = Screen.objects.all()
    context = {'User_login': User_login,
               'list_role_screen': list_role_screen,
               'roles': roles,
               'screens': screens}
    return render(request, 'role_screen_manage.html', context)


def home(request):
    global User_login, UserRole, dict_menu_level, List_user_Screen
    if request.method == "POST":
        if 'signout' in request.POST:
            User_login = None
            UserRole = None
    try:
        user_role = Role.objects.get(role_id=User_login.role)
    except AttributeError:
        return redirect("/")
    List_user_Screen = user_role.members.all()
    list_user_menu_lv0 = Menu.objects.filter(level=0).order_by('index')
    list_user_menu_lv1 = Menu.objects.filter(level=1).order_by('index')
    list_menu_role = []
    dict_menu_level = {}
    for menu_role in List_user_Screen:
        try:
            list_menu_role.append(Menu.objects.get(screen=menu_role))
        except Machine_Management.models.Menu.DoesNotExist:
            pass
    for root in list_user_menu_lv0:
        if root in list_menu_role:
            dict_menu_level[root] = []
    for child in list_user_menu_lv1:
        if child in list_menu_role:
            root = Menu.objects.get(menu_id=child.parent_menu)
            dict_menu_level[root].append(child)
    user_org = User_login.org.org_line.all()
    User_org_machine_line = Machine.objects.filter(line__in=user_org)
    context = {'User_login': User_login, 'UserRole': UserRole, 'dict_menu_level': dict_menu_level.items(),
               'User_org_machine_line': User_org_machine_line, 'line_of_user': user_org}
    return render(request, 'home.html', context)


def test(request):

    text = ""
    if request.method == "GET":
        if 'skills' in request.GET:
            text = request.GET.getlist('skills')
            print(text)
    elif request.method == "POST":
        if 'ok' in request.POST:
            print(request.POST.getlist('check'))
            return redirect('/test/')

    context = {'text': text}
    return render(request, 'test.html', context)


def menumanage(request):
    global User_login
    if not Role_Screen.objects.filter(role=UserRole, screen_id='menumanage').exists():
        return redirect('/')
    if request.method == 'POST':
        if 'Addmenu' in request.POST:
            if not Menu.objects.filter(menu_id=request.POST['add_menu_id']).exists():
                add_menu_id = request.POST['add_menu_id']
                add_menu_name = request.POST['add_menu_name']
                add_menu_level = request.POST['add_menu_level']
                select_screen = request.POST['select_screen']
                select_parent = request.POST['select_parent']
                add_menu_index = request.POST['add_menu_index']
                add_menu_path = request.POST['add_menu_path']
                screen = Screen.objects.get(screen_id=select_screen)
                menu = Menu.objects.create(
                    menu_id=add_menu_id,
                    name=add_menu_name,
                    level=add_menu_level,
                    screen=screen,
                    parent_menu=select_parent,
                    index=add_menu_index,
                    path_url=add_menu_path
                )
                menu.save()
                messages.success(request, "สร้างรายการสำเร็จ")
            else:
                messages.error(request, "มีการใช้ Menu ID นี้แล้ว กรุณาตั้งชื่อใหม่")
        elif 'Editmenu' in request.POST:
            old_menu_id = request.POST['Editmenu']
            set_menu_id = request.POST['set_menu_id']
            set_menu_name = request.POST['set_menu_name']
            set_menu_level = request.POST['set_menu_level']
            select_screen = request.POST['select_screen']
            select_parent = request.POST['select_parent']
            set_menu_index = request.POST['set_menu_index']
            set_menu_path = request.POST['set_menu_path']
            screen = Screen.objects.get(screen_id=select_screen)
            if old_menu_id == set_menu_id:
                set_menu = Menu.objects.get(menu_id=set_menu_id)
                set_menu.name = set_menu_name
                set_menu.level = set_menu_level
                set_menu.screen = screen
                set_menu.parent_menu = select_parent
                set_menu.index = set_menu_index
                set_menu.path_url = set_menu_path
                set_menu.save()
                messages.success(request, "แก้ไขและบันทึกรายการสำเร็จ")
            else:
                old_menu = Menu.objects.get(menu_id=old_menu_id)
                old_menu.delete()
                set_menu = Menu.objects.create(
                    menu_id=set_menu_id,
                    name=set_menu_name,
                    level=set_menu_level,
                    screen=screen,
                    parent_menu=select_parent,
                    index=set_menu_index,
                    path_url=set_menu_path
                )
                set_menu.save()
                messages.success(request, "แก้ไขและบันทึกรายการสำเร็จ")
        elif 'deletemenu' in request.POST:
            del_menu_id = request.POST['deletemenu']
            menu_del = Menu.objects.get(menu_id=del_menu_id)
            menu_del.delete()
            messages.success(request, "ลบรายการสำเร็จ")

        return redirect('/usermanage/menu/')

    list_menu = Menu.objects.order_by('level')
    list_screen = Screen.objects.all()
    screen_of_menu = []
    for menu in list_menu:
        screen_of_menu.append(menu.screen_id)
    context = {
        'User_login': User_login,
        'list_menu': list_menu,
        'list_screen': list_screen,
        'screen_of_menu': screen_of_menu
    }
    return render(request, 'menumanage.html', context)


def organizemanage(request):
    global User_login
    if not Role_Screen.objects.filter(role=UserRole, screen_id='organize_manage').exists():
        return redirect('/')
    if request.method == 'POST':
        if 'Addorg' in request.POST:
            if not Organization.objects.filter(org_code=request.POST['add_org_code']).exists():
                add_org_code = request.POST['add_org_code']
                add_org_name = request.POST['add_org_name']
                organize = Organization.objects.create(
                    org_code=add_org_code,
                    org_name=add_org_name
                )
                organize.save()
                messages.success(request, "สร้างรายการสำเร็จ")
            else:
                messages.error(request, 'มีชื่อ Organize Code นี้แล้ว ไม่สามารถเพิ่มได้ กรุณาทำรายการใหม่')
        elif 'delete_org' in request.POST:
            organize = Organization.objects.get(org_id=request.POST['delete_org'])
            organize.delete()
            messages.success(request, "ลบรายการสำเร็จ")
        elif 'Editorg' in request.POST:
            organize = Organization.objects.get(org_id=request.POST['set_org_id'])
            organize.org_code = request.POST['set_org_code']
            organize.org_name = request.POST['set_org_name']
            organize.save()
            messages.success(request, "แก้ไขและบันทึกรายการสำเร็จ")

        return redirect('/organizemanage/organization')

    orgs = Organization.objects.all()
    context = {
        'orgs': orgs, 'User_login': User_login
    }
    return render(request, 'organizemanage.html', context)


def load_building(request):
    site_id = request.GET.get('location_site_id')
    building = Building.objects.filter(site_id=site_id).all()
    context = {'building': building}
    return render(request, 'building_dropdown_list.html', context)


def load_floor(request):
    site_id = request.GET.get('location_site_id')
    building_id = request.GET.get('location_building_id')
    floors = Floor.objects.filter(building_id=building_id, site_id=site_id).all()
    context = {'floors': floors}
    return render(request, 'floor_dropdown_list.html', context)


def production_line(request):
    global User_login, UserRole
    if not Role_Screen.objects.filter(role=UserRole, screen_id='production_line').exists():
        return redirect('/')
    if request.method == "POST":
        if 'Addprodline' in request.POST:
            try:
                if not Production_line.objects.filter(production_line=request.POST['add_prodline'],
                                                      location_site=Site.objects.get(
                                                          id=request.POST['add_select_site']),
                                                      location_building=Building.objects.get(
                                                          id=request.POST['add_select_building']),
                                                      location_floor=Floor.objects.get(
                                                          id=request.POST['add_select_floor'])
                                                      ).exists():
                    pline = Production_line.objects.create(
                        production_line=request.POST['add_prodline'],
                        location_site=Site.objects.get(id=request.POST['add_select_site']),
                        location_building=Building.objects.get(id=request.POST['add_select_building']),
                        location_floor=Floor.objects.get(id=request.POST['add_select_floor'])
                    )
                    pline.save()
                    messages.success(request, "สร้างรายการสำเร็จ")
                else:
                    messages.error(request, "มี Production Line นี้แล้วอยู่ในระบบ")
            except Machine_Management.models.Floor.DoesNotExist:
                messages.error(request, "คุณกรอกข้อมูลบางส่วนไม่สมบูรณ์ กรุณากรอกข้อมูลให้สมบูรณ์")

        elif 'Edit_prod_line' in request.POST:
            if not Production_line.objects.filter(production_line=request.POST['set_production_line'],
                                                  location_site=Site.objects.get(id=request.POST['select_site']),
                                                  location_building=Building.objects.get(
                                                      id=request.POST['select_building']),
                                                  location_floor=Floor.objects.get(id=request.POST['select_floor'])
                                                  ).exists():
                pline = Production_line.objects.get(pid=request.POST['set_prodline_id'])
                pline.production_line = request.POST['set_production_line']
                pline.location_site = Site.objects.get(id=request.POST['select_site'])
                pline.location_building = Building.objects.get(id=request.POST['select_building'])
                pline.location_floor = Floor.objects.get(id=request.POST['select_floor'])
                pline.save()
            else:
                messages.error(request, "มี Production Line นี้แล้วอยู่ในระบบ")
        elif 'delete_line' in request.POST:
            pline = Production_line.objects.get(pid=request.POST['delete_line'])
            pline.delete()
            messages.success(request, "ลบรายการสำเร็จ")

        return redirect('/organizemanage/line')

    lines = Production_line.objects.all()
    sites = Site.objects.all()
    buildings = Building.objects.all()
    floors = Floor.objects.all()
    context = {
        'User_login': User_login, 'lines': lines, 'sites': sites, 'buildings': buildings, 'floors': floors
    }
    return render(request, 'production_line.html', context)


def location(request):
    global User_login, UserRole
    if not Role_Screen.objects.filter(role=UserRole, screen_id='location').exists():
        return redirect('/')
    if request.method == "POST":
        if 'add_location' in request.POST:
            if Site.objects.filter(site=request.POST['add_site']).exists():
                site = Site.objects.get(site=request.POST['add_site'])
            else:
                site = Site.objects.create(site=request.POST['add_site'])
                site.save()
            if Building.objects.filter(building=request.POST['add_building'], site=site).exists():
                building = Building.objects.get(building=request.POST['add_building'], site=site)
            else:
                building = Building.objects.create(building=request.POST['add_building'], site=site)
                building.save()
            if Floor.objects.filter(floor=request.POST['add_floor'], site=site, building=building).exists():
                messages.error(request, "มี Location นี้แล้ว")
            else:
                floor = Floor.objects.create(floor=request.POST['add_floor'], site=site, building=building)
                floor.save()
                messages.success(request, "สร้างรายการสำเร็จ")
        elif 'Editlocation' in request.POST:
            floor = Floor.objects.get(id=request.POST['set_location_id'])
            if floor.site.site != request.POST['set_site']:
                if Site.objects.filter(site=request.POST['set_site']).exists():
                    site = Site.objects.get(site=request.POST['set_site'])
                else:
                    site = Site.objects.create(site=request.POST['set_site'])
                    site.save()
                floor.site = site
            else:
                site = floor.site
            if floor.building.building != request.POST['set_building']:
                if Building.objects.filter(building=request.POST['set_building'], site=site).exists():
                    building = Building.objects.get(building=request.POST['set_building'])
                else:
                    building = Building.objects.create(building=request.POST['set_building'], site=site)
                    building.save()
                floor.building = building
            else:
                building = floor.building
            if floor.floor != request.POST['set_floor']:
                if Floor.objects.filter(floor=request.POST['set_floor'], site=site, building=building).exists():
                    messages.error(request, "มี Location นี้แล้ว")
                else:
                    floor.floor = request.POST['set_floor']
                    floor.save()
            messages.success(request, "แก้ไขและบันทึกรายการสำเร็จ")
        elif 'delete_location' in request.POST:
            locations = Floor.objects.get(pk=request.POST['delete_location'])
            if Floor.objects.filter(site_id=locations.site_id).count() == 1:
                site = Site.objects.get(pk=locations.site_id)
                site.delete()
            if Floor.objects.filter(building_id=locations.building_id).count() == 1:
                building = Building.objects.get(pk=locations.building_id)
                building.delete()
            if Floor.objects.filter(pk=locations.pk).count() == 1:
                locations.delete()
            messages.success(request, "ลบรายการสำเร็จ")

        return redirect('/organizemanage/location')

    sites = Site.objects.all()
    buildings = Building.objects.all()
    floors = Floor.objects.all()
    context = {'User_login': User_login, 'sites': sites, 'buildings': buildings, 'floors': floors}
    return render(request, 'location.html', context)


def org_productline(request):
    global User_login, UserRole
    if not Role_Screen.objects.filter(role=UserRole, screen_id='location').exists():
        return redirect('/')
    if request.method == "POST":
        if "Editorgline" in request.POST:
            org = Organization.objects.get(org_id=request.POST["org_id"])
            line = Production_line.objects.get(pid=request.POST["select_line"])
            org.org_line.add(line)
            org.save()
            messages.success(request, "เพิ่มรายการสำเร็จ")
        elif "delete_org" in request.POST:
            org = Organization.objects.get(org_id=request.POST["delete_org"])
            line = Production_line.objects.get(pid=request.POST["select_del_line"])
            org.org_line.remove(line)
            org.save()
            messages.success(request, "ลบรายการสำเร็จ")

        return redirect('/organizemanage/orgline')

    org_lines = Organization.objects.all()
    prod_lines = Production_line.objects.all()
    context = {
        'org_lines': org_lines, 'prod_lines': prod_lines, 'User_login': User_login, 'UserRole': UserRole
    }
    return render(request, 'org_prodline.html', context)


@csrf_exempt
def check_role(request):
    if request.method == 'POST':
        response_data = {}
        add_roleid = request.POST["add_roleid"]
        roleid = Role.objects.filter(role_id=add_roleid)
        role = None
        try:
            try:
                # we are matching the input again hardcoded value to avoid use of DB.
                # You can use DB and fetch value from table and proceed accordingly.
                if roleid.count():
                    role = True  # alredy exist
                elif len(add_roleid) == 0:
                    role = None  # empty input
                else:
                    role = False  # avialble

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e

            if not role:
                response_data["role_success"] = True
            else:
                response_data["role_success"] = False
            if role is None:
                response_data["role_empty"] = True
        except Exception:
            response_data["role_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."

        return JsonResponse(response_data)


def productmanage(request):
    global User_login, UserRole
    if request.method == "POST":
        if 'Addpline' in request.POST:
            if not Product.objects.filter(product_code=request.POST['add_product_code']).exists():
                line = Production_line.objects.get(pk=request.POST['add_select_pline'])
                product = Product.objects.create(
                    product_name=request.POST['add_product_name'],
                    product_code=request.POST['add_product_code'],
                    capacity=request.POST['add_product_capacity'],
                    labour=request.POST['add_product_labour'],
                    line=line
                )
                product.save()
                messages.success(request, "สร้างรายการสำเร็จ")
            else:
                messages.info(request, "มีเลขรหัสผลิตภัณฑ์นี้แล้วนในไลน์การผลิต")
        elif 'Editproduct' in request.POST:
            line = Production_line.objects.get(pk=request.POST['set_select_pline'])
            product = Product.objects.get(pk=request.POST['Editproduct'])
            product.product_name = request.POST['set_product_name']
            product.product_code = request.POST['set_product_code']
            product.capacity = request.POST['set_product_capacity']
            product.labour = request.POST['set_product_labour']
            product.line = line
            product.save()
            messages.success(request, "แก้ไขและบันทึกรายการสำเร็จ")
        elif 'delete_line' in request.POST:
            product = Product.objects.get(pk=request.POST['delete_line'])
            product.delete()
            messages.success(request, "ลบรายการสำเร็จ")

        return redirect('/organizemanage/productmanage')

    products = Product.objects.all()
    plines = Production_line.objects.all()
    context = {"User_login": User_login, "UserRole": UserRole, "products": products, 'plines': plines}
    return render(request, 'productmanage.html', context)


def load_machine_subtype(request):
    mch_type = request.GET.get('mch_type')
    mch_subtype = Machine_subtype.objects.filter(mch_type_id=mch_type).all()
    context = {'mch_subtype': mch_subtype}
    return render(request, 'ajax_machine_subtype.html', context)


def machine_manage(request):
    global User_login, UserRole
    role_and_screen = Role_Screen.objects.filter(role_id=UserRole, screen_id='machine_management')
    if not role_and_screen.exists():
        return redirect('/')

    user_org = User_login.org.org_line.all()
    machine = Machine.objects.filter(line__in=user_org)
    mch_type_all = Machine_type.objects.all()
    mch_subtype_all = Machine_subtype.objects.all()
    pd_line = Production_line.objects.all()

    filter_mch_line = Machine.objects.order_by('line').values_list('line', flat=True).distinct()
    select_line_export = Production_line.objects.filter(pid__in=filter_mch_line)

    if request.method == "POST":
        if 'Addmachine' in request.POST:
            add_production_line = request.POST['add_production_line']
            add_type = request.POST['add_type']
            add_subtype = request.POST['add_subtype']
            add_serial = request.POST['add_serial']
            add_machine_production_line_code = request.POST['add_mpc']
            add_machine_name = request.POST['add_machine_name']
            add_machine_model = request.POST['add_machine_model']
            add_machine_brand = request.POST['add_machine_brand']
            add_supplier = request.POST['add_supplier_code']
            add_supplier_name = request.POST['add_supplier_name']
            add_supplier_contact = request.POST['add_supplier_contact']
            add_eng_emp_id = request.POST['add_eng_emp_id']
            add_eng_emp_name = request.POST['add_eng_emp_name']
            add_eng_emp_contact = request.POST['add_eng_emp_contact']
            add_pro_emp_id = request.POST['add_pro_emp_id']
            add_pro_emp_name = request.POST['add_pro_emp_name']
            add_pro_emp_contact = request.POST['add_pro_emp_contact']
            add_capacity_per_min = request.POST['add_cpm']
            add_capacity = request.POST['add_capacity']
            add_power = request.POST['add_power'] if request.POST['add_power'] != '' else ""
            add_install_date = request.POST['add_installdate']
            add_start_date = request.POST['add_startdate']
            add_hour = request.POST['add_hour'] if request.POST['add_hour'] != '' else 0
            add_core = request.POST.get('add_mch_core', False)
            if request.POST.get('add_mch_core', False):
                if Machine.objects.filter(line_id=add_production_line, machine_core=True).exists():
                    messages.error(request, 'ในไลน์ผลิตนี้มี Machine Core แล้วไม่สามารถทำรายการได้')
                    return redirect('/machinemanage/machine/')
            if not Machine.objects.filter(serial_id=add_serial,
                                          machine_production_line_code=add_machine_production_line_code).exists():
                add_new_machine = Machine.objects.create(
                    serial_id=add_serial,
                    machine_production_line_code=add_machine_production_line_code,
                    machine_name=add_machine_name,
                    machine_brand=add_machine_brand,
                    machine_model=add_machine_model,
                    machine_supplier_code=add_supplier,
                    machine_supplier_name=add_supplier_name,
                    machine_supplier_contact=add_supplier_contact,
                    machine_eng_emp_id=add_eng_emp_id,
                    machine_eng_emp_name=add_eng_emp_name,
                    machine_eng_emp_contact=add_eng_emp_contact,
                    machine_pro_emp_id=add_pro_emp_id,
                    machine_pro_emp_name=add_pro_emp_name,
                    machine_pro_emp_contact=add_pro_emp_contact,
                    machine_load_capacity=add_capacity_per_min,
                    machine_load_capacity_unit=add_capacity,
                    machine_power_use_kwatt_per_hour=add_power,
                    machine_installed_datetime=add_install_date,
                    machine_start_use_datetime=add_start_date,
                    line_id=add_production_line,
                    mch_type_id=add_type,
                    sub_type_id=add_subtype,
                    create_by=User_login.username,
                    create_date=datetime.date.today(),
                    machine_hour=add_hour,
                    machine_active=True,
                    machine_core=add_core
                )
                add_new_machine.save()
                messages.success(request, 'เพิ่มข้อมูล Machine เรียบร้อยแล้ว')
            else:
                messages.error(request, 'การเพิ่มข้อมูล Machine ล้มเหลว กรุณากด Add New Machine Type ใหม่อีกครั้ง')
        elif 'EditMch' in request.POST:
            edit_mch = Machine.objects.get(machine_id=request.POST['EditMch'])
            edit_mch.machine_production_line_code = request.POST['set_mch_code']
            edit_mch.machine_name = request.POST['set_mch_name']
            # edit_mch.machine_brand = request.POST['set_machine_brand']
            # edit_mch.machine_model = request.POST['set_machine_model']
            # edit_mch.serial_id = request.POST['set_serial']
            edit_mch.machine_supplier_code = request.POST['set_supplier_code']
            edit_mch.machine_supplier_name = request.POST['set_supplier_name']
            edit_mch.machine_supplier_contact = request.POST['set_supplier_contact']
            edit_mch.machine_eng_emp_id = request.POST['set_eng_emp_id']
            edit_mch.machine_eng_emp_name = request.POST['set_eng_emp_name']
            edit_mch.machine_eng_emp_contact = request.POST['set_eng_emp_contact']
            edit_mch.machine_pro_emp_id = request.POST['set_pro_emp_id']
            edit_mch.machine_pro_emp_name = request.POST['set_pro_emp_name']
            edit_mch.machine_pro_emp_contact = request.POST['set_pro_emp_contact']
            edit_mch.machine_load_capacity = request.POST['set_cpm']
            edit_mch.machine_load_capacity_unit = request.POST['set_capacity']
            edit_mch.machine_power_use_kwatt_per_hour = request.POST['set_power']
            edit_mch.machine_installed_datetime = request.POST['set_installdate']
            edit_mch.machine_start_use_datetime = request.POST['set_startdate']
            edit_mch.line_id = request.POST['select_line']
            edit_mch.mch_type_id = request.POST['select_type']
            edit_mch.sub_type_id = request.POST['select_subtype']
            edit_mch.last_update_by = str(User_login.username)
            edit_mch.last_update_date = datetime.date.today()
            edit_mch.machine_active = request.POST.get('set_mch_status', False)
            if request.POST.get('set_mch_core', False):
                if Machine.objects.filter(line_id=edit_mch.line_id, machine_core=True).exists():
                    if edit_mch != Machine.objects.get(line_id=edit_mch.line_id, machine_core=True):
                        messages.error(request, 'ในไลน์ผลิตนี้มี Machine Core แล้วไม่สามารถทำรายการได้')
                        return redirect('/machinemanage/machine/')
            edit_mch.machine_core = request.POST.get('set_mch_core', False)
            edit_mch.machine_hour = request.POST.get('set_hour', 0)
            edit_mch.machine_minute = request.POST.get('set_minute', 0)
            if edit_mch.machine_document1 != request.FILES.get('set_documentFile1', "") and request.FILES.get('set_documentFile1', False):
                edit_mch.machine_document1.delete()
                edit_mch.machine_document1 = request.FILES['set_documentFile1']
            if edit_mch.machine_document2 != request.FILES.get('set_documentFile2', "") and request.FILES.get('set_documentFile2', False):
                edit_mch.machine_document2.delete()
                edit_mch.machine_document2 = request.FILES['set_documentFile2']
            if edit_mch.machine_document3 != request.FILES.get('set_documentFile3', "") and request.FILES.get('set_documentFile3', False):
                edit_mch.machine_document3.delete()
                edit_mch.machine_document3 = request.FILES['set_documentFile3']
            if edit_mch.machine_document4 != request.FILES.get('set_documentFile4', "") and request.FILES.get('set_documentFile4', False):
                edit_mch.machine_document4.delete()
                edit_mch.machine_document4 = request.FILES['set_documentFile2']
            if edit_mch.machine_document5 != request.FILES.get('set_documentFile5', "") and request.FILES.get('set_documentFile5', False):
                edit_mch.machine_document5.delete()
                edit_mch.machine_document5 = request.FILES['set_documentFile5']
            if edit_mch.machine_image1 != request.FILES.get('set_pictureFile1', "") and request.FILES.get('set_pictureFile1', False):
                edit_mch.machine_image1.delete()
                edit_mch.machine_image1 = request.FILES['set_pictureFile1']
            if edit_mch.machine_image2 != request.FILES.get('set_pictureFile2', "") and request.FILES.get('set_pictureFile2', False):
                edit_mch.machine_image2.delete()
                edit_mch.machine_image2 = request.FILES['set_pictureFile2']
            if edit_mch.machine_image3 != request.FILES.get('set_pictureFile3', "") and request.FILES.get('set_pictureFile3', False):
                edit_mch.machine_image3.delete()
                edit_mch.machine_image3 = request.FILES['set_pictureFile3']
            if edit_mch.machine_image4 != request.FILES.get('set_pictureFile4', "") and request.FILES.get('set_pictureFile4', False):
                edit_mch.machine_image4.delete()
                edit_mch.machine_image4 = request.FILES['set_pictureFile4']
            if edit_mch.machine_image5 != request.FILES.get('set_pictureFile5', "") and request.FILES.get('set_pictureFile5', False):
                edit_mch.machine_image5.delete()
                edit_mch.machine_image5 = request.FILES['set_pictureFile5']
            edit_mch.save()
            messages.success(request, 'แก้ไขข้อมูล Machine สำเร็จ')

        elif 'deletemachine' in request.POST:
            del_machine = request.POST['deletemachine']
            machine_id = Machine.objects.get(machine_id=del_machine)
            machine_id.delete()
            messages.success(request, "ลบรายการสำเร็จ")

        elif 'Export_machine' in request.POST:
            file_report = request.POST['file_type']
            if file_report == 'docx':
                machine_id = request.POST.get('Export_machine').split(',')
                line_id = Machine.objects.filter(machine_id__in=machine_id).order_by('line_id').values('line_id').distinct()
                list_production_line = Production_line.objects.filter(pid__in=line_id).order_by('production_line')
                document = Document()
                for line in list_production_line:
                    document.add_heading(f'Production Line {line.production_line}', 0)

                    document.add_paragraph(
                        f'สถานที่ตั้งโรงงาน {line.location_site} อาคารที่ {line.location_building} ชั้นที่ {line.location_floor}')
                    document.add_paragraph('ผลิตภัณฑ์ที่ผลิต', style='List Bullet')

                    list_product = []
                    for product in Product.objects.filter(line_id=line.pk):
                        try:
                            capacity_core = Machine_capacity.objects.get(machine_id=Machine.objects.get(line_id=line, machine_core=1), product_id=product)
                            list_product.append([str(product.product_name), str(product.product_code), int(capacity_core.fg_capacity)])
                        except Machine_Management.models.Machine.DoesNotExist:
                            capacity_core = "-"
                            list_product.append([str(product.product_name), str(product.product_code), capacity_core])
                        except Machine_Management.models.Machine_capacity.DoesNotExist:
                            capacity_core = "-"
                            list_product.append([str(product.product_name), str(product.product_code), capacity_core])

                    table = document.add_table(rows=1, cols=3)
                    table.style = 'Light List Accent 3'
                    hdr_cells = table.rows[0].cells
                    hdr_cells[0].text = 'Product Name'
                    hdr_cells[1].text = 'Product Code'
                    hdr_cells[2].text = 'Product Capacity'
                    for name, code, capacity in list_product:
                        row_cells = table.add_row().cells
                        row_cells[0].text = str(name)
                        row_cells[1].text = str(code)
                        row_cells[2].text = str(capacity)

                    # document.add_heading('เครื่องจักร', level=1)
                    machine_in_line = Machine.objects.filter(line_id=line, machine_id__in=machine_id).order_by('machine_production_line_code')
                    for mch in machine_in_line:

                        document.add_heading(f'ชื่อเครื่องจักร : {mch.machine_name}', level=1)
                        if mch.machine_image1:
                            picture_mch = document.add_picture(mch.machine_image1, width=Inches(2))
                            last_paragraph = document.paragraphs[-1]
                            last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        # run = document.add_paragraph(f'{mch.machine_name}', style='Intense Quote').add_run()
                        # font = run.font
                        # font.size = Pt(20)
                        document.add_paragraph('ข้อมูลเครื่องจักร', style='List Bullet')

                        records = (
                            ('Machine Name', mch.machine_name),
                            ('Machine Brand', mch.machine_brand),
                            ('Machine Model', mch.machine_model),
                            ('Machine Serial', mch.serial_id),
                            ('Machine Type', mch.mch_type),
                            ('Machine Subtype', mch.sub_type),
                            ('Machine Production Line', mch.line),
                            ('Machine Line Code', mch.machine_production_line_code),
                            ('Machine Load Capacity', str(mch.machine_load_capacity) + " " + str(mch.machine_load_capacity_unit)),
                            ('Machine Power', str(mch.machine_power_use_kwatt_per_hour)+" KWatt/Hour"),
                            ('Machine Installed Date', mch.machine_installed_datetime),
                            ('Machine Start Date', mch.machine_start_use_datetime),
                            ('Machine Hours', str(mch.machine_hour)),
                            ('Machine Supplier', mch.machine_supplier_code),
                            ('Machine Supplier Name', str(mch.machine_supplier_name)+" (ติดต่อ : "+str(mch.machine_supplier_contact)+" )"),
                            ('Engineer Emp in Charge', "รหัสพนักงาน :"+str(mch.machine_eng_emp_id)+" ชื่อ: "+str(mch.machine_eng_emp_name)+" (ติดต่อ : "+str(mch.machine_eng_emp_contact)+" )"),
                            ('Production Emp in Charge', "รหัสพนักงาน :"+str(mch.machine_pro_emp_id)+" ชื่อ: "+str(mch.machine_pro_emp_name)+" (ติดต่อ : "+str(mch.machine_pro_emp_contact)+" )")
                        )

                        table = document.add_table(rows=1, cols=2)
                        table.style = 'Light List Accent 1'
                        hdr_cells = table.rows[0].cells
                        hdr_cells[0].text = 'Title'
                        hdr_cells[1].text = 'Specification'
                        for title, data in records:
                            row_cells = table.add_row().cells
                            row_cells[0].text = title
                            row_cells[1].text = str(data)

                        mch_capacity = Machine_capacity.objects.filter(machine_id=mch.machine_id)
                        if mch_capacity.exists():
                            document.add_paragraph(' ')
                            document.add_paragraph('ข้อมูลกำลังการผลิต', style='List Bullet')
                            list_table = []
                            for mch_cap in mch_capacity:
                                list_table.append([str(mch_cap.product.product_name), str(mch_cap.product.product_code), str(int(mch_cap.fg_capacity))])
                            table = document.add_table(rows=1, cols=3)
                            table.style = 'Light List Accent 2'
                            hdr_cells = table.rows[0].cells
                            hdr_cells[0].text = 'Product Name'
                            hdr_cells[1].text = 'Product Code'
                            hdr_cells[2].text = 'FG Capacity/Hour'
                            for name, code, capacity in list_table:
                                row_cells = table.add_row().cells
                                row_cells[0].text = name
                                row_cells[1].text = code
                                row_cells[2].text = capacity

                        if mch != machine_in_line.last():
                            document.add_page_break()

                    if line != list_production_line.last():
                        document.add_page_break()

                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = 'attachment; filename=machine_data.docx'
                document.save(response)
                return response

            elif file_report == 'excel':
                ## Prepare exporting
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename="Machines.xls"'

                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet('Machines Data', cell_overwrite_ok=True)      # this will make a sheet named Machines Data

                # Sheet header, first row
                row_num = 0
                ws.row(0).height_mismatch = True
                ws.row(0).height = 200*2
                style = xlwt.easyxf('pattern: pattern solid, fore_colour gray25;''font: colour black, bold True;''align: vert centre, horiz centre')

                columns = ['Production Line', 'Machine Type', 'Machine Subtype', 'Machine Name', 'Line Code', 'Machine Brand', 'Machine Model', 'Machine Serial',
                           'Load Capacity', 'Load Unit', 'Power (Kwatt/Hour)', 'Machine Hour', 'Installed Date', 'Start Date']

                for col_num in range(len(columns)):
                    ws.col(col_num).width = 4500
                    ws.write(row_num, col_num, columns[col_num], style)             # at 0 row

                # Sheet body, remaining rows
                styles = ['pattern: pattern solid, fore_colour ice_blue;' 'align: vert centre, horiz centre',
                          'pattern: pattern solid, fore_colour ivory;''align: vert centre, horiz centre',
                          'pattern: pattern solid, fore_colour light_green;' 'align: vert centre, horiz centre',
                          'pattern: pattern solid, fore_colour lavender;' 'align: vert centre, horiz centre',
                          'pattern: pattern solid, fore_colour light_turquoise;' 'align: vert centre, horiz centre',
                          'pattern: pattern solid, fore_colour tan;' 'align: vert centre, horiz centre',
                          'pattern: pattern solid, fore_colour rose;' 'align: vert centre, horiz centre']

                machine_submit = request.POST.get('Export_machine')
                queryset = Machine.objects.filter(machine_id__in=machine_submit.split(',')).order_by('line__production_line', 'machine_production_line_code')

                rows = queryset.values_list('line__production_line', 'mch_type__mtype_name', 'sub_type__subtype_name', 'machine_name',
                                            'machine_production_line_code', 'machine_brand', 'machine_model', 'serial_id', 'machine_load_capacity',
                                            'machine_load_capacity_unit', 'machine_power_use_kwatt_per_hour', 'machine_hour', 'machine_installed_datetime',
                                            'machine_start_use_datetime')

                get_lines = rows.values('line__production_line')

                lines = []
                for l in get_lines:
                    lines.append(l.get('line__production_line'))

                for row in rows:
                    row_num += 1
                    for col_num in range(len(row)):
                        if col_num == 0:
                            for l in range(len(lines)):
                                if l == 0:
                                    findex = lines.index(lines[l])
                                    # Get last index of item in list
                                    lindex = len(lines) - lines[::-1].index(lines[l]) - 1
                                    style = xlwt.easyxf(styles[0])
                                    ws.write_merge(findex+1, lindex+1, 0, 0, lines[l], style)

                                elif lines[l] != lines[l-1]:
                                    styles = styles[1:]+styles[0:1]
                                    findex = lines.index(lines[l])
                                    # Get last index of item in list
                                    lindex = len(lines) - lines[::-1].index(lines[l]) - 1
                                    style = xlwt.easyxf(styles[0])
                                    ws.write_merge(findex+1, lindex+1, 0, 0, lines[l], style)
                        else:
                            if isinstance(row[col_num], datetime.date):
                                date_format = xlwt.XFStyle()
                                date_format.num_format_str = 'dd/mm/yyyy'
                                ws.write(row_num, col_num, row[col_num], date_format)
                            else:
                                ws.write(row_num, col_num, row[col_num])

                wb.save(response)

                return response

        return redirect('/machinemanage/machine/')

    context = {
        'User_login': User_login,
        'machine': machine, 'mch_subtype_all': mch_subtype_all,
        'production_line': pd_line, 'mch_type_all': mch_type_all, 'role_and_screen': role_and_screen,
        'select_line_export': select_line_export, 'filter_mch_line': filter_mch_line}
    return render(request, 'machine_manage.html', context)


@csrf_exempt
def check_serial(request):
    if request.method == 'POST':
        response_data = {}
        add_machine_serial = request.POST["add_serial"]
        add_brand = request.POST['add_brand']
        add_model = request.POST['add_model']
        serial = Machine.objects.filter(serial_id=add_machine_serial, machine_model=add_model, machine_brand=add_brand)

        if serial.count():
            serial_status = True  # alredy exist
        else:
            serial_status = False  # avialble

        if not serial_status:
            response_data["serial_success"] = True
        else:
            response_data["serial_success"] = False

        return JsonResponse(response_data)


def machine_type(request):
    global User_login
    role_and_screen = Role_Screen.objects.filter(role_id=UserRole, screen_id='machine_type')
    if not role_and_screen.exists():
        return redirect('/')
    mch_types = Machine_type.objects.all()
    if request.method == "POST":
        if 'Addtype' in request.POST:
            add_type_name = request.POST['add_type']
            add_type_code = request.POST['add_type_code']
            added_by = User_login.username
            now = datetime.datetime.now()
            created_date = now.date()
            if not Machine_type.objects.filter(mtype_code=add_type_code, mtype_name=add_type_name).exists():
                add_new_type = Machine_type.objects.create(
                    mtype_code=add_type_code,
                    mtype_name=add_type_name,
                    create_by=added_by,
                    create_date=created_date,
                )
                add_new_type.save()
                messages.success(request, 'เพิ่มข้อมูล Machine Type เรียบร้อยแล้ว')
            else:
                messages.error(request, 'การเพิ่มข้อมูล Machine Type ล้มเหลว กรุณากด Add New Machine Type ใหม่อีกครั้ง')

        elif 'Edittype' in request.POST:
            edit_type = Machine_type.objects.get(mtype_id=request.POST['Edittype'])
            if Machine_type.objects.filter(mtype_code=request.POST['set_type_code']).exists() and edit_type.mtype_code != request.POST['set_type_code']:
                messages.error(request, 'การแก้ไขไม่สำเร็จ เนื่องจาก Machine Code นี้มีอยู่แล้วในระบบ')
            else:
                edit_type.mtype_code = request.POST['set_type_code']
                edit_type.mtype_name = request.POST['set_mch_type']
                edit_type.last_update_by = User_login.username
                now = datetime.datetime.now()
                edit_type.last_update_date = now.date()
                edit_type.save()
                messages.success(request, 'แก้ไขข้อมูล Machine Type สำเร็จ')
        elif 'Delete_type' in request.POST:
            del_type = request.POST['Delete_type']
            typeid = Machine_type.objects.get(mtype_id=del_type)
            typeid.delete()
            messages.success(request, "ลบรายการสำเร็จ")

        return redirect('/machinemanage/machinetype/')

    context = {'mch_types': mch_types, 'User_login': User_login, 'role_and_screen': role_and_screen}
    return render(request, 'machine_type.html', context)


@csrf_exempt
def check_machine_type_code(request):
    if request.method == 'POST':
        response_data = {}
        add_type_code = request.POST["add_type_code"]
        typeid = Machine_type.objects.filter(mtype_code=add_type_code)
        typecode = None

        try:
            try:
                if typeid.count():
                    typecode = True  # alredy exist
                elif len(add_type_code) == 0:
                    typecode = None  # empty input
                else:
                    typecode = False  # avialble

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e

            if not typecode:
                response_data["typecode_success"] = True
            else:
                response_data["typecode_success"] = False
            if typecode is None:
                response_data["typecode_empty"] = True

        except Exception:
            response_data["typecode_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."

        return JsonResponse(response_data)


def machine_subtype(request):
    global User_login
    role_and_screen = Role_Screen.objects.filter(role_id=UserRole, screen_id='machine_sub_type')
    if not role_and_screen.exists():
        return redirect('/')
    mch_subtype = Machine_subtype.objects.all()
    mch_type_all = Machine_type.objects.all()
    if request.method == "POST":
        if 'AddSubtype' in request.POST:
            add_subtype_name = request.POST['add_subtype']
            add_subtype_code = request.POST['add_subtype_code']
            added_by = User_login.username
            now = datetime.datetime.now()
            created_date = now.date()
            add_type = request.POST['add_type']

            if not Machine_subtype.objects.filter(subtype_code=add_subtype_code, subtype_name=add_subtype_name,
                                                  mch_type_id=add_type).exists():
                add_new_subtype = Machine_subtype.objects.create(
                    subtype_code=add_subtype_code,
                    subtype_name=add_subtype_name,
                    create_by=added_by,
                    create_date=created_date,
                    mch_type_id=add_type
                )
                add_new_subtype.save()
                messages.success(request, 'เพิ่มข้อมูล Machine Subtype เรียบร้อยแล้ว')
            else:
                messages.error(request, 'การเพิ่มข้อมูล Machine Subtype ล้มเหลว กรุณากด Add New Machine Subtype ใหม่อีกครั้ง')

        elif 'EditSubtype' in request.POST:
            edit_subtype = Machine_subtype.objects.get(subtype_id=request.POST['EditSubtype'])
            edit_subtype.subtype_name = request.POST['set_subtype']
            edit_subtype.mch_type_id = request.POST['select_type']
            edit_subtype.last_update_by = User_login.username
            now = datetime.datetime.now()
            edit_subtype.last_update_date = now.date()
            if not Machine_subtype.objects.filter(subtype_name=request.POST['set_subtype'],
                                                  mch_type_id=request.POST['select_type']).exists():
                edit_subtype.save()
                messages.success(request, 'แก้ไขข้อมูล Machine Subtype สำเร็จ')
            elif edit_subtype.subtype_name == request.POST['set_subtype'] and edit_subtype.mch_type_id == request.POST['select_type']:
                messages.success(request, 'ไม่มีการ Update รายการใหม่')
            else:
                messages.error(request, 'การแก้ข้อมูล Machine Subtype ไม่ถูกต้อง กรุณาแก้ไขใหม่อีกครั้ง')
        elif 'DeleteSubtype' in request.POST:
            del_subtype = request.POST['DeleteSubtype']
            subtypeid = Machine_subtype.objects.get(subtype_id=del_subtype)
            subtypeid.delete()

        return redirect('/machinemanage/machinesubtype/')

    context = {'subtypes': mch_subtype, 'mch_type_all': mch_type_all, 'User_login': User_login,
               'role_and_screen': role_and_screen}
    return render(request, 'machine_subtype.html', context)


@csrf_exempt
def check_screen_id(request):
    if request.method == 'POST':
        response_data = {}
        screen_id = request.POST["screen_id"]
        screen = Screen.objects.filter(screen_id=screen_id)
        screen_status = None
        try:
            try:
                # we are matching the input again hardcoded value to avoid use of DB.
                # You can use DB and fetch value from table and proceed accordingly.
                if screen.exists():
                    screen_status = True  # already exist
                elif len(screen_id) == 0:
                    screen_status = None  # empty input
                else:
                    screen_status = False  # avialble

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e
            if not screen_status:
                response_data["screen_status_success"] = True
            else:
                response_data["screen_status_success"] = False
            if screen_status is None:
                response_data["screen_status_empty"] = True

        except Exception:
            response_data["screen_status_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."
        return JsonResponse(response_data)


@csrf_exempt
def check_menu_id(request):
    if request.method == 'POST':
        response_data = {}
        menu_id = request.POST["menu_id"]
        menu = Menu.objects.filter(menu_id=menu_id)
        menu_status = None

        try:
            try:
                # we are matching the input again hardcoded value to avoid use of DB.
                # You can use DB and fetch value from table and proceed accordingly.
                if menu.exists():
                    menu_status = True  # already exist
                elif len(menu_id) == 0:
                    menu_status = None  # empty input
                else:
                    menu_status = False  # avialble

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e
            if not menu_status:
                response_data["menu_status_success"] = True
            else:
                response_data["menu_status_success"] = False
            if menu_status is None:
                response_data["menu_status_empty"] = True

        except Exception:
            response_data["menu_status_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."
        return JsonResponse(response_data)


@csrf_exempt
def check_org_code(request):
    if request.method == 'POST':
        response_data = {}
        org_code = request.POST["org_code"]
        organize = Organization.objects.filter(org_code=org_code)
        org_status = None

        try:
            try:
                # we are matching the input again hardcoded value to avoid use of DB.
                # You can use DB and fetch value from table and proceed accordingly.
                if organize.exists():
                    org_status = True  # already exist
                elif len(request.POST["org_code"]) == 0:
                    org_status = None  # empty input
                else:
                    org_status = False  # avialble

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e
            if not org_status:
                response_data["org_status_success"] = True
            else:
                response_data["org_status_success"] = False
            if org_status is None:
                response_data["org_status_empty"] = True

        except Exception:
            response_data["org_status_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."
        return JsonResponse(response_data)


@csrf_exempt
def check_machine_subtype_code(request):
    if request.method == 'POST':
        response_data = {}
        add_subtype_code = request.POST["add_subtype_code"]
        add_mch_type = request.POST['add_mch_type']
        subtype_id = Machine_subtype.objects.filter(subtype_code=add_subtype_code, mch_type_id=add_mch_type)

        if subtype_id.count():
            subtype_code = True  # alredy exist
        else:
            subtype_code = False  # avialble

        if not subtype_code:
            response_data["subtype_code_success"] = True
        else:
            response_data["subtype_code_success"] = False

        return JsonResponse(response_data)


def home_machine(request, line):
    global User_login, UserRole, dict_menu_level
    if not Role_Screen.objects.filter(role=UserRole).exists():
        return redirect('/')
    product_line = Production_line.objects.filter(pid=line)
    products = Product.objects.filter(line__in=product_line)
    machine_line = Machine.objects.filter(line__in=product_line)
    context = {'User_login': User_login, 'UserRole': UserRole, 'dict_menu_level': dict_menu_level.items(),
               'machine_line': machine_line, 'product_line': product_line, 'products': products}
    return render(request, 'home_machine.html', context)


def machine_details(request, line, machine):
    global User_login, UserRole, dict_menu_level
    if not Role_Screen.objects.filter(role=UserRole).exists():
        return redirect('/')
    machine = Machine.objects.filter(machine_id=machine, line_id=line)
    spare_part_of_mch = Machine_sparepart.objects.filter(machine_id__in=machine)
    context = {'User_login': User_login, 'UserRole': UserRole, 'dict_menu_level': dict_menu_level.items(),
               'machine': machine, 'spare_part_of_mch': spare_part_of_mch}
    return render(request, 'machine_details.html', context)


def spare_part_manage(request):
    global User_login
    role_and_screen = Role_Screen.objects.filter(role=UserRole, screen_id='spare_part_manage')
    if not role_and_screen.exists():
        return redirect('/')
    spare_part_all = Spare_part.objects.all()
    spare_part_group_all = Spare_part_group.objects.all()
    if request.method == 'POST':
        if 'add_spare_part' in request.POST:
            if request.POST['id_sp_type'] == "0" or request.POST['id_sp_subtype'] == "0" or request.POST['id_sp_group'] == "0":
                messages.error(request, "ทำรายการไม่สำเร็จ กรุณาระบุกลุ่มอะไหล่ ประเภทอะไหล่ และชนิดอะไหล่")
            else:
                spare_part = Spare_part.objects.create(spare_part_name=request.POST['add_sp_name'],
                                                       spare_part_model=request.POST['add_sp_model'],
                                                       spare_part_brand=request.POST['add_sp_brand'],
                                                       service_life=request.POST['add_service_life'] if request.POST['add_service_life'] != "" else None,
                                                       service_plan_life=request.POST['add_service_plan_life'] if request.POST['add_service_plan_life'] != "" else None,
                                                       spare_part_detail=request.POST['add_detail'],
                                                       spare_part_group_id=request.POST['id_sp_group'],
                                                       spare_part_type_id=request.POST['id_sp_type'],
                                                       spare_part_sub_type_id=request.POST['id_sp_subtype'],
                                                       create_by=User_login.username,
                                                       create_date=datetime.date.today(),
                                                       spare_part_active=True)
                spare_part.save()
                messages.success(request, "สร้างรายการสำเร็จ")
        elif 'edit_spare_part' in request.POST:
            spare_part = Spare_part.objects.get(pk=request.POST['edit_spare_part'])
            spare_part.spare_part_name = request.POST['set_sp_name']
            spare_part.spare_part_model = request.POST['set_sp_model']
            spare_part.spare_part_brand = request.POST['set_sp_brand']
            spare_part.service_life = request.POST['set_service_life'] if request.POST['set_service_life'] != "" else None
            spare_part.service_plan_life = request.POST['set_service_plan_life'] if request.POST['set_service_plan_life'] != "" else None
            spare_part.spare_part_detail = request.POST['set_detail']
            spare_part.last_update_by = User_login.username
            spare_part.last_update_date = datetime.date.today()
            spare_part.spare_part_active = request.POST.get('set_sp_status', False)
            spare_part.save()
            messages.success(request, "แก้ไขและบันทึกรายการสำเร็จ")
        elif 'delete_spare_part' in request.POST:
            spare_part = Spare_part.objects.get(pk=request.POST['delete_spare_part'])
            spare_part.delete()
            messages.success(request, "ลบรายการสำเร็จ")

        return redirect('/sparepartmanage/sparepart/')

    context = {'User_login': User_login, 'spare_part_all': spare_part_all, 'spare_part_group_all': spare_part_group_all,
               'role_and_screen': role_and_screen}
    return render(request, 'spare_part_manage.html', context)


def load_spare_part_subtype(request):
    sp_type_id = request.GET.get('sp_type_id')
    spare_part_sub_type = Spare_part_sub_type.objects.filter(spare_part_type_id=sp_type_id).all()
    context = {'spare_part_subtype': spare_part_sub_type}
    return render(request, 'ajax_spare_part_subtype.html', context)


def load_spare_part(request):
    sp_subtype_id = request.GET.get('sp_subtype_id')
    spare_part = Spare_part.objects.filter(spare_part_sub_type=sp_subtype_id).all()
    context = {'spare_part': spare_part}
    return render(request, 'ajax_spare_part.html', context)


def spare_part_subtype(request):
    global User_login
    role_and_screen = Role_Screen.objects.filter(role=UserRole, screen_id='spare_part_subtype')
    if not role_and_screen.exists():
        return redirect('/')
    spare_part_subtype_all = Spare_part_sub_type.objects.all()
    spare_part_group_all = Spare_part_group.objects.all()
    if request.method == 'POST':
        if 'add_spare_part_subtype' in request.POST:
            if request.POST['select_sp_type'] != "0":
                sp_subtype = Spare_part_sub_type.objects.create(
                    spare_part_sub_type_code=request.POST['add_sp_subtype_code'],
                    spare_part_sub_type_name=request.POST['add_sp_subtype_name'],
                    spare_part_type_id=request.POST['select_sp_type'],
                    create_by=User_login.username,
                    create_date=datetime.date.today())
                sp_subtype.save()
                messages.success(request, "การเพิ่มรายการชนิดอะไหล่เสร็จสมบูรณ์")
            else:
                messages.error(request, "การทำรายการไม่สำเร็จ เนื่องจากกรอกประเภทอะไหล่ไม่ถูกต้อง")
        elif 'edit_spare_part_subtype' in request.POST:
            sp_subtype = Spare_part_sub_type.objects.get(pk=request.POST['edit_spare_part_subtype'])
            sp_subtype.spare_part_sub_type_name = request.POST['set_sp_suptype_name']
            sp_subtype.last_update_by = User_login.username
            sp_subtype.last_update_date = datetime.date.today()
            sp_subtype.save()
            messages.success(request, "การแก้ไขรายการชนิดอะไหล่เสร็จสมบูรณ์")
        elif 'delete_spare_part_subtype' in request.POST:
            sp_subtype = Spare_part_sub_type.objects.get(pk=request.POST['delete_spare_part_subtype'])
            sp_subtype.delete()
            messages.success(request, "การลบรายการชนิดอะไหล่เสร็จสมบูรณ์")

        return redirect('/sparepartmanage/subtype/')

    context = {'User_login': User_login, 'spare_part_subtype_all': spare_part_subtype_all,
               'spare_part_group_all': spare_part_group_all, 'role_and_screen': role_and_screen}
    return render(request, 'spare_part_subtype.html', context)


def spare_part_type(request):
    global User_login
    role_and_screen = Role_Screen.objects.filter(role=UserRole, screen_id='spare_part_type')
    if not role_and_screen.exists():
        return redirect('/')
    spare_part_group_all = Spare_part_group.objects.all()
    sp_type_all = Spare_part_type.objects.all()
    if request.method == "POST":
        if 'add_spare_part_type' in request.POST:
            spare_type = Spare_part_type.objects.create(spare_part_type_code=request.POST['add_sp_type_code'],
                                                        spare_part_type_name=request.POST['add_sp_type_name'],
                                                        create_by=User_login.username,
                                                        create_date=datetime.date.today(),
                                                        spare_part_group_id=request.POST['select_sp_group'])
            spare_type.save()
            messages.success(request, "สร้างรายการสำเร็จ")
        elif 'edit_spare_part_type' in request.POST:
            spare_type = Spare_part_type.objects.get(pk=request.POST['edit_spare_part_type'])
            spare_type.spare_part_type_name = request.POST['set_sp_name']
            spare_type.last_update_by = User_login.username
            spare_type.last_update_date = datetime.date.today()
            spare_type.save()
            messages.success(request, "แก้ไขและบันทึกรายการสำเร็จ")
        elif 'delete_spare_part' in request.POST:
            spare_type = Spare_part_type.objects.get(pk=request.POST['delete_spare_part'])
            spare_type.delete()
            messages.success(request, "ลบรายการสำเร็จ")

        return redirect('/sparepartmanage/type/')

    context = {'User_login': User_login, 'sp_type_all': sp_type_all, 'spare_part_group_all': spare_part_group_all,
               'role_and_screen': role_and_screen}
    return render(request, 'spare_part_type.html', context)


def spare_part_group(request):
    global User_login
    role_and_screen = Role_Screen.objects.filter(role_id=UserRole, screen_id='spare_part_group')
    if not role_and_screen.exists():
        return redirect('/')
    sp_group_all = Spare_part_group.objects.all()
    if request.method == "POST":
        if 'add_spare_part_group' in request.POST:
            spare_group = Spare_part_group.objects.create(spare_part_group_code=request.POST['add_sp_group_code'],
                                                        spare_part_group_name=request.POST['add_sp_group_name'],
                                                        create_by=User_login.username,
                                                        create_date=datetime.date.today())
            spare_group.save()
            messages.success(request, "สร้างรายการสำเร็จ")
        elif 'edit_spare_part_group' in request.POST:
            spare_group = Spare_part_group.objects.get(pk=request.POST['edit_spare_part_group'])
            spare_group.spare_part_group_name = request.POST['set_sp_group_name']
            spare_group.last_update_by = User_login.username
            spare_group.last_update_date = datetime.date.today()
            spare_group.save()
            messages.success(request, "แก้ไขและบันทึกรายการสำเร็จ")
        elif 'delete_spare_part' in request.POST:
            spare_group = Spare_part_group.objects.get(pk=request.POST['delete_spare_part'])
            spare_group.delete()
            messages.success(request, "ลบรายการสำเร็จ")

        return redirect('/sparepartmanage/group/')

    context = {'User_login': User_login, 'sp_group_all': sp_group_all, 'role_and_screen': role_and_screen}
    return render(request, 'spare_part_group.html', context)


@csrf_exempt
def ajax_dropdown_sp_type(request):
    if request.method == 'POST':
        if request.POST['filter_sp_type'] != "":
            sp_type = Spare_part_type.objects.filter(spare_part_group_id=request.POST['filter_sp_type'])
            data = serializers.serialize('json', sp_type)
        else:
            data = [{}]
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def ajax_dropdown_sp_subtype(request):
    if request.method == 'POST':
        if request.POST['filter_sp_subtype'] != "":
            sp_type = Spare_part_sub_type.objects.filter(spare_part_type_id=request.POST['filter_sp_subtype'])
            data = serializers.serialize('json', sp_type)
        else:
            data = [{}]
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def ajax_dropdown_sp(request):
    if request.method == 'POST':
        if request.POST['filter_sp'] != "":
            sp_type = Spare_part.objects.filter(spare_part_sub_type_id=request.POST['filter_sp'])
            data = serializers.serialize('json', sp_type)
        else:
            data = [{}]
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def check_spare_part_group_code(request):
    if request.method == 'POST':
        response_data = {}
        spare_group = Spare_part_group.objects.filter(spare_part_group_code=request.POST['add_code'])
        spare_group_code = None
        try:
            if spare_group.count():
                spare_group_code = True  # alredy exist
            elif len(request.POST['add_code']) == 0:
                spare_group_code = None  # empty input
            else:
                spare_group_code = False  # avialble

        except ObjectDoesNotExist:
            pass
        except Exception as e:
            raise e
        if not spare_group_code:
            response_data["spare_group_code_success"] = True
        else:
            response_data["spare_group_code_success"] = False
        if spare_group_code is None:
            response_data["spare_group_code_empty"] = True
        return JsonResponse(response_data)


@csrf_exempt
def check_spare_part_type_code(request):
    if request.method == 'POST':
        response_data = {}
        spare_type = Spare_part_type.objects.filter(spare_part_type_code=request.POST['add_code'], spare_part_group_id=request.POST['group_code'])
        if spare_type.count():
            spare_type_code = True  # alredy exist
        else:
            spare_type_code = False  # avialble
        if not spare_type_code:
            response_data["spare_type_code_success"] = True
        else:
            response_data["spare_type_code_success"] = False
        return JsonResponse(response_data)


@csrf_exempt
def check_spare_part_subtype_code(request):
    if request.method == 'POST':
        response_data = {}
        spare_subtype = Spare_part_sub_type.objects.filter(spare_part_sub_type_code=request.POST['add_subtype_code'], spare_part_type_id=request.POST['add_sp_type'])
        if spare_subtype.count():
            spare_subtype_code = True  # alredy exist
        else:
            spare_subtype_code = False  # avialble

        if not spare_subtype_code:
            response_data["spare_subtype_code_success"] = True
        else:
            response_data["spare_subtype_code_success"] = False
        return JsonResponse(response_data)


def machine_and_spare_part(request):
    global User_login
    role_and_screen = Role_Screen.objects.filter(role_id=UserRole, screen_id='machine_spare_part')
    if not role_and_screen.exists():
        return redirect('/')
    dict_mch_sp = {}
    user_org = User_login.org.org_line.all()
    machine = Machine.objects.filter(line__in=user_org)
    mch_and_sp_all = Machine_sparepart.objects.filter(machine__in=machine)
    spare_part_group_all = Spare_part_group.objects.all()
    spare_part_all = Spare_part.objects.all()

    if request.method == "POST":
        if "add_mch_and_sp" in request.POST:
            mch_sp_check_exists = Machine_sparepart.objects.filter(machine_id=request.POST["add_mch_and_sp"], spare_part_id=request.POST["select_sp_name"])

            if request.POST["select_sp_name"] == "0":
                messages.error(request, "การทำรายการผิดพลาด กรุณาระบุอะไหล่")
            elif not mch_sp_check_exists.exists():
                mch_and_sp = Machine_sparepart.objects.create(machine_id=request.POST["add_mch_and_sp"],
                                                              spare_part_id=request.POST["select_sp_name"])
                mch_and_sp.save()
            else:
                messages.error(request, "การทำรายการผิดพลาด เครื่องจักรนี้ มีอะไหล่นี้แล้ว")
        elif "delete_spare_part" in request.POST:
            mch_and_sp = Machine_sparepart.objects.filter(machine_id=request.POST['delete_spare_part'],
                                                          spare_part_id=request.POST['select_delete_spare_part'])
            mch_and_sp.delete()
        elif "setting" in request.POST:
            mch_and_sp = Machine_sparepart.objects.get(machine_id=request.POST['select_machine'],
                                                       spare_part_id=request.POST['select_spare_part'])

            mch_and_sp.last_mtnchng_hour = request.POST['last_mtn_change'] if request.POST['last_mtn_change'] != "" else None
            mch_and_sp.mtnchng_life_hour = request.POST['life_mtn_hour'] if request.POST['life_mtn_hour'] != "" else None
            mch_and_sp.next_mtnchng_hour = request.POST['next_mtn_change'] if request.POST['next_mtn_change'] != "" else None
            mch_and_sp.last_mtnchk_hour = request.POST['last_mtn_check'] if request.POST['last_mtn_check'] != "" else None
            mch_and_sp.mtnchk_life_hour = request.POST['life_check_hour'] if request.POST['life_check_hour'] != "" else None
            mch_and_sp.next_mtnchk_hour = request.POST['next_mtn_check'] if request.POST['next_mtn_check'] != "" else None
            mch_and_sp.save()

        return redirect('/machinemanage/machine_spare_part/')

    for mch in machine:
        dict_mch_sp[mch] = []
    for mch_sp in mch_and_sp_all:
        dict_mch_sp[mch_sp.machine].append(mch_sp.spare_part)

    context = {'User_login': User_login,
               'mch_and_sp_all': mch_and_sp_all, 'dict_mch_sp': dict_mch_sp, 'spare_part_all': spare_part_all,
               'role_and_screen': role_and_screen, 'spare_part_group_all': spare_part_group_all, 'machine_all': machine}
    return render(request, 'machine&spare_part.html', context)


def maintenance_job(request):

    role_and_screen = Role_Screen.objects.filter(role_id=UserRole, screen_id='maintenance_job')
    if not role_and_screen.exists():
        return redirect('/')

    mch_sp_not_gen = Machine_sparepart.objects.filter(gen_mtnchng_date__isnull=True, gen_mtnchk_date__isnull=True)

    for mch_sp in mch_sp_not_gen:
        if mch_sp.machine.machine_hour:
            # Change Maintenance
            if mch_sp.last_mtnchng_hour and mch_sp.mtnchng_life_hour:
                if mch_sp.machine.machine_hour >= mch_sp.last_mtnchng_hour + mch_sp.mtnchng_life_hour:
                    mch_sp.gen_mtnchng_date = datetime.date.today()
                    mch_sp.save()
                    main_job = Maintenance_job.objects.create(job_gen_date=datetime.date.today(),
                                                              job_mch_sp_id=mch_sp.pk,
                                                              job_status="รอการมอบหมาย")
                    main_job.save()
                    continue
            elif mch_sp.next_mtnchng_hour:
                if mch_sp.machine.machine_hour >= mch_sp.next_mtnchng_hour:
                    mch_sp.gen_mtnchng_date = datetime.date.today()
                    mch_sp.save()
                    main_job = Maintenance_job.objects.create(job_gen_date=datetime.date.today(),
                                                              job_mch_sp_id=mch_sp.pk,
                                                              job_status="รอการมอบหมาย")
                    main_job.save()
                    continue
            # Checking Maintenance
            if mch_sp.last_mtnchk_hour and mch_sp.mtnchk_life_hour:
                if mch_sp.machine.machine_hour >= mch_sp.last_mtnchk_hour + mch_sp.mtnchk_life_hour:
                    mch_sp.gen_mtnchk_date = datetime.date.today()
                    mch_sp.save()
                    main_job = Maintenance_job.objects.create(job_gen_date=datetime.date.today(),
                                                              job_mch_sp_id=mch_sp.pk,
                                                              job_status="รอการมอบหมาย")
                    main_job.save()
                    continue
            elif mch_sp.next_mtnchk_hour:
                if mch_sp.machine.machine_hour >= mch_sp.next_mtnchk_hour:
                    mch_sp.gen_mtnchk_date = datetime.date.today()
                    mch_sp.save()
                    main_job = Maintenance_job.objects.create(job_gen_date=datetime.date.today(),
                                                              job_mch_sp_id=mch_sp.pk,
                                                              job_status="รอการมอบหมาย")
                    main_job.save()
                    continue

    if request.method == "POST":
        if "assign_submit" in request.POST:
            if request.POST.getlist('assign_list[]') != "":
                for job_pk in request.POST.getlist('assign_list[]'):
                    job = Maintenance_job.objects.get(pk=job_pk)
                    if job.job_status == 'รอการอนุมัติงาน' or job.job_status == 'งานเสร็จสิ้น':
                        messages.error(request, 'ไม่สามารถมอบหมายงานได้ เนื่องจากงานอยู่ในสถานะรอการอนุมัติงานแล้วหรืองานเสร็จสิ้น')
                        continue
                    job.job_assign_user_id = User_login.pk
                    job.job_response_user_id = request.POST['user_response'] if request.POST['user_response'] != "" else None
                    job.job_assign_date = datetime.date.today()
                    job.job_status = "รอการดำเนินงาน" if request.POST['user_response'] != "" else "รอการมอบหมาย"
                    job.save()
            return redirect('/preventive/plan')

        elif "set_maintenance_data" in request.POST:
            mch_and_sp = Machine_sparepart.objects.get(pk=request.POST['set_maintenance_data'])
            mch_and_sp.last_mtnchng_hour = request.POST['last_mtn_change'] if request.POST['last_mtn_change'] != "" else None
            mch_and_sp.mtnchng_life_hour = request.POST['life_mtn_hour'] if request.POST['life_mtn_hour'] != "" else None
            mch_and_sp.next_mtnchng_hour = request.POST['next_mtn_change'] if request.POST['next_mtn_change'] != "" else None
            mch_and_sp.last_mtnchk_hour = request.POST['last_mtn_check'] if request.POST['last_mtn_check'] != "" else None
            mch_and_sp.mtnchk_life_hour = request.POST['life_check_hour'] if request.POST['life_check_hour'] != "" else None
            mch_and_sp.next_mtnchk_hour = request.POST['next_mtn_check'] if request.POST['next_mtn_check'] != "" else None
            mch_and_sp.save()
            return redirect('/preventive/plan')

    maintenance_job_gen = Maintenance_job.objects.all()

    context = {'User_login': User_login, 'maintenance_job_gen': maintenance_job_gen}
    return render(request, 'maintenance_job.html', context)


def machine_capacity(request):
    global User_login, UserRole
    role_and_screen = Role_Screen.objects.filter(role_id=UserRole, screen_id='machine_capacity')
    if not role_and_screen.exists():
        return redirect('/')
    if request.method == "POST":
        if 'Add_machine_capacity' in request.POST:
            mch_capacity = Machine_capacity.objects.filter(machine=request.POST['add_mch'],
                                                           product=request.POST['add_product'])
            if not mch_capacity.exists():
                create_mch_capacity = Machine_capacity.objects.create(
                    machine_id=request.POST['add_mch'],
                    product_id=request.POST['add_product'],
                    rm_name=request.POST['add_rm_name'],
                    rm_batch_size=request.POST['add_rm_batch_size'],
                    rm_unit=request.POST['add_rm_batch_unit'],
                    fg_batch_size=request.POST['add_fg_batch_size'],
                    fg_batch_time=request.POST['add_fg_batch_time'],
                    fg_capacity=request.POST['add_fg_capacity']
                )
                create_mch_capacity.save()
            else:
                messages.info(request, 'รายการเครื่องจักรและผลิตภัณฑ์นี้มีข้อมูลแล้ว ไม่สามารถทำการเพิ่มรายการได้')
        elif 'Edit_mch_capacity' in request.POST:
            edit_mch_cap = Machine_capacity.objects.get(pk=request.POST['Edit_mch_capacity'])
            edit_mch_cap.rm_name = request.POST['set_rm_name']
            edit_mch_cap.rm_batch_size = request.POST['set_rm_batch_size']
            edit_mch_cap.rm_unit = request.POST['set_rm_batch_unit']
            edit_mch_cap.fg_batch_size = request.POST['set_fg_batch_size']
            edit_mch_cap.fg_batch_time = request.POST['set_fg_batch_time']
            edit_mch_cap.fg_capacity = request.POST['set_fg_capacity']
            edit_mch_cap.save()
        elif 'delete_machine_capacity' in request.POST:
            delete_machine_capacity = Machine_capacity.objects.get(pk=request.POST['delete_machine_capacity'])
            delete_machine_capacity.delete()

        return redirect('/machinemanage/capacity/')

    mch_capacity_all = Machine_capacity.objects.all()
    production_line = Production_line.objects.all()
    context = {'User_login': User_login, 'mch_capacity_all': mch_capacity_all, 'production_line': production_line, 'role_and_screen':role_and_screen}
    return render(request, 'machine_capacity.html', context)


def load_machine_from_line(request):
    line_id = request.GET.get('line_id')
    machine = Machine.objects.filter(line_id=line_id).all()
    context = {'machine': machine}
    return render(request, 'ajax_machine.html', context)


def load_product(request):
    line_id = request.GET.get('line_id')
    product_all = Product.objects.filter(line_id=line_id).all()
    context = {'product_all': product_all}
    return render(request, 'ajax_product.html', context)


@csrf_exempt
def check_machine_product(request):
    if request.method == 'POST':
        try:
            response_data = {}
            machine_product = Machine_capacity.objects.filter(machine_id=request.POST['mch_id'],
                                                              product_id=request.POST['product_id'])
            machine_product_code = None
            try:
                if machine_product.count():
                    machine_product_code = True  # alredy exist
                elif len(request.POST['mch_id']) == 0 or len(request.POST['product_id']) == 0:
                    machine_product_code = None  # empty input
                else:
                    machine_product_code = False  # avialble

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e
            if not machine_product_code:
                response_data["data_code_success"] = True
            else:
                response_data["data_code_success"] = False
            if machine_product_code is None:
                response_data["data_code_empty"] = True
        except ValueError:
            pass
        return JsonResponse(response_data)


def document_create1(request):
    from docx import Document
    from docx.shared import Pt

    line_id = Machine.objects.filter(machine_id__in=machine_id).order_by('line_id').values('line_id').distinct()
    list_production_line = Production_line.objects.filter(pid__in=line_id).order_by('production_line')
    document = Document()
    for line in list_production_line:
        document.add_heading(f'Production Line {line.production_line}', 0)

        document.add_paragraph(
            f'สถานที่ตั้งโรงงาน {line.location_site} อาคารที่ {line.location_building} ชั้นที่ {line.location_floor}')
        document.add_paragraph('ผลิตภัณฑ์ที่ผลิต', style='List Bullet')

        list_product = []
        for product in Product.objects.filter(line_id=line.pk):
            capacity_core = Machine_capacity.objects.get(machine_id=Machine.objects.get(line_id=line, machine_core=1), product_id=product)
            list_product.append([str(product.product_name), str(product.product_code), int(capacity_core.fg_capacity)])

        table = document.add_table(rows=1, cols=3)
        table.style = 'Light List Accent 3'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Product Name'
        hdr_cells[1].text = 'Product Code'
        hdr_cells[2].text = 'Product Capacity'
        for name, code, capacity in list_product:
            row_cells = table.add_row().cells
            row_cells[0].text = str(name)
            row_cells[1].text = str(code)
            row_cells[2].text = str(capacity)

        # document.add_heading('เครื่องจักร', level=1)
        machine_in_line = Machine.objects.filter(line_id=line, machine_id__in=machine_id).order_by('machine_production_line_code')
        for mch in machine_in_line:

            document.add_heading(f'ชื่อเครื่องจักร : {mch.machine_name}', level=1)
            document.add_paragraph(' ')
            # run = document.add_paragraph(f'{mch.machine_name}', style='Intense Quote').add_run()
            # font = run.font
            # font.size = Pt(20)
            document.add_paragraph('ข้อมูลเครื่องจักร', style='List Bullet')

            records = (
                ('Machine Brand', mch.machine_brand),
                ('Machine Model', mch.machine_model),
                ('Machine Serial', mch.serial_id),
                ('Machine Type', mch.mch_type),
                ('Machine Subtype', mch.sub_type),
                ('Machine Production Line', mch.line),
                ('Machine Line Code', mch.machine_production_line_code),
                ('Machine Name', mch.machine_name),
                ('Machine Load Capacity', str(mch.machine_load_capacity) + " " + str(mch.machine_load_capacity_unit)),
                ('Machine Power', str(mch.machine_power_use_kwatt_per_hour)+" KWatt/Hour"),
                ('Machine Installed Date', mch.machine_installed_datetime),
                ('Machine Start Date', mch.machine_start_use_datetime),
                ('Machine Hours', str(mch.machine_hour)),
                ('Machine Supplier', mch.machine_supplier_code),
                ('Machine Supplier Name', str(mch.machine_supplier_name)+" (ติดต่อ : "+str(mch.machine_supplier_contact)+" )"),
                ('Engineer Emp in Charge', "รหัสพนักงาน :"+str(mch.machine_eng_emp_id)+" ชื่อ: "+str(mch.machine_eng_emp_name)+" (ติดต่อ : "+str(mch.machine_eng_emp_contact)+" )"),
                ('Production Emp in Charge', "รหัสพนักงาน :"+str(mch.machine_pro_emp_id)+" ชื่อ: "+str(mch.machine_pro_emp_name)+" (ติดต่อ : "+str(mch.machine_pro_emp_contact)+" )")
            )

            table = document.add_table(rows=1, cols=2)
            table.style = 'Light List Accent 1'
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = 'Title'
            hdr_cells[1].text = 'Specification'
            for title, data in records:
                row_cells = table.add_row().cells
                row_cells[0].text = title
                row_cells[1].text = str(data)

            # mch_and_spare = Machine_and_spare_part.objects.filter(machine_id=mch.machine_id)
            # if mch_and_spare.exists():
            #     document.add_paragraph(' ')
            #     document.add_paragraph('ข้อมูลอะไหล่', style='List Bullet')
            #     list_table = []
            #     for mch_spare_part in mch_and_spare:
            #         list_table.append([str(mch_spare_part.spare_part), str(mch_spare_part.spare_part.spare_part_code), str(mch_spare_part.spare_part.spare_part_model)])
            #     table = document.add_table(rows=1, cols=3)
            #     table.style = 'Light List Accent 2'
            #     hdr_cells = table.rows[0].cells
            #     hdr_cells[0].text = 'Spare Part Name'
            #     hdr_cells[1].text = 'Spare Part Code'
            #     hdr_cells[2].text = 'Spare Part Model'
            #     for name, code, model in list_table:
            #         row_cells = table.add_row().cells
            #         row_cells[0].text = name
            #         row_cells[1].text = code
            #         row_cells[2].text = model
            #
            mch_capacity = Machine_capacity.objects.filter(machine_id=mch.machine_id)
            if mch_capacity.exists():
                document.add_paragraph(' ')
                document.add_paragraph('ข้อมูลกำลังการผลิต', style='List Bullet')
                list_table = []
                for mch_cap in mch_capacity:
                    list_table.append([str(mch_cap.product.product_name), str(mch_cap.product.product_code), str(int(mch_cap.fg_capacity))])
                table = document.add_table(rows=1, cols=3)
                table.style = 'Light List Accent 3'
                hdr_cells = table.rows[0].cells
                hdr_cells[0].text = 'Product Name'
                hdr_cells[1].text = 'Product Code'
                hdr_cells[2].text = 'FG Capacity/Hour'
                for name, code, capacity in list_table:
                    row_cells = table.add_row().cells
                    row_cells[0].text = name
                    row_cells[1].text = code
                    row_cells[2].text = capacity

            if mch != machine_in_line.last():
                document.add_page_break()

        if line != list_production_line.last():
            document.add_page_break()

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename=machine_data.docx'
    document.save(response)

    return response


def load_selected_lines(request):
    input_line = request.GET['selected_lines']
    change_type = ast.literal_eval(input_line)
    machine_list = Machine.objects.filter(line__in=change_type)
    data = serializers.serialize('json', machine_list)
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def load_role_screen(request):
    role_id = request.POST['role_id']
    rs = Role_Screen.objects.filter(role_id=role_id).values_list('screen_id', flat="True")
    screen = Screen.objects.exclude(screen_id__in=rs)
    data = serializers.serialize('json', screen)
    return HttpResponse(data, content_type="application/json")


def document2_excel(request):

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Spare_Part.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Machines Data', cell_overwrite_ok=True)
    # Style
    style_title = xlwt.easyxf('font: bold True; align: vert centre, horiz centre')
    style_merge = xlwt.easyxf('align: vert top')

    # Set column title
    for i in range(9):
        ws.col(i).width = 4600

    ws.write_merge(1, 1, 0, 8, "รายงานข้อมูลอะไหล่", style_title)
    ws.write_merge(3, 3, 0, 5, "อะไหล่", style_title)
    ws.write_merge(3, 3, 6, 8, "เครื่องจักร", style_title)

    cols = ["กลุ่ม", "ประเภท", "ชนิด", "ชื่อ", "แบรนด์", "โมเดล", "ไลน์ผลิต", "ชื่อ", "รหัสเครื่องจักร"]
    for index, col in enumerate(cols):
        ws.write(4, index, col, style_title)

    query_sp = Spare_part.objects.all().order_by('spare_part_group_id', 'spare_part_type_id', 'spare_part_sub_type_id')
    list_sp = query_sp.values_list('spare_part_group__spare_part_group_name', 'spare_part_type__spare_part_type_name',
                                   'spare_part_sub_type__spare_part_sub_type_name', 'spare_part_name', 'spare_part_brand',
                                   'spare_part_model')

    list_sp_transpose = list(map(list, (zip(*list_sp))))
    row_index = 5
    for col_index, col_list_data in enumerate(list_sp_transpose):
        row_reset = 0
        for col_data, len_merge in dict(Counter(col_list_data)).items():
            ws.write_merge(row_index, row_index+len_merge-1, col_index, col_index, col_data, style_merge)
            row_index += len_merge
            row_reset += len_merge
        row_index -= row_reset

    wb.save(response)

    return response


def spare_part_and_machine(request):
    global User_login, UserRole
    role_and_screen = Role_Screen.objects.filter(role_id=UserRole, screen_id='machine_capacity')
    if not role_and_screen.exists():
        return redirect('/')
    dict_mch_sp = {}
    user_org = User_login.org.org_line.all()
    machine = Machine.objects.filter(line__in=user_org)
    sp_and_mch_all = Machine_sparepart.objects.filter(machine__in=machine)
    spare_part_all = Spare_part.objects.all()
    machine_type_all = Machine_type.objects.all()

    if request.method == "POST":
        if "add_sp_and_mch" in request.POST:
            try:
                sp_and_mch = Machine_sparepart.objects.create(machine_id=request.POST['select_mch'], spare_part_id=request.POST['add_sp_and_mch'])
                sp_and_mch.save()
                messages.success(request, 'บันทึกรายการเครื่องจักรออกจากอะไหล่สำเร็จ')
            except:
                messages.error(request, 'ลบรายการเครื่องจักรออกจากอะไหล่ไม่สำเร็จ')
        elif "delete_machine" in request.POST:
            try:
                sp_and_mch = Machine_sparepart.objects.filter(machine_id=request.POST['select_delete_machine'], spare_part_id=request.POST['delete_machine'])
                sp_and_mch.delete()
                messages.success(request, 'ลบรายการเครื่องจักรออกจากอะไหล่สำเร็จ')
            except:
                messages.error(request, 'ลบรายการเครื่องจักรออกจากอะไหล่ไม่สำเร็จ')

        return redirect('/sparepartmanage/spare_pare_machine/')

    for sp in spare_part_all:
        dict_mch_sp[sp] = []
    for sp_mch in sp_and_mch_all:
        dict_mch_sp[sp_mch.spare_part].append(sp_mch.machine)

    context = {'role_and_screen': role_and_screen, 'spare_part_all': spare_part_all, 'dict_mch_sp': dict_mch_sp, 'user_org': user_org,
               'machine_type_all': machine_type_all, 'User_login': User_login}
    return render(request, 'spare_and_machine.html', context)


@csrf_exempt
def load_machine(request):
    sp_id = request.POST['spID']
    line_id = request.POST['lineID']
    sub_type_id = request.POST['subtypeID']
    machine_spare = Machine_sparepart.objects.filter(spare_part_id=sp_id).values_list('machine')
    machine = Machine.objects.filter(line_id=line_id, sub_type_id=sub_type_id).exclude(pk__in=machine_spare)
    data = serializers.serialize('json', machine)
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def load_machine_sparepart(request):
    machine_id = request.POST['machine_id']
    mch_sp = Machine_sparepart.objects.filter(machine_id=machine_id).values('spare_part_id')
    spare_part_of_mch = Spare_part.objects.filter(pk__in=mch_sp)
    data = serializers.serialize('json', spare_part_of_mch)
    return HttpResponse(data, content_type="application/json")


def maintenance_data(request):
    global User_login
    role_and_screen = Role_Screen.objects.filter(role_id=UserRole, screen_id='maintenance_data')
    if not role_and_screen.exists():
        return redirect('/')
    line_of_user = User_login.org.org_line.all()
    mch_sp_all = Machine_sparepart.objects.filter(machine__line__in=line_of_user)
    if request.method == 'POST':

        if 'prd_mch' in request.POST:
            if request.POST['production_line'] == "0":
                mch_sp_all = Machine_sparepart.objects.filter(machine__line__in=line_of_user)
            elif request.POST['production_line'] != "0" and request.POST['machine'] == "":
                mch_sp_all = Machine_sparepart.objects.filter(machine__line__in=request.POST['production_line'])
            elif request.POST['production_line'] != "0" and request.POST['machine'] != 0:
                mch_sp_all = Machine_sparepart.objects.filter(machine_id=request.POST['machine'])

        elif "set_maintenance_data" in request.POST:
            mch_and_sp = Machine_sparepart.objects.get(pk=request.POST['set_maintenance_data'])
            mch_and_sp.last_mtnchng_hour = request.POST['last_mtn_change'] if request.POST['last_mtn_change'] != "" else None
            mch_and_sp.mtnchng_life_hour = request.POST['life_mtn_hour'] if request.POST['life_mtn_hour'] != "" else None
            mch_and_sp.next_mtnchng_hour = request.POST['next_mtn_change'] if request.POST['next_mtn_change'] != "" else None
            mch_and_sp.last_mtnchk_hour = request.POST['last_mtn_check'] if request.POST['last_mtn_check'] != "" else None
            mch_and_sp.mtnchk_life_hour = request.POST['life_check_hour'] if request.POST['life_check_hour'] != "" else None
            mch_and_sp.next_mtnchk_hour = request.POST['next_mtn_check'] if request.POST['next_mtn_check'] != "" else None
            mch_and_sp.save()
            return redirect('/preventive/data')

    context = {'User_login': User_login, 'line_of_user': line_of_user, 'mch_sp_all': mch_sp_all,
               'menu_job': dict_menu_level[Menu.objects.get(menu_id='preventive_data')], 'menu_assign': Menu.objects.get(menu_id='maintenance_job')}
    return render(request, 'maintenance_data.html', context)


def maintenance_report(request):
    role_and_screen = Role_Screen.objects.filter(role_id=UserRole, screen_id='maintenance_report')
    if not role_and_screen.exists():
        return redirect('/')
    job = Maintenance_job.objects.filter(Q(job_response_user_id=User_login.username) | Q(job_assign_user_id=User_login.username))
    if request.method == "POST":
        if 'report_submit' in request.POST:
            mtn_report = Maintenance_job.objects.get(pk=request.POST['report_submit'])
            mch_sp = Machine_sparepart.objects.get(pk=mtn_report.job_mch_sp_id)
            mtn_report.job_mtn_type = request.POST['mtn_type']
            mtn_report.job_result_type = request.POST['mtn_result']
            mtn_report.job_result_description = request.POST['mtn_result_description'] if request.POST['mtn_result_description'] != "" else None
            mtn_report.job_fix_plan_hour = request.POST['chang_life_hour_sp'] if request.POST['chang_life_hour_sp'] != "" else request.POST['chang_life_hour_pv']
            mtn_report.job_mch_hour = request.POST['machine_hour_sp'] if request.POST['machine_hour_sp'] != "" else request.POST['machine_hour_pv']
            mtn_report.job_plan_hour = request.POST['check_life_hour_sp'] if request.POST['check_life_hour_sp'] != "" else request.POST['check_life_hour_pv']
            mtn_report.job_report_date = datetime.datetime.today()
            mtn_report.problem_cause = request.POST['problem_cause']
            mtn_report.corrective_action = request.POST['corrective_action']
            mtn_report.after_repair = request.POST['after_repair']
            mtn_report.job_status = "รอการอนุมัติงาน"
            mtn_report.equipment_code1 = request.POST['equipment_code1'] if request.POST['equipment_code1'] != "" else None
            mtn_report.equipment_code2 = request.POST['equipment_code2'] if request.POST['equipment_code2'] != "" else None
            mtn_report.equipment_code3 = request.POST['equipment_code3'] if request.POST['equipment_code3'] != "" else None
            mtn_report.equipment_detail1 = request.POST['equipment_detail1'] if request.POST['equipment_detail1'] != "" else None
            mtn_report.equipment_detail2 = request.POST['equipment_detail2'] if request.POST['equipment_detail2'] != "" else None
            mtn_report.equipment_detail3 = request.POST['equipment_detail3'] if request.POST['equipment_detail3'] != "" else None
            mtn_report.equipment_quantity1 = request.POST['equipment_quantity1'] if request.POST['equipment_quantity1'] != "" else None
            mtn_report.equipment_quantity2 = request.POST['equipment_quantity2'] if request.POST['equipment_quantity2'] != "" else None
            mtn_report.equipment_quantity3 = request.POST['equipment_quantity3'] if request.POST['equipment_quantity3'] != "" else None
            mtn_report.equipment_note1 = request.POST['equipment_note1'] if request.POST['equipment_note1'] != "" else None
            mtn_report.equipment_note2 = request.POST['equipment_note2'] if request.POST['equipment_note2'] != "" else None
            mtn_report.equipment_note3 = request.POST['equipment_note3'] if request.POST['equipment_note3'] != "" else None
            mtn_report.job_remark = request.POST['job_remark'] if request.POST['job_remark'] != "" else None
            mtn_report.estimate_cost = request.POST['estimate_cost'] if request.POST['estimate_cost'] != "" else None
            try:
                mtn_report.save()
            except ValueError:
                messages.error(request, 'กรุณากรอกชั่วโมงการเปลี่ยนและชั่วโมงการตรวจสอบของอะไหล่')
                return redirect('/preventive/report')
            # mch_sp.gen_mtnchng_date = None
            # mch_sp.gen_mtnchk_date = None
            if request.POST['mtn_type'] == "change" or request.POST['mtn_type'] == "repair":
                mch_sp.last_mtnchk_hour = mtn_report.job_mch_hour
                mch_sp.last_mtnchng_hour = mtn_report.job_mch_hour
            elif request.POST['mtn_type'] == "checking":
                mch_sp.last_mtnchk_hour = mtn_report.job_mch_hour
            mch_sp.mtnchng_life_hour = mtn_report.job_fix_plan_hour
            mch_sp.mtnchk_life_hour = mtn_report.job_plan_hour
            if mch_sp.mtnchk_life_hour:
                mch_sp.next_mtnchk_hour = int(mch_sp.last_mtnchk_hour) + int(mch_sp.mtnchk_life_hour)
            if mch_sp.mtnchng_life_hour:
                mch_sp.next_mtnchng_hour = int(mch_sp.last_mtnchng_hour) + int(mch_sp.mtnchng_life_hour)
            mch_sp.save()

        elif "report_update" in request.POST:
            mtn_report = Maintenance_job.objects.get(pk=request.POST['report_update'])
            mch_sp = Machine_sparepart.objects.get(pk=mtn_report.job_mch_sp_id)
            mtn_report.job_mtn_type = request.POST['mtn_type']
            mtn_report.job_result_type = request.POST['mtn_result']
            mtn_report.job_result_description = request.POST['mtn_result_description'] if request.POST['mtn_result_description'] != "" else None
            mtn_report.job_fix_plan_hour = request.POST['chang_life_hour_sp'] if request.POST['chang_life_hour_sp'] != "" else request.POST['chang_life_hour_pv']
            mtn_report.job_mch_hour = request.POST['machine_hour_sp'] if request.POST['machine_hour_sp'] != "" else request.POST['machine_hour_pv']
            mtn_report.job_plan_hour = request.POST['check_life_hour_sp'] if request.POST['check_life_hour_sp'] != "" else request.POST['check_life_hour_pv']
            mtn_report.job_report_date = datetime.datetime.today()
            mtn_report.problem_cause = request.POST['problem_cause']
            mtn_report.corrective_action = request.POST['corrective_action']
            mtn_report.after_repair = request.POST['after_repair']
            # mtn_report.job_status = "รอการอนุมัติงาน"
            mtn_report.equipment_code1 = request.POST['equipment_code1'] if request.POST['equipment_code1'] != "" else None
            mtn_report.equipment_code2 = request.POST['equipment_code2'] if request.POST['equipment_code2'] != "" else None
            mtn_report.equipment_code3 = request.POST['equipment_code3'] if request.POST['equipment_code3'] != "" else None
            mtn_report.equipment_detail1 = request.POST['equipment_detail1'] if request.POST['equipment_detail1'] != "" else None
            mtn_report.equipment_detail2 = request.POST['equipment_detail2'] if request.POST['equipment_detail2'] != "" else None
            mtn_report.equipment_detail3 = request.POST['equipment_detail3'] if request.POST['equipment_detail3'] != "" else None
            mtn_report.equipment_quantity1 = request.POST['equipment_quantity1'] if request.POST['equipment_quantity1'] != "" else None
            mtn_report.equipment_quantity2 = request.POST['equipment_quantity2'] if request.POST['equipment_quantity2'] != "" else None
            mtn_report.equipment_quantity3 = request.POST['equipment_quantity3'] if request.POST['equipment_quantity3'] != "" else None
            mtn_report.equipment_note1 = request.POST['equipment_note1'] if request.POST['equipment_note1'] != "" else None
            mtn_report.equipment_note2 = request.POST['equipment_note2'] if request.POST['equipment_note2'] != "" else None
            mtn_report.equipment_note3 = request.POST['equipment_note3'] if request.POST['equipment_note3'] != "" else None
            mtn_report.job_remark = request.POST['job_remark'] if request.POST['job_remark'] != "" else None
            mtn_report.estimate_cost = request.POST['estimate_cost'] if request.POST['estimate_cost'] != "" else None
            mtn_report.save()
            # mch_sp.gen_mtnchng_date = None
            # mch_sp.gen_mtnchk_date = None
            if request.POST['mtn_type'] == "change":
                mch_sp.last_mtnchk_hour = mtn_report.job_mch_hour
                mch_sp.last_mtnchng_hour = mtn_report.job_mch_hour
            elif request.POST['mtn_type'] == "checking":
                mch_sp.last_mtnchk_hour = mtn_report.job_mch_hour
            mch_sp.mtnchng_life_hour = mtn_report.job_fix_plan_hour
            mch_sp.mtnchk_life_hour = mtn_report.job_plan_hour
            if mch_sp.mtnchk_life_hour:
                mch_sp.next_mtnchk_hour = int(mch_sp.last_mtnchk_hour) + int(mch_sp.mtnchk_life_hour)
            if mch_sp.mtnchng_life_hour:
                mch_sp.next_mtnchng_hour = int(mch_sp.last_mtnchng_hour) + int(mch_sp.mtnchng_life_hour)
            mch_sp.save()

        elif "approve_job" in request.POST:
            mtn_report = Maintenance_job.objects.get(pk=request.POST['approve_job'])
            mch_sp = Machine_sparepart.objects.get(pk=mtn_report.job_mch_sp_id)
            mtn_report.is_approve = True if request.POST.get('is_approve', False) else False
            mtn_report.job_approve_date = datetime.datetime.today() if request.POST.get('is_approve', False) else None
            mtn_report.job_status = "งานเสร็จสิ้น" if request.POST.get('is_approve', False) else "รอการอนุมัติงาน"
            mch_sp.gen_mtnchng_date = None
            mch_sp.gen_mtnchk_date = None
            mch_sp.save()
            mtn_report.save()

        return redirect('/preventive/report')

    context = {'User_login': User_login, 'job': job, 'menu_job': dict_menu_level[Menu.objects.get(menu_id='preventive_data')],
               'menu_assign': Menu.objects.get(menu_id='maintenance_job')}
    return render(request, 'maintenance_report.html', context)


def machine_hour_update(request):
    role_and_screen = Role_Screen.objects.filter(role_id=UserRole, screen_id='machine_hour_update')
    if not role_and_screen.exists():
        return redirect('/')

    if request.method == 'POST':
        if 'hour_submit' in request.POST:
            hour_update = request.POST['hour_update']
            if request.POST.get('mch_update[]', False) and request.POST['hour_update']:
                mch_pk = request.POST.getlist('mch_update[]')
                for mch in Machine.objects.filter(pk__in=mch_pk):
                    if mch.machine_hour_update_date == datetime.date.today():
                        mch.machine_hour = mch.machine_hour_last_update + int(hour_update)
                    else:
                        mch.machine_hour_update_date = datetime.date.today()
                        mch.machine_hour_last_update = mch.machine_hour
                        mch.machine_hour += int(hour_update)
                    mch.save()
                return redirect('/preventive/machine')
            # elif not request.POST.get('mch_update[]', False):
            #     return redirect('/preventive/machine')
            else:
                return redirect('/preventive/machine')

    user_org = User_login.org.org_line.all()
    machine_all = Machine.objects.filter(line__in=user_org)

    context = {'User_login': User_login, 'machine_all': machine_all, 'menu_job': dict_menu_level[Menu.objects.get(menu_id='preventive_data')],
               'menu_assign': Menu.objects.get(menu_id='maintenance_job')}
    return render(request, 'machine_hour_update.html', context)


@csrf_exempt
def assign_check_user(request):
    machine_id = request.POST['machine_id']
    mch_sp = Machine_sparepart.objects.filter(machine_id=machine_id).values('spare_part_id')
    spare_part_of_mch = Spare_part.objects.filter(pk__in=mch_sp)
    data = serializers.serialize('json', spare_part_of_mch)
    return HttpResponse(data, content_type="application/json")


def repair_notice(request):
    global User_login
    role_and_screen = Role_Screen.objects.filter(role_id=UserRole, screen_id='repair_notice')
    if not role_and_screen.exists():
        return redirect('/')
    username = str(User_login.username)
    line_of_user = User_login.org.org_line.all()
    list_repair_notice = Repair_notice.objects.all()
    spare_part_group_all = Spare_part_group.objects.all()
    check_repair_notice = Repair_notice.objects.filter(repair_status='รอการดำเนินงาน')
    for check_rp in check_repair_notice:
        if check_rp.job1:
            if check_rp.job1.job_status != 'งานเสร็จสิ้น':
                continue
        if check_rp.job2:
            if check_rp.job2.job_status != 'งานเสร็จสิ้น':
                continue
        if check_rp.job3:
            if check_rp.job3.job_status != 'งานเสร็จสิ้น':
                continue
        if check_rp.job4:
            if check_rp.job4.job_status != 'งานเสร็จสิ้น':
                continue
        if check_rp.job5:
            if check_rp.job5.job_status != 'งานเสร็จสิ้น':
                continue
        check_rp.repair_status = 'การซ่อมสำเร็จ'
        check_rp.save()
    if request.method == "POST":
        if "create_repair" in request.POST:
            repair_notice_model = Repair_notice.objects.create(
                agency_notifying=request.POST['agency_notifying'],
                use_date=request.POST['use_date'],
                repairer_user=request.POST['repairer_user'],
                repairer_contact=request.POST['repairer_contact'],
                machine_id=request.POST['machine'],
                problem_report=request.POST['problem_report'],
                effect_problem=request.POST['effect_problem'],
                repair_status='รอช่างมายืนยัน'
            )
            repair_notice_model.save()
            messages.success(request, "สร้างรายการสำเร็จ")
            return redirect('repair_notice')
        elif "repair_submit" in request.POST:
            repair_notice_model = Repair_notice.objects.get(pk=request.POST['repair_submit'])
            repair_notice_model.repair_status = 'รอการดำเนินงาน'

            list_check = [request.POST['select_sp_name1'], request.POST['select_sp_name2'], request.POST['select_sp_name3'], request.POST['select_sp_name4'], request.POST['select_sp_name5']]
            list_check = list(filter(lambda i: i != "0", list_check))
            if len(list_check) != len(set(list_check)):
                messages.error(request, "ทำรายการไม่สำเร็จ เนื่องจากเลือกชิ้นส่วนอะไหล่ซ้ำ")
                return redirect('repair_notice')
            if len(list_check) == 0:
                messages.error(request, "ทำรายการไม่สำเร็จ เนื่องจากไม่ได้เลือกชิ้นส่วนอะไหล่")
                return redirect('repair_notice')
            else:
                for sp_id_test in list_check:
                    try:
                        Machine_sparepart.objects.get(machine_id=repair_notice_model.machine_id, spare_part_id=sp_id_test)
                    except ObjectDoesNotExist:
                        messages.error(request, "ทำรายการไม่สำเร็จ เนื่องจากเครื่องจักรยังไม่ได้เชื่อมต่อกับอะไหล่")
                        return redirect('repair_notice')

            if request.POST.get('select_sp_name1', False):
                if request.POST['select_sp_name1'] != '0':
                    repair_notice_model.spare_part_1_id = request.POST['select_sp_name1']
                    mch_sp1 = Machine_sparepart.objects.get(machine_id=repair_notice_model.machine_id, spare_part_id=request.POST['select_sp_name1'])
                    mch_sp1.gen_mtnchng_date = datetime.date.today()
                    mch_sp1.save()
                    job_repair1 = Maintenance_job.objects.create(job_no=randomJobRepairOrder(),
                                                                 job_gen_date=datetime.date.today(),
                                                                 job_mch_sp_id=mch_sp1.pk,
                                                                 job_status="รอการมอบหมาย",
                                                                 job_mtn_type="repair",
                                                                 job_gen_user_id=username)
                    repair_notice_model.job1_id = job_repair1.pk
                    job_repair1.save()
            if request.POST.get('select_sp_name2', False):
                if request.POST['select_sp_name2'] != '0':
                    repair_notice_model.spare_part_2_id = request.POST['select_sp_name2']
                    mch_sp2 = Machine_sparepart.objects.get(machine_id=repair_notice_model.machine_id, spare_part_id=request.POST['select_sp_name2'])
                    mch_sp2.gen_mtnchng_date = datetime.date.today()
                    mch_sp2.save()
                    job_repair2 = Maintenance_job.objects.create(job_no=randomJobRepairOrder(),
                                                                 job_gen_date=datetime.date.today(),
                                                                 job_mch_sp_id=mch_sp2.pk,
                                                                 job_status="รอการมอบหมาย",
                                                                 job_mtn_type="repair",
                                                                 job_gen_user_id=username)
                    repair_notice_model.job2_id = job_repair2.pk
                    job_repair2.save()
            if request.POST.get('select_sp_name3', False):
                if request.POST['select_sp_name3'] != '0':
                    repair_notice_model.spare_part_3_id = request.POST['select_sp_name3']
                    mch_sp3 = Machine_sparepart.objects.get(machine_id=repair_notice_model.machine_id, spare_part_id=request.POST['select_sp_name3'])
                    mch_sp3.gen_mtnchng_date = datetime.date.today()
                    mch_sp3.save()
                    job_repair3 = Maintenance_job.objects.create(job_no=randomJobRepairOrder(),
                                                                 job_gen_date=datetime.date.today(),
                                                                 job_mch_sp_id=mch_sp3.pk,
                                                                 job_status="รอการมอบหมาย",
                                                                 job_mtn_type="repair",
                                                                 job_gen_user_id=username)
                    repair_notice_model.job3_id = job_repair3.pk
                    job_repair3.save()
            if request.POST.get('select_sp_name4', False):
                if request.POST['select_sp_name4'] != '0':
                    repair_notice_model.spare_part_4_id = request.POST['select_sp_name4']
                    mch_sp4 = Machine_sparepart.objects.get(machine_id=repair_notice_model.machine_id, spare_part_id=request.POST['select_sp_name4'])
                    mch_sp4.gen_mtnchng_date = datetime.date.today()
                    mch_sp4.save()
                    job_repair4 = Maintenance_job.objects.create(job_no=randomJobRepairOrder(),
                                                                 job_gen_date=datetime.date.today(),
                                                                 job_mch_sp_id=mch_sp4.pk,
                                                                 job_status="รอการมอบหมาย",
                                                                 job_mtn_type="repair",
                                                                 job_gen_user_id=username)
                    repair_notice_model.job4_id = job_repair4.pk
                    job_repair4.save()
            if request.POST.get('select_sp_name5', False):
                if request.POST['select_sp_name5'] != '0':
                    repair_notice_model.spare_part_5_id = request.POST['select_sp_name5'] if request.POST['select_sp_name5'] != '0' else None
                    mch_sp5 = Machine_sparepart.objects.get(machine_id=repair_notice_model.machine_id, spare_part_id=request.POST['select_sp_name5'])
                    mch_sp5.gen_mtnchng_date = datetime.date.today()
                    mch_sp5.save()
                    job_repair5 = Maintenance_job.objects.create(job_no=randomJobRepairOrder(),
                                                                 job_gen_date=datetime.date.today(),
                                                                 job_mch_sp_id=mch_sp5.pk,
                                                                 job_status="รอการมอบหมาย",
                                                                 job_mtn_type="repair",
                                                                 job_gen_user_id=username)
                    repair_notice_model.job5_id = job_repair5.pk
                    job_repair5.save()

            repair_notice_model.save()
            messages.success(request, "บันทึกรายการสำเร็จ")
            return redirect('repair_notice')

    context = {'line_of_user': line_of_user, 'User_login': User_login, 'list_repair_notice': list_repair_notice, 'spare_part_group_all': spare_part_group_all,
               'menu_job': dict_menu_level[Menu.objects.get(menu_id='preventive_data')], 'menu_assign': Menu.objects.get(menu_id='maintenance_job')}
    return render(request, 'repair_notice.html', context)
