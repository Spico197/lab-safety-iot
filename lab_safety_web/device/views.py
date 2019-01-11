import datetime

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from user.models import *
from device.models import *


def device(request):
    phone_number = request.session.get('phone_number', '')
    user = UserModel.objects.get(phone_number=phone_number)
    if user.is_admin:
        if user.device_id:
            device = DeviceModel.objects.get(device_id=user.device_id)
            status = device.status
            devices = DeviceModel.objects.all()
        else:
            device = '管理员设备'
            status = True
            devices = DeviceModel.objects.all()
    else:
        devices = DeviceModel.objects.filter(device_id=user.device_id)
        device = DeviceModel.objects.get(device_id=user.device_id)
        status = device.status

    # print(devices)

    status = 'offline' if status is False else 'online'

    limit = 11
    print(devices)
    paginator = Paginator(devices, limit)

    page = request.GET.get('page', 1)
    loaded = paginator.page(page)
    # print([dat.data_time for dat in devices[0:6]])

    context_data = {
        'name': user.name,
        'device_id': device.device_id,
        'device_status': status,
        'devices': loaded,
    }

    return render(request, 'device_base.html', context=context_data)


def log(request):
    phone_number = request.session.get('phone_number', '')
    user = UserModel.objects.get(phone_number=phone_number)
    if user.is_admin:
        if user.device_id:
            device = DeviceModel.objects.get(device_id=user.device_id)
            status = device.status
            logs = DeviceLogModel.objects.order_by('-data_time')
        else:
            device = '管理员设备'
            status = True
            logs = DeviceLogModel.objects.order_by('-data_time')
    else:
        logs = DeviceModel.objects.filter(device_id=user.device_id).order_by('-data_time')
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

    return render(request, 'device_log.html', context=context_data)


def new(request):
    phone_number = request.session.get('phone_number', '')
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
        context_data['return_instruction'] = "只有管理员才有权限新增设备！"
        return render(request, 'device_base.html', context=context_data)

    if request.POST.get('device_id', '') == '':
        context_data['return_instruction'] = "请注意，设备号不能为空"
        return render(request, 'device_base.html', context=context_data)

    dev_new = DeviceModel()
    dev_new.device_id = request.POST.get('device_id', '')
    dev_new.comment = request.POST.get('comment', '')
    dev_new.status = False
    dev_new.date_joined = datetime.datetime.now()
    dev_new.save()
    context_data['return_instruction'] = "保存成功"

    return render(request, 'device_new.html', context=context_data)


def edit(request):
    phone_number = request.session.get('phone_number', '')
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
        'edit_device_id': request.GET.get('device_id', ''),
        'edit_comment': device.comment,
    }

    if not user.is_admin:
        context_data['return_instruction'] = "只有管理员才有权限编辑设备！"
        return render(request, 'device_base.html', context=context_data)

    if request.POST:
        status = request.POST.get('status', '上线')

        dev = DeviceModel.objects.get(device_id=request.POST.get('edit_device_id', ''))
        dev.comment = request.POST.get('comment', '')
        dev.status = False if status == "下线" else True
        dev.save()

        context_data['return_instruction'] = "编辑成功"

    return render(request, 'device_edit.html', context=context_data)


def delete(request):
    phone_number = request.session.get('phone_number', '')
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
        return render(request, 'device_base.html', context=context_data)

    if request.GET.get('device_id', '') == '':
        context_data['return_instruction'] = "请注意，设备号不能为空"
        return render(request, 'device_base.html', context=context_data)

    DeviceModel.objects.filter(device_id=request.GET.get('device_id', '')).delete()
    context_data['return_instruction'] = "删除成功"
    # print('删除成功')
    return redirect('/device/device/')


def search(request):
    phone_number = request.session.get('phone_number', '')
    user = UserModel.objects.get(phone_number=phone_number)
    if user.is_admin:
        if user.device_id:
            device = DeviceModel.objects.get(device_id=user.device_id)
            status = device.status
            devices = DeviceModel.objects.filter(device_id=request.GET.get('device_id', ''))
        else:
            device = '管理员设备'
            status = True
            devices = DeviceModel.objects.filter(device_id=request.GET.get('device_id', ''))
    else:
        if request.GET.get('device_id', '') != user.device_id:
            devices = []
        else:
            devices = DeviceModel.objects.filter(device_id=user.device_id)
        device = DeviceModel.objects.get(device_id=user.device_id)
        status = device.status

    # print(devices)

    status = 'offline' if status is False else 'online'

    limit = 11
    # print(devices)
    paginator = Paginator(devices, limit)

    page = request.GET.get('page', 1)
    loaded = paginator.page(page)
    # print([dat.data_time for dat in devices[0:6]])

    context_data = {
        'name': user.name,
        'device_id': device.device_id,
        'device_status': status,
        'devices': loaded,
        'return_instruction': '',
    }

    if not devices:
        context_data['return_instruction'] = '您没有权限搜索设备或该设备不存在'

    return render(request, 'device_base.html', context=context_data)


def log_search(request):
    req_device_id = request.GET.get('device_id', '')
    req_action = request.GET.get('action', '')
    req_phone_number = request.GET.get('phone_number', '')
    filter_terms = {}
    if req_device_id:
        filter_terms['device_id'] = req_device_id
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
            logs = DeviceLogModel.objects.filter(**filter_terms).order_by('-data_time')
        else:
            device = '管理员设备'
            status = True
            logs = DeviceLogModel.objects.filter(**filter_terms).order_by('-data_time')
    else:
        logs = DeviceModel.objects.filter(**filter_terms).order_by('-data_time')
        device = DeviceModel.objects.get(device_id=user.device_id)
        status = device.status
        status = 'offline' if status is False else 'online'

        if req_device_id != user.device_id:
            logs = []
            context_data = {
                'name': user.name,
                'device_id': device.device_id,
                'device_status': status,
                'logs': logs,
                'return_instruction': '您无权查看其它设备的日志',
            }
            return render(request, 'device_log.html', context=context_data)

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
        'return_instruction': '',
    }

    return render(request, 'device_log.html', context=context_data)
