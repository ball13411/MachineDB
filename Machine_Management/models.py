from django.db import models


# Create your models here.


class Screen(models.Model):
    screen_id = models.CharField(max_length=30, primary_key=True)
    screen_name = models.CharField(max_length=40)
    file_py = models.CharField(max_length=40)
    file_html = models.CharField(max_length=30)

    def __str__(self):
        return self.screen_id

    class Meta:
        db_table = "Screen_management"


class Menu(models.Model):
    menu_id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=40)
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
        return str(self.location_site) + " Line" + str(self.production_line)

    class Meta:
        db_table = "Production_line"
        ordering = ["location_site", "location_building","production_line"]


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
    mch_type = models.ForeignKey(Machine_type, on_delete=models.CASCADE)

    def __str__(self):
        return self.subtype_code

    class Meta:
        db_table = "Machine_subtype"


class Spare_part_group(models.Model):
    spare_part_group_id = models.AutoField(primary_key=True)
    spare_part_group_code = models.CharField(max_length=30)
    spare_part_group_name = models.CharField(max_length=40)
    create_by = models.CharField(max_length=20)
    create_date = models.DateField()
    last_update_by = models.CharField(max_length=20, default=None, null=True)
    last_update_date = models.DateField(default=None, null=True)

    def __str__(self):
        return self.spare_part_group_name

    class Meta:
        db_table = "Spare_part_group"


class Spare_part_type(models.Model):
    spare_part_type_id = models.AutoField(primary_key=True)
    spare_part_type_code = models.CharField(max_length=30)
    spare_part_type_name = models.CharField(max_length=40)
    spare_part_group = models.ForeignKey(Spare_part_group, on_delete=models.CASCADE)
    create_by = models.CharField(max_length=20)
    create_date = models.DateField()
    last_update_by = models.CharField(max_length=20, default=None, null=True)
    last_update_date = models.DateField(default=None, null=True)

    def __str__(self):
        return self.spare_part_type_name

    class Meta:
        db_table = "Spare_part_type"


class Spare_part_sub_type(models.Model):
    spare_part_sub_type_id = models.AutoField(primary_key=True)
    spare_part_sub_type_code = models.CharField(max_length=30)
    spare_part_sub_type_name = models.CharField(max_length=40)
    spare_part_type = models.ForeignKey(Spare_part_type, on_delete=models.CASCADE)
    create_by = models.CharField(max_length=20)
    create_date = models.DateField()
    last_update_by = models.CharField(max_length=20, default=None, null=True)
    last_update_date = models.DateField(default=None, null=True)

    def __str__(self):
        return self.spare_part_sub_type_name

    class Meta:
        db_table = "Spare_part_sub_type"
        ordering = ["spare_part_type"]


class Spare_part(models.Model):
    spare_part_id = models.AutoField(primary_key=True)
    spare_part_name = models.CharField(max_length=40, blank=True)
    spare_part_code = models.CharField(max_length=40, blank=True)
    spare_part_model = models.CharField(max_length=40, blank=True)
    spare_part_brand = models.CharField(max_length=40, blank=True)
    spare_part_serial = models.CharField(max_length=40, blank=True)
    service_life = models.IntegerField()
    service_plan_life = models.IntegerField()
    spare_part_type = models.ForeignKey(Spare_part_type, on_delete=models.CASCADE)
    spare_part_sub_type = models.ForeignKey(Spare_part_sub_type, on_delete=models.CASCADE)
    create_by = models.CharField(max_length=20)
    create_date = models.DateField()
    last_update_by = models.CharField(max_length=20, default=None, null=True)
    last_update_date = models.DateField(default=None, null=True)
    spare_part_active = models.BooleanField()
    spare_part_group = models.ForeignKey(Spare_part_group, on_delete=models.CASCADE)

    def __str__(self):
        return self.spare_part_name

    class Meta:
        db_table = "Spare_part"


class Machine(models.Model):
    machine_id = models.AutoField(primary_key=True)
    serial_id = models.CharField(max_length=50, default=None, null=True)
    machine_production_line_code = models.CharField(max_length=30, default=None, null=True)
    machine_name = models.CharField(max_length=50, blank=True)
    machine_brand = models.CharField(max_length=50, blank=True)
    machine_model = models.CharField(max_length=50, blank=True)
    machine_supplier_code = models.CharField(max_length=50, blank=True)
    machine_supplier_name = models.CharField(max_length=50, blank=True)
    machine_supplier_contact = models.CharField(max_length=50, blank=True)
    machine_eng_emp_id = models.CharField(max_length=50, blank=True)
    machine_eng_emp_name = models.CharField(max_length=50, blank=True)
    machine_eng_emp_contact = models.CharField(max_length=50, blank=True)
    machine_pro_emp_id = models.CharField(max_length=50, blank=True)
    machine_pro_emp_name = models.CharField(max_length=50, blank=True)
    machine_pro_emp_contact = models.CharField(max_length=50, blank=True)
    machine_load_capacity = models.CharField(max_length=10, blank=True)
    machine_load_capacity_unit = models.CharField(max_length=10, blank=True)
    machine_power_use_kwatt_per_hour = models.FloatField(max_length=10, blank=True,)
    machine_installed_datetime = models.DateField(default=None, null=True)
    machine_start_use_datetime = models.DateField(default=None, null=True)
    machine_hour = models.IntegerField(default=None, null=True, blank=True)
    machine_minute = models.IntegerField(default=None, null=True, blank=True)
    create_by = models.CharField(max_length=20)
    create_date = models.DateField()
    last_update_by = models.CharField(max_length=20, default=None, null=True)
    last_update_date = models.DateField(default=None, null=True)
    line = models.ForeignKey(Production_line, on_delete=models.CASCADE)
    sub_type = models.ForeignKey(Machine_subtype, on_delete=models.CASCADE)
    mch_type = models.ForeignKey(Machine_type, on_delete=models.CASCADE)
    machine_image1 = models.FileField(upload_to='pictures/', blank=True, null=True)
    machine_image2 = models.FileField(upload_to='pictures/', blank=True, null=True)
    machine_image3 = models.FileField(upload_to='pictures/', blank=True, null=True)
    machine_image4 = models.FileField(upload_to='pictures/', blank=True, null=True)
    machine_image5 = models.FileField(upload_to='pictures/', blank=True, null=True)
    machine_document1 = models.FileField(upload_to='documents/', blank=True, null=True)
    machine_document2 = models.FileField(upload_to='documents/', blank=True, null=True)
    machine_document3 = models.FileField(upload_to='documents/', blank=True, null=True)
    machine_document4 = models.FileField(upload_to='documents/', blank=True, null=True)
    machine_document5 = models.FileField(upload_to='documents/', blank=True, null=True)
    machine_details = models.CharField(max_length=256, blank=True)
    machine_active = models.BooleanField()
    machine_core = models.BooleanField()

    class Meta:
        db_table = "Machine_master"
        ordering = ["machine_production_line_code"]


class Machine_capacity(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    fg_batch_size = models.IntegerField(default=None, null=True, blank=True)
    fg_batch_time = models.IntegerField(default=None, null=True, blank=True)
    rm_name = models.CharField(max_length=30)
    rm_batch_size = models.IntegerField(default=None, null=True, blank=True)
    rm_unit = models.CharField(max_length=20)
    fg_capacity = models.IntegerField(default=None, null=True, blank=True)

    class Meta:
        db_table = "Machine_capacity"


class Machine_and_spare_part(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    spare_part = models.ForeignKey(Spare_part, on_delete=models.CASCADE)
    last_maintenance_hour = models.IntegerField(default=None, null=True, blank=True)

    class Meta:
        db_table = "Machine_and_spare_part"
        ordering = ["machine", "spare_part"]


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
    update_by = models.CharField(max_length=10, default=None, null=True)
    update_date = models.DateTimeField(default=None, null=True)
    last_login_date = models.DateTimeField(default=None, null=True)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user_active = models.BooleanField()

    class Meta:
        db_table = "User_management"


class Maintenance_order_head(models.Model):
    job_id = models.AutoField(primary_key=True)
    job_no = models.IntegerField()
    job_date = models.DateField()
    job_assignor_id = models.CharField(max_length=10)
    job_assignee_id = models.CharField(max_length=10)
    job_status = models.BooleanField()
    close_reason = models.CharField(max_length=255)

    class Meta:
        db_table = "Maintenance_order_head"


class Maintenance_plan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    gen_date = models.DateField()
    machine_and_spare = models.ForeignKey(Machine_and_spare_part, on_delete=models.CASCADE)

    class Meta:
        db_table = "Maintenance_plan"


class Maintenance_order_detail(models.Model):
    mtn_order_id = models.AutoField(primary_key=True)
    plan_work_start = models.DateTimeField()
    plan_work_finish = models.DateTimeField()
    actual_work_start = models.DateTimeField()
    actual_work_finish = models.DateTimeField()
    remark = models.CharField(max_length=255)
    status = models.BooleanField()

    class Meta:
        db_table = "Maintenance_order_detail"
