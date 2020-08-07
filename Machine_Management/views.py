from django.shortcuts import render,redirect
from django.contrib import messages
from .models import *
import Machine_Management
import datetime
import django
from .forms import *
# Create your views here.

# GLOBAL var
User_loinged,UserRole,List_user_Screen = None,None,[]         # User Login for use all pages

def signin(request):
    # Functions for Sign In to webapp
    # Templates/signin.html
    global User_loinged,UserRole,List_user_Screen
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
                    User_Screen = Role.objects.get(role_id=User_loinged.role)
                    List_user_Screen = []
                    for screenclass in User_Screen.members.all():
                        List_user_Screen.append(screenclass.screen_id)
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
            update_prod_line = request.POST.getlist('lines[]','')
            now = datetime.datetime.now()                       # Call Datetime now
            user = User.objects.get(username=username)          # Query user
            user.production.clear()
            for line in update_prod_line:
                user.production.add(line)
            user.update_date = now                              # Update UpdateDate to now
            user.update_by = str(User_loinged.username)         # Update UserUpdate of UserSelect
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
            conpasswd = request.POST['add_conpassword']
            create_prod_line = request.POST.getlist('lines[]','')
            now = datetime.datetime.now()
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
                        role = role
                    )
                    for line in create_prod_line:
                        user.production.add(line)
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
    roles = Role.objects.all()
    users = User.objects.all()
    context = {'users':users,
               'roles':roles,
               'User_loinged':User_loinged,
               'production_lines':production_lines}
    return render(request,'usermanage.html',context)

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
    global User_loinged     #Call User sign in
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
    global User_loinged,UserRole,List_user_Screen
    print(User_loinged.role)
    # print(Role_Screen.objects.get(role=User_loinged.role,screen=1))
    a=Role.objects.get(role_id=User_loinged.role)
    print(a.members.all())
    for i in a.members.all():
        print(type(i.screen_id))
    if request.method == "POST":
        if 'signout' in request.POST:
            User_loinged = None
    context = {'User_loinged':User_loinged,'UserRole':UserRole,'List_user_Screen':List_user_Screen}
    return render(request,'machinemanage.html',context)

def machine_register(request):
    global User_loinged,UserRole,List_user_Screen
    form = MachineForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = MachineForm()
        messages.info(request,'Register Success')
    UserRole = str(User_loinged.role)
    context = {
        'form':form,'User_loinged':User_loinged,'UserRole':UserRole,'List_user_Screen':List_user_Screen
    }
    return render(request,'machine_register.html',context)

def machine_data(request):
    global User_loinged,UserRole,List_user_Screen
    machine_data = Machine.objects.all()
    context = {
        'User_loinged':User_loinged,'UserRole':UserRole,'List_user_Screen':List_user_Screen,
        'machine_data':machine_data
    }
    return render(request,'machine_data.html',context)

def test(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = UserForm()
    context = {'form':form}
    return render(request,'test.html',context)
