from mongoengine import *


class DeviceModel(Document):
    device_id = StringField(db_field='device_id', unique=True)
    status = BooleanField(db_field='status',
                         choices=((True, '上线'), (False, '下线')))
    date_joined = DateTimeField()
    comment = StringField(db_field='comment')

    def __str__(self):
        return self.device_id


class DeviceLogModel(Document):
    data_time = DateTimeField(db_field='data_time')
    device_id = StringField(db_field='device_id')
    action = StringField(db_field='action',
                         choices=(('0', '下线'), ('1', '上线'), ('2', '验证失败')))
    ip = StringField(db_field='ip')
    phone_number = StringField(db_field='phone_number')


if __name__ == '__main__':
    import datetime
    connect('lab_safety')
    # device = DeviceModel()
    # device.device_id = '999'
    # device.status = '1'
    # device.date_joined = datetime.datetime.now()
    # device.comment = '测试设备'
    # device.save()

    # bind = DeviceUserBindModel()
    # bind.phone_number = '13780292320'
    # bind.device_id = '888'
    # # bind.save()

    # log = DeviceLogModel()
    # log.data_time = datetime.datetime.now()
    # log.device_id = '888'
    # log.action = '0'
    # log.phone_number =


# from djongo import models
# from django.db import models
#
# from django.db import models
#
# class Device(models.Model):
#     device_id = models.CharField(db_column="device_id", verbose_name="设备号", max_length=5)
#     comment = models.CharField(db_column="comment", verbose_name="备注", max_length=255)
#
#     def __str__(self):
#         return self.device_id
#
#     class Meta:
#         verbose_name = "设备"
#         verbose_name_plural = verbose_name
#
#
# class DeviceLog(models.Model):
#     data_time = models.DateTimeField(db_column="data_time", verbose_name="时间")
#     device_id = models.CharField(max_length=5)
#     action = models.CharField(db_column="action", verbose_name='动作号', max_length=2,
#                               choices=(('0', '下线'), ('1', '上线'), ('2', '验证失败')))
#     ip = models.CharField(db_column='ip', verbose_name='IP地址', max_length=25)
#     phone_number = models.CharField(max_length=15)
#
#     class Meta:
#         verbose_name = "设备日志"
#         verbose_name_plural = verbose_name
#
#
# class DeviceUserBind(models.Model):
#     device_id = models.CharField(db_column="device_id", verbose_name="设备号", max_length=5)
#     phone_number = models.CharField(max_length=15)
#
#     class Meta:
#         verbose_name = "设备用户绑定记录"
#         verbose_name_plural = verbose_name
