from django.db import models


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

