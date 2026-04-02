from rest_framework import serializers
from .models import Customer, Contact


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


class CustomerSerializer(serializers.ModelSerializer):
    """客户序列化器"""

    contacts = ContactSerializer(many=True, read_only=True)
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
            'notes',
            'status',
            'created_at',
            'updated_at',
            'contacts'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomerListSerializer(serializers.ModelSerializer):
    """客户列表序列化器（简化版）"""

    contacts_count = serializers.SerializerMethodField()
    # 字段映射以匹配前端
    name = serializers.CharField(source='client_name')
    region = serializers.CharField(source='area')

    class Meta:
        model = Customer
        fields = [
            'id',
            'name',
            'business_model',
            'region',
            'city',
            'level',
            'score_x',
            'score_y',
            'score_z',
            'potential_contribution',
            'contacts_count',
            'updated_at'
        ]

    def get_contacts_count(self, obj):
        return obj.contacts.count()

