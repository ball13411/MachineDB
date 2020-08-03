from django.shortcuts import render,redirect
from django.contrib import messages
from .models import *
import Machine_Management
import datetime
# Create your views here.

# GLOBAL var
User_loinged = None         # User Login for use all pages

def signin(request):
    # Functions for Sign In to webapp
    # Templates/signin.html
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
                elif datenow > user.expired_date:                 # Check ExpirdDate if expird link to resetpassword
                    messages.info(request,'รหัสผ่านหมดอายุแล้ว กรุณาทำการ Reset Password')
                if user is not None :                           # Check login User
                    global User_loinged                         # Set user login
                    User_loinged = user
                    if str(User_loinged.role) == "admin" :      # Check Role of User
                        return redirect('/adminmanage')
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
            username = request.POST['username']                 # Get var('username') from HTML
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
            username = request.POST['username']                 # Get var('username') form HTML
            fname = request.POST['fname']
            lname = request.POST['lname']
            email = request.POST['email']
            startdate = request.POST['startdate']
            create_role = request.POST['select_role']
            passwd = request.POST['password']
            conpasswd = request.POST['conpassword']
            create_prod_line = request.POST.getlist('lines[]','')
            now = datetime.datetime.now()
            role = Role.objects.get(role_id=create_role)
            if passwd==conpasswd:                               # Check password and confirm password
                if User.objects.filter(username=username).exists():    # Query username is exists in model(DB)
                    messages.info(request,"มีผู้ใช้ชื่อ Username นี้แล้ว")      # Show Message Username is exists
                elif User.objects.filter(email=email).exists():       # Query email is exists in model(DB)
                    messages.info(request,"มีผู้ใช้ Email นี้แล้ว")          # Show Message Email is exists
                else:
                    user = User.objects.create(                 # Create User (Set all arg*)
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
            role_id = request.POST['roleid']                 # Get var('role id') from HTML
            role_name = request.POST['rolename']           # Get var('role name') from HTML
            role = Role.objects.get(role_id=role_id)
            role.role_name = role_name
            role.save()
        elif 'Addrole' in request.POST:
            role_id = request.POST['roleid']                 # Get var('role id') from HTML
            role_name = request.POST['rolename']           # Get var('role name') from HTML
            role = Role.objects.create(role_id=role_id,role_name=role_name)
            role.save()
        elif 'deleterole' in request.POST:
            role_id = request.POST['deleterole']                 # Get var('role id') from HTML
            print(role_id)
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
    if request.method == "POST":
        if 'Addscreen' in request.POST:
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


