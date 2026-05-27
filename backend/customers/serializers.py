from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers
from .models import Customer, Contact, CustomerRevenue, WeeklyReport, get_last_quarter_range


class BlankableDateField(serializers.DateField):
    """Treat blank strings from forms as null for optional date fields."""

    def to_internal_value(self, value):
        if value in ('', None):
            return None
        return super().to_internal_value(value)


class ContactSerializer(serializers.ModelSerializer):
    """联系人序列化器"""

    class Meta:
        model = Contact
        fields = [
            'id',
            'customer',
            'name',
            'position',
            'phone',
            'email',
            'is_key_person',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


def _last_year_range():
    today = timezone.localdate()
    start_date = today.replace(year=today.year - 1, month=1, day=1)
    end_date = today.replace(year=today.year - 1, month=12, day=31)
    return start_date, end_date


def _sum_revenue(customer, date_range):
    start_date, end_date = date_range
    prefetched = getattr(customer, '_prefetched_objects_cache', {}).get('revenue_records')
    if prefetched is not None:
        total = sum(
            (record.revenue for record in prefetched if start_date <= record.month <= end_date),
            Decimal('0')
        )
        return f'{total or Decimal("0"):.2f}'

    total = customer.revenue_records.filter(
        month__gte=start_date,
        month__lte=end_date,
    ).aggregate(total=Sum('revenue'))['total']
    return f'{total or Decimal("0"):.2f}'


class CustomerSerializer(serializers.ModelSerializer):
    """客户序列化器"""

    contacts = ContactSerializer(many=True, read_only=True)
    last_year_revenue = serializers.SerializerMethodField()
    last_quarter_revenue = serializers.SerializerMethodField()
    # 字段映射以匹配前端
    name = serializers.CharField(source='client_name')
    region = serializers.CharField(source='area')
    score_x_desc = serializers.CharField(source='description_x', allow_blank=True, required=False)
    score_y_desc = serializers.CharField(source='description_y', allow_blank=True, required=False)
    score_z_desc = serializers.CharField(source='key_person', allow_blank=True, required=False)
    strategy = serializers.CharField(source='client_strategy', allow_blank=True, required=False)
    notes = serializers.CharField(source='remark', allow_blank=True, required=False)

    class Meta:
        model = Customer
        fields = [
            'id',
            'name',
            'alias',
            'business_model',
            'region',
            'city',
            'address',
            'score_x_desc',
            'score_x',
            'score_y_desc',
            'score_y',
            'score_z_desc',
            'score_z',
            'level',
            'strategy',
            'potential_contribution',
            'last_year_revenue',
            'last_quarter_revenue',
            'notes',
            'status',
            'created_at',
            'updated_at',
            'contacts'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_last_year_revenue(self, obj):
        return _sum_revenue(obj, _last_year_range())

    def get_last_quarter_revenue(self, obj):
        return _sum_revenue(obj, get_last_quarter_range())


class CustomerListSerializer(serializers.ModelSerializer):
    """客户列表序列化器（简化版）"""

    contacts_count = serializers.SerializerMethodField()
    last_year_revenue = serializers.SerializerMethodField()
    last_quarter_revenue = serializers.SerializerMethodField()
    # 字段映射以匹配前端
    name = serializers.CharField(source='client_name')
    region = serializers.CharField(source='area')

    class Meta:
        model = Customer
        fields = [
            'id',
            'name',
            'alias',
            'business_model',
            'region',
            'city',
            'address',
            'level',
            'score_x',
            'score_y',
            'score_z',
            'potential_contribution',
            'last_year_revenue',
            'last_quarter_revenue',
            'contacts_count',
            'updated_at'
        ]

    def get_contacts_count(self, obj):
        return obj.contacts.count()

    def get_last_year_revenue(self, obj):
        return _sum_revenue(obj, _last_year_range())

    def get_last_quarter_revenue(self, obj):
        return _sum_revenue(obj, get_last_quarter_range())


class CustomerRevenueSerializer(serializers.ModelSerializer):
    """客户营收序列化器"""

    customer_name = serializers.CharField(write_only=True, required=True)
    matched_customer_name = serializers.CharField(source='customer.client_name', read_only=True)

    class Meta:
        model = CustomerRevenue
        fields = [
            'id',
            'customer',
            'customer_name',
            'matched_customer_name',
            'month',
            'revenue',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'customer', 'matched_customer_name', 'created_at', 'updated_at']

    def validate_customer_name(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('客户名称不能为空')
        customer = Customer.objects.filter(client_name=value).first()
        if not customer:
            raise serializers.ValidationError('客户名称未完全匹配 Fishpool 客户，不会添加营收数据')
        self._matched_customer = customer
        return value

    def create(self, validated_data):
        validated_data.pop('customer_name', None)
        validated_data['customer'] = self._matched_customer
        record, _ = CustomerRevenue.objects.update_or_create(
            customer=validated_data['customer'],
            month=validated_data['month'],
            defaults={'revenue': validated_data['revenue']}
        )
        return record


class WeeklyReportSerializer(serializers.ModelSerializer):
    """Weekly Report 序列化器"""

    due_date = BlankableDateField(required=False, allow_null=True)
    revise_date = BlankableDateField(required=False, allow_null=True)
    finish_date = BlankableDateField(required=False, allow_null=True)
    customer_name = serializers.CharField(source='customer.client_name', read_only=True)
    actions_count = serializers.SerializerMethodField()

    class Meta:
        model = WeeklyReport
        fields = [
            'id',
            'client_name',
            'customer',
            'customer_name',
            'area',
            'address',
            'tasks',
            'definition',
            'status',
            'due_date',
            'revise_date',
            'finish_date',
            'revenue',
            'actions',
            'actions_count',
            'responsibility',
            'remark',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'customer_name', 'actions_count']

    def get_actions_count(self, obj):
        """获取行动记录数量"""
        return len(obj.actions) if obj.actions else 0

    def validate_client_name(self, value):
        """验证客户名称不能为空"""
        if not value or not value.strip():
            raise serializers.ValidationError("客户名称不能为空")
        return value.strip()

    def create(self, validated_data):
        """创建时自动匹配客户"""
        client_name = validated_data.get('client_name', '').strip()
        if client_name and not validated_data.get('customer'):
            # 尝试自动匹配客户
            customer = self._match_customer(client_name)
            if customer:
                validated_data['customer'] = customer
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """更新时自动匹配客户"""
        client_name = validated_data.get('client_name')
        if client_name:
            client_name = client_name.strip()
            validated_data['client_name'] = client_name
            # 如果客户名称变化，重新匹配
            if client_name != instance.client_name:
                customer = self._match_customer(client_name)
                validated_data['customer'] = customer
        return super().update(instance, validated_data)

    def _match_customer(self, client_name):
        """自动匹配客户（模糊匹配）"""
        from django.db.models import Q
        # 去除空格，不区分大小写
        normalized_name = client_name.replace(' ', '').lower()
        customers = Customer.objects.filter(
            Q(client_name__iexact=client_name) |
            Q(client_name__icontains=client_name)
        )
        for customer in customers:
            if customer.client_name.replace(' ', '').lower() == normalized_name:
                return customer
        return None


class WeeklyReportListSerializer(serializers.ModelSerializer):
    """Weekly Report 列表序列化器（简化版）"""

    customer_name = serializers.CharField(source='customer.client_name', read_only=True)
    actions_count = serializers.SerializerMethodField()

    class Meta:
        model = WeeklyReport
        fields = [
            'id',
            'client_name',
            'customer_name',
            'area',
            'tasks',
            'definition',
            'status',
            'due_date',
            'responsibility',
            'actions_count',
            'updated_at'
        ]

    def get_actions_count(self, obj):
        """获取行动记录数量"""
        return len(obj.actions) if obj.actions else 0
