import django_filters
from .models import Machine,Machine_type
from django import forms

def mtype(request):
    if request is None:
        return Machine.objects.none()
    mch_type = request.Machine.subtype
    print(mch_type)
    return mch_type.mtype_set.all()

class MachineFilter(django_filters.FilterSet):
    # mType = django_filters.ModelChoiceFilter(queryset=Machine_type.objects.all())
    # print(Machine_type.objects.all())
    machine_name = django_filters.CharFilter()
    print(machine_name)
    # print(mTest)
    class Meta:
        model = Machine
        fields = [
            'machine_production_line_code','subtype','line'
        ]
