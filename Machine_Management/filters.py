import django_filters
from .models import Machine
from django import forms

class MachineFilter(django_filters.FilterSet):
    class Meta:
        model = Machine
        fields = [
            'machine_code','machine_name','machine_type','line'
        ]
