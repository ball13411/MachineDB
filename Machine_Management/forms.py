from django import forms
from .models import *

from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from datetime import datetime
import datetime


class MachineForm(forms.ModelForm):
    serial_id = forms.CharField(label='หมายเลขซีเรียล : ', widget=forms.TextInput(attrs={"maxlength": 50}))
    machine_production_line_code = forms.CharField(label='รหัสไลน์ผลิตและเครื่องจักร : ', widget=forms.TextInput(attrs={"placeholder": "", "maxlength": 20}))
    machine_name = forms.CharField(label='ชื่อเครื่องจักร : ', required=False, widget=forms.TextInput(attrs={"placeholder": "", "maxlength": 50}))
    machine_brand = forms.CharField(label='แบรนด์เครื่องจักร : ', required=False, widget=forms.TextInput(attrs={"placeholder": "", "maxlength": 10}))
    machine_model = forms.CharField(label='โมเดลเครื่องจักร : ', required=False, widget=forms.TextInput(attrs={"placeholder": "", "maxlength": 10}))
    machine_supplier_code = forms.CharField(label='รหัสผู้จำหน่ายเครื่องจักร : ', required=False, widget=forms.TextInput(attrs={"placeholder":"", "maxlength": 10}))
    machine_location_id = forms.CharField(label='รหัสตำแหน่งเครื่อง : ', required=False,widget=forms.TextInput(attrs={"placeholder":"", "maxlength": 10}))
    machine_emp_id_response = forms.CharField(label='Machine emp id response : ', required=False,widget=forms.TextInput(attrs={"placeholder": "", "maxlength": 15}))
    machine_capacity_per_minute = forms.CharField(label='กำลังการผลิตเครื่อง (ชิ้น/นาที) : ', required=False,widget=forms.TextInput(attrs={"placeholder": "", "maxlength": 10}))
    machine_capacity_measure_unit = forms.CharField(label='หน่วยวัดความจุเครื่อง : ', required=False,widget=forms.TextInput(attrs={"placeholder": "", "maxlength": 10}))
    machine_power_use_watt_per_hour = forms.CharField(label='กำลังเครื่องจักร (วัตต์/ชม.) : ', required=False,widget=forms.TextInput(attrs={"placeholder": "", "maxlength": 10}))
    machine_installed_datetime = forms.DateField(label='วันที่ติดตั้งเครื่องจักร', required=False, widget=forms.DateInput(attrs={"type": "date"}))
    machine_start_use_datetime = forms.DateField(label='วันที่เริ่มใช้งาน', required=False, widget=forms.DateInput(attrs={"type": "date"}))
    line = forms.ModelChoiceField(label='ไลน์ผลิดเครื่องจักร', queryset=Production_line.objects.all(), widget=forms.Select(attrs={"class": "custom-select"}))
    mch_type = forms.ModelChoiceField(label='ประเภทเครื่องจักร', queryset=Machine_type.objects.all(), widget=forms.Select(attrs={"class": "custom-select"}))
    sub_type = forms.ModelChoiceField(label='ชนิดเครื่องจักร', queryset=Machine_subtype.objects.all(), widget=forms.Select(attrs={"class": "custom-select"}))

    class Meta:
        model = Machine
        fields = [
            'serial_id',
            'machine_production_line_code',
            'machine_name',
            'machine_brand',
            'machine_model',
            'machine_supplier_code',
            'machine_location_id',
            'machine_emp_id_response',
            'machine_capacity_per_minute',
            'machine_capacity_measure_unit',
            'machine_power_use_watt_per_hour',
            'machine_installed_datetime',
            'machine_start_use_datetime',
            'line',
            'mch_type',
            'sub_type'
        ]

    def clean_machine_code(self,*args,**kwargs):
        machine_production_line_code = self.cleaned_data.get("machine_production_line_code")
        if "mch" not in machine_production_line_code:
            raise forms.ValidationError("This is not 'mch'")
        return machine_production_line_code

class ProductLineForm(forms.ModelForm):
    class Meta:
        model = Production_line
        fields = [
            'pid',
            'production_line',
            'location_site',
            'location_building',
            'location_floor'
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location_building'].queryset = Building.objects.none()
        if 'location_site' in self.data:
            try:
                location_site_id = int(self.data.get('location_site'))
                self.fields['location_building'].queryset = Building.objects.filter(site_id=location_site_id).order_by('production_line')
            except (ValueError,TypeError):
                pass
        elif self.instance.pk:
            self.fields['location_building'].queryset = self.instance.location_site.location_building_set.order_by('production_line')

class UserForm(forms.ModelForm):
    username = forms.CharField(label='Username : ',widget=forms.TextInput(attrs={"maxlength":6}))
    firstname = forms.CharField(label='First name : ',widget=forms.TextInput(attrs={"maxlength":20}))
    lastname = forms.CharField(label='Last name : ',widget=forms.TextInput(attrs={"maxlength":20}))
    password = forms.CharField(label='password : ',widget=forms.TextInput(attrs={"maxlength":15,"type":"password"}))
    email = forms.CharField(label='Email : ',widget=forms.TextInput(attrs={"maxlength":30,"type":"email"}))
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type":"date"}))
    con_password = forms.CharField(label='confirm password : ',widget=forms.TextInput(attrs={"maxlength":15,"type":"password"}))
    create_by = ""
    now = datetime.datetime.now()
    create_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type":"datetime","value":now}))
    expired_date = forms.DateField(label='expired date : ',widget=forms.TextInput(attrs={"type":"date","value":(now - datetime.timedelta(1)).date()}))
    class Meta:
        model = User
        fields = [
            'username',
            'firstname',
            'lastname',
            'password',
            'email',
            'start_date',
            'create_by',
            'expired_date',
            'expired_day',
            'create_date',
            'role',
        ]

class AddUserForm(forms.ModelForm):

    add_username = forms.CharField(max_length=6)
    add_email = forms.EmailField()

    add_password = forms.CharField(widget=forms.PasswordInput)
    add_cfpassword = forms.CharField(widget=forms.PasswordInput)

    # write the name of models for which the form is made
    class Meta:
        model = User

        # Custom fields
        #fileds = '__all__'
        fields = ['add_username','add_email','add_password','add_cfpassword']

    # this function will be used for the validation
    def clean(self):

        super(AddUserForm, self).clean()

        username = self.cleaned_data.get('add_username')
        email = self.cleaned_data.get('add_email')
        password = self.cleaned_data.get('add_password')
        cfpassword = self.cleaned_data.get('add_cfpassword')

        userid = User.objects.filter(username=username)
        if userid.count():
            raise ValidationError("Username already exists")

        mail = User.objects.filter(email=email)

        if mail.count():
            raise ValidationError("Email already exists")

        if password and cfpassword and password != cfpassword:
            raise ValidationError("Password don't match")

        return self.cleaned_data
