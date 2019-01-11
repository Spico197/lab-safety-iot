from mongoengine import *

# Create your models here.

class DataModel(Document):
    data_time = DateTimeField(db_field='data_time')
    device_id = StringField(db_field='device_id')
    switch_status = BooleanField(db_field='switch_status', choices=((False, '关闭'), (True, '打开')))
    voltage_value = DecimalField(db_field='voltage_value', precision=4)
    current_value = DecimalField(db_field='current_value', precision=4)
    active_power_value = DecimalField(db_field='active_power_value', precision=4)
    total_active_power_value = DecimalField(db_field='total_active_power_value', precision=4)
    power_factor_value = DecimalField(db_field='power_factor_value', precision=3)
    co2_emission_value = DecimalField(db_field='co2_emission_value', precision=4)
    frequency_value = DecimalField(db_field='frequency_value', precision=2)
# FloatField()
# if __name__ == '__main__':
#     connect('lab_safety')
#     import datetime
#     data = DataModel()
#     data.data_time = datetime.datetime.now()
#     data.device_id = '888'
#     data.switch_status = '1'
#     data.voltage_value = 220.0001
#     data.current_value = 220.0001
#     data.active_power_value = 220.0001
#     data.total_active_power_value = 220.0001
#     data.power_factor_value = 220.0001
#     data.co2_emission_value = 220.0001
#     data.frequency_value = 220.0001
#     data.save()


# from djongo import models
#
# class Data(models.Model):
#     device_id = models.CharField(max_length=5, verbose_name='设备号')
#     data_time = models.DateTimeField(db_column='data_time', verbose_name='时间')
#     switch_status = models.CharField(db_column='switch_status', verbose_name='开关状态', max_length=2,
#                                      choices=(('0', '关闭'), ('1', '打开')))
#     voltage_value = models.DecimalField(db_column='voltage_value', verbose_name='电压值（V）', max_digits=10, decimal_places=4)
#     current_value = models.DecimalField(db_column='current_value', verbose_name='电流值（A）', max_digits=10, decimal_places=4)
#     active_power_value = models.DecimalField(db_column='active_power_value', verbose_name='有功功率（W）', max_digits=10, decimal_places=4)
#     total_active_power_value = models.DecimalField(db_column='total_active_power_value', verbose_name='有功总电量（KWH）', max_digits=10, decimal_places=4)
#     power_factor_value = models.DecimalField(db_column='power_factor_value', verbose_name='功率因数', max_digits=10, decimal_places=3)
#     co2_emission_value = models.DecimalField(db_column='co2_emission_value', verbose_name='二氧化碳排放量（kg）', max_digits=10, decimal_places=4)
#     frequency_value = models.DecimalField(db_column='frequency_value', verbose_name='频率（Hz）', max_digits=10, decimal_places=2)
#
#     class Meta:
#         verbose_name = "上传数据"
#         verbose_name_plural = verbose_name
