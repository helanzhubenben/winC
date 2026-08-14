"""
URL configuration for fishpool project.
"""
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path, include, re_path
from rest_framework import routers
from customers.views import (
    CustomerViewSet,
    ContactViewSet,
    CustomerRevenueViewSet,
    WeeklyReportViewSet,
    export_workbook,
)

router = routers.DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'customer-revenues', CustomerRevenueViewSet, basename='customer-revenue')
router.register(r'weekly-reports', WeeklyReportViewSet, basename='weekly-report')


def healthcheck(request):
    """返回本机启动器用于确认 Fishpool 服务可用的响应。"""
    return HttpResponse('ok', content_type='text/plain')


def frontend_index(request):
    """提供构建后的 Vue 单页应用，并支持浏览器直接访问任意前端路由。"""
    return render(request, 'fishpool/index.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/export/workbook/', export_workbook, name='export-workbook'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('health/', healthcheck, name='healthcheck'),
    re_path(r'^(?!api/|api-auth/|admin/|health/).*$', frontend_index, name='frontend-index'),
]
