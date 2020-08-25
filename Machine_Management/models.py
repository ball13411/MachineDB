from django.db import models


# Create your models here.


class Screen(models.Model):
    screen_id = models.CharField(max_length=20, primary_key=True)
    screen_name = models.CharField(max_length=20)
    file_py = models.CharField(max_length=30)
    file_html = models.CharField(max_length=20)

    def __str__(self):
        return self.screen_id

    class Meta:
        db_table = "Screen_management"


class Menu(models.Model):
    menu_id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=30)
    level = models.IntegerField()
    parent_menu = models.CharField(max_length=30, default=None, null=True)
    index = models.IntegerField()
    path_url = models.CharField(max_length=30, default=None, null=True)
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)

    def __str__(self):
        return self.menu_id

    class Meta:
        db_table = "Menu_management"
        ordering = ["level", "parent_menu", "index"]


class Role(models.Model):
    role_id = models.CharField(max_length=20, primary_key=True)
    role_name = models.CharField(max_length=20)
    members = models.ManyToManyField(Screen, through='Role_Screen')

    def __str__(self):
        return self.role_id

    class Meta:
        db_table = "Role_management"


class Role_Screen(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    permission_insert = models.CharField(max_length=5)
    permission_update = models.CharField(max_length=5)
    permission_delete = models.CharField(max_length=5)

    class Meta:
        db_table = "Role_Screen"
        ordering = ["role"]


class Site(models.Model):
    site = models.CharField(max_length=30)

    def __str__(self):
        return self.site

    class Meta:
        db_table = "Site"


class Building(models.Model):
    building = models.CharField(max_length=30)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    def __str__(self):
        return self.building

    class Meta:
        db_table = "Building"


class Floor(models.Model):
    floor = models.CharField(max_length=20)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)

    def __str__(self):
        return self.floor

    class Meta:
        db_table = "Floor"
        ordering = ["site", "building", "floor"]


class Production_line(models.Model):
    pid = models.AutoField(primary_key=True)
    production_line = models.IntegerField()
    location_site = models.ForeignKey(Site, on_delete=models.CASCADE, blank=True, null=True)
    location_building = models.ForeignKey(Building, on_delete=models.CASCADE, blank=True, null=True)
    location_floor = models.ForeignKey(Floor, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.location_site) + " Line:" + str(self.production_line)

    class Meta:
        db_table = "Production_line"
        ordering = ["location_site", "location_building"]


class Product(models.Model):
    product_name = models.CharField(max_length=30)
    product_code = models.CharField(max_length=30)
    capacity = models.CharField(max_length=15)
    labour = models.CharField(max_length=10)
    line = models.ForeignKey(Production_line, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name

    class Meta:
        db_table = "Product"


class Organization(models.Model):
    org_id = models.AutoField(primary_key=True)
    org_code = models.CharField(max_length=25)
    org_name = models.CharField(max_length=50)
    org_line = models.ManyToManyField(Production_line)

    def __str__(self):
        return self.org_code

    class Meta:
        db_table = "Organization"


class Machine_type(models.Model):
    mtype_id = models.AutoField(primary_key=True)
    mtype_code = models.CharField(max_length=30)
    mtype_name = models.CharField(max_length=50)
    create_by = models.CharField(max_length=20)
    create_date = models.DateField()
    last_update_by = models.CharField(max_length=20, default=None, null=True)
    last_update_date = models.DateField(default=None, null=True)
    line = models.ForeignKey(Production_line, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.mtype_code

    class Meta:
        db_table = "Machine_type"


class Machine_subtype(models.Model):
    subtype_id = models.AutoField(primary_key=True)
    subtype_code = models.CharField(max_length=30)
    subtype_name = models.CharField(max_length=50)
    create_by = models.CharField(max_length=20)
    create_date = models.DateField()
    last_update_by = models.CharField(max_length=20, default=None, null=True)
    last_update_date = models.DateField(default=None, null=True)
    mchtype = models.ForeignKey(Machine_type, on_delete=models.CASCADE)

    def __str__(self):
        return self.subtype_code

    class Meta:
        db_table = "Machine_subtype"


class Machine(models.Model):
    machine_id = models.AutoField(primary_key=True)
    serial_id = models.CharField(max_length=50, default=None, null=True)
    machine_production_line_code = models.CharField(max_length=30, default=None, null=True)
    machine_name = models.CharField(max_length=50, default=None, null=True)
    machine_brand = models.CharField(max_length=10, default=None, null=True)
    machine_model = models.CharField(max_length=10, default=None, null=True)
    machine_supplier_code = models.CharField(max_length=10, default=None, null=True)
    machine_location_id = models.CharField(max_length=10, default=None, null=True)
    machine_emp_id_response = models.CharField(max_length=15, default=None, null=True)
    machine_capacity_per_minute = models.CharField(max_length=10, default=None, null=True)
    machine_capacity_measure_unit = models.CharField(max_length=10, default=None, null=True)
    machine_power_use_watt_per_hour = models.CharField(max_length=10, default=None, null=True)
    machine_installed_datetime = models.DateField(default=None, null=True)
    machine_start_use_datetime = models.DateField(default=None, null=True)
    line = models.ForeignKey(Production_line, on_delete=models.CASCADE)
    subtype = models.ForeignKey(Machine_subtype, on_delete=models.CASCADE)

    class Meta:
        db_table = "Machine_master"


class User(models.Model):
    username = models.CharField(max_length=10, primary_key=True)
    firstname = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    password = models.CharField(max_length=15)
    email = models.CharField(max_length=30)
    create_by = models.CharField(max_length=10)
    create_date = models.DateTimeField()
    start_date = models.DateField()
    expired_date = models.DateField()
    expired_day = models.IntegerField(default=90)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    update_by = models.CharField(max_length=6, default=None, null=True)
    update_date = models.DateTimeField(default=None, null=True)
    last_login_date = models.DateTimeField(default=None, null=True)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)

    class Meta:
        db_table = "User_management"
