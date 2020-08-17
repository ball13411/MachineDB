from django.shortcuts import render,redirect
from django.contrib import messages
from .models import *
import Machine_Management
import datetime
import django
from .forms import *
from .filters import MachineFilter
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

# GLOBAL var
User_loinged,UserRole,List_user_Screen,dict_menu_level,User_org_machine_line = None,None,[],{},None         # User Login for use all pages

def signin(request):
    # Functions for Sign In to webapp
    # Templates/signin.html
    global User_loinged,UserRole
    User_loinged = None
    if request.method == "POST":
        # Form Sign In
        if 'signin' in request.POST:
            username = request.POST['inputUser']                # Get var('username') from HTML
            password = request.POST['inputPassword']            # Get var('password') from HTML
            try:    #Try connect username and passwd on Model
                user = User.objects.get(username=username,password=password)
                now = datetime.datetime.now()                   # Call Datetime now
                datenow = datetime.date.today()                 # Call Date now
                user.last_login_date = now                      # Update last_login to now
                user.save()                                     # Save Update
                if user.start_date > datenow:                   # Check StartDate and DateNow
                    messages.info(request,f'ชื่อผู้ใช้นี้ยังไม่สามารถเข้าสู่ระบบได้ สามารถเข้าได้ในวันที่ {user.start_date}')
                    return redirect('/')
                elif datenow > user.expired_date:                 # Check ExpirdDate if expird link to resetpassword
                    messages.info(request,'รหัสผ่านหมดอายุแล้ว กรุณาทำการ Reset Password')
                    return redirect('/')
                if user is not None :                           # Check login User                    # Set user login
                    User_loinged = user
                    UserRole = str(User_loinged.role)
                    if str(User_loinged.role) == "admin" :      # Check Role of User
                        return redirect('/adminmanage')
                    else:
                        return redirect('/machinemanage')
            except Machine_Management.models.User.DoesNotExist: # Message Wrong username or password
                messages.info(request,"username หรือ password ไม่ถูกต้อง")
    return render(request,'signin.html')

def usermanage(request):
    # Functions for User Management
    # Templates/usermanage.html
    global User_loinged     #Call User sign in
    production_lines = Production_line.objects.all()
    if str(User_loinged.role) != 'admin':
        User_loinged = None
        return redirect('/')
    if request.method == "POST":
        # Form Edituser (Settings of user)
        if 'Edituser' in request.POST:
            username = request.POST['set_username']                 # Get var('username') from HTML
            update_role = request.POST['select_role']           # Get var('role') from HTML
            update_org = request.POST['select_org']
            now = datetime.datetime.now()                       # Call Datetime now
            user = User.objects.get(username=username)          # Query user
            user.update_date = now                              # Update UpdateDate to now
            user.update_by = str(User_loinged.username)         # Update UserUpdate of UserSelect
            org = Organization.objects.get(org_id=update_org)
            user.org = org
            role = Role.objects.get(role_id=update_role)        # Get RoleID of UserSelect
            user.role = role                                    # Update Role of UserSelect
            user.save()                                         # Save all Update
        # Form Add User (Add New User)
        elif 'Adduser' in request.POST:
            username = request.POST['add_username']                 # Get var('username') form HTML
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
            if passwd==conpasswd:                               # Check password and confirm password
                if User.objects.filter(username=username).exists():    # Query username is exists in model(DB)
                    messages.info(request,"มีผู้ใช้ชื่อ Username นี้แล้ว")      # Show Message Username is exists
                elif User.objects.filter(email=email).exists():       # Query email is exists in model(DB)
                    messages.info(request,"มีผู้ใช้ Email นี้แล้ว")          # Show Message Email is exists
                else:
                    user = User.objects.create(
                        username=username,
                        email=email,
                        firstname=fname.capitalize(),
                        lastname=lname.capitalize(),
                        password=passwd,
                        create_by=str(User_loinged.username),
                        create_date=now,
                        expired_date=now-datetime.timedelta(1),
                        expired_day=90,
                        start_date=startdate,
                        update_by=None,
                        update_date=None,
                        last_login_date=None,
                        role = role,
                        org = org
                    )
                    user.save()                                 # Save User
                    # return redirect('/usermanage')
            else:
                messages.info(request,"รหัสผ่านไม่ตรงกัน กรุณาตรวจสอบใหม่")     # Show Message Password != ConPassword
        # Button Sign Out
        elif 'signout' in request.POST:
            User_loinged = None                                 # Set User_login is None
        # Form DeleteUser (icon delete)
        elif 'deleteuser' in request.POST:
            username = request.POST['deleteuser']               # get var('username') from HTML
            user = User.objects.get(username=username)          # Query Username
            user.delete()                                       # Delete User from Model(DB)
    # return var to HTML
    form = AddUserForm()
    roles = Role.objects.all()
    users = User.objects.all()
    orgs = Organization.objects.all()
    context = {'users':users,
               'roles':roles,
               'User_loinged':User_loinged,
               'production_lines':production_lines,
               'orgs':orgs,
               'form':form}
    return render(request,'usermanage.html',context)

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

            except ObjectDoesNotExist as e:
                pass
            except Exception as e:
                raise e
            print("status user:",user)

            if not user:
                response_data["username_success"] = True
            else:
                response_data["username_success"] = False

        except Exception as e:
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
            try:
                # we are matching the input again hardcoded value to avoid use of DB.
                # You can use DB and fetch value from table and proceed accordingly.
                if mail.count():
                    email = True

            except ObjectDoesNotExist as e:
                pass
            except Exception as e:
                raise e
            print("status email:",email)

            if not email:
                response_data["email_success"] = True
            else:
                response_data["email_success"] = False

        except Exception as e:
            response_data["email_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."

        return JsonResponse(response_data)

def resetpassword(requset):
    # Form Reset Password
    # Get variables from Input HTML
    if requset.method == "POST":
        username = requset.POST['inputUser']
        old_password = requset.POST['oldPassword']
        new_password = requset.POST['newPassword']
        con_new_password = requset.POST['conPassword']
        try:        # Test connect User in modals(DB)
            user = User.objects.get(username=username,password=old_password)
            if old_password != new_password:
                if new_password == con_new_password:            # Check new_pass and con_pass
                    user.password = new_password
                    now = datetime.date.today()
                    user.expired_date = now + datetime.timedelta(90)
                    user.save()
                    return redirect('/')
                else:                                           # NewPassword != ConPassword
                    messages.info(requset,'รหัสผ่านใหม่และรหัสผ่านยืนยันไม่ตรงกัน')
            else:                                               # OldPassword != NewPassword
                messages.info(requset,'รหัสผ่านเก่าต้องไม่ตรงกับรหัสผ่านใหม่')
        except Machine_Management.models.User.DoesNotExist:     # Failed Connect User in model(DB)
            messages.info(requset,'ชื่อผู้ใช้และรหัสผ่านเก่าไม่ถูกต้อง')
    return render(requset,'resetpassword.html')

def rolemanage(request):
    global User_loinged               #Call User sign in
    if str(User_loinged.role) != 'admin':
        User_loinged = None
        return redirect('/')
    if request.method == "POST":
        if 'Editrole' in request.POST:
            role_id = request.POST['set_roleid']                 # Get var('role id') from HTML
            role_name = request.POST['set_rolename']           # Get var('role name') from HTML
            role = Role.objects.get(role_id=role_id)
            role.role_name = role_name
            role.save()
        elif 'Addrole' in request.POST:
            role_id = request.POST['add_roleid']                 # Get var('role id') from HTML
            role_name = request.POST['add_rolename']           # Get var('role name') from HTML
            try:
                role = Role.objects.create(role_id=role_id,role_name=role_name)
                role.save()
            except django.db.utils.IntegrityError:
                messages.info(request,"มีชื่อ Role ID นี้แล้ว กรุณาตั้งใหม่")
        elif 'deleterole' in request.POST:
            role_id = request.POST['deleterole']                 # Get var('role id') from HTML
            role = Role.objects.get(role_id=role_id)
            role.delete()
        elif 'signout' in request.POST:
            User_loinged = None                                 # Set User_login is None
    roles = Role.objects.all()
    context = {'roles':roles,
               'User_loinged':User_loinged}
    return render(request,'rolemanage.html',context)

def screenmanage(request):
    global User_loinged
    if str(User_loinged.role) != 'admin':
        User_loinged = None
        return redirect('/')
    if request.method == "POST":
        if 'Addscreen' in request.POST:
            screen_id = request.POST['screen_id']
            screen_name = request.POST['screen_name']
            file_py = request.POST['file_py']
            file_html = request.POST['file_html']
            try:
                screen = Screen.objects.create(
                    screen_id=screen_id,
                    screen_name=screen_name,
                    file_py=file_py,
                    file_html=file_html
                )
                screen.save()
            except django.db.utils.IntegrityError:
                messages.info(request,"มีชื่อ Screen ID นี้แล้ว กรุณาตั้งใหม่")
        elif 'deletescreen' in request.POST:
            del_screen_id = request.POST['deletescreen']
            screen = Screen.objects.get(screen_id=del_screen_id)
            screen.delete()
        elif 'Editscreen' in request.POST:
            set_screen_id = request.POST['set_screenid']
            set_screen_name = request.POST['set_screenname']
            set_file_py = request.POST['set_filepy']
            set_file_html = request.POST['set_filehtml']
            screen = Screen.objects.get(screen_id=set_screen_id)
            screen.screen_name = set_screen_name
            screen.file_py = set_file_py
            screen.file_html = set_file_html
            screen.save()
    screens = Screen.objects.all()
    context = {'User_logined':User_loinged,
               'screens':screens}
    return render(request,'screenmanage.html',context)

def adminmanage(request):
    global User_loinged
    if str(User_loinged.role) != 'admin':
        User_loinged = None
        return redirect('/')
    context = {'User_loinged':User_loinged}
    return render(request,'machineoruser.html',context)

def role_screen(request):
    global User_loinged
    if str(User_loinged.role) != 'admin':
        User_loinged = None
        return redirect('/')
    if request.method == "POST":
        if 'delete_rs' in request.POST:
            rs_id = request.POST['delete_rs']
            role_screen = Role_Screen.objects.get(id=rs_id)
            role_screen.delete()
        elif 'Edit_rs' in request.POST:
            rs_id = request.POST['Edit_rs']
            rs_role_id = request.POST['set_rs_role']
            rs_screen_id = request.POST['set_rs_screen']
            rs_insert = request.POST['set_rs_insert']
            rs_update = request.POST['set_rs_update']
            rs_delete = request.POST['set_rs_delete']
            role_screen = Role_Screen.objects.get(id=rs_id)
            role_screen.role_id = rs_role_id
            role_screen.screen_id = rs_screen_id
            role_screen.permission_insert = rs_insert
            role_screen.permission_update = rs_update
            role_screen.permission_delete = rs_delete
            role_screen.save()
        elif 'Addrolescreen' in request.POST:
            rs_role_id = request.POST['add_rs_role']
            rs_screen_id = request.POST['add_rs_screen']
            rs_insert = request.POST['add_rs_insert']
            rs_update = request.POST['add_rs_update']
            rs_delete = request.POST['add_rs_delete']
            role_screen = Role_Screen.objects.create(
                role_id = rs_role_id,
                screen_id = rs_screen_id,
                permission_insert = rs_insert,
                permission_update = rs_update,
                permission_delete = rs_delete
            )
            role_screen.save()
    list_role_screen = Role_Screen.objects.all()
    roles = Role.objects.all()
    screens = Screen.objects.all()
    context = {'User_loinged':User_loinged,
               'list_role_screen':list_role_screen,
               'roles':roles,
               'screens':screens}
    return render(request,'role_screen_manage.html',context)

def machinemanage(request):
    global User_loinged,UserRole,dict_menu_level
    if request.method == "POST":
        if 'signout' in request.POST:
            User_loinged = None
    User_role = Role.objects.get(role_id=User_loinged.role)
    List_user_Screen = User_role.members.all()
    List_user_menu_lv0 = Menu.objects.filter(level=0).order_by('index')
    List_user_menu_lv1 = Menu.objects.filter(level=1).order_by('index')
    List_menu_role = []
    dict_menu_level = {}
    for menu_role in List_user_Screen:
        List_menu_role.append(Menu.objects.get(screen=menu_role))
    for root in List_user_menu_lv0 :
        if root in List_menu_role :
            dict_menu_level[root] = []
    for child in List_user_menu_lv1:
        if child in List_menu_role :
            root = Menu.objects.get(menu_id=child.parent_menu)
            dict_menu_level[root].append(child)
    print(dict_menu_level)
    context = {'User_loinged':User_loinged,'UserRole':UserRole,'dict_menu_level':dict_menu_level.items()}
    return render(request,'machinemanage.html',context)

def machine_register(request):
    global User_loinged,UserRole,dict_menu_level
    form = MachineForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = MachineForm()
        messages.info(request,'Register Success')
    UserRole = str(User_loinged.role)
    context = {
        'form':form,'User_loinged':User_loinged,'UserRole':UserRole,'List_user_Screen':List_user_Screen,
        'dict_menu_level':dict_menu_level.items()
    }
    return render(request,'machine_register.html',context)

def machine_data(request):
    global User_loinged,UserRole,dict_menu_level,User_org_machine_line
    # machine_data = Machine.objects.all()
    User_org = User_loinged.org.org_line.all()
    User_org_machine_line = Machine.objects.filter(line__in=User_org)
    context = {
        'User_loinged':User_loinged,'UserRole':UserRole,
        'dict_menu_level':dict_menu_level.items(),'User_org_machine_line':User_org_machine_line
    }
    return render(request,'machine_data.html',context)

def test(request):
    form = UserForm(request.POST or None)
    form = ProductLineForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = UserForm()
    context = {'form':form}
    return render(request,'test.html',context)

def menumanage(request):
    global User_loinged
    if str(User_loinged.role) != 'admin':
        User_loinged = None
        return redirect('/')
    if request.method == 'POST':
        if 'Addmenu' in request.POST:
            add_menu_id = request.POST['add_menu_id']
            add_menu_name = request.POST['add_menu_name']
            add_menu_level = request.POST['add_menu_level']
            select_screen = request.POST['select_screen']
            select_parent = request.POST['select_parent']
            add_menu_index = request.POST['add_menu_index']
            add_menu_path = request.POST['add_menu_path']
            screen = Screen.objects.get(screen_id=select_screen)
            menu = Menu.objects.create(
                menu_id = add_menu_id,
                name = add_menu_name,
                level = add_menu_level,
                screen = screen,
                parent_menu = select_parent,
                index = add_menu_index,
                path_url = add_menu_path
            )
            menu.save()
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
                menu_id = set_menu_id,
                name = set_menu_name,
                level = set_menu_level,
                screen = screen,
                parent_menu = select_parent,
                index = set_menu_index,
                path_url = set_menu_path
                )
                set_menu.save()
        elif 'deletemenu' in request.POST:
            del_menu_id = request.POST['deletemenu']
            menu_del = Menu.objects.get(menu_id=del_menu_id)
            menu_del.delete()
    list_menu = Menu.objects.order_by('level')
    list_screen = Screen.objects.all()
    context = {
        'User_loinged':User_loinged,
        'list_menu':list_menu,
        'list_screen':list_screen
    }
    return render(request,'menumanage.html',context)

def organization(request):
    global User_loinged
    if str(User_loinged.role) != 'admin':
        User_loinged = None
        return redirect('/')
    if request.method == 'POST':
        if 'Addorg' in request.POST:
            add_org_code = request.POST['add_org_code']
            add_org_name = request.POST['add_org_name']
            organize = Organization.objects.create(
                org_code = add_org_code,
                org_name = add_org_name
            )
            organize.save()
    orgs = Organization.objects.all()
    context = {
        'orgs':orgs,'User_loinged':User_loinged
    }
    return render(request,'organization.html',context)

def machine_search(request):
    global User_loinged,dict_menu_level,UserRole,User_org_machine_line
    User_org = User_loinged.org.org_line.all()
    User_org_machine_line = Machine.objects.filter(line__in=User_org)
    filtered_machine = MachineFilter(request.GET,queryset=User_org_machine_line)
    context = {
        'User_loinged':User_loinged,'dict_menu_level':dict_menu_level.items(),'UserRole':UserRole,'filtered_machine':filtered_machine
    }
    return render(request,'machine_search.html',context)

def machine_update(request):
    global User_loinged,UserRole,User_org_machine_line,dict_menu_level
    User_org = User_loinged.org.org_line.all()
    User_org_machine_line = Machine.objects.filter(line__in=User_org)
    print(User_org_machine_line)
    context = {
        'User_loinged':User_loinged,'UserRole':UserRole,'User_org_machine_line':User_org_machine_line,
        'dict_menu_level':dict_menu_level.items()
    }
    return render(request,'machine_update.html',context)

def machine_edit(request):
    return render(request,'machine_edit.html')
