"""
URL configuration for fishpool project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers
from customers.views import CustomerViewSet, ContactViewSet, CustomerRevenueViewSet, WeeklyReportViewSet

router = routers.DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'customer-revenues', CustomerRevenueViewSet, basename='customer-revenue')
router.register(r'weekly-reports', WeeklyReportViewSet, basename='weekly-report')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
