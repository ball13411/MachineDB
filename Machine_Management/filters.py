import django_filters
from .models import Machine, Machine_type, Machine_subtype, Production_line
from django import forms


def mtype(request):
    if request is None:
        return Machine.objects.none()
    mch_type = request.Machine.subtype
    print(mch_type)
    return mch_type.mtype_set.all()


class MachineFilter(django_filters.FilterSet):
    machine_production_line_code = django_filters.CharFilter(field_name="machine_production_line_code", label='รหัสไลน์และเครื่องจักร')
    mch_type = django_filters.ModelChoiceFilter(queryset=Machine_type.objects.all(), label='ประเภทเครื่องจักร')
    sub_type = django_filters.ModelChoiceFilter(queryset=Machine_subtype.objects.all(), label='ชนิดเครื่องจักร')
    line = django_filters.ModelChoiceFilter(queryset=Production_line.objects.all(), label='ไลน์ผลิต')


    class Meta:
        model = Machine
        fields = [
            'machine_production_line_code'
        ]
