from datetime import timedelta

from django.db import models
from django.utils import timezone


class Customer(models.Model):
    """客户模型"""

    BUSINESS_MODEL_CHOICES = [
        ('Hunting', 'Hunting'),
        ('Farming', 'Farming'),
    ]

    LEVEL_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]

    # 基本信息
    client_name = models.CharField(max_length=200, verbose_name='客户名称', db_index=True)
    alias = models.CharField(max_length=200, blank=True, verbose_name='别名', db_index=True)
    business_model = models.CharField(
        max_length=20,
        choices=BUSINESS_MODEL_CHOICES,
        verbose_name='业务模式',
        db_index=True
    )
    area = models.CharField(max_length=100, blank=True, verbose_name='区域', db_index=True)
    city = models.CharField(max_length=100, blank=True, verbose_name='城市', db_index=True)
    address = models.TextField(blank=True, verbose_name='详细地址')

    # X轴：客户潜力
    description_x = models.TextField(blank=True, verbose_name='客户描述')
    score_x = models.IntegerField(default=0, verbose_name='客户潜力评分')

    # Y轴：竞争环境
    description_y = models.TextField(blank=True, verbose_name='竞争环境描述')
    score_y = models.IntegerField(default=0, verbose_name='竞争评分')

    # Z轴：关键人关系
    key_person = models.CharField(max_length=200, blank=True, verbose_name='关键联系人')
    score_z = models.IntegerField(default=0, verbose_name='关系评分')

    # 分级和战略
    level = models.CharField(
        max_length=1,
        choices=LEVEL_CHOICES,
        blank=True,
        verbose_name='客户等级',
        db_index=True
    )
    client_strategy = models.TextField(blank=True, verbose_name='客户策略')
    potential_contribution = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='年度潜在贡献(KEUR)'
    )

    remark = models.TextField(blank=True, verbose_name='备注')
    status = models.CharField(max_length=20, default='active', verbose_name='状态')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'customers'
        verbose_name = '客户'
        verbose_name_plural = '客户'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client_name']),
            models.Index(fields=['level']),
            models.Index(fields=['business_model']),
            models.Index(fields=['area', 'city']),
        ]

    def __str__(self):
        return self.client_name


class Contact(models.Model):
    """联系人模型"""

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name='客户'
    )
    name = models.CharField(max_length=100, verbose_name='姓名')
    position = models.CharField(max_length=100, blank=True, verbose_name='职位')
    phone = models.CharField(max_length=50, blank=True, verbose_name='电话')
    email = models.CharField(max_length=100, blank=True, verbose_name='邮箱')
    is_key_person = models.BooleanField(default=False, verbose_name='是否关键人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'contacts'
        verbose_name = '联系人'
        verbose_name_plural = '联系人'
        ordering = ['-is_key_person', 'name']

    def __str__(self):
        return f"{self.name} - {self.customer.client_name}"


class CustomerRevenue(models.Model):
    """客户月度营收数据"""

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='revenue_records',
        verbose_name='客户'
    )
    month = models.DateField(verbose_name='月份', db_index=True)
    revenue = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='营收')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'customer_revenues'
        verbose_name = '客户营收'
        verbose_name_plural = '客户营收'
        ordering = ['-month', 'customer__client_name']
        constraints = [
            models.UniqueConstraint(fields=['customer', 'month'], name='unique_customer_month_revenue')
        ]
        indexes = [
            models.Index(fields=['customer', 'month']),
        ]

    def __str__(self):
        return f"{self.customer.client_name} - {self.month:%Y-%m}: {self.revenue}"


def get_last_quarter_range(reference_date=None):
    """Return the first and last day for the previous calendar quarter."""
    reference_date = reference_date or timezone.localdate()
    current_quarter = (reference_date.month - 1) // 3 + 1
    if current_quarter == 1:
        year = reference_date.year - 1
        quarter = 4
    else:
        year = reference_date.year
        quarter = current_quarter - 1

    start_month = (quarter - 1) * 3 + 1
    end_month = start_month + 2
    start_date = reference_date.replace(year=year, month=start_month, day=1)

    if end_month == 12:
        next_month = reference_date.replace(year=year + 1, month=1, day=1)
    else:
        next_month = reference_date.replace(year=year, month=end_month + 1, day=1)
    end_date = next_month - timedelta(days=1)
    return start_date, end_date


class WeeklyReport(models.Model):
    """Weekly Report 项目跟进记录模型"""

    STATUS_CHOICES = [
        ('in_progress', '进行中'),
        ('completed', '已完成'),
    ]

    # 客户信息（弱关联）
    client_name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='客户名称',
        help_text='手动输入或从客户列表选择'
    )
    customer = models.ForeignKey(
        Customer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='weekly_reports',
        verbose_name='关联客户'
    )

    # 项目基本信息
    area = models.CharField(max_length=100, blank=True, verbose_name='区域', db_index=True)
    address = models.CharField(max_length=500, blank=True, verbose_name='地址')
    tasks = models.CharField(max_length=200, blank=True, verbose_name='任务类型', db_index=True)
    definition = models.TextField(verbose_name='项目定义/名称')

    # 项目状态
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        verbose_name='项目状态',
        db_index=True
    )

    # 时间信息
    due_date = models.DateField(null=True, blank=True, verbose_name='截止日期', db_index=True)
    revise_date = models.DateField(null=True, blank=True, verbose_name='修订日期')
    finish_date = models.DateField(null=True, blank=True, verbose_name='完成日期')

    # 营收和责任人
    revenue = models.CharField(max_length=100, blank=True, verbose_name='营收')
    responsibility = models.CharField(max_length=100, blank=True, verbose_name='责任人', db_index=True)

    # 行动记录（JSON 存储）
    actions = models.JSONField(
        default=list,
        verbose_name='行动记录',
        help_text='格式: [{"timestamp": "2026-04-12T10:30:00", "content": "...", "user": "..."}]'
    )

    # 备注
    remark = models.TextField(blank=True, verbose_name='备注')

    # 系统字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'weekly_reports'
        verbose_name = 'Weekly Report'
        verbose_name_plural = 'Weekly Reports'
        ordering = ['-due_date', '-created_at']
        indexes = [
            models.Index(fields=['client_name']),
            models.Index(fields=['area']),
            models.Index(fields=['tasks']),
            models.Index(fields=['responsibility']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.client_name} - {self.definition[:50]}"
