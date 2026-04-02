"""
URL configuration for fishpool project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from customers.views import CustomerViewSet, ContactViewSet

router = routers.DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'contacts', ContactViewSet, basename='contact')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
