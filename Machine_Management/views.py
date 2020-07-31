from django.shortcuts import render,redirect
from django.contrib import messages
from .models import *
import Machine_Management
import datetime
# Create your views here.
User_loinged = None

def signin(request):
    if request.method == "POST":
        username = request.POST['inputUser']
        password = request.POST['inputPassword']
        try:
            user = User.objects.get(username=username,password=password)
            now = datetime.datetime.now()
            print(now)
            user.last_login_date = now
            user.save()
            if user is not None :
                global User_loinged
                User_loinged = user
                print(type(User_loinged.username))
                if str(User_loinged.role) == "admin" :
                    return redirect('/usermanage')
        except Machine_Management.models.User.DoesNotExist:
            messages.info(request,"username หรือ password ไม่ถูกต้อง")

    return render(request,'signin.html')

def usermanage(request):
    global User_loinged
    print(str(User_loinged.username))
    if request.method == "POST":
        if 'Edituser' in request.POST:
            username = request.POST['username']
            update_role = request.POST['select_role']
            user = User.objects.get(username=username)
            role = Role.objects.get(role_id=update_role)
            user.role = role
            user.save()
        elif 'Adduser' in request.POST:
            username = request.POST['username']
            fname = request.POST['fname']
            lname = request.POST['lname']
            email = request.POST['email']
            startdate = request.POST['startdate']
            create_role = request.POST['select_role']
            passwd = request.POST['password']
            conpasswd = request.POST['conpassword']
            now = datetime.datetime.now()
            role = Role.objects.get(role_id=create_role)
            if passwd==conpasswd:
                if User.objects.filter(username=username).exists():
                    messages.info(request,"มีผู้ใช้ชื่อ Username นี้แล้ว")
                elif User.objects.filter(email=email).exists():
                    messages.info(request,"มีผู้ใช้ Email นี้แล้ว")
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
                    user.save()
                    return redirect('/usermanage')
            else:
                messages.info(request,"รหัสผ่านไม่ตรงกัน กรุณาตรวจสอบใหม่")


    roles = Role.objects.all()
    users = User.objects.all()
    context = {'users':users,
               'roles':roles}
    return render(request,'usermanage.html',context)
