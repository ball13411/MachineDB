from django.db import models

# Create your models here.


class Screen(models.Model):
    screen_id = models.CharField(max_length=15,primary_key=True)
    screen_name = models.CharField(max_length=20)
    file_py = models.CharField(max_length=30)
    file_html = models.CharField(max_length=20)
    def __str__(self):
        return self.screen_id
    class Meta:
        db_table = "Screen"

class Role(models.Model):
    role_id = models.CharField(max_length=5,primary_key=True)
    role_name = models.CharField(max_length=15)
    members = models.ManyToManyField(Screen,through='Role_Screen')
    def __str__(self):
        return self.role_id
    class Meta:
        db_table = "Role"

class Role_Screen(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    permission_insert = models.CharField(max_length=5)
    permission_update = models.CharField(max_length=5)
    permission_delete = models.CharField(max_length=5)
    class Meta:
        db_table = "Role_Screen"

class Production_line(models.Model):
    line_id = models.CharField(max_length=6,primary_key=True)
    def __str__(self):
        return self.line_id
    class Meta:
        db_table = "Production_line"

class Machine(models.Model):
    serial_id = models.CharField(max_length=10,default=None,null=True)
    machine_code = models.CharField(max_length=10,default=None,null=True)
    machine_name = models.CharField(max_length=20,default=None,null=True)
    machine_type = models.CharField(max_length=10,default=None,null=True)
    machine_brand = models.CharField(max_length=10,default=None,null=True)
    machine_model = models.CharField(max_length=10,default=None,null=True)
    machine_supplier_code = models.CharField(max_length=10,default=None,null=True)
    machine_location_id = models.CharField(max_length=10,default=None,null=True)
    machine_emp_id_response = models.CharField(max_length=15,default=None,null=True)
    machine_capacity_per_minute = models.CharField(max_length=10,default=None,null=True)
    machine_capacity_measure_unit = models.CharField(max_length=10,default=None,null=True)
    machine_power_use_watt_per_hour = models.CharField(max_length=10,default=None,null=True)
    machine_installed_datetime = models.DateField(default=None,null=True)
    machine_start_use_datetime = models.DateField(default=None,null=True)
    line = models.ForeignKey(Production_line,on_delete=models.CASCADE)
    class Meta:
        db_table = "Machine_master"

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






