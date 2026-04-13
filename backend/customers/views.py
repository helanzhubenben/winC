from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Customer, Contact, WeeklyReport
from .serializers import (
    CustomerSerializer, CustomerListSerializer, ContactSerializer,
    WeeklyReportSerializer, WeeklyReportListSerializer
)


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

    @action(detail=True, methods=['get'], url_path='weekly-reports')
    def weekly_reports(self, request, pk=None):
        """获取客户的所有 Weekly Report"""
        customer = self.get_object()
        reports = customer.weekly_reports.all().order_by('-due_date', '-created_at')
        serializer = WeeklyReportListSerializer(reports, many=True)
        return Response(serializer.data)


class ContactViewSet(viewsets.ModelViewSet):
    """联系人视图集"""

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['customer', 'is_key_person']
    search_fields = ['name', 'position', 'phone', 'email']

    def get_queryset(self):
        """优化查询性能"""
        return super().get_queryset().select_related('customer')


class WeeklyReportViewSet(viewsets.ModelViewSet):
    """Weekly Report 视图集"""

    queryset = WeeklyReport.objects.all()
    serializer_class = WeeklyReportSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['client_name', 'area', 'tasks', 'responsibility', 'customer', 'status']
    search_fields = ['client_name', 'definition', 'remark']
    ordering_fields = ['due_date', 'created_at', 'updated_at']
    ordering = ['-due_date', '-created_at']

    def get_serializer_class(self):
        """根据 action 选择序列化器"""
        if self.action == 'list':
            return WeeklyReportListSerializer
        return WeeklyReportSerializer

    def get_queryset(self):
        """优化查询性能"""
        queryset = super().get_queryset()
        if self.action in ['list', 'retrieve']:
            queryset = queryset.select_related('customer')
        return queryset

    @action(detail=True, methods=['get', 'post'], url_path='actions')
    def actions_list(self, request, pk=None):
        """获取或创建行动记录"""
        report = self.get_object()

        if request.method == 'GET':
            # 获取行动记录列表
            actions_with_id = []
            if report.actions:
                for index, action in enumerate(report.actions):
                    action_data = {
                        'id': index,
                        'action_date': action.get('action_date', ''),
                        'action': action.get('action', action.get('content', '')),  # 兼容旧格式
                        'result': action.get('result', ''),
                        'next_step': action.get('next_step', ''),
                        'timestamp': action.get('timestamp', ''),
                        'user': action.get('user', '')
                    }
                    actions_with_id.append(action_data)
            return Response(actions_with_id)

        elif request.method == 'POST':
            # 创建行动记录
            action_date = request.data.get('action_date', '').strip()
            action_content = request.data.get('action', '').strip()
            result = request.data.get('result', '').strip()
            next_step = request.data.get('next_step', '').strip()

            if not action_content:
                return Response(
                    {'error': '行动内容不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 创建新的行动记录
            action_record = {
                'timestamp': timezone.now().isoformat(),
                'action_date': action_date,
                'action': action_content,
                'result': result,
                'next_step': next_step
            }

            # 添加到 actions 列表
            if report.actions is None:
                report.actions = []
            report.actions.append(action_record)
            report.save()

            # 返回新创建的记录（带 id）
            new_action = {
                'id': len(report.actions) - 1,
                **action_record
            }
            return Response(new_action, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put', 'delete'], url_path='actions/(?P<action_id>[0-9]+)')
    def actions_detail(self, request, pk=None, action_id=None):
        """更新或删除行动记录（RESTful 风格）"""
        report = self.get_object()
        try:
            action_id = int(action_id)
        except (ValueError, TypeError):
            return Response(
                {'error': '无效的行动记录 ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not report.actions or action_id >= len(report.actions):
            return Response(
                {'error': '行动记录不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'PUT':
            # 更新行动记录
            action_date = request.data.get('action_date', '').strip()
            action_content = request.data.get('action', '').strip()
            result = request.data.get('result', '').strip()
            next_step = request.data.get('next_step', '').strip()

            if not action_content:
                return Response(
                    {'error': '行动内容不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 更新行动记录（保留原始时间戳）
            report.actions[action_id].update({
                'action_date': action_date,
                'action': action_content,
                'result': result,
                'next_step': next_step
            })
            report.save()

            # 返回更新后的记录
            updated_action = {
                'id': action_id,
                **report.actions[action_id]
            }
            return Response(updated_action)

        elif request.method == 'DELETE':
            # 删除行动记录
            report.actions.pop(action_id)
            report.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='add-action')
    def add_action(self, request, pk=None):
        """添加行动记录"""
        report = self.get_object()
        content = request.data.get('content', '').strip()
        user = request.data.get('user', '').strip()

        if not content:
            return Response(
                {'error': '行动记录内容不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建新的行动记录
        action_record = {
            'timestamp': timezone.now().isoformat(),
            'content': content,
            'user': user
        }

        # 添加到 actions 列表
        if report.actions is None:
            report.actions = []
        report.actions.append(action_record)
        report.save()

        serializer = self.get_serializer(report)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='actions/(?P<index>[0-9]+)/update')
    def update_action(self, request, pk=None, index=None):
        """编辑行动记录"""
        report = self.get_object()
        try:
            index = int(index)
        except (ValueError, TypeError):
            return Response(
                {'error': '无效的索引'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not report.actions or index >= len(report.actions):
            return Response(
                {'error': '行动记录不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        content = request.data.get('content', '').strip()
        user = request.data.get('user', '').strip()

        if not content:
            return Response(
                {'error': '行动记录内容不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 更新行动记录（保留原始时间戳）
        report.actions[index]['content'] = content
        if user:
            report.actions[index]['user'] = user
        report.save()

        serializer = self.get_serializer(report)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='actions/(?P<index>[0-9]+)/delete')
    def delete_action(self, request, pk=None, index=None):
        """删除行动记录"""
        report = self.get_object()
        try:
            index = int(index)
        except (ValueError, TypeError):
            return Response(
                {'error': '无效的索引'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not report.actions or index >= len(report.actions):
            return Response(
                {'error': '行动记录不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 删除行动记录
        report.actions.pop(index)
        report.save()

        serializer = self.get_serializer(report)
        return Response(serializer.data)
