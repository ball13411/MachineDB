from django.db import models

# Create your models here.

class Screen(models.Model):
    screen_id = models.CharField(max_length=6,primary_key=True)
    screen_name = models.CharField(max_length=15)
    file_py = models.CharField(max_length=10)
    file_html = models.CharField(max_length=10)
    class Meta:
        db_table = "Screen"

class Role(models.Model):
    role_id = models.CharField(max_length=5,primary_key=True)
    role_name = models.CharField(max_length=15)
    screen = models.ManyToManyField(Screen)
    def __str__(self):
        return self.role_name
    class Meta:
        db_table = "Role"

class Production_line(models.Model):
    line_id = models.CharField(max_length=6,primary_key=True)
    def __str__(self):
        return self.line_id
    class Meta:
        db_table = "Production_line"

class Machine(models.Model):
    machine_code = models.CharField(max_length=10)
    machine_name = models.CharField(max_length=20)
    machine_type = models.CharField(max_length=10)
    line = models.ForeignKey(Production_line,on_delete=models.CASCADE)
    class Meta:
        db_table = "Machine"

class User(models.Model):
    username = models.CharField(max_length=6,primary_key=True)
    firstname = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    password = models.CharField(max_length=15)
    email = models.CharField(max_length=30)
    create_by = models.CharField(max_length=6)
    create_date = models.DateTimeField()
    start_date = models.DateField()
    expired_date = models.DateField()
    expired_day = models.IntegerField(default=90)
    role = models.ForeignKey(Role,on_delete=models.CASCADE)
    update_by = models.CharField(max_length=6,default=None,null=True)
    update_date = models.DateTimeField(default=None,null=True)
    last_login_date = models.DateTimeField(default=None,null=True)
    production = models.ManyToManyField(Production_line)
    class Meta:
        db_table = "User"






