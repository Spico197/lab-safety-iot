from django.shortcuts import render
from django.core.paginator import Paginator
from pyecharts import Line

from user.models import *
from data.models import *
from device.models import *


def charts(request):
    phone_number = request.session.get('phone_number')
    user = UserModel.objects.get(phone_number=phone_number)

    if user.is_admin:
        data = DataModel.objects.order_by('data_time')[0:21]
        if user.device_id:
            device = DeviceModel.objects.get(device_id=user.device_id)
            status = device.status
        else:
            device = '管理员设备'
            status = True
    else:
        device = DeviceModel.objects.get(device_id=user.device_id)
        data = DataModel.objects.filter(device_id=device.device_id).order_by('data_time')[0:21]
        status = device.status
    status = 'offline' if status is False else 'online'

    attr = [str(dat.data_time).split('.')[0] for dat in data]
    voltage_value = [float(dat.voltage_value) for dat in data]
    current_value = [float(dat.current_value) for dat in data]
    switch_status_value = [int(dat.switch_status) for dat in data]
    active_power_value = [float(dat.active_power_value) for dat in data]
    total_active_power_value = [float(dat.total_active_power_value) for dat in data]
    power_factor_value = [float(dat.power_factor_value) for dat in data]
    co2_emission_value = [float(dat.co2_emission_value) for dat in data]
    frequency_value = [float(dat.frequency_value) for dat in data]

    voltage = Line(height=200, width=400)
    voltage.add("电压值", attr, voltage_value)
    current = Line(height=200, width=400)
    current.add("电流值", attr, current_value)
    switch_status = Line(height=200, width=400)
    switch_status.add("开关状态", attr, switch_status_value)
    active_power = Line(height=200, width=400)
    active_power.add("有功功率", attr, active_power_value)
    total_active_power = Line(height=200, width=400)
    total_active_power.add("有功总电量", attr, total_active_power_value)
    power_factor = Line(height=200, width=400)
    power_factor.add("功率因数", attr, power_factor_value)
    co2_emission = Line(height=200, width=400)
    co2_emission.add("二氧化碳排放量", attr, co2_emission_value)
    frequency = Line(height=200, width=400)
    frequency.add("频率", attr, frequency_value)

    context_data = {
        'name': user.name,
        'device_id': device.device_id,
        'device_status': status,
        'voltage': voltage.render_embed(),
        'current': current.render_embed(),
        'switch_status': switch_status.render_embed(),
        'active_power': active_power.render_embed(),
        'total_active_power': total_active_power.render_embed(),
        'power_factor': power_factor.render_embed(),
        'co2_emission': co2_emission.render_embed(),
        'frequency': frequency.render_embed(),
    }

    return render(request, 'figures_base.html', context=context_data)

def tables(request):
    phone_number = request.session.get('phone_number', '')
    user = UserModel.objects.get(phone_number=phone_number)
    if user.is_admin:
        data = DataModel.objects.order_by('-data_time')
        if user.device_id:
            device = DeviceModel.objects.get(device_id=user.device_id)
            status = device.status
        else:
            device = '管理员设备'
            status = True
    else:
        data = DataModel.objects.filter(device_id=user.device_id).order_by('-data_time')
        device = DeviceModel.objects.get(device_id=user.device_id)
        status = device.status

    # for i in range(len(data)):
    #     year = data[i].data_time.year
    #     month = data[i].data_time.month
    #     day = data[i].data_time.day
    #     hour = data[i].data_time.hour
    #     minute = data[i].data_time.minute
    #     second = data[i].data_time.second
    #     # new_data[i]['time'] = "{}年{}月{}日 {:0>d}:{:0>d}:{:0>d}".format(year, month, day, hour, minute, second)
    #     # print(new_data[i]['time'])

    status = 'offline' if status is False else 'online'

    limit = 11

    paginator = Paginator(data, limit)

    page = request.GET.get('page', 1)
    loaded = paginator.page(page)
    print([dat.data_time for dat in data[0:6]])

    context_data = {
        'name': user.name,
        'device_id': device.device_id,
        'device_status': status,
        'data': loaded,
    }

    return render(request, 'tables_base.html', context=context_data)

def operation_log(request):
    pass
