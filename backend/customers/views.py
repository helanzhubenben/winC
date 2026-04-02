from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Customer, Contact
from .serializers import CustomerSerializer, CustomerListSerializer, ContactSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """客户视图集"""

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'area', 'city', 'business_model', 'status']
    search_fields = ['client_name', 'address', 'remark']
    ordering_fields = ['created_at', 'updated_at', 'score_x', 'score_y', 'score_z', 'potential_contribution']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        """根据action选择序列化器"""
        if self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer

    def get_queryset(self):
        """优化查询性能"""
        queryset = super().get_queryset()
        if self.action == 'list':
            queryset = queryset.prefetch_related('contacts')
        elif self.action == 'retrieve':
            queryset = queryset.prefetch_related('contacts')
        return queryset

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取统计数据"""
        queryset = self.filter_queryset(self.get_queryset())

        stats = {
            'total': queryset.count(),
            'by_level': {},
            'by_business_model': {},
            'by_area': {},
        }

        # 按等级统计
        for level in ['A', 'B', 'C', 'D']:
            stats['by_level'][level] = queryset.filter(level=level).count()

        # 按业务模式统计
        for model in ['Hunting', 'Farming']:
            stats['by_business_model'][model] = queryset.filter(business_model=model).count()

        # 按区域统计（前10）
        areas = queryset.values('area').distinct()
        for area_dict in areas[:10]:
            area = area_dict['area']
            if area:
                stats['by_area'][area] = queryset.filter(area=area).count()

        return Response(stats)


class ContactViewSet(viewsets.ModelViewSet):
    """联系人视图集"""

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['customer', 'is_key_person']
    search_fields = ['name', 'position', 'phone', 'email']

    def get_queryset(self):
        """优化查询性能"""
        return super().get_queryset().select_related('customer')

