from mongoengine import *


class UserModel(Document):
    phone_number = StringField(unique=True)
    password = StringField()
    device_id = StringField()
    name = StringField()
    class_number = StringField()
    id_number = StringField()
    comment = StringField()
    is_admin = BooleanField(default=False)
    last_login_time = DateTimeField()
    date_joined = DateTimeField()

    def __str__(self):
        return self.phone_number


class UserLogModel(Document):
    data_time = DateTimeField()
    phone_number = StringField()
    ip = StringField()
    action = StringField(choices=(('0', '下线'), ('1', '上线'), ('2', '验证失败')))

if __name__ == '__main__':
    connect('lab_safety')
    # import datetime
    # userlog = UserLogModel()
    # userlog.data_time = datetime.datetime.now()
    # userlog.phone_number = '18300864707'
    # userlog.ip = '127.0.0.1'
    # userlog.action = '1'
    # userlog.save()
#     user = UserModel()
#     user.phone_number = '18300864707'
#     user.password = '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'
#     user.name = '用户2'
#     user.is_admin = True
#     user.device_id = '888'
    # user.save()



# from djongo import models
#
# from django.db import models
# from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
#
#
# class UserProfileManager(BaseUserManager):
#     use_in_migrations = True
#
#     def _create_user(self, phone_number, password, **extra_fields):
#         if not phone_number:
#             raise ValueError('The given phone_number must be set')
#
#         user = self.model(phone_number=phone_number, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_user(self, phone_number, password=None, **extra_fields):
#         extra_fields.setdefault('is_superuser', False)
#         return self._create_user(phone_number, password, **extra_fields)
#
#     def create_superuser(self, phone_number, password, **extra_fields):
#         extra_fields.setdefault('is_superuser', True)
#
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')
#
#         return self._create_user(phone_number, password, **extra_fields)
#
#
# class UserProfile(AbstractBaseUser, PermissionsMixin):
#
#     phone_number = models.CharField(verbose_name="手机号码", max_length=15, unique=True)
#     device_password = models.CharField(verbose_name="密码", max_length=50)
#     name = models.CharField(verbose_name="姓名", max_length=20)
#     class_number = models.CharField(verbose_name='班级', max_length=20)
#     id_number = models.CharField(verbose_name="学号", max_length=20)
#
#     comment = models.CharField(verbose_name="备注", max_length=255)
#
#     objects = UserProfileManager()
#
#     USERNAME_FIELD = 'phone_number'
#
#     def __str__(self):
#         return self.phone_number
#
#     class Meta:
#         verbose_name = "用户"
#         verbose_name_plural = verbose_name
#         ordering = ['name']
#
#
# class UserLog(models.Model):
#     data_time = models.DateTimeField(db_column="data_time", verbose_name="时间")
#     # phone_number = models.CharField(db_column="phone_number", verbose_name="手机号码", max_length=15)
#     phone_number = models.CharField(max_length=15)
#     ip = models.CharField(db_column="ip", verbose_name="IP地址", max_length=25)
#
#     class Meta:
#         verbose_name = "用户日志"
#         verbose_name_plural = verbose_name

