import datetime

import jdatetime
from django.core.validators import MinValueValidator
from django.db import models
from django_jalali.db import models as jmodels
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from util.sms import send_sms


class Customer(models.Model):
    phone = models.PositiveBigIntegerField(unique=True, verbose_name='شماره تلفن')
    name = models.CharField(max_length=200, verbose_name='نام')
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'مشتری'
        verbose_name_plural = 'مشتری ها'


class Task(models.Model):
    customer_device = models.ForeignKey('CustomerDevice', on_delete=models.CASCADE, verbose_name='دستگاه',
                                        related_name='device_task', null=True, blank=True)
    customer = models.ForeignKey('Customer', unique=False, on_delete=models.CASCADE, null=True, blank=True,
                                 verbose_name='مشتری')
    serviceman = models.ForeignKey('Serviceman', unique=False, on_delete=models.CASCADE, null=True, blank=True,
                                   verbose_name='کاربر پذیرش')
    reception_datetime = jmodels.jDateField(default=datetime.datetime.now(), verbose_name='تاریخ پذیرش',
                                            editable=False)
    reception_datetime_m = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ میلادی')
    reception_no = models.BigAutoField(verbose_name='شماره پذیرش', primary_key=True,
                                       unique_for_date=reception_datetime_m)
    reception_choices = (
        ('1', 'حضوری'),
        ('2', 'آنلاین'),
    )
    reception_type = models.CharField(
        max_length=2,
        choices=reception_choices,
        default='1',
        verbose_name='نوع پذیرش'
    )

    type_choices = (
        ('1', 'تعمیر'),
        ('2', 'گارانتی'),
    )

    service_type = models.CharField(
        max_length=2,
        choices=type_choices,
        default='1',
        verbose_name='نوع خدمات'
    )

    deposit = models.CharField(max_length=200, verbose_name='بیعانه', null=True, blank=True, default=0)
    estimated_cost = models.CharField(max_length=200, verbose_name='هزینه حدودی', null=True, blank=True, default=0)
    preparation = jmodels.jDateField(default=datetime.datetime.now() + datetime.timedelta(days=3),
                                     verbose_name='زمان تحویل حدودی', null=True, blank=True)
    status_choices = (
        ('1', 'پذیرش شده'),
        ('2', 'در حال تعمیر'),
        ('3', 'آماده تحویل'),
        ('4', 'تحویل داده شده'),
    )

    status = models.CharField(
        max_length=2,
        choices=status_choices,
        default='1',
        verbose_name='وضعیت'
    )

    def save(self, *args, **kwargs):
        # self.reception_no = self.reception_datetime_m.strftime("%y%m%d%H%M%S") + str(self.pk)
        if self.status == '1':
            message = f"پذیرش شده"
        elif self.status == '2':
            message = 'در حال تعمیر'
        elif self.status == '3':
            message = 'آماده تحویل'
        elif self.status == '4':
            message = f"تحویل داده شده"
        else:
            message = 'نامشخص'

        try:
            send_sms(self, message)
            print('***********************sms************************')
        except:
            pass
        super(Task, self).save(*args, **kwargs)
        # raise Exception('sms not sent')

    def __str__(self):
        return str(
            self.reception_no)  # f"{self.customer_device.device.device_type.type_name} {self.customer.name} {self.reception_no}"

    class Meta:
        verbose_name = 'پذیرش'
        verbose_name_plural = 'لیست پذیرش'


class Serviceman(models.Model):
    serviceman = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name='نام سرویس دهنده', null=True,
                                   blank=True)

    def __str__(self):
        return self.serviceman.username


class Appearance(models.Model):
    appearance_problem = models.CharField(max_length=200, null=True, unique=True)

    def __str__(self):
        return self.appearance_problem


class Component(models.Model):
    component = models.CharField(max_length=200, verbose_name='قطعه', unique=True, blank=True, null=True)
    price = models.PositiveBigIntegerField(verbose_name='قیمت', blank=True, null=True)

    def __str__(self):
        return f'{self.component} - {self.price} تومان '


class ProblemType(models.Model):
    problem = models.CharField(max_length=200, verbose_name='عنوان مشکل', unique=True, blank=True, null=True)

    def __str__(self):
        return self.problem


class Problem(models.Model):
    problem = models.ForeignKey('ProblemType', on_delete=models.CASCADE, verbose_name='مشکل', null=True, blank=True,
                                related_name='problem_name')
    problem_detail = models.TextField(verbose_name='توضیحات', null=True, blank=True)
    component = models.ForeignKey('Component', on_delete=models.CASCADE, verbose_name='قطعه', null=True, blank=True)
    serviceman = models.ForeignKey('Serviceman', on_delete=models.CASCADE, verbose_name='سرویس دهنده', null=True,
                                   blank=True)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, verbose_name='مشکل', null=True, blank=True,
                             related_name='task_problem')
    device = models.PositiveSmallIntegerField(verbose_name='دستگاه', null=True, blank=True, default=1)
    status_choices = (
        ('1', 'پذیرش شده'),
        ('2', 'در دست انجام'),
        ('3', 'انجام شده'),
    )

    status = models.CharField(
        max_length=2,
        choices=status_choices,
        default='1',
        verbose_name='وضعیت'
    )

    # device = models.ForeignKey('CustomerDevice', on_delete=models.CASCADE, verbose_name='دستگاه', null=True,
    # blank=True, related_name='problem_device')

    class Meta:
        verbose_name = 'مشکل'
        verbose_name_plural = 'مشکلات'


class DeviceTypes(models.Model):
    type_name = models.CharField(max_length=200, verbose_name='نوع دستگاه', blank=True, null=True)

    def __str__(self):
        return self.type_name


class Brand(models.Model):
    brand_name = models.CharField(max_length=200, verbose_name='برند', blank=True, null=True)

    def __str__(self):
        return self.brand_name


class Device(models.Model):
    device_type = models.ForeignKey('DeviceTypes', on_delete=models.CASCADE, verbose_name='نوع دستگاه',
                                    blank=True, null=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, verbose_name='برند', blank=True, null=True)
    model = models.CharField(max_length=200, verbose_name='مدل', blank=True, null=True)

    def __str__(self):
        return f"{self.device_type.type_name} {self.brand.brand_name} {self.model}"

    class Meta:
        verbose_name = 'دستگاه'
        verbose_name_plural = 'دستگاه ها'


class Accessories(models.Model):
    accessory_name = models.CharField(max_length=200, verbose_name='لوازم همراه', null=True, blank=True)

    def __str__(self):
        return self.accessory_name

    class Meta:
        verbose_name = 'لوازم همراه'
        verbose_name_plural = 'لوازم همراه'


class CustomerDevice(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, blank=True,
                             related_name='customer_device_task')
    device = models.ForeignKey('Device', on_delete=models.CASCADE, verbose_name='دستگاه', null=True, blank=True)
    device_password = models.CharField(max_length=20, verbose_name='پسورد دستگاه', null=True, blank=True)
    device_serial_no = models.CharField(max_length=200, verbose_name='سریال دستگاه', null=True, blank=True)
    import_files = models.BooleanField(verbose_name='اطلاعات مهم', null=True, blank=True)
    import_files_detail = models.TextField(verbose_name='جزئیات اطلاعات مهم', null=True, blank=True)
    accessories = models.BooleanField(verbose_name='لوازم همراه', null=True, blank=True)
    accessories_detail = models.ForeignKey('Accessories',
                                           verbose_name='لوازم همراه', null=True, blank=True, on_delete=models.CASCADE)
    problem = models.ForeignKey("Problem", on_delete=models.CASCADE, verbose_name='مشکل دستگاه', null=True, blank=True)
    problem_detail = models.TextField(verbose_name='توضیحات', null=True, blank=True)
    appearance = models.ForeignKey('Appearance', on_delete=models.CASCADE, verbose_name='ظاهر', null=True, blank=True,
                                   default='سالم')
    appearance_detail = models.TextField(verbose_name='جزئیات ظاهر', null=True, blank=True)
    photo = models.ForeignKey('Photo', on_delete=models.CASCADE, null=True, blank=True, related_name='device_photo')

    def save(self, *args, **kwargs):
        if self.device:
            super(CustomerDevice, self).save(*args, **kwargs)
            task = Task.objects.get(reception_no=self.task.reception_no)
            task.customer_device = self
            task.save()
        else:
            pass

    def __str__(self):
        if self.device:
            return f"{self.device.device_type.type_name}"
        else:
            return f"{self.device}"

    class Meta:
        verbose_name = 'دستگاه'
        verbose_name_plural = 'دستگاه های مشتری'


class Photo(models.Model):
    photo = models.ImageField(upload_to='photos')
    device = models.ForeignKey(Task, on_delete=models.CASCADE,
                               null=True, blank=True, related_name='device_photo')

    class Meta:
        verbose_name = 'عکس'
        verbose_name_plural = 'عکس های دستگاه'
