<template>
  <div class="weekly-report-list">
    <el-card class="toolbar-card" shadow="never">
      <!-- 状态筛选标签 -->
      <el-row :gutter="16" style="margin-bottom: 16px">
        <el-col :span="24">
          <el-radio-group v-model="searchParams.status" @change="handleSearch">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="in_progress">进行中</el-radio-button>
            <el-radio-button label="completed">已完成</el-radio-button>
          </el-radio-group>
        </el-col>
      </el-row>

      <!-- 搜索和筛选 -->
      <el-row :gutter="16" style="margin-bottom: 12px">
        <el-col :xs="24" :sm="12" :md="5">
          <el-input
            v-model="searchParams.search"
            placeholder="搜索客户名称、项目定义"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :xs="12" :sm="6" :md="3">
          <el-input
            v-model="searchParams.area"
            placeholder="区域"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :xs="12" :sm="6" :md="3">
          <el-input
            v-model="searchParams.tasks"
            placeholder="任务类型"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :xs="12" :sm="6" :md="3">
          <el-input
            v-model="searchParams.responsibility"
            placeholder="责任人"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleDateRangeChange"
            style="width: 100%"
          />
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="24" style="text-align: right">
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建报告
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="16" class="content-row">
      <!-- 左侧：周报列表 -->
      <el-col :xs="24" :lg="14">
        <el-card class="table-card" shadow="never">
          <el-table
            v-loading="loading"
            :data="reports"
            stripe
            highlight-current-row
            style="width: 100%"
            @row-click="handleRowClick"
            @current-change="handleCurrentChange"
            @sort-change="handleSortChange"
          >
            <el-table-column prop="client_name" label="客户名称" min-width="130" />
            <el-table-column prop="area" label="区域" width="100" />
            <el-table-column prop="tasks" label="任务" min-width="120" show-overflow-tooltip />
            <el-table-column prop="definition" label="项目定义" min-width="150" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 'completed' ? 'success' : 'warning'" size="small">
                  {{ row.status === 'completed' ? '已完成' : '进行中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="due_date" label="到期日期" width="110" sortable="custom" />
            <el-table-column prop="responsibility" label="责任人" width="90" />
            <el-table-column prop="actions_count" label="行动" width="70" align="center" />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button
                  link
                  :type="row.status === 'completed' ? 'warning' : 'success'"
                  size="small"
                  @click.stop="handleToggleStatus(row)"
                >
                  {{ row.status === 'completed' ? '进行中' : '完成' }}
                </el-button>
                <el-button link type="primary" size="small" @click.stop="handleEdit(row)">
                  编辑
                </el-button>
                <el-button link type="danger" size="small" @click.stop="handleDelete(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
            style="margin-top: 16px; justify-content: flex-end"
          />
        </el-card>
      </el-col>

      <!-- 右侧：行动记录详情 -->
      <el-col :xs="24" :lg="10">
        <el-card class="action-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>行动记录</span>
              <el-button
                v-if="selectedReport"
                type="primary"
                size="small"
                @click="handleAddAction"
              >
                <el-icon><Plus /></el-icon>
                添加行动
              </el-button>
            </div>
          </template>

          <div v-if="!selectedReport" class="empty-state">
            <el-empty description="请选择一个客户查看行动记录" />
          </div>

          <div v-else-if="loadingActions" class="loading-state">
            <el-skeleton :rows="5" animated />
          </div>

          <div v-else-if="actions.length === 0" class="empty-state">
            <el-empty description="暂无行动记录">
              <el-button type="primary" @click="handleAddAction">添加第一条行动</el-button>
            </el-empty>
          </div>

          <div v-else class="actions-list">
            <el-card
              v-for="action in actions"
              :key="action.id"
              class="action-item"
              shadow="hover"
            >
              <div class="action-content">
                <p><strong>行动内容：</strong>{{ action.action }}</p>
                <p v-if="action.result"><strong>结果：</strong>{{ action.result }}</p>
              </div>
              <div class="action-meta">
                <el-tag size="small">{{ formatDate(action.action_date) }}</el-tag>
                <el-tag v-if="action.next_step" type="info" size="small">
                  下一步：{{ action.next_step }}
                </el-tag>
              </div>
              <div class="action-actions">
                <el-button link type="primary" size="small" @click="handleEditAction(action)">
                  编辑
                </el-button>
                <el-button link type="danger" size="small" @click="handleDeleteAction(action)">
                  删除
                </el-button>
              </div>
            </el-card>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加/编辑行动对话框 -->
    <el-dialog
      v-model="actionDialogVisible"
      :title="actionForm.id !== null ? '编辑行动' : '添加行动'"
      width="600px"
    >
      <el-form ref="actionFormRef" :model="actionForm" :rules="actionRules" label-width="100px">
        <el-form-item label="行动日期" prop="action_date">
          <el-date-picker
            v-model="actionForm.action_date"
            type="date"
            placeholder="选择行动日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="行动内容" prop="action">
          <el-input
            v-model="actionForm.action"
            type="textarea"
            :rows="3"
            placeholder="请输入行动内容"
          />
        </el-form-item>

        <el-form-item label="结果">
          <el-input
            v-model="actionForm.result"
            type="textarea"
            :rows="2"
            placeholder="请输入结果"
          />
        </el-form-item>

        <el-form-item label="下一步">
          <el-input
            v-model="actionForm.next_step"
            type="textarea"
            :rows="2"
            placeholder="请输入下一步计划"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="actionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveAction">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import {
  getWeeklyReports,
  deleteWeeklyReport,
  updateWeeklyReport,
  patchWeeklyReport,
  getWeeklyReportActions,
  createWeeklyReportAction,
  updateWeeklyReportAction,
  deleteWeeklyReportAction
} from '../api/weeklyReport'

const router = useRouter()

const loading = ref(false)
const reports = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const searchParams = ref({
  search: '',
  area: '',
  tasks: '',
  responsibility: '',
  status: '',
  due_date_after: '',
  due_date_before: '',
  ordering: ''
})

const dateRange = ref(null)

// 选中的报告和行动记录
const selectedReport = ref(null)
const loadingActions = ref(false)
const actions = ref([])

// 行动对话框
const actionDialogVisible = ref(false)
const actionFormRef = ref(null)
const actionForm = ref({
  id: null,
  action_date: '',
  action: '',
  result: '',
  next_step: ''
})

const actionRules = {
  action_date: [{ required: true, message: '请选择行动日期', trigger: 'change' }],
  action: [{ required: true, message: '请输入行动内容', trigger: 'blur' }]
}

const loadReports = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...searchParams.value
    }

    // 移除空值参数
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })

    const response = await getWeeklyReports(params)
    reports.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    ElMessage.error('加载报告列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadActions = async (reportId) => {
  loadingActions.value = true
  try {
    const response = await getWeeklyReportActions(reportId)
    actions.value = response.data
  } catch (error) {
    ElMessage.error('加载行动记录失败')
    console.error(error)
  } finally {
    loadingActions.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadReports()
}

const handleDateRangeChange = (value) => {
  if (value && value.length === 2) {
    searchParams.value.due_date_after = value[0]
    searchParams.value.due_date_before = value[1]
  } else {
    searchParams.value.due_date_after = ''
    searchParams.value.due_date_before = ''
  }
  handleSearch()
}

const handleSortChange = ({ prop, order }) => {
  if (order === 'ascending') {
    searchParams.value.ordering = 'due_date'
  } else if (order === 'descending') {
    searchParams.value.ordering = '-due_date'
  } else {
    searchParams.value.ordering = ''
  }
  handleSearch()
}

const handleReset = () => {
  searchParams.value = {
    search: '',
    area: '',
    tasks: '',
    responsibility: '',
    status: '',
    due_date_after: '',
    due_date_before: '',
    ordering: ''
  }
  dateRange.value = null
  handleSearch()
}

const handlePageChange = () => {
  loadReports()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadReports()
}

const handleCreate = () => {
  router.push('/weekly-reports/new')
}

const handleEdit = (row) => {
  router.push(`/weekly-reports/${row.id}`)
}

const handleRowClick = (row) => {
  selectedReport.value = row
  loadActions(row.id)
}

const handleCurrentChange = (currentRow) => {
  if (currentRow) {
    selectedReport.value = currentRow
    loadActions(currentRow.id)
  }
}

const handleToggleStatus = async (row) => {
  try {
    const newStatus = row.status === 'completed' ? 'in_progress' : 'completed'
    const statusText = newStatus === 'completed' ? '已完成' : '进行中'

    await patchWeeklyReport(row.id, { status: newStatus })
    ElMessage.success(`已标记为${statusText}`)
    loadReports()

    // 如果是当前选中的报告，更新选中状态
    if (selectedReport.value && selectedReport.value.id === row.id) {
      selectedReport.value.status = newStatus
    }
  } catch (error) {
    ElMessage.error('更新状态失败')
    console.error(error)
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除报告"${row.client_name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteWeeklyReport(row.id)
    ElMessage.success('删除成功')

    // 如果删除的是当前选中的报告，清空右侧
    if (selectedReport.value && selectedReport.value.id === row.id) {
      selectedReport.value = null
      actions.value = []
    }

    loadReports()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

const handleAddAction = () => {
  actionForm.value = {
    id: null,
    action_date: new Date().toISOString().split('T')[0],
    action: '',
    result: '',
    next_step: ''
  }
  actionDialogVisible.value = true
}

const handleEditAction = (action) => {
  actionForm.value = {
    id: action.id,
    action_date: action.action_date,
    action: action.action,
    result: action.result || '',
    next_step: action.next_step || ''
  }
  actionDialogVisible.value = true
}

const handleSaveAction = async () => {
  try {
    await actionFormRef.value.validate()

    if (actionForm.value.id !== null) {
      // 更新
      await updateWeeklyReportAction(
        selectedReport.value.id,
        actionForm.value.id,
        actionForm.value
      )
      ElMessage.success('更新成功')
    } else {
      // 创建
      await createWeeklyReportAction(selectedReport.value.id, actionForm.value)
      ElMessage.success('添加成功')
    }

    actionDialogVisible.value = false
    loadActions(selectedReport.value.id)
    loadReports() // 刷新列表以更新行动记录数量
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('保存失败')
      console.error(error)
    }
  }
}

const handleDeleteAction = async (action) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条行动记录吗？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteWeeklyReportAction(selectedReport.value.id, action.id)
    ElMessage.success('删除成功')
    loadActions(selectedReport.value.id)
    loadReports() // 刷新列表以更新行动记录数量
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadReports()
})
</script>

<style scoped>
.weekly-report-list {
  padding: 20px;
}

.toolbar-card {
  margin-bottom: 16px;
}

.content-row {
  min-height: calc(100vh - 250px);
}

.table-card {
  min-height: 600px;
}

.action-card {
  min-height: 600px;
  max-height: calc(100vh - 250px);
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.loading-state {
  padding: 20px;
}

.actions-list {
  max-height: calc(100vh - 370px);
  overflow-y: auto;
}

.action-item {
  margin-bottom: 12px;
}

.action-content {
  margin-bottom: 12px;
}

.action-content p {
  margin: 0 0 8px 0;
  line-height: 1.6;
  word-break: break-word;
}

.action-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.action-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

/* 响应式布局 */
@media (max-width: 992px) {
  .content-row {
    flex-direction: column;
  }

  .action-card {
    margin-top: 16px;
    max-height: 500px;
  }
}
</style>
