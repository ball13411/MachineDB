from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
import Machine_Management
import datetime
import django
from .forms import *
from .filters import MachineFilter
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

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
            try:  # Try connect username and passwd on Model
                user = User.objects.get(username=username, password=password)
                now = datetime.datetime.now()  # Call Datetime now
                datenow = datetime.date.today()  # Call Date now
                user.last_login_date = now  # Update last_login to now
                user.save()  # Save Update
                if user.start_date > datenow:  # Check StartDate and DateNow
                    messages.info(request,
                                  f'ชื่อผู้ใช้นี้ยังไม่สามารถเข้าสู่ระบบได้ สามารถเข้าได้ในวันที่ {user.start_date}')
                    return redirect('/')
                elif datenow > user.expired_date:  # Check Expired Date if expired link to resetpassword
                    messages.info(request, 'รหัสผ่านหมดอายุแล้ว กรุณาทำการ Reset Password')
                    return redirect('/')
                if user is not None:  # Check login User                    # Set user login
                    User_login = user
                    UserRole = str(User_login.role)
                    return redirect('/home')
            except Machine_Management.models.User.DoesNotExist:  # Message Wrong username or password
                messages.info(request, "username หรือ password ไม่ถูกต้อง")
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
            now = datetime.datetime.now()   # Call Datetime now
            user = User.objects.get(username=username)  # Query user
            user.user_active = request.POST.get('set_user_status', False)
            user.update_date = now  # Update UpdateDate to now
            user.update_by = str(User_login.username)  # Update UserUpdate of UserSelect
            org = Organization.objects.get(org_id=update_org)
            user.org = org
            role = Role.objects.get(role_id=update_role)  # Get RoleID of UserSelect
            user.role = role  # Update Role of UserSelect
            user.save()  # Save all Update
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
                    messages.info(request, "มีผู้ใช้ชื่อ Username นี้แล้ว")  # Show Message Username is exists
                elif User.objects.filter(email=email).exists():  # Query email is exists in model(DB)
                    messages.info(request, "มีผู้ใช้ Email นี้แล้ว")  # Show Message Email is exists
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
                    user.save()  # Save User
                    # return redirect('/usermanage')
            else:
                messages.info(request, "รหัสผ่านไม่ตรงกัน กรุณาตรวจสอบใหม่")  # Show Message Password != ConPassword
        # Button Sign Out
        elif 'signout' in request.POST:
            User_login = None  # Set User_login is None
        # Form DeleteUser (icon delete)
        elif 'deleteuser' in request.POST:
            username = request.POST['deleteuser']  # get var('username') from HTML
            user = User.objects.get(username=username)  # Query Username
            user.delete()  # Delete User from Model(DB)
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
                    return redirect('/')
                else:  # NewPassword != ConPassword
                    messages.info(request, 'รหัสผ่านใหม่และรหัสผ่านยืนยันไม่ตรงกัน')
            else:  # OldPassword != NewPassword
                messages.info(request, 'รหัสผ่านเก่าต้องไม่ตรงกับรหัสผ่านใหม่')
        except Machine_Management.models.User.DoesNotExist:  # Failed Connect User in model(DB)
            messages.info(request, 'ชื่อผู้ใช้และรหัสผ่านเก่าไม่ถูกต้อง')
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
        elif 'Addrole' in request.POST:
            role_id = request.POST['add_roleid']  # Get var('role id') from HTML
            role_name = request.POST['add_rolename']  # Get var('role name') from HTML
            try:
                role = Role.objects.create(role_id=role_id, role_name=role_name)
                role.save()
            except django.db.utils.IntegrityError:
                messages.info(request, "มีชื่อ Role ID นี้แล้ว กรุณาตั้งใหม่")
        elif 'deleterole' in request.POST:
            role_id = request.POST['deleterole']  # Get var('role id') from HTML
            role = Role.objects.get(role_id=role_id)
            role.delete()
        elif 'signout' in request.POST:
            User_login = None  # Set User_login is None
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
            else:
                messages.info(request, "มีชื่อ Screen ID นี้แล้ว กรุณาตั้งใหม่")
        elif 'deletescreen' in request.POST:
            del_screen_id = request.POST['deletescreen']
            screen = Screen.objects.get(screen_id=del_screen_id)
            screen.delete()
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
            elif not Role_Screen.objects.filter(role_id=request.POST['set_rs_role'], screen_id=request.POST['set_rs_screen']).exists():
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
            else:
                messages.info(request, 'Role และ Screen นี้มีแล้ว!! ไม่สามารถสร้างซ้ำได้')
        elif 'Addrolescreen' in request.POST:
            if not Role_Screen.objects.filter(role_id=request.POST['add_rs_role'], screen_id=request.POST['add_rs_screen']).exists():
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
            else:
                messages.info(request, 'Role และ Screen นี้มีแล้ว!! ไม่สามารถสร้างซ้ำได้')
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


def machine_register(request):
    global User_login, UserRole, dict_menu_level
    if not Role_Screen.objects.filter(role=UserRole, screen_id='mch_register').exists():
        return redirect('/')
    user_org = User_login.org.org_line.all()
    form = MachineForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = MachineForm()
        messages.info(request, 'Register Success')
    UserRole = str(User_login.role)
    context = {
        'form': form, 'User_login': User_login, 'UserRole': UserRole, 'List_user_Screen': List_user_Screen,
        'dict_menu_level': dict_menu_level.items(), 'lines': user_org
    }
    return render(request, 'machine_register.html', context)


def machine_data(request):
    global User_login, UserRole, dict_menu_level, User_org_machine_line
    if not Role_Screen.objects.filter(role=UserRole, screen_id='mch_data').exists():
        return redirect('/')
    user_org = User_login.org.org_line.all()
    User_org_machine_line = Machine.objects.filter(line__in=user_org)
    context = {
        'User_login': User_login, 'UserRole': UserRole,
        'dict_menu_level': dict_menu_level.items(), 'User_org_machine_line': User_org_machine_line, 'line_of_user': user_org
    }
    return render(request, 'machine_data.html', context)


def test(request):
    mch = Machine.objects.all()
    # form = UserForm(request.POST or None)
    form = ProductLineForm(request.POST or None)
    if 'toggle' in request.POST:
        a = request.POST.get('toggle', False)
        print(type(a),a)
    if form.is_valid():
        form.save()
        form = UserForm()
    context = {'form': form, 'mch': mch}
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
            else:
                messages.info(request, "มีการใช้ Menu ID นี้แล้ว กรุณาตั้งชื่อใหม่")
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
        elif 'deletemenu' in request.POST:
            del_menu_id = request.POST['deletemenu']
            menu_del = Menu.objects.get(menu_id=del_menu_id)
            menu_del.delete()
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
            else:
                messages.info(request, 'มีชื่อ Organize Code นี้แล้ว ไม่สามารถเพิ่มได้ กรุณาทำรายการใหม่')
        elif 'delete_org' in request.POST:
            organize = Organization.objects.get(org_id=request.POST['delete_org'])
            organize.delete()
        elif 'Editorg' in request.POST:
            organize = Organization.objects.get(org_id=request.POST['set_org_id'])
            organize.org_code = request.POST['set_org_code']
            organize.org_name = request.POST['set_org_name']
            organize.save()
    orgs = Organization.objects.all()
    context = {
        'orgs': orgs, 'User_login': User_login
    }
    return render(request, 'organizemanage.html', context)


def machine_search(request):
    global User_login, dict_menu_level, UserRole, User_org_machine_line
    if not Role_Screen.objects.filter(role=UserRole, screen_id='mch_search').exists():
        return redirect('/')
    User_org = User_login.org.org_line.all()
    User_org_machine_line = Machine.objects.filter(line__in=User_org)
    filtered_machine = MachineFilter(request.GET, queryset=User_org_machine_line)
    context = {
        'User_login': User_login, 'dict_menu_level': dict_menu_level.items(), 'UserRole': UserRole,
        'filtered_machine': filtered_machine
    }
    return render(request, 'machine_search.html', context)


def machine_update(request):
    global User_login, UserRole, User_org_machine_line, dict_menu_level
    if not Role_Screen.objects.filter(role=UserRole, screen_id='mch_update').exists():
        return redirect('/')
    User_org = User_login.org.org_line.all()
    User_org_machine_line = Machine.objects.filter(line__in=User_org)
    context = {
        'User_login': User_login, 'UserRole': UserRole, 'User_org_machine_line': User_org_machine_line,
        'dict_menu_level': dict_menu_level.items()
    }
    return render(request, 'machine_update.html', context)


def machine_edit(request):
    global User_login, UserRole, dict_menu_level
    if not Role_Screen.objects.filter(role=UserRole, screen_id='mch_update').exists():
        return redirect('/')
    get_machine = None
    list_mtype = Machine_type.objects.all()
    list_stype = Machine_subtype.objects.all()
    list_line = Production_line.objects.all()
    if request.method == "POST":
        if 'edit_mch_id' in request.POST:
            machine_id = request.POST['edit_mch_id']
            get_machine = Machine.objects.filter(machine_id=machine_id)
        elif 'mch_update' in request.POST:
            machine = Machine.objects.get(machine_id=request.POST['edit_machine_id'])
            machine.serial_id = request.POST['edit_serial_id']
            machine.machine_production_line_code = request.POST['edit_machine_code']
            machine.machine_name = request.POST['edit_machine_name']
            machine.sub_type_id = request.POST['select_stype']
            machine.mch_type_id = request.POST['select_mtype']
            machine.machine_brand = request.POST['edit_machine_brand']
            machine.machine_model = request.POST['edit_machine_model']
            machine.machine_supplier_code = request.POST['edit_machine_supplier_code']
            machine.machine_location_id = request.POST['edit_machine_location_id']
            machine.machine_emp_id_response = request.POST['edit_machine_emp_id_response']
            machine.machine_capacity_per_minute = request.POST['edit_machine_capacity_per_minute']
            machine.machine_capacity_measure_unit = request.POST['edit_machine_capacity_measure_unit']
            machine.machine_power_use_watt_per_hour = request.POST['edit_machine_power_use_watt_per_hour']
            machine.machine_installed_datetime = request.POST['edit_machine_installed_datetime']
            machine.machine_start_use_datetime = request.POST['edit_machine_start_use_datetime']
            machine.line_id = request.POST['select_pline']
            machine.save()
    context = {
        'User_login': User_login, 'UserRole': UserRole,
        'dict_menu_level': dict_menu_level.items(), 'get_machine': get_machine, 'list_mtype': list_mtype,
        'list_line': list_line, 'list_stype': list_stype
    }
    return render(request, 'machine_edit.html', context)


def production_line_create(request):
    form = ProductLineForm()
    if request.method == "POST":
        form = ProductLineForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, 'line_create.html', context)


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
                                                      location_site=Site.objects.get(id=request.POST['add_select_site']),
                                                      location_building=Building.objects.get(
                                                          id=request.POST['add_select_building']),
                                                      location_floor=Floor.objects.get(id=request.POST['add_select_floor'])
                                                      ).exists():
                    pline = Production_line.objects.create(
                        production_line=request.POST['add_prodline'],
                        location_site=Site.objects.get(id=request.POST['add_select_site']),
                        location_building=Building.objects.get(id=request.POST['add_select_building']),
                        location_floor=Floor.objects.get(id=request.POST['add_select_floor'])
                    )
                    pline.save()
                else:
                    messages.info(request, "มี Production Line นี้แล้วอยู่ในระบบ")
            except Machine_Management.models.Floor.DoesNotExist:
                messages.info(request, "คุณกรอกข้อมูลบางส่วนไม่สมบูรณ์ กรุณากรอกข้อมูลให้สมบูรณ์")

        elif 'Editprodline' in request.POST:
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
                messages.info(request, "มี Production Line นี้แล้วอยู่ในระบบ")
        elif 'delete_line' in request.POST:
            pline = Production_line.objects.get(pid=request.POST['delete_line'])
            pline.delete()
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
                messages.info(request, "มี Location นี้แล้ว")
            else:
                floor = Floor.objects.create(floor=request.POST['add_floor'], site=site, building=building)
                floor.save()
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
                    messages.info(request, "มี Location นี้แล้ว")
                else:
                    floor.floor = request.POST['set_floor']
                    floor.save()
        elif 'delete_location' in request.POST:
            locations = Floor.objects.get(pk=request.POST['delete_location'])
            if Floor.objects.filter(site_id=locations.site_id).count() == 1:
                site = Site.objects.get(pk=locations.site_id)
                print('site : ', site)
                site.delete()
            if Floor.objects.filter(building_id=locations.building_id).count() == 1:
                building = Building.objects.get(pk=locations.building_id)
                print('building : ', building)
                building.delete()
            if Floor.objects.filter(pk=locations.pk).count() == 1:
                print('location : ', locations)
                locations.delete()

    sites = Site.objects.all()
    buildings = Building.objects.all()
    floors = Floor.objects.all()
    context = {
        'User_login': User_login, 'sites': sites, 'buildings': buildings, 'floors': floors
    }
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
        elif "delete_org" in request.POST:
            org = Organization.objects.get(org_id=request.POST["delete_org"])
            line = Production_line.objects.get(pid=request.POST["select_del_line"])
            org.org_line.remove(line)
            org.save()
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
        elif 'delete_line' in request.POST:
            product = Product.objects.get(pk=request.POST['delete_line'])
            product.delete()
    products = Product.objects.all()
    plines = Production_line.objects.all()
    context = {
        "User_login": User_login, "UserRole": UserRole, "products": products, 'plines': plines
    }
    return render(request, 'productmanage.html', context)


def machine_searching(request):
    global User_login, UserRole, dict_menu_level
    if not Role_Screen.objects.filter(role=UserRole, screen_id='mch_searching').exists():
        return redirect('/')
    User_org = User_login.org.org_line.all()
    user_org_machine_line = Machine.objects.filter(line__in=User_org)
    filter_mch_type = Machine_type.objects.values('mtype_code').distinct()
    filter_sub_type = Machine_subtype.objects.values('subtype_code').distinct()

    if request.method == "POST":
        if "searching" in request.POST:
            line_production = request.POST["line_production"] or None
            mch_type = request.POST["mch_type"] or None
            sub_type = request.POST["sub_type"] or None
            # user_org_machine_line = Machine.objects.filter(Q(line_id=line_production) & Q(mch_type_id=mch_type) & Q(sub_type_id=sub_type))
            if line_production == "0" and mch_type != "0":
                user_org_machine_line = Machine.objects.filter(mch_type__mtype_code=mch_type)
            elif line_production == "0" and mch_type == "0" and sub_type != "0":
                user_org_machine_line = Machine.objects.filter(sub_type__subtype_code=sub_type)
            elif line_production != "0" and mch_type == "0":
                user_org_machine_line = Machine.objects.filter(line_id=line_production)
            elif line_production != "0" and mch_type != "0" and sub_type == "0":
                user_org_machine_line = Machine.objects.filter(line_id=line_production, mch_type_id=mch_type)
            elif line_production != "0" and mch_type != "0" and sub_type != "0":
                user_org_machine_line = Machine.objects.filter(
                    line_id=line_production, mch_type_id=mch_type, sub_type_id=sub_type)
        elif "searching_mch_code" in request.POST:
            machine_line_code = request.POST["machine_line_code"] or None
            if machine_line_code is not None:
                user_org_machine_line = Machine.objects.filter(machine_production_line_code__contains=machine_line_code, line__in=User_org)
    context = {"User_login": User_login, "UserRole": UserRole, "dict_menu_level": dict_menu_level.items(), "machines": user_org_machine_line,
               "lines": User_org, "filter_mch_type": filter_mch_type, "filter_sub_type": filter_sub_type}

    return render(request, 'machine_searching.html', context)


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

    if request.method == "POST":
        if 'Addmachine' in request.POST:
            add_production_line = request.POST['add_production_line']
            add_type = request.POST['add_type']
            add_subtype = request.POST['add_subtype']
            add_serial = request.POST['add_serial']
            add_machine_production_line_code = request.POST['add_mpc']
            add_machine_name = request.POST['add_machinename']
            add_machine_model = request.POST['add_machinemodel']
            add_machine_brand = request.POST['add_machinebrand']
            add_supplier = request.POST['add_supplier']
            add_person_in_change = request.POST['add_pic']
            add_machine_emp_contact = request.POST['add_contact']
            add_capacity_per_min = request.POST['add_cpm']
            add_capacity = request.POST['add_capacity']
            add_power = request.POST['add_power']
            add_install_date = request.POST['add_installdate']
            add_start_date = request.POST['add_startdate']
            add_hour = request.POST['add_hour'] if request.POST['add_hour'] != '' else None
            add_minute = request.POST['add_minute'] if request.POST['add_minute'] != '' else None
            if not Machine.objects.filter(serial_id=add_serial,
                                          machine_production_line_code=add_machine_production_line_code).exists():
                add_new_machine = Machine.objects.create(
                    serial_id=add_serial,
                    machine_production_line_code=add_machine_production_line_code,
                    machine_name=add_machine_name,
                    machine_brand=add_machine_brand,
                    machine_model=add_machine_model,
                    machine_supplier_code=add_supplier,
                    machine_emp_id_response=add_person_in_change,
                    machine_emp_contact=add_machine_emp_contact,
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
                    machine_minute=add_minute,
                    machine_active=True
                )
                add_new_machine.save()
                messages.success(request, 'เพิ่มข้อมูล Machine เรียบร้อยแล้ว')
            else:
                messages.error(request, 'การเพิ่มข้อมูล Machine ล้มเหลว กรุณากด Add New Machine Type ใหม่อีกครั้ง')
        elif 'EditMch' in request.POST:
            edit_mch = Machine.objects.get(machine_id=request.POST['EditMch'])
            edit_mch.machine_code = request.POST['set_mch_code']
            edit_mch.machine_name = request.POST['set_mch_name']
            edit_mch.machine_brand = request.POST['set_machinebrand']
            edit_mch.machine_model = request.POST['set_machinemodel']
            edit_mch.machine_supplier_code = request.POST['set_supplier']
            edit_mch.machine_emp_id_response = request.POST['set_pic']
            edit_mch.machine_emp_contact = request.POST['set_contact']
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
            edit_mch.machine_active = request.POST['set_mch_status']
            edit_mch.machine_hour = request.POST['set_hour'] if request.POST['set_hour'] != '' else None
            edit_mch.machine_minute = request.POST['set_minute'] if request.POST['set_minute'] != '' else None
            edit_mch.save()
            messages.success(request, 'แก้ไขข้อมูล Machine สำเร็จ')

        elif 'deletemachine' in request.POST:
            del_machine = request.POST['deletemachine']
            machine_id = Machine.objects.get(machine_id=del_machine)
            machine_id.delete()
    context = {
        'User_login': User_login,
        'machine': machine, 'mch_subtype_all': mch_subtype_all,
        'production_line': pd_line, 'mch_type_all': mch_type_all, 'role_and_screen': role_and_screen}
    return render(request, 'machine_manage.html', context)


@csrf_exempt
def check_serial(request):
    if request.method == 'POST':
        response_data = {}
        add_machine_serial = request.POST["add_serial"]

        serial = Machine.objects.filter(serial_id=add_machine_serial)
        serial_status = None

        try:
            try:
                # we are matching the input again hardcoded value to avoid use of DB.
                # You can use DB and fetch value from table and proceed accordingly.
                if serial.count():
                    serial_status = True  # alredy exist
                elif len(add_machine_serial) == 0:
                    serial_status = None  # empty input
                else:
                    serial_status = False  # avialble

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e

            if not serial_status:
                response_data["serial_success"] = True
            else:
                response_data["serial_success"] = False
            if serial_status is None:
                response_data["serial_empty"] = True

        except Exception:
            response_data["serial_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."

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
            edit_type.mtype_code = request.POST['set_type_code']
            edit_type.mtype_name = request.POST['set_mch_type']
            edit_type.last_update_by = User_login.username
            now = datetime.datetime.now()
            edit_type.last_update_date = now.date()
            if not Machine_type.objects.filter(mtype_code=edit_type.mtype_code, mtype_name=edit_type.mtype_name).exists():
                edit_type.save()
                messages.success(request, 'แก้ไขข้อมูล Machine Type สำเร็จ')
            elif edit_type.mtype_code == request.POST['set_type_code'] and edit_type.line_id == request.POST['select_line']:
                messages.success(request, 'ไม่มีการ Update รายการใหม่')
            else:
                messages.error(request, 'การแก้ข้อมูล Machine Type ไม่ถูกต้อง กรุณาแก้ไขใหม่อีกครั้ง')
        elif 'Delete_type' in request.POST:
            del_type = request.POST['Delete_type']
            typeid = Machine_type.objects.get(mtype_id=del_type)
            typeid.delete()
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
                # we are matching the input again hardcoded value to avoid use of DB.
                # You can use DB and fetch value from table and proceed accordingly.
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
                messages.error(request,
                               'การเพิ่มข้อมูล Machine Subtype ล้มเหลว กรุณากด Add New Machine Subtype ใหม่อีกครั้ง')

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
    context = {'subtypes': mch_subtype, 'mch_type_all': mch_type_all, 'User_login': User_login, 'role_and_screen': role_and_screen}
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
        subtypeid = Machine_subtype.objects.filter(subtype_code=add_subtype_code)
        subtypecode = None

        try:
            try:
                # we are matching the input again hardcoded value to avoid use of DB.
                # You can use DB and fetch value from table and proceed accordingly.
                if subtypeid.count():
                    subtypecode = True  # alredy exist
                elif len(add_subtype_code) == 0:
                    subtypecode = None  # empty input
                else:
                    subtypecode = False  # avialble

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e
            if not subtypecode:
                response_data["subtypecode_success"] = True
            else:
                response_data["subtypecode_success"] = False
            if subtypecode is None:
                response_data["subtypecode_empty"] = True

        except Exception:
            response_data["subtypecode_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."

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
    spare_part_of_mch = Machine_and_spare_part.objects.filter(machine_id__in=machine)
    context = {'User_login': User_login, 'UserRole': UserRole, 'dict_menu_level': dict_menu_level.items(),
               'machine': machine, 'spare_part_of_mch': spare_part_of_mch}
    return render(request, 'machine_details.html', context)


def spare_part_manage(request):
    global User_login
    if not Role_Screen.objects.filter(role=UserRole, screen_id='spare_part_manage').exists():
        return redirect('/')
    spare_part_all = Spare_part.objects.all()
    spare_part_type_all = Spare_part_type.objects.all()
    if request.method == 'POST':
        if 'add_spare_part' in request.POST:
            spare_part = Spare_part.objects.create(spare_part_name=request.POST['add_sp_name'],
                                                   spare_part_code=request.POST['add_sp_code'],
                                                   spare_part_model=request.POST['add_sp_model'],
                                                   service_life=request.POST['add_service_life'],
                                                   service_plan_life=request.POST['add_service_plan_life'],
                                                   spare_part_type_id=request.POST['id_sp_type'],
                                                   spare_part_sub_type_id=request.POST['id_sp_subtype'],
                                                   create_by=User_login.username,
                                                   create_date=datetime.date.today(),
                                                   spare_part_active=True)
            spare_part.save()
        elif 'edit_spare_part' in request.POST:
            spare_part = Spare_part.objects.get(pk=request.POST['edit_spare_part'])
            spare_part.spare_part_name = request.POST['set_sp_name']
            spare_part.spare_part_model = request.POST['set_sp_model']
            spare_part.service_life = request.POST['set_service_life']
            spare_part.service_plan_life = request.POST['set_service_plan_life']
            spare_part.last_update_by = User_login.username
            spare_part.last_update_date = datetime.date.today()
            spare_part.spare_part_active = request.POST.get('set_sp_status',False)
            spare_part.save()
        elif 'delete_spare_part' in request.POST:
            spare_part = Spare_part.objects.get(pk=request.POST['delete_spare_part'])
            spare_part.delete()
    context = {'User_login': User_login, 'spare_part_all': spare_part_all, 'spare_part_type_all': spare_part_type_all}
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
    if not Role_Screen.objects.filter(role=UserRole, screen_id='spare_part_subtype').exists():
        return redirect('/')
    spare_part_subtype_all = Spare_part_sub_type.objects.all()
    spare_part_type_all = Spare_part_type.objects.all()
    if request.method == 'POST':
        if 'add_spare_part_subtype' in request.POST:
            sp_subtype = Spare_part_sub_type.objects.create(spare_part_sub_type_code=request.POST['add_sp_subtype_code'],
                                                            spare_part_sub_type_name=request.POST['add_sp_subtype_name'],
                                                            spare_part_type_id=request.POST['select_sp_type'],
                                                            create_by=User_login.username,
                                                            create_date=datetime.date.today())
            sp_subtype.save()
        elif 'edit_spare_part_subtype' in request.POST:
            sp_subtype = Spare_part_sub_type.objects.get(pk=request.POST['edit_spare_part_subtype'])
            sp_subtype.spare_part_sub_type_name = request.POST['set_sp_suptype_name']
            sp_subtype.last_update_by = User_login.username
            sp_subtype.last_update_date = datetime.date.today()
            sp_subtype.save()
        elif 'delete_spare_part_subtype' in request.POST:
            sp_subtype = Spare_part_sub_type.objects.get(pk=request.POST['delete_spare_part_subtype'])
            sp_subtype.delete()
    context = {'User_login': User_login, 'spare_part_subtype_all': spare_part_subtype_all, 'spare_part_type_all': spare_part_type_all}
    return render(request, 'spare_part_subtype.html', context)


def spare_part_type(request):
    global User_login
    if not Role_Screen.objects.filter(role=UserRole, screen_id='spare_part_type').exists():
        return redirect('/')
    sp_type_all = Spare_part_type.objects.all()
    if request.method == "POST":
        if 'add_spare_part_type' in request.POST:
            spare_type = Spare_part_type.objects.create(spare_part_type_code=request.POST['add_sp_type_code'],
                                                        spare_part_type_name=request.POST['add_sp_type_name'],
                                                        create_by=User_login.username,
                                                        create_date=datetime.date.today())
            spare_type.save()
        elif 'edit_spare_part_type' in request.POST:
            spare_type = Spare_part_type.objects.get(pk=request.POST['edit_spare_part_type'])
            spare_type.spare_part_type_name = request.POST['set_sp_name']
            spare_type.last_update_by = User_login.username
            spare_type.last_update_date = datetime.date.today()
            spare_type.save()
        elif 'delete_spare_part' in request.POST:
            spare_type = Spare_part_type.objects.get(pk=request.POST['delete_spare_part'])
            spare_type.delete()
    context = {'User_login': User_login, 'sp_type_all': sp_type_all}
    return render(request, 'spare_part_type.html', context)


@csrf_exempt
def check_spare_part_type_code(request):
    if request.method == 'POST':
        response_data = {}
        spare_type = Spare_part_type.objects.filter(spare_part_type_code=request.POST['add_code'])
        spare_type_code = None
        try:
            if spare_type.count():
                spare_type_code = True  # alredy exist
            elif len(request.POST['add_code']) == 0:
                spare_type_code = None  # empty input
            else:
                spare_type_code = False  # avialble

        except ObjectDoesNotExist:
            pass
        except Exception as e:
            raise e
        if not spare_type_code:
            response_data["spare_type_code_success"] = True
        else:
            response_data["spare_type_code_success"] = False
        if spare_type_code is None:
            response_data["spare_type_code_empty"] = True
        return JsonResponse(response_data)


@csrf_exempt
def check_spare_part_subtype_code(request):
    if request.method == 'POST':
        response_data = {}
        spare_subtype = Spare_part_sub_type.objects.filter(spare_part_sub_type_code=request.POST['add_subtype_code'])
        spare_subtype_code = None
        try:
            if spare_subtype.count():
                spare_subtype_code = True  # alredy exist
            elif len(request.POST['add_subtype_code']) == 0:
                spare_subtype_code = None  # empty input
            else:
                spare_subtype_code = False  # avialble

        except ObjectDoesNotExist:
            pass
        except Exception as e:
            raise e
        if not spare_subtype_code:
            response_data["spare_subtype_code_success"] = True
        else:
            response_data["spare_subtype_code_success"] = False
        if spare_subtype_code is None:
            response_data["spare_subtype_code_empty"] = True
        return JsonResponse(response_data)


@csrf_exempt
def check_spare_part_code(request):
    if request.method == 'POST':
        response_data = {}
        spare_part = Spare_part.objects.filter(spare_part_code=request.POST['add_sp_code'])
        spare_part_code = None
        try:
            if spare_part.count():
                spare_part_code = True  # alredy exist
            elif len(request.POST['add_sp_code']) == 0:
                spare_part_code = None  # empty input
            else:
                spare_part_code = False  # avialble

        except ObjectDoesNotExist:
            pass
        except Exception as e:
            raise e
        if not spare_part_code:
            response_data["spare_part_code_success"] = True
        else:
            response_data["spare_part_code_success"] = False
        if spare_part_code is None:
            response_data["spare_part_code_empty"] = True
        return JsonResponse(response_data)


def machine_and_spare_part(request):
    global User_login
    role_and_screen = Role_Screen.objects.filter(role_id=UserRole, screen_id='machine_spare_part')
    if not role_and_screen.exists():
        return redirect('/')
    dict_mch_sp = {}
    user_org = User_login.org.org_line.all()
    machine = Machine.objects.filter(line__in=user_org)
    mch_and_sp_all = Machine_and_spare_part.objects.filter(machine__in=machine)
    spare_part_type_all = Spare_part_type.objects.all()
    spare_part_subtype_all = Spare_part_sub_type.objects.all()
    spare_part_all = Spare_part.objects.all()

    if request.method == "POST":
        if "add_mch_and_sp" in request.POST:
            mch_and_sp = Machine_and_spare_part.objects.create(machine_id=request.POST["add_mch_and_sp"],
                                                               spare_part_id=request.POST["select_sp_name"])
            mch_and_sp.save()
        elif "delete_spare_part" in request.POST:
            mch_and_sp = Machine_and_spare_part.objects.filter(machine_id=request.POST['delete_spare_part'],
                                                               spare_part_id=request.POST['select_delete_spare_part'])
            mch_and_sp.delete()
    for mch in machine:
        dict_mch_sp[mch] = []
    for mch_sp in mch_and_sp_all:
        dict_mch_sp[mch_sp.machine].append(mch_sp.spare_part)

    context = {'User_login': User_login,
               'mch_and_sp_all': mch_and_sp_all, 'dict_mch_sp': dict_mch_sp, 'spare_part_type_all': spare_part_type_all,
               'spare_part_subtype_all': spare_part_subtype_all, 'spare_part_all': spare_part_all, 'role_and_screen': role_and_screen}
    return render(request, 'machine&spare_part.html', context)


def maintenance_plan(request):
    global User_login
    list_mch_mtn = []
    mch_sp_all = Machine_and_spare_part.objects.all()
    for mch_sp in mch_sp_all:
        if Maintenance_plan.objects.filter(machine_and_spare=mch_sp):
            continue
        try:
            if mch_sp.machine.machine_hour > mch_sp.spare_part.service_plan_life + mch_sp.last_maintenance_hour:
                list_mch_mtn.append(mch_sp)
                mtn_plan = Maintenance_plan.objects.create(machine_and_spare=mch_sp, gen_date=datetime.date.today())
                mtn_plan.save()
        except TypeError:
            continue
    list_plan = Maintenance_plan.objects.all()
    list_user = User.objects.all()
    context = {'User_login': User_login, 'list_plan': list_plan, 'list_user': list_user}
    return render(request, 'maintenance_plan.html', context)


def machine_capacity(request):
    global User_login, UserRole
    role_and_screen = Role_Screen.objects.filter(role_id=UserRole, screen_id='machine_capacity')
    if not role_and_screen.exists():
        return redirect('/')
    if request.method == "POST":
        if 'Add_machine_capacity' in request.POST:
            mch_capacity = Machine_capacity.objects.filter(machine=request.POST['add_mch'], product=request.POST['add_product'])
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

    mch_capacity_all = Machine_capacity.objects.all()
    production_line = Production_line.objects.all()
    context = {'User_login': User_login, 'mch_capacity_all': mch_capacity_all, 'production_line': production_line}
    return render(request, 'machine_capacity.html', context)


def load_machine(request):
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
            machine_product = Machine_capacity.objects.filter(machine_id=request.POST['mch_id'], product_id=request.POST['product_id'])
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
