from django.contrib import admin
from .models import Customer, Contact


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """客户管理后台"""

    list_display = [
        'client_name',
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
    search_fields = ['client_name', 'address', 'remark']
    ordering = ['-updated_at']
    list_per_page = 20

    fieldsets = (
        ('基本信息', {
            'fields': ('client_name', 'business_model', 'area', 'city', 'address')
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
