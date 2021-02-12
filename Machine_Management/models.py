from django.db import models
import datetime

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
        ordering = ["location_site", "location_building", "production_line"]


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
    spare_part_model = models.CharField(max_length=40, blank=True)
    spare_part_brand = models.CharField(max_length=40, blank=True)
    service_life = models.PositiveIntegerField(default=None, null=True)
    service_plan_life = models.PositiveIntegerField(default=None, null=True)
    spare_part_type = models.ForeignKey(Spare_part_type, on_delete=models.CASCADE)
    spare_part_sub_type = models.ForeignKey(Spare_part_sub_type, on_delete=models.CASCADE)
    create_by = models.CharField(max_length=20)
    create_date = models.DateField()
    last_update_by = models.CharField(max_length=20, default=None, null=True)
    last_update_date = models.DateField(default=None, null=True)
    spare_part_active = models.BooleanField(default=True)
    spare_part_group = models.ForeignKey(Spare_part_group, on_delete=models.CASCADE)
    spare_part_detail = models.TextField(blank=True, default=None, null=True)

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
    machine_power_use_kwatt_per_hour = models.FloatField(max_length=10, blank=True)
    machine_installed_datetime = models.DateField(default=None, null=True)
    machine_start_use_datetime = models.DateField(default=None, null=True)
    machine_hour = models.IntegerField(default=None, null=True, blank=True)
    machine_hour_last_update = models.IntegerField(default=None, null=True, blank=True)
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
    machine_hour_update_date = models.DateField(default=None, null=True)
    machine_asset_code = models.CharField(max_length=30, default=None, null=True)

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


class Machine_sparepart(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    spare_part = models.ForeignKey(Spare_part, on_delete=models.CASCADE)
    last_mtnchng_hour = models.IntegerField(blank=True, default=None, null=True)
    last_mtnchk_hour = models.IntegerField(blank=True, default=None, null=True)
    mtnchng_life_hour = models.IntegerField(blank=True, default=None, null=True)
    mtnchk_life_hour = models.IntegerField(blank=True, default=None, null=True)
    next_mtnchng_hour = models.IntegerField(blank=True, default=None, null=True)
    next_mtnchk_hour = models.IntegerField(blank=True, default=None, null=True)
    last_mtnchng_job_id = models.IntegerField(blank=True, default=None, null=True)
    last_mtnchk_job_id = models.IntegerField(blank=True, default=None, null=True)
    gen_mtnchng_date = models.DateField(blank=True, default=None, null=True)
    gen_mtnchk_date = models.DateField(blank=True, default=None, null=True)
    warning_hour = models.IntegerField(blank=True, default=None, null=True)

    class Meta:
        db_table = "Machine_Sparepart"
        ordering = ["machine", "spare_part"]


class Department(models.Model):
    department_code = models.CharField(max_length=30, unique=True)
    department_name = models.CharField(max_length=40, default=None, null=True)
    create_by = models.CharField(max_length=10, default=None, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_by = models.CharField(max_length=10, default=None, null=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Department"
        ordering = ["department_code"]


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
    user_active = models.BooleanField(default=True)
    departments = models.ManyToManyField(Department, through='User_and_department')

    class Meta:
        db_table = "User_management"


class User_and_department(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    is_inform = models.BooleanField(default=None, null=True)
    is_inspect = models.BooleanField(default=None, null=True)
    is_approve = models.BooleanField(default=None, null=True)
    is_receive = models.BooleanField(default=None, null=True)
    is_assign = models.BooleanField(default=None, null=True)
    is_report = models.BooleanField(default=None, null=True)
    is_verify = models.BooleanField(default=None, null=True)
    is_close = models.BooleanField(default=None, null=True)

    class Meta:
        db_table = "User_department"
        ordering = ["department__department_code", "user__firstname"]


class Maintenance_job(models.Model):
    job_no = models.CharField(max_length=25, unique=True)
    job_gen_date = models.DateField(auto_now_add=True)
    job_assign_user = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE, related_name='+')
    job_response_user = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE, related_name='+')
    job_assign_date = models.DateField(default=None, null=True)
    job_mtn_type = models.CharField(max_length=20, default=None, null=True)
    job_result_type = models.CharField(max_length=20, default=None, null=True)
    job_result_description = models.TextField(default=None, null=True)
    job_fix_plan_hour = models.IntegerField(default=None, null=True)
    job_mch_hour = models.IntegerField(default=None, null=True)
    job_plan_hour = models.IntegerField(default=None, null=True)
    job_report_date = models.DateField(default=None, null=True)
    job_gen_user = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE, related_name='+')
    job_mch_sp = models.ForeignKey(Machine_sparepart, on_delete=models.CASCADE)
    problem_cause = models.TextField(default=None, null=True)
    corrective_action = models.TextField(default=None, null=True)
    after_repair = models.TextField(default=None, null=True)
    is_approve = models.BooleanField(default=False)
    job_status = models.CharField(max_length=30, default=None, null=True)
    job_remark = models.TextField(default=None, null=True)
    estimate_cost = models.PositiveIntegerField(default=None, null=True)
    equipment_code1 = models.TextField(default=None, null=True)
    equipment_code2 = models.TextField(default=None, null=True)
    equipment_code3 = models.TextField(default=None, null=True)
    equipment_detail1 = models.TextField(default=None, null=True)
    equipment_detail2 = models.TextField(default=None, null=True)
    equipment_detail3 = models.TextField(default=None, null=True)
    equipment_quantity1 = models.PositiveIntegerField(default=None, null=True)
    equipment_quantity2 = models.PositiveIntegerField(default=None, null=True)
    equipment_quantity3 = models.PositiveIntegerField(default=None, null=True)
    equipment_note1 = models.TextField(default=None, null=True)
    equipment_note2 = models.TextField(default=None, null=True)
    equipment_note3 = models.TextField(default=None, null=True)
    job_approve_date = models.DateField(default=None, null=True)

    class Meta:
        db_table = "maintenance_job"


class Repair_notice(models.Model):
    repair_no = models.CharField(max_length=25, unique=True)
    department_notifying = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='+')
    department_receive = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='+')
    maintenance_jobs = models.ManyToManyField(Maintenance_job)
    notification_date = models.DateField(default=None, null=True)
    problem_report = models.TextField(default=None, null=True)
    effect_problem = models.TextField(default=None, null=True)
    use_date = models.DateField(default=None, null=True)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    repair_status = models.CharField(max_length=30, default=None, null=True)
    repair_gen_date = models.DateField(auto_now_add=True)
    repair_close_date = models.DateField(default=None, null=True)
    repairer_user = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE, related_name='+')
    inspect_user = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE, related_name='+')
    approve_user = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE, related_name='+')
    receive_user = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE, related_name='+')
    inspect_remark = models.TextField(default=None, null=True)
    approve_remark = models.TextField(default=None, null=True)
    receive_remark = models.TextField(default=None, null=True)
    close_remark = models.TextField(default=None, null=True)
    is_cancel = models.BooleanField(default=None, null=True)
    is_inspect = models.BooleanField(default=None, null=True)
    is_approve = models.BooleanField(default=None, null=True)
    is_receive = models.BooleanField(default=None, null=True)
    is_close = models.BooleanField(default=None, null=True)

    class Meta:
        db_table = 'repair_notice'


def autoJobNumber():
    date_now = datetime.datetime.today()
    date_no = date_now.strftime('%y') + date_now.strftime('%m') + date_now.strftime('%d')
    last_no = Maintenance_job.objects.filter(job_no__startswith="MTN"+date_no).last()
    if not last_no:
        new_mtn_number = "MTN" + date_no + "001"
    else:
        job_no = last_no.job_no
        mtn_int = int(job_no.split(date_no)[-1])
        new_mtn_int = mtn_int + 1
        new_mtn_number = "MTN" + date_no + '{:03}'.format(new_mtn_int)
    return new_mtn_number


def genJobNumber():
    date_now = datetime.datetime.today()
    date_no = date_now.strftime('%y') + date_now.strftime('%m') + date_now.strftime('%d')
    last_no = Maintenance_job.objects.filter(job_no__startswith="RP-MTN"+date_no).last()
    if not last_no:
        new_mtn_number = "RP-MTN" + date_no + "001"
    else:
        job_no = last_no.job_no
        mtn_int = int(job_no.split(date_no)[-1])
        new_mtn_int = mtn_int + 1
        new_mtn_number = "RP-MTN" + date_no + '{:03}'.format(new_mtn_int)
    return new_mtn_number
