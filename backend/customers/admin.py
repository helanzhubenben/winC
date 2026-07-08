from django.contrib import admin
from .models import Customer, Contact, CustomerContactRecord, CustomerRevenue, WeeklyReport


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """客户管理后台"""

    list_display = [
        'client_name',
        'alias',
        'business_model',
        'area',
        'city',
        'level',
        'score_x',
        'score_y',
        'score_z',
        'potential_contribution',
        'status',
        'updated_at'
    ]
    list_filter = ['level', 'business_model', 'area', 'city', 'status']
    search_fields = ['client_name', 'alias', 'address', 'remark']
    ordering = ['-updated_at']
    list_per_page = 20

    fieldsets = (
        ('基本信息', {
            'fields': ('client_name', 'alias', 'business_model', 'area', 'city', 'address')
        }),
        ('三维评分', {
            'fields': (
                ('description_x', 'score_x'),
                ('description_y', 'score_y'),
                ('key_person', 'score_z'),
            )
        }),
        ('分级和战略', {
            'fields': ('level', 'client_strategy', 'potential_contribution')
        }),
        ('其他信息', {
            'fields': ('remark', 'status')
        }),
    )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """联系人管理后台"""

    list_display = ['name', 'customer', 'position', 'phone', 'email', 'is_key_person', 'created_at']
    list_filter = ['is_key_person', 'customer']
    search_fields = ['name', 'position', 'phone', 'email']
    ordering = ['-created_at']


@admin.register(CustomerContactRecord)
class CustomerContactRecordAdmin(admin.ModelAdmin):
    """客户联系记录管理后台"""

    list_display = ['customer', 'contacted_at', 'contact_date', 'created_at']
    list_filter = ['contact_date', 'customer']
    search_fields = ['customer__client_name', 'customer__alias']
    ordering = ['-contacted_at']
    raw_id_fields = ['customer']


@admin.register(CustomerRevenue)
class CustomerRevenueAdmin(admin.ModelAdmin):
    """客户营收管理后台"""

    list_display = ['customer', 'month', 'revenue', 'updated_at']
    list_filter = ['month', 'customer']
    search_fields = ['customer__client_name']
    ordering = ['-month', 'customer__client_name']
    raw_id_fields = ['customer']


@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    """Weekly Report 管理后台"""

    list_display = [
        'client_name',
        'definition',
        'area',
        'tasks',
        'due_date',
        'responsibility',
        'customer',
        'updated_at'
    ]
    list_filter = ['area', 'tasks', 'responsibility', 'due_date']
    search_fields = ['client_name', 'definition', 'remark']
    ordering = ['-due_date', '-updated_at']
    list_per_page = 20
    raw_id_fields = ['customer']

    fieldsets = (
        ('客户信息', {
            'fields': ('client_name', 'customer', 'area', 'address')
        }),
        ('项目信息', {
            'fields': ('tasks', 'definition', 'revenue', 'responsibility')
        }),
        ('时间信息', {
            'fields': ('due_date', 'revise_date', 'finish_date')
        }),
        ('行动记录', {
            'fields': ('actions',),
            'classes': ('collapse',)
        }),
        ('其他信息', {
            'fields': ('remark',)
        }),
    )
