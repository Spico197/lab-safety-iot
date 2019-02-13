import hashlib
import datetime

# import pyecharts
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator
from pyecharts import Line

from user.models import *
from device.models import *
from data.models import *

# pyecharts.configure(
#     global_theme='roma'
# )

def sha256(password):
    return hashlib.sha256(password.encode()).hexdigest()


def page_not_found(request, exception, template_name="error-404.html"):
    # response = render_to_response('error-404.html')
    # response.status_code = 404
    # return response
    # return render(request, 'error-404.html')
    return render(request, template_name, status=404)


def page_error(request):
    return render(request, 'error-500.html', status=500)


def logout(request):
    log = UserLogModel()
    log.data_time = datetime.datetime.now()
    log.phone_number = request.session.get('phone_number', '')
    log.action = '0'

    if request.META.get('HTTP_X_FORWARDED_FOR', ''):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']

    log.ip = ip
    log.save()

    if request.session.get('phone_number', ''):
        request.session.flush()
    return redirect('/login/')


def login(request):
    context = {
        'title': "欢迎来到实验室用电信息统计平台"
    }
    if request.method == "POST":
        # print(request.POST)
        phone_number = request.POST.get('phone_number', '0')
        password = sha256(request.POST.get('password'))
        # print(UserModel.objects.all())
        users = UserModel.objects.filter(phone_number=phone_number)
        # print(users)
        if users:
            if users[0].password == password:
                context['title'] = "登录成功"
                request.session['phone_number'] = phone_number

                user = UserModel.objects.get(phone_number=phone_number)
                user.last_login_time = datetime.datetime.now()
                user.save()
                log = UserLogModel()
                log.data_time = datetime.datetime.now()
                log.phone_number = request.session.get('phone_number', '')
                log.action = '1'

                if request.META.get('HTTP_X_FORWARDED_FOR', ''):
                    ip = request.META['HTTP_X_FORWARDED_FOR']
                else:
                    ip = request.META['REMOTE_ADDR']

                log.ip = ip
                log.save()

                # print(request.POST.get('remember_me', 'off'))
                if request.POST.get('remember_me', 'off') == 'on':
                    request.session.set_expiry(3600*24*7)
                # return dashboard(request)
                return redirect('/dashboard/')
            else:
                log = UserLogModel()
                log.data_time = datetime.datetime.now()
                log.phone_number = request.POST.get('phone_number', '')
                log.action = '2'

                if request.META.get('HTTP_X_FORWARDED_FOR', ''):
                    ip = request.META['HTTP_X_FORWARDED_FOR']
                else:
                    ip = request.META['REMOTE_ADDR']

                log.ip = ip
                log.save()
                context['title'] = "密码错误"
        else:
            log = UserLogModel()
            log.data_time = datetime.datetime.now()
            log.phone_number = request.POST.get('phone_number', '')
            log.action = '2'

            if request.META.get('HTTP_X_FORWARDED_FOR', ''):
                ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                ip = request.META['REMOTE_ADDR']

            log.ip = ip
            log.save()
            context['title'] = "用户不存在"
    elif request.session.get('phone_number', ''):
        return redirect('/dashboard/')
    else:
        context['title'] = "欢迎来到实验室用电信息统计平台"
    return render(request, 'login_staradmin.html', context=context)


def dashboard(request):
    phone_number = request.session.get('phone_number', '')
    if phone_number == '':
        return redirect('/')
    user = UserModel.objects.get(phone_number=phone_number)
    time_delta = datetime.datetime.now() - datetime.datetime(2019, 1, 1)

    if user.is_admin:
        data = DataModel.objects.order_by('data_time')[0:51]

        user_number = UserModel.objects.count()
        device_number = DeviceModel.objects.count()
        data_number = DataModel.objects.count()

        if user.device_id:
            device = DeviceModel.objects.get(device_id=user.device_id)
            status = device.status
        else:
            device = '管理员设备'
            status = True
    else:
        user_number = UserModel.objects.filter(phone_number=phone_number).count()
        device_number = DeviceModel.objects.filter(device_id=user.device_id).count()
        data_number = DataModel.objects.filter(device_id=user.device_id).count()

        device = DeviceModel.objects.get(device_id=user.device_id)
        data = DataModel.objects.filter(device_id=device.device_id).order_by('data_time')[0:51]
        status = device.status

    status = 'offline' if status is False else 'online'

    attr = [str(dat.data_time).split('.')[0] for dat in data]
    current_values = [float(dat.current_value) for dat in data]
    active_power_values = [float(dat.active_power_value) for dat in data]
    total_active_power_values = [float(dat.total_active_power_value) for dat in data]

    line = Line("近50条数据", "电流、有功功率和有功总电量")
    line.add("电流", attr, current_values, is_fill=True, mark_point=["max", "min"])
    line.add("有功功率", attr, active_power_values, mark_point=["max", "min"])
    line.add("有功总电量", attr, total_active_power_values, mark_point=["max", "min"])

    # if user.is_admin:
    #     devices = DeviceModel.objects.filter(device_id=user.device_id)
    #     status = 'offline'
    #     if devices:
    #         status = devices[0].status
    #     else:
    #         status = 'online'

    # user_number = UserModel.objects.count()
    # device_number = DeviceModel.objects.count()
    # data_number = DataModel.objects.count()

    context_data = {
        'name': user.name,
        'device_id': user.device_id,
        'device_status': status,
        'instruction': '若系统使用时遇到问题，请及时向系统管理员进行反馈。谢谢大家的配合~',
        'user_number': user_number,
        'device_number': device_number,
        'running_days': time_delta.days,
        'data_number': data_number,
        'current_peak_value': max([dat.current_value for dat in data]) if len(data) > 0 else 0,
        'active_power_peak_value': max([dat.active_power_value for dat in data]) if len(data) > 0 else 0,
        'total_active_power_peak_value': max([dat.total_active_power_value for dat in data]) if len(data) > 0 else 0,
        'dashboard_chart': line.render_embed(),
    }
    # else:
    #     device = DeviceModel.objects.get(device_id=user.device_id)
    #     data = DataModel.objects.filter(device_id=device.device_id).order_by('data_time')[0:50]
    #     print(data)
    #
    #     attr = [str(dat.data_time).split('.')[0] for dat in data]
    #     current_values = [dat.current_value for dat in data]
    #     active_power_values = [dat.active_power_value for dat in data]
    #     total_active_power_values = [dat.total_active_power_value for dat in data]
    #
    #     line = Line("近50条数据", "电流、有功功率和有功总电量")
    #     # line.use_theme('macarons')
    #     line.add("电流", attr, current_values, is_fill=True, mark_point=["max", "min"])
    #     line.add("有功功率", attr, active_power_values, mark_point=["max", "min"])
    #     line.add("有功总电量", attr, total_active_power_values, mark_point=["max", "min"])
    #
    #     context_data = {
    #         'name': user.name,
    #         'device_id': user.device_id,
    #         'device_status': 'online' if device.status == '1' else 'offline',
    #         'instruction': '若系统使用时遇到问题，请及时向系统管理员进行反馈。谢谢大家的配合~',
    #         'user_number': 1,
    #         'device_number': 1,
    #         'running_days': time_delta.days,
    #         'data_number': len(data),
    #         'current_peak_value': max([dat.current_value for dat in data]),
    #         'active_power_peak_value': max([dat.active_power_value for dat in data]),
    #         'total_active_power_peak_value': max([dat.total_active_power_value for dat in data]),
    #         'dashboard_chart': line.render_embed(),
    #     }
        # print(line.get_js_dependencies())
    return render(request, 'dashboard_homepage.html', context=context_data)


def user(request):
    phone_number = request.session.get('phone_number', '')
    if phone_number == '':
        return redirect('/')
    user = UserModel.objects.get(phone_number=phone_number)
    if user.is_admin:
        if user.device_id:
            device = DeviceModel.objects.get(device_id=user.device_id)
            status = device.status
            users = UserModel.objects.all()
        else:
            device = '管理员设备'
            status = True
            users = UserModel.objects.all()
    else:
        users = UserModel.objects.filter(phone_number=phone_number)
        device = DeviceModel.objects.get(device_id=user.device_id)
        status = device.status

    # print(devices)

    status = 'offline' if status is False else 'online'

    limit = 11

    paginator = Paginator(users, limit)

    page = request.GET.get('page', 1)
    loaded = paginator.page(page)
    # print([dat.data_time for dat in devices[0:6]])

    context_data = {
        'name': user.name,
        'device_id': device.device_id,
        'device_status': status,
        'users': loaded,
    }

    return render(request, 'user_base.html', context=context_data)


def log(request):
    phone_number = request.session.get('phone_number', '')
    if phone_number == '':
        return redirect('/')
    user = UserModel.objects.get(phone_number=phone_number)
    if user.is_admin:
        if user.device_id:
            device = DeviceModel.objects.get(device_id=user.device_id)
            status = device.status
            logs = UserLogModel.objects.order_by('-data_time')
        else:
            device = '管理员设备'
            status = True
            logs = UserLogModel.objects.order_by('-data_time')
    else:
        logs = UserLogModel.objects.filter(phone_number=user.phone_number).order_by('-data_time')
        device = DeviceModel.objects.get(device_id=user.device_id)
        status = device.status

    status = 'offline' if status is False else 'online'

    limit = 10

    paginator = Paginator(logs, limit)

    page = request.GET.get('page', 1)
    loaded = paginator.page(page)
    # print([dat.data_time for dat in devices[0:6]])

    context_data = {
        'name': user.name,
        'device_id': device.device_id,
        'device_status': status,
        'logs': loaded,
    }

    return render(request, 'user_log.html', context=context_data)


def new(request):
    phone_number = request.session.get('phone_number', '')
    if phone_number == '':
        return redirect('/')
    user = UserModel.objects.get(phone_number=phone_number)
    if user.is_admin:
        if user.device_id:
            device = DeviceModel.objects.get(device_id=user.device_id)
            status = device.status
        else:
            device = '管理员设备'
            status = True
    else:
        device = DeviceModel.objects.get(device_id=user.device_id)
        status = device.status

    status = 'offline' if status is False else 'online'

    context_data = {
        'name': user.name,
        'device_id': user.device_id,
        'device_status': status,
        'return_instruction': '',
    }

    if request.method == "GET":
       return render(request, 'user_new.html', context=context_data)

    if not user.is_admin:
        context_data['return_instruction'] = "只有管理员才有权限新增用户！"
        return render(request, 'user_base.html', context=context_data)

    if request.POST.get('phone_number', '') == '':
        context_data['return_instruction'] = "请注意，电话号码不能为空"
        return render(request, 'user_base.html', context=context_data)

    try:
        device = DeviceModel.objects.get(device_id=request.POST.get('device_id', ''))
    except:
        context_data['return_instruction'] = "设备号不存在！"
        return render(request, 'user_base.html', context=context_data)

    user_new = UserModel()
    user_new.phone_number = request.POST.get('phone_number', '')
    user_new.device_id = request.POST.get('device_id', '')
    user_new.password = sha256(request.POST.get('password', ''))
    user_new.name = request.POST.get('name', '')
    user_new.class_number = request.POST.get('class_number', '')
    user_new.id_number = request.POST.get('id_number', '')
    user_new.is_admin = True if request.POST.get('is_admin', '') == '是' else False
    user_new.comment = request.POST.get('comment', '')
    user_new.date_joined = datetime.datetime.now()
    user_new.save()

    context_data['return_instruction'] = "保存成功"

    return render(request, 'user_new.html', context=context_data)


def edit(request):
    phone_number = request.session.get('phone_number', '')
    if phone_number == '':
        return redirect('/')
    user = UserModel.objects.get(phone_number=phone_number)
    if user.is_admin:
        if user.device_id:
            device = DeviceModel.objects.get(device_id=user.device_id)
            status = device.status
        else:
            device = '管理员设备'
            status = True
    else:
        device = DeviceModel.objects.get(device_id=user.device_id)
        status = device.status

    status = 'offline' if status is False else 'online'

    if request.method == "GET":
        edit_user = UserModel.objects.get(phone_number=request.GET.get('phone_number', ''))

        context_data = {
            'name': user.name,
            'device_id': user.device_id,
            'device_status': status,
            'return_instruction': '',
            'edit_phone_number': request.GET.get('phone_number', ''),
            'edit_device_id': edit_user.device_id,
            'edit_name': edit_user.name,
            'edit_class_number': edit_user.class_number,
            'edit_id_number': edit_user.id_number,
            'edit_comment': edit_user.comment,
        }

        if not user.is_admin:
            context_data['return_instruction'] = "只有管理员才有权限编辑用户！"
            return render(request, 'user_base.html', context=context_data)
        else:
            return render(request, 'user_edit.html', context=context_data)

    if request.POST:
        edit_user = UserModel.objects.get(phone_number=request.POST.get('edit_phone_number', ''))
        if request.POST.get('device_id', ''):
            try:
                dev = DeviceModel.objects.get(device_id=request.POST.get('device_id', ''))
            except:
                context_data = {}
                context_data['return_instruction'] = "设备不存在！"
                return render(request, 'user_edit.html', context=context_data)

        edit_user.device_id = request.POST.get('device_id', '')
        edit_user.name = request.POST.get('name', '')
        edit_user.class_number = request.POST.get('class_number', '')
        edit_user.id_number = request.POST.get('id_number', '')
        edit_user.is_admin = True if request.POST.get('is_admin', '') == '是' else False
        edit_user.comment = request.POST.get('comment', '')
        if request.POST.get('password', ''):
            edit_user.password = sha256(request.POST.get('password', ''))
        edit_user.save()

        context_data = {
            'name': user.name,
            'device_id': user.device_id,
            'device_status': status,
            'return_instruction': '',
            'edit_phone_number': request.GET.get('phone_number', ''),
            'edit_device_id': edit_user.device_id,
            'edit_name': edit_user.name,
            'edit_class_number': edit_user.class_number,
            'edit_id_number': edit_user.id_number,
            'edit_comment': edit_user.comment,
        }

        context_data['return_instruction'] = "编辑成功"

        return render(request, 'user_edit.html', context=context_data)


def delete(request):
    phone_number = request.session.get('phone_number', '')
    if phone_number == '':
        return redirect('/')
    user = UserModel.objects.get(phone_number=phone_number)
    if user.is_admin:
        if user.device_id:
            device = DeviceModel.objects.get(device_id=user.device_id)
            status = device.status
        else:
            device = '管理员设备'
            status = True
    else:
        device = DeviceModel.objects.get(device_id=user.device_id)
        status = device.status

    status = 'offline' if status is False else 'online'

    context_data = {
        'name': user.name,
        'device_id': user.device_id,
        'device_status': status,
        'return_instruction': '',
    }

    if not user.is_admin:
        context_data['return_instruction'] = "只有管理员才有权限删除设备！"
        return render(request, 'user_base.html', context=context_data)

    if request.GET.get('phone_number', '') == '':
        context_data['return_instruction'] = "请注意，手机号不能为空"
        return render(request, 'user_base.html', context=context_data)

    UserModel.objects.filter(phone_number=request.GET.get('phone_number', '')).delete()
    context_data['return_instruction'] = "删除成功"
    # print('删除成功')
    return redirect('/user/user/')


def search(request):
    phone_number = request.session.get('phone_number', '')
    if phone_number == '':
        return redirect('/')
    user = UserModel.objects.get(phone_number=phone_number)
    if user.is_admin:
        if user.device_id:
            device = DeviceModel.objects.get(device_id=user.device_id)
            status = device.status
            users = UserModel.objects.filter(phone_number=request.GET.get('phone_number', ''))
        else:
            device = '管理员设备'
            status = True
            users = UserModel.objects.filter(phone_number=request.GET.get('phone_number', ''))
    else:
        device = DeviceModel.objects.get(device_id=user.device_id)
        status = device.status
        if request.GET.get('phone_number', '') != user.phone_number:
            users = []
        else:
            users = UserModel.objects.filter(phone_number=user.phone_number)

    # print(devices)

    status = 'offline' if status is False else 'online'

    limit = 11

    paginator = Paginator(users, limit)

    page = request.GET.get('page', 1)
    loaded = paginator.page(page)
    # print([dat.data_time for dat in devices[0:6]])

    context_data = {
        'name': user.name,
        'device_id': device.device_id,
        'device_status': status,
        'users': loaded,
    }

    return render(request, 'user_base.html', context=context_data)


def log_search(request):
    req_action = request.GET.get('action', '')
    req_phone_number = request.GET.get('phone_number', '')
    if req_phone_number == '':
        return redirect('/')
    filter_terms = {}
    if req_action:
        filter_terms['action'] = req_action
    if req_phone_number:
        filter_terms['phone_number'] = req_phone_number

    phone_number = request.session.get('phone_number', '')
    user = UserModel.objects.get(phone_number=phone_number)
    if user.is_admin:
        if user.device_id:
            device = DeviceModel.objects.get(device_id=user.device_id)
            status = device.status
            logs = UserLogModel.objects.filter(**filter_terms).order_by('-data_time')
        else:
            device = '管理员设备'
            status = True
            logs = UserLogModel.objects.filter(**filter_terms).order_by('-data_time')
    else:
        logs = UserLogModel.objects.filter(phone_number=user.phone_number).order_by('-data_time')
        device = DeviceModel.objects.get(device_id=user.device_id)
        status = device.status
        if req_phone_number != user.phone_number:
            logs = []
            context_data = {
                'name': user.name,
                'device_id': device.device_id,
                'device_status': status,
                'logs': logs,
                'return_instruction': '您无权查看其它用户的日志',
            }
            return render(request, 'user_log.html', context=context_data)

    status = 'offline' if status is False else 'online'

    limit = 10

    paginator = Paginator(logs, limit)

    page = request.GET.get('page', 1)
    loaded = paginator.page(page)
    # print([dat.data_time for dat in devices[0:6]])

    context_data = {
        'name': user.name,
        'device_id': device.device_id,
        'device_status': status,
        'logs': loaded,
    }

    return render(request, 'user_log.html', context=context_data)
