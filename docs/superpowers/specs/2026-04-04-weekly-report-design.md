# Weekly Report 功能设计文档

**日期**: 2026-04-04  
**项目**: Fishpool 客户池管理系统  
**功能**: Weekly Report 项目跟进管理

---

## 一、需求概述

将现有 Excel Weekly Report 表格整合到 Fishpool 系统中，实现项目跟进管理功能。核心需求是管理客户项目的行动记录，支持查看所有项目列表和在客户详情页查看特定客户的项目。

### 1.1 功能范围

- **混合模式**: 独立的 Weekly Report 列表页面 + 客户详情页子功能
- **数据字段**: 完全保留 Excel 中的所有字段
- **客户关联**: 弱关联（允许手动输入客户名称，系统自动匹配）
- **功能优先级**: 行动记录管理 > 项目列表和筛选 = 项目详情和编辑

### 1.2 Excel 数据结构

原始 Excel 包含以下字段：
- Client（客户名称）
- Area（区域）、Address（地址）
- Tasks（任务类型）
- Definition（任务定义/项目名称）
- Due Date（截止日期）
- Revise Date（修订日期）
- Finish Date（完成日期）
- Revenue（营收，可能包含范围描述如 "100-200万"）
- Actions（行动记录，时间线格式）
- Responsibility（责任人）
- Remark（备注）

---

## 二、技术方案

### 2.1 方案选择

**选择：单表设计 + JSON 存储行动记录**

**Why**:
- 行动记录是时间序列数据，频繁追加但很少修改
- JSON 字段避免了多表关联查询的性能开销
- Django JSONField 原生支持查询和索引
- 简化了数据模型，降低维护成本

**How to apply**:
- 使用 `models.JSONField` 存储行动记录数组
- 每条记录包含 `timestamp`、`content`、`user` 字段
- 前端使用 Element Plus Timeline 组件渲染
- 后端提供专门的 API 端点管理行动记录

### 2.2 数据模型设计

**文件位置**: `backend/customers/models.py`

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class WeeklyReport(models.Model):
    """Weekly Report 项目跟进记录"""
    
    # 客户信息（弱关联）
    client_name = models.CharField(
        max_length=200, 
        db_index=True,
        verbose_name="客户名称",
        help_text="手动输入或从客户列表选择"
    )
    customer = models.ForeignKey(
        'Customer',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='weekly_reports',
        verbose_name="关联客户",
        help_text="系统自动匹配或手动关联"
    )
    
    # 基本信息
    area = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="区域"
    )
    address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="地址"
    )
    tasks = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="任务类型"
    )
    definition = models.TextField(
        verbose_name="任务定义/项目名称"
    )
    
    # 时间管理
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="截止日期"
    )
    revise_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="修订日期"
    )
    finish_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="完成日期"
    )
    
    # 营收（使用 CharField 因为可能包含范围描述）
    revenue = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="营收",
        help_text="例如: 100万, 50-100万"
    )
    
    # 行动记录（JSON 数组）
    actions = models.JSONField(
        default=list,
        verbose_name="行动记录",
        help_text="格式: [{timestamp, content, user}]"
    )
    
    # 其他字段
    responsibility = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="责任人"
    )
    remark = models.TextField(
        blank=True,
        verbose_name="备注"
    )
    
    # 元数据
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reports',
        verbose_name="创建人"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )
    
    class Meta:
        db_table = 'weekly_report'
        verbose_name = 'Weekly Report'
        verbose_name_plural = 'Weekly Reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client_name']),
            models.Index(fields=['due_date']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.client_name} - {self.definition[:30]}"
    
    def save(self, *args, **kwargs):
        """保存时自动匹配客户"""
        if not self.customer and self.client_name:
            from .models import Customer
            # 尝试精确匹配
            try:
                self.customer = Customer.objects.get(name__iexact=self.client_name)
            except Customer.DoesNotExist:
                pass
            except Customer.MultipleObjectsReturned:
                # 如果有多个匹配，取第一个
                self.customer = Customer.objects.filter(
                    name__iexact=self.client_name
                ).first()
        super().save(*args, **kwargs)
```

---

## 三、API 设计

### 3.1 RESTful 端点

**基础 CRUD**

```
GET    /api/weekly-reports/          # 获取项目列表
POST   /api/weekly-reports/          # 创建新项目
GET    /api/weekly-reports/{id}/     # 获取项目详情
PUT    /api/weekly-reports/{id}/     # 更新项目
PATCH  /api/weekly-reports/{id}/     # 部分更新项目
DELETE /api/weekly-reports/{id}/     # 删除项目
```

**行动记录管理**

```
POST   /api/weekly-reports/{id}/add-action/           # 添加行动记录
PUT    /api/weekly-reports/{id}/actions/{index}/      # 更新指定行动记录
DELETE /api/weekly-reports/{id}/actions/{index}/      # 删除指定行动记录
```

**客户关联**

```
GET    /api/customers/{id}/weekly-reports/            # 获取客户的所有项目
```

### 3.2 查询参数

**列表筛选** (`GET /api/weekly-reports/`)

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `client_name` | string | 客户名称（模糊搜索） | `?client_name=华为` |
| `area` | string | 区域 | `?area=华东` |
| `tasks` | string | 任务类型 | `?tasks=新项目` |
| `responsibility` | string | 责任人 | `?responsibility=张三` |
| `due_date_from` | date | 截止日期起始 | `?due_date_from=2026-04-01` |
| `due_date_to` | date | 截止日期结束 | `?due_date_to=2026-04-30` |
| `is_finished` | boolean | 是否完成 | `?is_finished=false` |
| `search` | string | 全文搜索（客户名称、定义、备注） | `?search=5G` |
| `ordering` | string | 排序字段 | `?ordering=-due_date` |
| `page` | integer | 页码 | `?page=2` |
| `page_size` | integer | 每页数量 | `?page_size=20` |

### 3.3 请求/响应示例

**创建项目** (`POST /api/weekly-reports/`)

```json
// Request
{
  "client_name": "华为技术有限公司",
  "area": "华东",
  "address": "上海市浦东新区",
  "tasks": "新项目开发",
  "definition": "5G 基站设备采购项目",
  "due_date": "2026-06-30",
  "revenue": "500-800万",
  "responsibility": "张三",
  "remark": "重点项目，需要密切跟进"
}

// Response (201 Created)
{
  "id": 1,
  "client_name": "华为技术有限公司",
  "customer": {
    "id": 5,
    "name": "华为技术有限公司",
    "level": "A"
  },
  "area": "华东",
  "address": "上海市浦东新区",
  "tasks": "新项目开发",
  "definition": "5G 基站设备采购项目",
  "due_date": "2026-06-30",
  "revise_date": null,
  "finish_date": null,
  "revenue": "500-800万",
  "actions": [],
  "responsibility": "张三",
  "remark": "重点项目，需要密切跟进",
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "created_at": "2026-04-04T10:30:00Z",
  "updated_at": "2026-04-04T10:30:00Z"
}
```

**添加行动记录** (`POST /api/weekly-reports/{id}/add-action/`)

```json
// Request
{
  "content": "与客户技术负责人李工进行了初步沟通，确认了技术需求"
}

// Response (200 OK)
{
  "id": 1,
  "actions": [
    {
      "timestamp": "2026-04-04T14:30:00Z",
      "content": "与客户技术负责人李工进行了初步沟通，确认了技术需求",
      "user": "张三"
    }
  ]
}
```

**获取项目列表** (`GET /api/weekly-reports/?is_finished=false&ordering=-due_date`)

```json
// Response (200 OK)
{
  "count": 25,
  "next": "http://localhost:8000/api/weekly-reports/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "client_name": "华为技术有限公司",
      "customer": {
        "id": 5,
        "name": "华为技术有限公司",
        "level": "A"
      },
      "definition": "5G 基站设备采购项目",
      "due_date": "2026-06-30",
      "revenue": "500-800万",
      "actions_count": 3,
      "latest_action": {
        "timestamp": "2026-04-04T14:30:00Z",
        "content": "与客户技术负责人李工进行了初步沟通..."
      },
      "responsibility": "张三",
      "created_at": "2026-04-04T10:30:00Z"
    }
  ]
}
```

---

## 四、前端设计

### 4.1 页面结构

**路由配置** (`frontend/src/router/index.js`)

```javascript
{
  path: '/weekly-reports',
  name: 'WeeklyReportList',
  component: () => import('@/views/WeeklyReportListPage.vue'),
  meta: { title: 'Weekly Report 项目管理' }
}
```

**页面组件**

1. **WeeklyReportListPage.vue** - 项目列表页
   - 顶部筛选栏（客户名称、区域、任务类型、责任人、截止日期范围）
   - 项目列表表格（显示客户、项目名称、截止日期、营收、最新行动、责任人）
   - 新建项目按钮
   - 分页组件

2. **CustomerDetailPage.vue** - 客户详情页（扩展）
   - 新增 "Weekly Report" Tab
   - 显示该客户的所有项目列表
   - 快速创建项目按钮（自动填充客户信息）

### 4.2 核心组件

**1. WeeklyReportDialog.vue** - 项目详情/编辑对话框

**布局**: 左右分栏设计

```vue
<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑项目' : '项目详情'"
    width="1200px"
    @close="handleClose"
  >
    <div class="dialog-content">
      <!-- 左侧：表单区域 (60%) -->
      <div class="form-section">
        <WeeklyReportForm
          :model-value="formData"
          :is-edit="isEdit"
          @update:model-value="handleFormUpdate"
        />
      </div>
      
      <!-- 右侧：行动记录时间线 (40%) -->
      <div class="timeline-section">
        <ActionTimeline
          :actions="formData.actions"
          :report-id="formData.id"
          @action-added="handleActionAdded"
          @action-updated="handleActionUpdated"
          @action-deleted="handleActionDeleted"
        />
      </div>
    </div>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button v-if="isEdit" type="primary" @click="handleSave">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.dialog-content {
  display: flex;
  gap: 24px;
  min-height: 600px;
}

.form-section {
  flex: 0 0 60%;
  overflow-y: auto;
}

.timeline-section {
  flex: 0 0 40%;
  border-left: 1px solid #e4e7ed;
  padding-left: 24px;
  overflow-y: auto;
}
</style>
```

**2. WeeklyReportForm.vue** - 项目表单

**关键功能**: 客户名称自动完成

```vue
<template>
  <el-form :model="formData" label-width="100px">
    <!-- 客户名称（自动完成） -->
    <el-form-item label="客户名称" required>
      <el-autocomplete
        v-model="formData.client_name"
        :fetch-suggestions="searchCustomers"
        placeholder="输入客户名称"
        @select="handleCustomerSelect"
      >
        <template #default="{ item }">
          <div class="customer-item">
            <span>{{ item.name }}</span>
            <el-tag :type="getLevelType(item.level)" size="small">
              {{ item.level }}
            </el-tag>
          </div>
        </template>
      </el-autocomplete>
    </el-form-item>
    
    <!-- 区域 -->
    <el-form-item label="区域">
      <el-input v-model="formData.area" />
    </el-form-item>
    
    <!-- 地址 -->
    <el-form-item label="地址">
      <el-input v-model="formData.address" />
    </el-form-item>
    
    <!-- 任务类型 -->
    <el-form-item label="任务类型">
      <el-input v-model="formData.tasks" />
    </el-form-item>
    
    <!-- 任务定义/项目名称 -->
    <el-form-item label="项目名称" required>
      <el-input
        v-model="formData.definition"
        type="textarea"
        :rows="3"
      />
    </el-form-item>
    
    <!-- 时间管理 -->
    <el-form-item label="截止日期">
      <el-date-picker
        v-model="formData.due_date"
        type="date"
        placeholder="选择日期"
      />
    </el-form-item>
    
    <el-form-item label="修订日期">
      <el-date-picker
        v-model="formData.revise_date"
        type="date"
        placeholder="选择日期"
      />
    </el-form-item>
    
    <el-form-item label="完成日期">
      <el-date-picker
        v-model="formData.finish_date"
        type="date"
        placeholder="选择日期"
      />
    </el-form-item>
    
    <!-- 营收 -->
    <el-form-item label="营收">
      <el-input
        v-model="formData.revenue"
        placeholder="例如: 100万, 50-100万"
      />
    </el-form-item>
    
    <!-- 责任人 -->
    <el-form-item label="责任人">
      <el-input v-model="formData.responsibility" />
    </el-form-item>
    
    <!-- 备注 -->
    <el-form-item label="备注">
      <el-input
        v-model="formData.remark"
        type="textarea"
        :rows="3"
      />
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref } from 'vue'
import { searchCustomers as apiSearchCustomers } from '@/api/customer'

const props = defineProps({
  modelValue: Object,
  isEdit: Boolean
})

const emit = defineEmits(['update:modelValue'])

const formData = ref(props.modelValue)

// 客户搜索
const searchCustomers = async (queryString, cb) => {
  if (!queryString) {
    cb([])
    return
  }
  
  try {
    const { data } = await apiSearchCustomers({ search: queryString })
    cb(data.results)
  } catch (error) {
    console.error('搜索客户失败:', error)
    cb([])
  }
}

// 选择客户
const handleCustomerSelect = (item) => {
  formData.value.client_name = item.name
  formData.value.customer_id = item.id
  // 自动填充区域和地址
  if (item.area) formData.value.area = item.area
  if (item.city) formData.value.address = item.city
}

const getLevelType = (level) => {
  const types = { A: 'danger', B: 'warning', C: 'success', D: 'info' }
  return types[level] || 'info'
}
</script>
```

**3. ActionTimeline.vue** - 行动记录时间线（核心组件）

**功能**: 使用 Element Plus Timeline 组件展示和管理行动记录

```vue
<template>
  <div class="action-timeline">
    <div class="timeline-header">
      <h3>行动记录</h3>
      <el-button
        type="primary"
        size="small"
        :icon="Plus"
        @click="showAddDialog = true"
      >
        添加记录
      </el-button>
    </div>
    
    <el-timeline v-if="actions.length > 0">
      <el-timeline-item
        v-for="(action, index) in sortedActions"
        :key="index"
        :timestamp="formatTimestamp(action.timestamp)"
        placement="top"
      >
        <div class="action-content">
          <div class="action-text">{{ action.content }}</div>
          <div class="action-meta">
            <span class="action-user">{{ action.user }}</span>
            <div class="action-operations">
              <el-button
                link
                type="primary"
                size="small"
                @click="handleEdit(index)"
              >
                编辑
              </el-button>
              <el-button
                link
                type="danger"
                size="small"
                @click="handleDelete(index)"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>
      </el-timeline-item>
    </el-timeline>
    
    <el-empty v-else description="暂无行动记录" />
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editIndex !== null ? '编辑行动记录' : '添加行动记录'"
      width="500px"
    >
      <el-input
        v-model="actionContent"
        type="textarea"
        :rows="5"
        placeholder="请输入行动记录内容"
      />
      <template #footer>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { addAction, updateAction, deleteAction } from '@/api/weeklyReport'

const props = defineProps({
  actions: {
    type: Array,
    default: () => []
  },
  reportId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['action-added', 'action-updated', 'action-deleted'])

const showAddDialog = ref(false)
const actionContent = ref('')
const editIndex = ref(null)

// 按时间倒序排列
const sortedActions = computed(() => {
  return [...props.actions].sort((a, b) => 
    new Date(b.timestamp) - new Date(a.timestamp)
  )
})

// 格式化时间戳
const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 添加/编辑行动记录
const handleSubmit = async () => {
  if (!actionContent.value.trim()) {
    ElMessage.warning('请输入行动记录内容')
    return
  }
  
  try {
    if (editIndex.value !== null) {
      // 编辑
      await updateAction(props.reportId, editIndex.value, {
        content: actionContent.value
      })
      emit('action-updated', editIndex.value, actionContent.value)
      ElMessage.success('更新成功')
    } else {
      // 添加
      const { data } = await addAction(props.reportId, {
        content: actionContent.value
      })
      emit('action-added', data.actions)
      ElMessage.success('添加成功')
    }
    
    handleCancel()
  } catch (error) {
    ElMessage.error('操作失败: ' + error.message)
  }
}

// 编辑
const handleEdit = (index) => {
  editIndex.value = index
  actionContent.value = props.actions[index].content
  showAddDialog.value = true
}

// 删除
const handleDelete = async (index) => {
  try {
    await ElMessageBox.confirm('确定删除这条行动记录吗？', '提示', {
      type: 'warning'
    })
    
    await deleteAction(props.reportId, index)
    emit('action-deleted', index)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

// 取消
const handleCancel = () => {
  showAddDialog.value = false
  actionContent.value = ''
  editIndex.value = null
}
</script>

<style scoped>
.action-timeline {
  height: 100%;/re
  display: flex;
  flex-direction: column;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.timeline-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.action-content {
  padding: 8px 0;
}

.action-text {
  margin-bottom: 8px;
  line-height: 1.6;
  color: #303133;
}

.action-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-user {
  font-size: 12px;
  color: #909399;
}

.action-operations {
  display: flex;
  gap: 8px;
}
</style>
```

### 4.3 API 层

**文件位置**: `frontend/src/api/weeklyReport.js`

```javascript
import request from '@/utils/request'

// 获取项目列表
export function getWeeklyReports(params) {
  return request({
    url: '/api/weekly-reports/',
    method: 'get',
    params
  })
}

// 获取项目详情
export function getWeeklyReport(id) {
  return request({
    url: `/api/weekly-reports/${id}/`,
    method: 'get'
  })
}

// 创建项目
export function createWeeklyReport(data) {
  return request({
    url: '/api/weekly-reports/',
    method: 'post',
    data
  })
}

// 更新项目
export function updateWeeklyReport(id, data) {
  return request({
    url: `/api/weekly-reports/${id}/`,
    method: 'put',
    data
  })
}

// 删除项目
export function deleteWeeklyReport(id) {
  return request({
    url: `/api/weekly-reports/${id}/`,
    method: 'delete'
  })
}

// 添加行动记录
export function addAction(reportId, data) {
  return request({
    url: `/api/weekly-reports/${reportId}/add-action/`,
    method: 'post',
    data
  })
}

// 更新行动记录
export function updateAction(reportId, index, data) {
  return request({
    url: `/api/weekly-reports/${reportId}/actions/${index}/`,
    method: 'put',
    data
  })
}

// 删除行动记录
export function deleteAction(reportId, index) {
  return request({
    url: `/api/weekly-reports/${reportId}/actions/${index}/`,
    method: 'delete'
  })
}

// 获取客户的项目列表
export function getCustomerReports(customerId) {
  return request({
    url: `/api/customers/${customerId}/weekly-reports/`,
    method: 'get'
  })
}
```

---

## 五、关键逻辑

### 5.1 客户自动匹配

**Why**:
- 用户可能手动输入客户名称，也可能从列表选择
- 需要自动关联到系统中的客户记录，以便在客户详情页显示
- 匹配失败时不应阻止创建，保持弱关联的灵活性

**How to apply**:

**后端实现** (`backend/customers/models.py`)

```python
def save(self, *args, **kwargs):
    """保存时自动匹配客户"""
    if not self.customer and self.client_name:
        from .models import Customer
        # 尝试精确匹配（不区分大小写）
        try:
            self.customer = Customer.objects.get(name__iexact=self.client_name)
        except Customer.DoesNotExist:
            # 尝试模糊匹配
            customers = Customer.objects.filter(name__icontains=self.client_name)
            if customers.count() == 1:
                self.customer = customers.first()
        except Customer.MultipleObjectsReturned:
            # 如果有多个匹配，取第一个
            self.customer = Customer.objects.filter(
                name__iexact=self.client_name
            ).first()
    super().save(*args, **kwargs)
```

**前端实现** (`WeeklyReportForm.vue`)

```javascript
// 客户搜索（防抖）
const searchCustomers = debounce(async (queryString, cb) => {
  if (!queryString || queryString.length < 2) {
    cb([])
    return
  }
  
  try {
    const { data } = await apiSearchCustomers({ 
      search: queryString,
      page_size: 10 
    })
    cb(data.results)
  } catch (error) {
    console.error('搜索客户失败:', error)
    cb([])
  }
}, 300)

// 选择客户后自动填充
const handleCustomerSelect = (item) => {
  formData.value.client_name = item.name
  formData.value.customer_id = item.id
  
  // 自动填充区域和地址（如果为空）
  if (!formData.value.area && item.area) {
    formData.value.area = item.area
  }
  if (!formData.value.address && item.city) {
    formData.value.address = item.city
  }
}
```

### 5.2 行动记录添加

**Why**:
- 行动记录是时间序列数据，需要自动记录时间戳和操作人
- 使用 JSON 数组存储，避免多表关联
- 需要保证数据一致性，防止并发修改冲突

**How to apply**:

**后端实现** (`backend/customers/views.py`)

```python
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

@action(detail=True, methods=['post'])
def add_action(self, request, pk=None):
    """添加行动记录"""
    report = self.get_object()
    content = request.data.get('content', '').strip()
    
    if not content:
        return Response(
            {'error': '行动记录内容不能为空'},
            status=400
        )
    
    # 创建新的行动记录
    new_action = {
        'timestamp': timezone.now().isoformat(),
        'content': content,
        'user': request.user.username
    }
    
    # 追加到数组
    report.actions.append(new_action)
    report.save()
    
    return Response({
        'id': report.id,
        'actions': report.actions
    })

@action(detail=True, methods=['put'], url_path='actions/(?P<index>[0-9]+)')
def update_action(self, request, pk=None, index=None):
    """更新指定行动记录"""
    report = self.get_object()
    index = int(index)
    
    if index < 0 or index >= len(report.actions):
        return Response(
            {'error': '行动记录索引无效'},
            status=400
        )
    
    content = request.data.get('content', '').strip()
    if not content:
        return Response(
            {'error': '行动记录内容不能为空'},
            status=400
        )
    
    # 更新内容，保留原时间戳和用户
    report.actions[index]['content'] = content
    report.save()
    
    return Response({
        'id': report.id,
        'actions': report.actions
    })

@action(detail=True, methods=['delete'], url_path='actions/(?P<index>[0-9]+)')
def delete_action(self, request, pk=None, index=None):
    """删除指定行动记录"""
    report = self.get_object()
    index = int(index)
    
    if index < 0 or index >= len(report.actions):
        return Response(
            {'error': '行动记录索引无效'},
            status=400
        )
    
    # 删除记录
    report.actions.pop(index)
    report.save()
    
    return Response({
        'id': report.id,
        'actions': report.actions
    })
```

### 5.3 错误处理

**Why**:
- 用户输入可能不完整或格式错误
- 网络请求可能失败
- 需要友好的错误提示，避免数据丢失

**How to apply**:

**前端统一错误处理** (`frontend/src/utils/request.js`)

```javascript
// 响应拦截器
service.interceptors.response.use(
  response => response,
  error => {
    const { response } = error
    
    if (response) {
      // 服务器返回错误
      const message = response.data?.error || 
                     response.data?.detail || 
                     '操作失败'
      
      ElMessage.error({
        message,
        duration: 3000
      })
    } else {
      // 网络错误
      ElMessage.error({
        message: '网络连接失败，请检查网络设置',
        duration: 3000
      })
    }
    
    return Promise.reject(error)
  }
)
```

**表单验证** (`WeeklyReportForm.vue`)

```javascript
const rules = {
  client_name: [
    { required: true, message: '请输入客户名称', trigger: 'blur' }
  ],
  definition: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 5, message: '项目名称至少 5 个字符', trigger: 'blur' }
  ],
  due_date: [
    { 
      validator: (rule, value, callback) => {
        if (value && new Date(value) < new Date()) {
          callback(new Error('截止日期不能早于今天'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}
```

---

## 六、实现计划

### 6.1 后端开发（预计 3-4 天）

**第 1 天：数据模型和迁移**
- 创建 `WeeklyReport` 模型
- 生成数据库迁移文件
- 运行迁移并测试
- 在 Django Admin 中注册模型

**第 2 天：API 基础功能**
- 创建 `WeeklyReportSerializer`
- 实现 `WeeklyReportViewSet`（CRUD）
- 配置 URL 路由
- 实现列表筛选和搜索
- 编写单元测试

**第 3 天：行动记录管理**
- 实现 `add_action` 端点
- 实现 `update_action` 端点
- 实现 `delete_action` 端点
- 添加权限控制（只能编辑自己的记录）
- 编写单元测试

**第 4 天：客户关联和优化**
- 实现客户关联端点
- 优化查询性能（select_related, prefetch_related）
- 添加数据验证
- 完善错误处理
- API 文档编写

### 6.2 前端开发（预计 4-5 天）

**第 1 天：基础架构**
- 创建 API 层（`api/weeklyReport.js`）
- 配置路由
- 创建页面骨架（`WeeklyReportListPage.vue`）
- 实现基础布局和导航

**第 2 天：列表页功能**
- 实现项目列表表格
- 实现筛选栏（客户、区域、日期范围等）
- 实现搜索功能
- 实现分页
- 实现排序

**第 3 天：表单和对话框**
- 创建 `WeeklyReportForm.vue`
- 实现客户自动完成
- 创建 `WeeklyReportDialog.vue`
- 实现左右分栏布局
- 实现表单验证

**第 4 天：行动记录时间线**
- 创建 `ActionTimeline.vue`
- 实现 Timeline 展示
- 实现添加行动记录
- 实现编辑/删除行动记录
- 实现实时更新

**第 5 天：客户详情页集成**
- 在 `CustomerDetailPage.vue` 添加 Weekly Report Tab
- 实现客户项目列表
- 实现快速创建功能（自动填充客户信息）
- 整体测试和优化

### 6.3 测试和优化（预计 1-2 天）

**功能测试**
- 创建、编辑、删除项目
- 添加、编辑、删除行动记录
- 客户自动匹配
- 筛选和搜索
- 分页和排序

**性能优化**
- 数据库查询优化
- 前端列表虚拟滚动（如果数据量大）
- API 响应缓存
- 图片/文件上传优化（如果需要）

**用户体验优化**
- 加载状态提示
- 错误提示优化
- 表单自动保存（草稿功能）
- 快捷键支持

**总计：8-11 天**

---

## 七、未来扩展

### 7.1 可选功能列表

**优先级 P1（高）**
- 行动记录支持附件上传（图片、文档）
- 项目状态管理（进行中、已完成、已取消）
- 截止日期提醒（邮件/站内通知）
- 导出功能（Excel、PDF）

**优先级 P2（中）**
- 项目模板功能（快速创建常见项目类型）
- 批量操作（批量分配责任人、批量修改截止日期）
- 项目统计看板（按区域、责任人、状态统计）
- 行动记录评论功能（多人协作）

**优先级 P3（低）**
- 项目甘特图视图
- 项目依赖关系管理
- 自动生成周报/月报
- 移动端适配

### 7.2 技术债务

- 考虑使用 Redis 缓存热门项目数据
- 考虑使用 Elasticsearch 实现全文搜索
- 考虑使用 WebSocket 实现实时协作
- 考虑使用 Celery 实现异步任务（邮件提醒、报表生成）

---

## 八、附录

### 8.1 数据库索引策略

```sql
-- 客户名称索引（用于搜索和关联）
CREATE INDEX idx_weekly_report_client_name ON weekly_report(client_name);

-- 截止日期索引（用于排序和筛选）
CREATE INDEX idx_weekly_report_due_date ON weekly_report(due_date);

-- 创建时间索引（用于默认排序）
CREATE INDEX idx_weekly_report_created_at ON weekly_report(created_at DESC);

-- 客户外键索引（Django 自动创建）
CREATE INDEX idx_weekly_report_customer_id ON weekly_report(customer_id);

-- 复合索引（用于常见查询组合）
CREATE INDEX idx_weekly_report_client_due ON weekly_report(client_name, due_date);
```

### 8.2 API 性能优化

**查询优化示例**

```python
# ViewSet 中的优化
class WeeklyReportViewSet(viewsets.ModelViewSet):
    queryset = WeeklyReport.objects.select_related(
        'customer', 'created_by'
    ).prefetch_related(
        'customer__contacts'
    )
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 只返回必要字段（列表页）
        if self.action == 'list':
            queryset = queryset.only(
                'id', 'client_name', 'definition', 
                'due_date', 'revenue', 'responsibility',
                'created_at'
            )
        
        return queryset
```

### 8.3 前端性能优化

**虚拟滚动示例**（如果列表数据量大）

```vue
<template>
  <el-table-v2
    :columns="columns"
    :data="tableData"
    :width="1200"
    :height="600"
    fixed
  />
</template>
```

**分页加载优化**

```javascript
// 使用 IntersectionObserver 实现无限滚动
const observer = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting && hasMore.value) {
    loadMore()
  }
})
```

---

## 九、总结

本设计文档提供了 Weekly Report 功能的完整技术方案，包括：

1. **数据模型**：单表设计 + JSON 存储行动记录，平衡了灵活性和性能
2. **API 设计**：RESTful 风格，提供完整的 CRUD 和行动记录管理端点
3. **前端架构**：混合模式（独立页面 + 客户详情页集成），核心是行动记录时间线组件
4. **关键逻辑**：客户自动匹配、行动记录管理、错误处理
5. **实现计划**：8-11 天完成核心功能
6. **未来扩展**：附件上传、状态管理、提醒通知等

该方案完全保留了 Excel 中的所有字段，采用弱关联设计保持灵活性，优先实现行动记录管理这一核心功能，为后续扩展预留了空间。
