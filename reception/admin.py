from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.forms import TextInput, Textarea
from .views import receipt
from django_object_actions import DjangoObjectActions, action
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin

from jalali_date import datetime2jalali
from jalali_date.admin import ModelAdminJalaliMixin
from reception.models import Task, Device, Customer, DeviceTypes, Brand, Problem, Photo, Serviceman, Appearance, \
    CustomerDevice, Component, ProblemType, Accessories
import nested_admin
from django.db import models


class ProblemTypeAdmin(admin.ModelAdmin):
    search_fields = ['problem']


admin.site.register(ProblemType, ProblemTypeAdmin)


class AppearanceAdmin(nested_admin.NestedModelAdmin):
    pass


class BrandAdmin(nested_admin.NestedModelAdmin):
    # model = Device
    # extra = 1
    pass


class CustomerAdmin(nested_admin.NestedModelAdmin):
    search_fields = ["name", 'phone']


class DeviceTypesAdmin(nested_admin.NestedModelAdmin):
    # inlines = [DeviceInline]
    pass


class DeviceAdmin(nested_admin.NestedModelAdmin):
    search_fields = ['model', 'brand__brand_name']


class ServicemanAdmin(nested_admin.NestedModelAdmin):
    search_fields = ['serviceman']


class AccessoriesAdmin(nested_admin.NestedModelAdmin):
    pass


admin.site.register(DeviceTypes, DeviceTypesAdmin)
admin.site.register(Accessories, AccessoriesAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Device, DeviceAdmin)


class TaskResource(resources.ModelResource):
    customer = fields.Field(
        column_name='مشتری',
        attribute='customer',
        widget=ForeignKeyWidget(Customer, field='name'))

    device = fields.Field(
        column_name='دستگاه',
        attribute='device',
        widget=ForeignKeyWidget(Device, field='device_type'))

    brand = fields.Field(
        column_name='برند',
        attribute='device',
        widget=ForeignKeyWidget(Device, field='brand__brand_name'))

    model = fields.Field(
        column_name='مدل',
        attribute='device',
        widget=ForeignKeyWidget(Device, field='model'))

    serviceman = fields.Field(
        column_name='کاربر',
        attribute='serviceman',
        widget=ForeignKeyWidget(Task, field='serviceman'))

    problem = fields.Field(
        column_name='مشکل',
        attribute='problem',
        widget=ForeignKeyWidget(Problem, field='problem'))

    appearance = fields.Field(
        column_name='وضعیت ظاهر',
        attribute='appearance',
        widget=ForeignKeyWidget(Appearance, field='appearance_problem'))

    accessories = fields.Field(
        column_name='لوازم همراه',
        attribute='accessories_detail',
        widget=ForeignKeyWidget(Accessories, field='accessory_name')
    )

    class Meta:
        model = Task
        fields = (
            'customer', 'customer_device', 'brand', 'model', 'serviceman', 'reception_no', 'reception_datetime',
            'reception_type',
            'service_type', 'device_password', 'device_serial_no', 'import_files', 'import_files_detail',
            'accessories', 'accessories_detail', 'problem', 'problem_detail', 'appearance', 'appearance_detail',
            'photo', 'deposit', 'estimated_cost', 'preparation', 'status')


class ProblemInline(admin.TabularInline):
    model = Problem
    extra = 1
    autocomplete_fields = ['problem', 'component']

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 20})},
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
    }


class ComponentAdmin(admin.ModelAdmin):
    search_fields = ['component']


class PhotoAdminInline(admin.StackedInline):
    model = Photo
    extra = 0


admin.site.register(Component, ComponentAdmin)


class CustomerDeviceInline(admin.StackedInline):
    model = CustomerDevice
    extra = 1
    fieldsets = (
        ('اطلاعات دستگاه', {
            'fields': ('device', ('device_serial_no',))
        }),

        ('پسورد دستگاه', {
            'classes': ('collapse',),
            'fields': ('device_password',)
        }),
        ('اطلاعات مهم', {
            'classes': ('collapse',),
            'fields': ('import_files', 'import_files_detail')
        }),
        ('لوازم همراه', {
            'classes': ('collapse',),
            'fields': ('accessories',  'accessories_detail')
        }),
        # ('اشکالات', {
        #     'fields': ('problem', 'problem_detail')
        # }),
        ('وضعیت ظاهری', {
            'fields': ('appearance', 'appearance_detail')
        }),
    )
    autocomplete_fields = ['device']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 28})},
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 28})},
    }


class CustomerDeviceModelAdmin(admin.ModelAdmin):
    # search_fields = ['model', 'brand__brand_name']
    autocomplete_fields = ['device'] # 'problem']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 28})},
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 28})},
    }


class TaskAdmin(DjangoObjectActions, ImportExportModelAdmin, ModelAdminJalaliMixin, admin.ModelAdmin):
    # confirm_add = True
    # confirmation_fields = ['customer']
    resource_classes = [TaskResource]
    fieldsets = (

        ('اطلاعات پذیرش', {
            'fields': ('customer', ('reception_type', 'service_type'),)
        }),
        ('حسابداری', {
            'fields': (('deposit', 'estimated_cost', 'preparation', 'serviceman'), 'status',)
        }),
    )
    change_form_template = "admin/task_change_form.html"
    inlines = [CustomerDeviceInline, PhotoAdminInline, ProblemInline]

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 28})},
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 28})},
    }

    list_display = ['reception_no', 'customer', 'customer_device', 'reception_type',
                    'service_type', 'reception_datetime', 'status']
    list_filter = ['customer_device__device__device_type__type_name', 'reception_type', 'service_type', 'reception_datetime',
                   'customer_device__problem__problem', 'preparation', 'serviceman', 'status']
    sortable_by = ['reception_datetime']
    list_editable = ['status']
    search_fields = ['customer__name', 'customer__phone', 'device__device_type__type_name',
                     'device__brand__brand_name', 'device__model', 'device_serial_no']
    search_help_text = 'جستجو '
    radio_fields = {"service_type": admin.HORIZONTAL, "reception_type": admin.HORIZONTAL}
    autocomplete_fields = ['customer', 'serviceman']
    actions = ['task_done']

    def task_done(self, request, queryset):
        updated = queryset.update(status=4)
        self.message_user(
            request, f"{updated}  وضعیت کارهای انتخاب شده به 'انجام شده' تغییر یافت", messages.SUCCESS
        )

    task_done.short_description = 'تغییر وضعیت کار ها'

    @admin.display(description='تاریخ پذیرش', ordering='reception_datetime')
    def get_created_jalali(self, obj):
        return datetime2jalali(obj.reception_datetime).strftime('%Y-%m-%d, ساعت %H:%M')

    @action(
        label="چاپ رسید",  # optional
        description="چاپ رسید مشتری"  # optional
    )
    def toolfunc(self, request, obj):
        return receipt(request, obj.reception_no)
    #
    # def make_published(modeladmin, request, queryset):
    #     queryset.update(status='p')

    change_actions = ('toolfunc',)
    # changelist_actions = ('make_published',)

    def response_add(self, request, obj, post_url_continue=None):
        # save CustomerDevice obj
        return receipt(request, obj.reception_no)


class PhotoModelAdmin(admin.ModelAdmin):
    fields = ('photo',)


admin.site.register(Photo, PhotoModelAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(CustomerDevice, CustomerDeviceModelAdmin)
admin.site.register(Serviceman, ServicemanAdmin)
admin.site.register(Appearance, AppearanceAdmin)


AdminSite.site_header = 'سیستم پذیرش تاپ کامپیوتر'
AdminSite.site_title = 'تاپ'
AdminSite.index_title = 'پنل مدیریت'

import random
from datetime import datetime, timedelta

import pytz

from reception.models import *

#
# def create_device(amount):
#     plrs = ['ارتقا رم', 'ارتقا حافظه', 'تعویض ال سی دی', 'نصب نرم افزار']
#     for p in plrs:
#         ProblemType.objects.create(problem=p)
#
#     stats = ['شکسته', 'خش خوردگی', 'ال سی دی معیوب']
#     for s in stats:
#         Appearance.objects.create(appearance_problem=s)
#     brands = ['Asus', 'Lenovo', 'Apple', 'Sony', 'HP', 'Dell', 'Acer', 'Samsung', 'LG', 'Microsoft']
#     for b in brands:
#         Brand.objects.get_or_create(brand_name=b)
#     models = ['X510UA', 'Pro', '3550', 'XS', 'L4234', 'P3232', 'Air']
#     device_types = [
#         DeviceTypes.objects.get_or_create(type_name="لپتاپ"),
#         DeviceTypes.objects.get_or_create(type_name="کنسول"),
#         DeviceTypes.objects.get_or_create(type_name="پرینتر"),
#         DeviceTypes.objects.get_or_create(type_name="کامپیوتر"),
#     ]
#     for i in range(50):
#         Device.objects.create(
#             device_type=device_types[i % 4][0],
#             brand=random.choice(Brand.objects.all()),
#             model=random.choice(models)
#         )
#
#     names = ["علی", "حسین", "سامان", "محمد", "سیروس", "کامران", "داوود", "سعید", "زهرا", "سارا"]
#     surname = ["حسینی", "طالبی", "عباسی", "محمودی", "میرکریمی", "تهرانی", "موسوی", "بیات", "کاظمی", "سعیدی"]
#
#     amount = amount if amount else 50
#     for i in range(0, amount):
#         # dt = pytz.utc.localize(datetime.now() - timedelta(days=random.randint(0, 1825)))
#         Customer.objects.create(
#             name=random.choice(names) + " " + random.choice(surname),
#             phone=random.randint(911111111, 9999999999)
#         )
#         # purchase.time = dt
#
#
# create_device(50)
