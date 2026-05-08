import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO, StringIO

from django.http import HttpResponse
from openpyxl import Workbook, load_workbook
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Customer, Contact, CustomerRevenue, WeeklyReport
from .serializers import (
    CustomerSerializer, CustomerListSerializer, ContactSerializer,
    CustomerRevenueSerializer, WeeklyReportSerializer, WeeklyReportListSerializer
)


REVENUE_REQUIRED_COLUMNS = {'month', 'customer name', 'revenue'}
EXCEL_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def _xlsx_response(workbook, filename):
    output = BytesIO()
    workbook.save(output)
    workbook.close()
    output.seek(0)

    response = HttpResponse(output.getvalue(), content_type=EXCEL_CONTENT_TYPE)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def _normalize_header(value):
    return str(value or '').strip().lower()


def _format_export_date(value):
    return value.strftime('%Y-%m-%d') if value else ''


def _format_export_datetime(value):
    return timezone.localtime(value).strftime('%Y-%m-%d %H:%M:%S') if value else ''


def _add_customers_sheet(workbook, queryset=None):
    sheet = workbook.active
    sheet.title = '客户池'
    sheet.append([
        '客户名称',
        '业务模式',
        '区域',
        '城市',
        '客户等级',
        'X评分',
        'Y评分',
        'Z评分',
        '潜在贡献',
        '去年营收',
        '上季度营收',
        '联系人数',
        '更新时间',
    ])

    queryset = queryset or Customer.objects.all().prefetch_related('contacts', 'revenue_records')
    serializer = CustomerListSerializer(queryset, many=True)
    for item in serializer.data:
        sheet.append([
            item.get('name', ''),
            item.get('business_model', ''),
            item.get('region', ''),
            item.get('city', ''),
            item.get('level', ''),
            item.get('score_x', 0),
            item.get('score_y', 0),
            item.get('score_z', 0),
            item.get('potential_contribution') or '',
            item.get('last_year_revenue', '0.00'),
            item.get('last_quarter_revenue', '0.00'),
            item.get('contacts_count', 0),
            item.get('updated_at', ''),
        ])
    return sheet


def _action_value(action, key, fallback=''):
    if isinstance(action, dict):
        return action.get(key, fallback)
    return fallback


def _add_weekly_reports_sheet(workbook, queryset=None):
    sheet = workbook.active if workbook.sheetnames == ['Sheet'] else workbook.create_sheet('周报')
    sheet.title = '周报'
    sheet.append([
        '客户名称',
        '匹配客户',
        '区域',
        '地址',
        '任务',
        '项目定义',
        '状态',
        '到期日期',
        '修订日期',
        '完成日期',
        '营收',
        '责任人',
        '备注',
        'Action序号',
        'Action日期',
        'Action内容',
        'Action结果',
        'Action下一步',
        'Action用户',
        'Action创建时间',
        '更新时间',
    ])

    queryset = queryset or WeeklyReport.objects.all().select_related('customer')
    for report in queryset:
        actions = report.actions or [None]
        for index, action in enumerate(actions, start=1):
            action_content = _action_value(action, 'action') or _action_value(action, 'content')
            sheet.append([
                report.client_name,
                report.customer.client_name if report.customer else '',
                report.area,
                report.address,
                report.tasks,
                report.definition,
                '已完成' if report.status == 'completed' else '进行中',
                _format_export_date(report.due_date),
                _format_export_date(report.revise_date),
                _format_export_date(report.finish_date),
                report.revenue,
                report.responsibility,
                report.remark,
                index if action else '',
                _action_value(action, 'action_date'),
                action_content,
                _action_value(action, 'result'),
                _action_value(action, 'next_step'),
                _action_value(action, 'user'),
                _action_value(action, 'timestamp'),
                _format_export_datetime(report.updated_at),
            ])
    return sheet


@api_view(['GET'])
def export_workbook(request):
    workbook = Workbook()
    _add_customers_sheet(workbook)
    _add_weekly_reports_sheet(workbook)
    return _xlsx_response(workbook, 'fishpool-export.xlsx')


def _read_revenue_rows(upload):
    filename = upload.name.lower()
    if filename.endswith('.xlsx'):
        return _read_xlsx_revenue_rows(upload)
    if filename.endswith('.csv'):
        return _read_csv_revenue_rows(upload)
    raise ValueError('仅支持 .xlsx 或 .csv 文件')


def _read_csv_revenue_rows(upload):
    content = upload.read().decode('utf-8-sig')
    reader = csv.DictReader(StringIO(content))
    if not reader.fieldnames:
        raise ValueError('文件缺少表头')

    headers = {_normalize_header(name): name for name in reader.fieldnames}
    missing = REVENUE_REQUIRED_COLUMNS - set(headers.keys())
    if missing:
        raise ValueError(f"缺少字段: {', '.join(sorted(missing))}")

    rows = []
    for index, row in enumerate(reader, start=2):
        rows.append((
            index,
            {column: row.get(headers[column]) for column in REVENUE_REQUIRED_COLUMNS}
        ))
    return rows


def _read_xlsx_revenue_rows(upload):
    workbook = load_workbook(upload, read_only=True, data_only=True)
    sheet = workbook.active
    header_row = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True), None)
    if not header_row:
        raise ValueError('文件缺少表头')

    headers = {_normalize_header(name): position for position, name in enumerate(header_row)}
    missing = REVENUE_REQUIRED_COLUMNS - set(headers.keys())
    if missing:
        raise ValueError(f"缺少字段: {', '.join(sorted(missing))}")

    rows = []
    for index, values in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        rows.append((
            index,
            {column: values[headers[column]] if headers[column] < len(values) else None for column in REVENUE_REQUIRED_COLUMNS}
        ))
    workbook.close()
    return rows


def _parse_month(value):
    if isinstance(value, datetime):
        return value.date().replace(day=1)
    if isinstance(value, date):
        return value.replace(day=1)

    raw_value = str(value or '').strip()
    if not raw_value:
        raise ValueError('month 不能为空')

    for date_format in ('%Y-%m', '%Y/%m', '%Y.%m', '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d'):
        try:
            parsed = datetime.strptime(raw_value, date_format).date()
            return parsed.replace(day=1)
        except ValueError:
            continue
    raise ValueError('month 格式不正确，请使用 YYYY-MM 或 YYYY-MM-DD')


def _parse_revenue(value):
    raw_value = str(value or '').strip().replace(',', '')
    if not raw_value:
        raise ValueError('revenue 不能为空')
    try:
        return Decimal(raw_value)
    except InvalidOperation as exc:
        raise ValueError('revenue 必须是数字') from exc


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
            queryset = queryset.prefetch_related('contacts', 'revenue_records')
        elif self.action == 'retrieve':
            queryset = queryset.prefetch_related('contacts', 'revenue_records')
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

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        queryset = self.filter_queryset(
            self.get_queryset().prefetch_related('contacts', 'revenue_records')
        )

        workbook = Workbook()
        _add_customers_sheet(workbook, queryset)
        return _xlsx_response(workbook, 'customers.xlsx')


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


class CustomerRevenueViewSet(viewsets.ModelViewSet):
    """客户营收视图集"""

    queryset = CustomerRevenue.objects.all()
    serializer_class = CustomerRevenueSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'month']
    search_fields = ['customer__client_name']
    ordering_fields = ['month', 'revenue', 'created_at', 'updated_at']
    ordering = ['-month', 'customer__client_name']
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        return super().get_queryset().select_related('customer')

    @action(detail=False, methods=['post'], url_path='import')
    def import_file(self, request):
        upload = request.FILES.get('file')
        if not upload:
            return Response({'error': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = _read_revenue_rows(upload)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        imported = 0
        updated = 0
        skipped = 0
        errors = []

        for row_number, row in rows:
            customer_name = (row.get('customer name') or '').strip()
            customer = Customer.objects.filter(client_name=customer_name).first()
            if not customer:
                skipped += 1
                errors.append({
                    'row': row_number,
                    'customer_name': customer_name,
                    'reason': '客户名称未完全匹配 Fishpool 客户'
                })
                continue

            try:
                month = _parse_month(row.get('month'))
                revenue = _parse_revenue(row.get('revenue'))
            except ValueError as exc:
                skipped += 1
                errors.append({
                    'row': row_number,
                    'customer_name': customer_name,
                    'reason': str(exc)
                })
                continue

            _, created = CustomerRevenue.objects.update_or_create(
                customer=customer,
                month=month,
                defaults={'revenue': revenue}
            )
            if created:
                imported += 1
            else:
                updated += 1

        return Response({
            'imported': imported,
            'updated': updated,
            'skipped': skipped,
            'errors': errors[:50],
        })


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
        """优化查询性能，支持日期范围筛选"""
        queryset = super().get_queryset()
        if self.action in ['list', 'retrieve']:
            queryset = queryset.select_related('customer')

        # 日期范围筛选
        due_date_after = self.request.query_params.get('due_date_after')
        due_date_before = self.request.query_params.get('due_date_before')

        if due_date_after:
            queryset = queryset.filter(due_date__gte=due_date_after)
        if due_date_before:
            queryset = queryset.filter(due_date__lte=due_date_before)

        return queryset

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset().select_related('customer'))

        workbook = Workbook()
        _add_weekly_reports_sheet(workbook, queryset)
        return _xlsx_response(workbook, 'weekly-reports.xlsx')

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
        """添加行动记录（兼容旧格式）"""
        report = self.get_object()

        # 支持新旧两种格式
        action_date = request.data.get('action_date', '').strip()
        action_content = request.data.get('action', request.data.get('content', '')).strip()
        result = request.data.get('result', '').strip()
        next_step = request.data.get('next_step', '').strip()
        user = request.data.get('user', '').strip()

        if not action_content:
            return Response(
                {'error': '行动记录内容不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建新的行动记录
        action_record = {
            'timestamp': timezone.now().isoformat(),
            'action_date': action_date,
            'action': action_content,
            'result': result,
            'next_step': next_step,
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
        """编辑行动记录（兼容旧格式）"""
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

        # 支持新旧两种格式
        action_date = request.data.get('action_date', '').strip()
        action_content = request.data.get('action', request.data.get('content', '')).strip()
        result = request.data.get('result', '').strip()
        next_step = request.data.get('next_step', '').strip()
        user = request.data.get('user', '').strip()

        if not action_content:
            return Response(
                {'error': '行动记录内容不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 更新行动记录（保留原始时间戳）
        report.actions[index].update({
            'action_date': action_date,
            'action': action_content,
            'result': result,
            'next_step': next_step,
            'user': user
        })
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
