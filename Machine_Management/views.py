from django.shortcuts import render,redirect
from django.contrib import messages
from .models import *
# Create your views here.
def signin(request):
    if request.method == "POST":
        username = request.POST['inputUser']
        password = request.POST['inputPassword']
        try:
            user = User.objects.get(username=username,password=password)
            if user is not None :
                return redirect('')
        except:
            messages.info(request,"username หรือ password ไม่ถูกต้อง")
    return render(request,'signin.html')

def usermanage(request):
    if request.method == "POST":
        username = request.POST['username']
        update_role=request.POST['select_role']
        user = User.objects.get(username=username)
        user.role = update_role
        user.save()
        print(user.update_date)

    roles = Role.objects.all()
    users = User.objects.all()
    context = {'users':users,
               'roles':roles}
    return render(request,'usermanage.html',context)
