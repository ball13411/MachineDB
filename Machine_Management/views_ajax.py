from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render
import ast


@csrf_exempt
def check_username(request):
    if request.method == 'POST':
        response_data = {}
        add_username = request.POST["add_username"]
        userid = User.objects.filter(username=add_username)
        user = None
        try:
            try:
                # we are matching the input again hardcoded value to avoid use of DB.
                # You can use DB and fetch value from table and proceed accordingly.
                if userid.count():
                    user = True

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e

            if not user:
                response_data["username_success"] = True
            else:
                response_data["username_success"] = False

        except Exception:
            response_data["username_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."

        return JsonResponse(response_data)


@csrf_exempt
def check_email(request):
    if request.method == 'POST':
        response_data = {}
        add_email = request.POST["add_email"]
        mail = User.objects.filter(email=add_email)
        email = None

        try:
            # we are matching the input again hardcoded value to avoid use of DB.
            # You can use DB and fetch value from table and proceed accordingly.
            if mail.count():
                email = True

        except ObjectDoesNotExist:
            pass
        except Exception as e:
            raise e

        if not email:
            response_data["email_success"] = True
        else:
            response_data["email_success"] = False

        return JsonResponse(response_data)


def load_building(request):
    site_id = request.GET.get('location_site_id')
    building = Building.objects.filter(site_id=site_id).all()
    context = {'building': building}
    return render(request, 'ajax_response/building_dropdown_list.html', context)


def load_floor(request):
    site_id = request.GET.get('location_site_id')
    building_id = request.GET.get('location_building_id')
    floors = Floor.objects.filter(building_id=building_id, site_id=site_id).all()
    context = {'floors': floors}
    return render(request, 'ajax_response/floor_dropdown_list.html', context)


@csrf_exempt
def check_role(request):
    if request.method == 'POST':
        response_data = {}
        add_roleid = request.POST["add_roleid"]
        roleid = Role.objects.filter(role_id=add_roleid)
        role = None
        try:
            try:
                # we are matching the input again hardcoded value to avoid use of DB.
                # You can use DB and fetch value from table and proceed accordingly.
                if roleid.count():
                    role = True  # alredy exist
                elif len(add_roleid) == 0:
                    role = None  # empty input
                else:
                    role = False  # avialble

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e

            if not role:
                response_data["role_success"] = True
            else:
                response_data["role_success"] = False
            if role is None:
                response_data["role_empty"] = True
        except Exception:
            response_data["role_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."

        return JsonResponse(response_data)


def load_machine_subtype(request):
    mch_type = request.GET.get('mch_type')
    mch_subtype = Machine_subtype.objects.filter(mch_type_id=mch_type).all()
    context = {'mch_subtype': mch_subtype}
    return render(request, 'ajax_response/ajax_machine_subtype.html', context)


@csrf_exempt
def check_serial(request):
    if request.method == 'POST':
        response_data = {}
        add_machine_serial = request.POST["add_serial"]
        add_brand = request.POST['add_brand']
        add_model = request.POST['add_model']
        serial = Machine.objects.filter(serial_id=add_machine_serial, machine_model=add_model, machine_brand=add_brand)

        if serial.count():
            serial_status = True  # alredy exist
        else:
            serial_status = False  # avialble

        if not serial_status:
            response_data["serial_success"] = True
        else:
            response_data["serial_success"] = False

        return JsonResponse(response_data)


@csrf_exempt
def check_machine_type_code(request):
    if request.method == 'POST':
        response_data = {}
        add_type_code = request.POST["add_type_code"]
        typeid = Machine_type.objects.filter(mtype_code=add_type_code)
        typecode = None

        try:
            try:
                if typeid.count():
                    typecode = True  # alredy exist
                elif len(add_type_code) == 0:
                    typecode = None  # empty input
                else:
                    typecode = False  # avialble

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e

            if not typecode:
                response_data["typecode_success"] = True
            else:
                response_data["typecode_success"] = False
            if typecode is None:
                response_data["typecode_empty"] = True

        except Exception:
            response_data["typecode_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."

        return JsonResponse(response_data)


@csrf_exempt
def check_screen_id(request):
    if request.method == 'POST':
        response_data = {}
        screen_id = request.POST["screen_id"]
        screen = Screen.objects.filter(screen_id=screen_id)
        screen_status = None
        try:
            try:
                # we are matching the input again hardcoded value to avoid use of DB.
                # You can use DB and fetch value from table and proceed accordingly.
                if screen.exists():
                    screen_status = True  # already exist
                elif len(screen_id) == 0:
                    screen_status = None  # empty input
                else:
                    screen_status = False  # avialble

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e
            if not screen_status:
                response_data["screen_status_success"] = True
            else:
                response_data["screen_status_success"] = False
            if screen_status is None:
                response_data["screen_status_empty"] = True

        except Exception:
            response_data["screen_status_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."
        return JsonResponse(response_data)


@csrf_exempt
def check_menu_id(request):
    if request.method == 'POST':
        response_data = {}
        menu_id = request.POST["menu_id"]
        menu = Menu.objects.filter(menu_id=menu_id)
        menu_status = None

        try:
            try:
                # we are matching the input again hardcoded value to avoid use of DB.
                # You can use DB and fetch value from table and proceed accordingly.
                if menu.exists():
                    menu_status = True  # already exist
                elif len(menu_id) == 0:
                    menu_status = None  # empty input
                else:
                    menu_status = False  # avialble

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e
            if not menu_status:
                response_data["menu_status_success"] = True
            else:
                response_data["menu_status_success"] = False
            if menu_status is None:
                response_data["menu_status_empty"] = True

        except Exception:
            response_data["menu_status_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."
        return JsonResponse(response_data)


@csrf_exempt
def check_org_code(request):
    if request.method == 'POST':
        response_data = {}
        org_code = request.POST["org_code"]
        organize = Organization.objects.filter(org_code=org_code)
        org_status = None

        try:
            try:
                # we are matching the input again hardcoded value to avoid use of DB.
                # You can use DB and fetch value from table and proceed accordingly.
                if organize.exists():
                    org_status = True  # already exist
                elif len(request.POST["org_code"]) == 0:
                    org_status = None  # empty input
                else:
                    org_status = False  # avialble

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e
            if not org_status:
                response_data["org_status_success"] = True
            else:
                response_data["org_status_success"] = False
            if org_status is None:
                response_data["org_status_empty"] = True

        except Exception:
            response_data["org_status_success"] = False
            response_data["msg"] = "Some error occurred. Please let Admin know."
        return JsonResponse(response_data)


@csrf_exempt
def check_machine_subtype_code(request):
    if request.method == 'POST':
        response_data = {}
        add_subtype_code = request.POST["add_subtype_code"]
        add_mch_type = request.POST['add_mch_type']
        subtype_id = Machine_subtype.objects.filter(subtype_code=add_subtype_code, mch_type_id=add_mch_type)

        if subtype_id.count():
            subtype_code = True  # alredy exist
        else:
            subtype_code = False  # avialble

        if not subtype_code:
            response_data["subtype_code_success"] = True
        else:
            response_data["subtype_code_success"] = False

        return JsonResponse(response_data)


def load_spare_part_subtype(request):
    sp_type_id = request.GET.get('sp_type_id')
    spare_part_sub_type = Spare_part_sub_type.objects.filter(spare_part_type_id=sp_type_id).all()
    context = {'spare_part_subtype': spare_part_sub_type}
    return render(request, 'ajax_response/ajax_spare_part_subtype.html', context)


def load_spare_part(request):
    sp_subtype_id = request.GET.get('sp_subtype_id')
    spare_part = Spare_part.objects.filter(spare_part_sub_type=sp_subtype_id).all()
    context = {'spare_part': spare_part}
    return render(request, 'ajax_response/ajax_spare_part.html', context)


@csrf_exempt
def ajax_dropdown_sp_type(request):
    if request.method == 'POST':
        if request.POST['filter_sp_type'] != "":
            sp_type = Spare_part_type.objects.filter(spare_part_group_id=request.POST['filter_sp_type'])
            data = serializers.serialize('json', sp_type)
        else:
            data = [{}]
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def ajax_dropdown_sp_subtype(request):
    if request.method == 'POST':
        if request.POST['filter_sp_subtype'] != "":
            sp_type = Spare_part_sub_type.objects.filter(spare_part_type_id=request.POST['filter_sp_subtype'])
            data = serializers.serialize('json', sp_type)
        else:
            data = [{}]
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def ajax_dropdown_sp(request):
    if request.method == 'POST':
        if request.POST['filter_sp'] != "":
            sp_type = Spare_part.objects.filter(spare_part_sub_type_id=request.POST['filter_sp'])
            data = serializers.serialize('json', sp_type)
        else:
            data = [{}]
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def check_spare_part_group_code(request):
    if request.method == 'POST':
        response_data = {}
        spare_group = Spare_part_group.objects.filter(spare_part_group_code=request.POST['add_code'])
        spare_group_code = None
        try:
            if spare_group.count():
                spare_group_code = True  # alredy exist
            elif len(request.POST['add_code']) == 0:
                spare_group_code = None  # empty input
            else:
                spare_group_code = False  # avialble

        except ObjectDoesNotExist:
            pass
        except Exception as e:
            raise e
        if not spare_group_code:
            response_data["spare_group_code_success"] = True
        else:
            response_data["spare_group_code_success"] = False
        if spare_group_code is None:
            response_data["spare_group_code_empty"] = True
        return JsonResponse(response_data)


@csrf_exempt
def check_spare_part_type_code(request):
    if request.method == 'POST':
        response_data = {}
        spare_type = Spare_part_type.objects.filter(spare_part_type_code=request.POST['add_code'], spare_part_group_id=request.POST['group_code'])
        if spare_type.count():
            spare_type_code = True  # alredy exist
        else:
            spare_type_code = False  # avialble
        if not spare_type_code:
            response_data["spare_type_code_success"] = True
        else:
            response_data["spare_type_code_success"] = False
        return JsonResponse(response_data)


@csrf_exempt
def check_spare_part_subtype_code(request):
    if request.method == 'POST':
        response_data = {}
        spare_subtype = Spare_part_sub_type.objects.filter(spare_part_sub_type_code=request.POST['add_subtype_code'], spare_part_type_id=request.POST['add_sp_type'])
        if spare_subtype.count():
            spare_subtype_code = True  # alredy exist
        else:
            spare_subtype_code = False  # avialble

        if not spare_subtype_code:
            response_data["spare_subtype_code_success"] = True
        else:
            response_data["spare_subtype_code_success"] = False
        return JsonResponse(response_data)


def load_machine_from_line(request):
    line_id = request.GET.get('line_id')
    machine = Machine.objects.filter(line_id=line_id).all()
    context = {'machine': machine}
    return render(request, 'ajax_response/ajax_machine.html', context)


def load_product(request):
    line_id = request.GET.get('line_id')
    product_all = Product.objects.filter(line_id=line_id).all()
    context = {'product_all': product_all}
    return render(request, 'ajax_response/ajax_product.html', context)


@csrf_exempt
def check_machine_product(request):
    if request.method == 'POST':
        try:
            response_data = {}
            machine_product = Machine_capacity.objects.filter(machine_id=request.POST['mch_id'],
                                                              product_id=request.POST['product_id'])
            machine_product_code = None
            try:
                if machine_product.count():
                    machine_product_code = True  # alredy exist
                elif len(request.POST['mch_id']) == 0 or len(request.POST['product_id']) == 0:
                    machine_product_code = None  # empty input
                else:
                    machine_product_code = False  # avialble

            except ObjectDoesNotExist:
                pass
            except Exception as e:
                raise e
            if not machine_product_code:
                response_data["data_code_success"] = True
            else:
                response_data["data_code_success"] = False
            if machine_product_code is None:
                response_data["data_code_empty"] = True
        except ValueError:
            pass
        return JsonResponse(response_data)


def load_selected_lines(request):
    input_line = request.GET['selected_lines']
    change_type = ast.literal_eval(input_line)
    machine_list = Machine.objects.filter(line__in=change_type)
    data = serializers.serialize('json', machine_list)
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def load_role_screen(request):
    role_id = request.POST['role_id']
    rs = Role_Screen.objects.filter(role_id=role_id).values_list('screen_id', flat="True")
    screen = Screen.objects.exclude(screen_id__in=rs)
    data = serializers.serialize('json', screen)
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def load_machine(request):
    sp_id = request.POST['spID']
    line_id = request.POST['lineID']
    sub_type_id = request.POST['subtypeID']
    machine_spare = Machine_sparepart.objects.filter(spare_part_id=sp_id).values_list('machine')
    machine = Machine.objects.filter(line_id=line_id, sub_type_id=sub_type_id).exclude(pk__in=machine_spare)
    data = serializers.serialize('json', machine)
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def load_machine_sparepart(request):
    machine_id = request.POST['machine_id']
    mch_sp = Machine_sparepart.objects.filter(machine_id=machine_id).values('spare_part_id')
    spare_part_of_mch = Spare_part.objects.filter(pk__in=mch_sp)
    data = serializers.serialize('json', spare_part_of_mch)
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def assign_check_user(request):
    machine_id = request.POST['machine_id']
    mch_sp = Machine_sparepart.objects.filter(machine_id=machine_id).values('spare_part_id')
    spare_part_of_mch = Spare_part.objects.filter(pk__in=mch_sp)
    data = serializers.serialize('json', spare_part_of_mch)
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def check_department_code(request):
    if request.method == 'POST':
        response_data = {}
        dep_code = request.POST["department_code"]
        department_model = Department.objects.filter(department_code=dep_code)
        if department_model.exists():
            response_data["department_success"] = False
        else:
            response_data["department_success"] = True

    return JsonResponse(response_data)


@csrf_exempt
def load_username(request):
    if request.method == 'POST':
        response_data = {}
        username = request.POST["username"]
        user_model = User.objects.get(pk=username)
        if user_model:
            response_data["user_success"] = True
            response_data["user_username"] = user_model.username
            response_data["user_firstname"] = user_model.firstname
            response_data["user_lastname"] = user_model.lastname
            response_data["user_email"] = user_model.email
        else:
            response_data["user_success"] = False

    return JsonResponse(response_data)


@csrf_exempt
def load_userInOrg(request):
    if request.method == 'POST':
        list_org = request.POST.getlist("list_org[]", [])
        user_model = User.objects.filter(org__in=list_org)
        if user_model:
            data = serializers.serialize('json', user_model, fields=["username", "firstname", "lastname"])
        else:
            data = {}

    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def load_department_name(request):
    data = {}
    if request.method == 'POST':
        department_code = request.POST["department_code"]
        dep_model = Department.objects.filter(department_code=department_code)
        if dep_model:
            data = serializers.serialize('json', dep_model, fields=["department_name"])

    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def load_round_username(request):
    if request.method == 'POST':
        response_data = {}
        round_engineer = request.POST["round_engineer"]
        round_user_model = User.objects.get(pk=round_engineer)

        if round_user_model:
            response_data["round_success"] = True
            response_data["round_username"] = round_user_model.username
            response_data["round_firstname"] = round_user_model.firstname
            response_data["round_lastname"] = round_user_model.lastname
        else:
            response_data["round_success"] = False

    return JsonResponse(response_data)


def load_spare_part_subtype2(request):
    sp_type_id = request.GET.get('sp_type_id')
    spare_part_sub_type = Spare_part_sub_type.objects.filter(spare_part_type_id=sp_type_id).all()
    context = {'spare_part_subtype': spare_part_sub_type}
    return render(request, 'ajax_response/ajax_spare_part_subtype2.html', context)
