<template>
  <div class="customer-list">
    <el-card class="toolbar-card" shadow="never">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="12" :md="6">
          <el-input
            v-model="searchParams.search"
            placeholder="搜索客户名称"
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
          <el-select
            v-model="searchParams.level"
            placeholder="客户等级"
            clearable
            style="width: 100%"
            @change="handleSearch"
          >
            <el-option label="Level A" value="A" />
            <el-option label="Level B" value="B" />
            <el-option label="Level C" value="C" />
            <el-option label="Level D" value="D" />
          </el-select>
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
            v-model="searchParams.city"
            placeholder="城市"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-select
            v-model="searchParams.business_model"
            placeholder="业务模式"
            clearable
            style="width: 100%"
            @change="handleSearch"
          >
            <el-option label="Hunting" value="Hunting" />
            <el-option label="Farming" value="Farming" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="6" :md="2">
          <el-button class="full-width" type="primary" @click="handleSearch">
            搜索
          </el-button>
        </el-col>
      </el-row>

      <div class="toolbar-actions">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增客户
        </el-button>
        <input
          ref="revenueFileInput"
          class="hidden-file-input"
          type="file"
          accept=".xlsx,.csv"
          @change="handleRevenueFileChange"
        />
        <input
          ref="customerFileInput"
          class="hidden-file-input"
          type="file"
          accept=".xlsx"
          @change="handleCustomerFileChange"
        />
        <el-button :loading="templateDownloading" @click="handleDownloadCustomerTemplate">
          <el-icon><Download /></el-icon>
          下载模板
        </el-button>
        <el-button :loading="customerImporting" @click="handleCustomerImportClick">
          <el-icon><Upload /></el-icon>
          导入客户
        </el-button>
        <el-button :loading="revenueImporting" @click="handleRevenueImportClick">
          <el-icon><Upload /></el-icon>
          导入营收
        </el-button>
        <el-button :loading="exporting" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出全部
        </el-button>
      </div>
    </el-card>

    <div v-loading="loading" class="content-area">
      <el-row v-if="customers.length" :gutter="20">
        <el-col
          v-for="customer in customers"
          :key="customer.id"
          :xs="24"
          :sm="12"
          :md="8"
          :xl="6"
        >
          <el-card class="customer-card" shadow="hover" @click="handleCardClick(customer.id)">
            <div class="card-header">
              <div>
                <h3>{{ customer.name }}</h3>
                <p>{{ customer.region || '未填写区域' }} / {{ customer.city || '未填写城市' }}</p>
              </div>
              <el-tag :type="getLevelType(customer.level)" size="large">
                {{ customer.level || 'D' }}
              </el-tag>
            </div>

            <div class="card-section">
              <span>业务模式</span>
              <strong>{{ customer.business_model || '未填写' }}</strong>
            </div>

            <div class="score-row">
              <el-tag>X: {{ customer.score_x ?? 0 }}</el-tag>
              <el-tag>Y: {{ customer.score_y ?? 0 }}</el-tag>
              <el-tag>Z: {{ customer.score_z ?? 0 }}</el-tag>
            </div>

            <div class="card-section">
              <span>潜在贡献</span>
              <strong>{{ customer.potential_contribution || '暂无' }}</strong>
            </div>

            <div class="revenue-grid">
              <div>
                <span>去年营收</span>
                <strong>{{ formatCurrency(customer.last_year_revenue) }}</strong>
              </div>
              <div>
                <span>上季度营收</span>
                <strong>{{ formatCurrency(customer.last_quarter_revenue) }}</strong>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty
        v-else-if="!loading"
        description="暂无客户数据"
      />
    </div>

    <el-pagination
      v-if="total > 0"
      v-model:current-page="searchParams.page"
      v-model:page-size="searchParams.page_size"
      class="pagination"
      :page-sizes="[12, 24, 48, 96]"
      :total="total"
      background
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handlePageSizeChange"
      @current-change="fetchCustomers"
    />

    <CustomerDialog
      v-model:visible="formVisible"
      :customer="currentCustomer"
      @success="fetchCustomers"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Download, Plus, Search, Upload } from '@element-plus/icons-vue'
import { downloadCustomerImportTemplate, getCustomers, importCustomers } from '../api/customer'
import { importCustomerRevenues } from '../api/customerRevenue'
import { exportWorkbook } from '../api/export'
import CustomerDialog from '../components/CustomerDialog.vue'

const router = useRouter()
const loading = ref(false)
const customers = ref([])
const total = ref(0)
const formVisible = ref(false)
const currentCustomer = ref(null)
const revenueFileInput = ref(null)
const customerFileInput = ref(null)
const revenueImporting = ref(false)
const customerImporting = ref(false)
const templateDownloading = ref(false)
const exporting = ref(false)

const searchParams = ref({
  search: '',
  level: '',
  area: '',
  city: '',
  business_model: '',
  page: 1,
  page_size: 12
})

const getLevelType = (level) => {
  const types = {
    A: 'danger',
    B: 'primary',
    C: 'success',
    D: 'info'
  }
  return types[level] || 'info'
}

const formatCurrency = (value) => {
  const amount = Number(value || 0)
  return amount.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const fetchCustomers = async () => {
  loading.value = true
  try {
    const response = await getCustomers(searchParams.value)
    const results = response.data?.results ?? response.data ?? []

    customers.value = Array.isArray(results) ? results : []
    total.value = response.data?.count ?? customers.value.length
  } catch (error) {
    customers.value = []
    total.value = 0
    ElMessage.error('获取客户列表失败，请确认后端服务已启动')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  searchParams.value.page = 1
  fetchCustomers()
}

const handlePageSizeChange = () => {
  searchParams.value.page = 1
  fetchCustomers()
}

const handleAdd = () => {
  currentCustomer.value = null
  formVisible.value = true
}

const handleCustomerImportClick = () => {
  customerFileInput.value?.click()
}

const handleDownloadCustomerTemplate = async () => {
  templateDownloading.value = true
  try {
    const response = await downloadCustomerImportTemplate()
    downloadBlob(response.data, 'customer_import_template.xlsx')
    ElMessage.success('模板下载完成')
  } catch (error) {
    ElMessage.error('模板下载失败')
    console.error(error)
  } finally {
    templateDownloading.value = false
  }
}

const handleCustomerFileChange = async (event) => {
  const file = event.target.files?.[0]
  if (!file) {
    return
  }

  customerImporting.value = true
  try {
    const response = await importCustomers(file)
    const {
      customers_created = 0,
      customers_updated = 0,
      contacts_created = 0,
      contacts_updated = 0,
      skipped = 0,
      warnings = []
    } = response.data ?? {}

    ElMessage.success(
      `导入完成：客户新增 ${customers_created}，客户更新 ${customers_updated}，联系人新增 ${contacts_created}，联系人更新 ${contacts_updated}，跳过 ${skipped}`
    )
    if (warnings.length) {
      console.warn('客户导入警告', warnings)
    }
    fetchCustomers()
  } catch (error) {
    const message = error?.response?.data?.error || '客户导入失败'
    ElMessage.error(message)
    console.error(error)
  } finally {
    customerImporting.value = false
    event.target.value = ''
  }
}

const handleRevenueImportClick = () => {
  revenueFileInput.value?.click()
}

const handleRevenueFileChange = async (event) => {
  const file = event.target.files?.[0]
  if (!file) {
    return
  }

  revenueImporting.value = true
  try {
    const response = await importCustomerRevenues(file)
    const { imported = 0, updated = 0, skipped = 0 } = response.data ?? {}
    ElMessage.success(`导入完成：新增 ${imported}，更新 ${updated}，跳过 ${skipped}`)
    fetchCustomers()
  } catch (error) {
    const message = error?.response?.data?.error || '营收导入失败'
    ElMessage.error(message)
    console.error(error)
  } finally {
    revenueImporting.value = false
    event.target.value = ''
  }
}

const downloadBlob = (blob, filename) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

const handleExport = async () => {
  exporting.value = true
  try {
    const response = await exportWorkbook()
    downloadBlob(response.data, 'fishpool-export.xlsx')
    ElMessage.success('导出完成')
  } catch (error) {
    ElMessage.error('导出失败')
    console.error(error)
  } finally {
    exporting.value = false
  }
}

const handleCardClick = (id) => {
  router.push(`/customers/${id}`)
}

onMounted(() => {
  fetchCustomers()
})
</script>

<style scoped>
.customer-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.toolbar-card {
  border: 1px solid rgba(64, 158, 255, 0.16);
  border-radius: 20px;
}

.toolbar-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 18px;
}

.hidden-file-input {
  display: none;
}

.content-area {
  min-height: 320px;
}

.customer-card {
  margin-bottom: 20px;
  border-radius: 18px;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.customer-card:hover {
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid #ebeef5;
}

.card-header h3 {
  margin: 0 0 6px;
  font-size: 18px;
  color: #111827;
}

.card-header p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}

.card-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  color: #4b5563;
}

.card-section strong {
  color: #111827;
}

.score-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.revenue-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.revenue-grid div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.revenue-grid span {
  font-size: 12px;
  color: #6b7280;
}

.revenue-grid strong {
  font-size: 15px;
  color: #111827;
}

.pagination {
  justify-content: center;
  margin-top: 4px;
}

.full-width {
  width: 100%;
}
</style>
