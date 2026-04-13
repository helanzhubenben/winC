<template>
  <div class="weekly-report-list">
    <el-card class="toolbar-card" shadow="never">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="12" :md="6">
          <el-input
            v-model="searchParams.search"
            placeholder="搜索客户名称、任务"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-input
            v-model="searchParams.area"
            placeholder="区域"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-input
            v-model="searchParams.responsibility"
            placeholder="责任人"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </el-col>
        <el-col :xs="12" :sm="6" :md="4" style="text-align: right">
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建报告
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="reports"
        stripe
        style="width: 100%"
        @row-click="handleRowClick"
      >
        <el-table-column prop="client_name" label="客户名称" min-width="150" />
        <el-table-column prop="area" label="区域" width="120" />
        <el-table-column prop="tasks" label="任务" min-width="200" />
        <el-table-column prop="definition" label="项目定义" min-width="200" show-overflow-tooltip />
        <el-table-column prop="due_date" label="到期日期" width="120" />
        <el-table-column prop="responsibility" label="责任人" width="120" />
        <el-table-column prop="actions_count" label="行动记录" width="100" align="center" />
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { getWeeklyReports, deleteWeeklyReport } from '../api/weeklyReport'

const router = useRouter()

const loading = ref(false)
const reports = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const searchParams = ref({
  search: '',
  area: '',
  responsibility: ''
})

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

const handleSearch = () => {
  currentPage.value = 1
  loadReports()
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
  router.push(`/weekly-reports/${row.id}`)
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
    loadReports()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

const formatDateTime = (dateTime) => {
  if (!dateTime) return ''
  return new Date(dateTime).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
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

.table-card {
  min-height: 400px;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>
