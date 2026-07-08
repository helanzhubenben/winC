<template>
  <div class="customer-list">
    <el-card class="toolbar-card" shadow="never">
      <el-row :gutter="16">
        <el-col :xs="24" :md="10">
          <el-input
            v-model="searchParams.search"
            placeholder="搜索客户名称或别名"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :xs="24" :md="14">
          <div class="filter-actions">
            <el-button @click="handleAddFilter">
              <el-icon><Plus /></el-icon>
              添加筛选条件
            </el-button>
            <el-button @click="handleResetFilters">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
            <el-button @click="handleClearFilterAndSort">
              <el-icon><Refresh /></el-icon>
              清除筛选排序
            </el-button>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </div>
        </el-col>
      </el-row>

      <div v-if="filterConditions.length" class="filter-builder">
        <div
          v-for="condition in filterConditions"
          :key="condition.id"
          class="condition-row"
        >
          <el-select
            v-model="condition.field"
            class="condition-field"
            placeholder="字段"
            @change="handleFilterFieldChange(condition)"
          >
            <el-option
              v-for="field in filterFields"
              :key="field.value"
              :label="field.label"
              :value="field.value"
            />
          </el-select>
          <el-select
            v-model="condition.operator"
            class="condition-operator"
            placeholder="条件"
            @change="handleFilterOperatorChange(condition)"
          >
            <el-option
              v-for="operator in getOperators(condition)"
              :key="operator.value"
              :label="operator.label"
              :value="operator.value"
            />
          </el-select>
          <template v-if="condition.operator === 'between'">
            <el-date-picker
              v-if="getFieldType(condition.field) === 'date'"
              v-model="condition.value[0]"
              class="condition-value"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="开始日期"
            />
            <el-input
              v-else
              v-model="condition.value[0]"
              class="condition-value"
              placeholder="最小值"
              @keyup.enter="handleSearch"
            />
            <el-date-picker
              v-if="getFieldType(condition.field) === 'date'"
              v-model="condition.value[1]"
              class="condition-value"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="结束日期"
            />
            <el-input
              v-else
              v-model="condition.value[1]"
              class="condition-value"
              placeholder="最大值"
              @keyup.enter="handleSearch"
            />
          </template>
          <el-select
            v-else-if="getFieldType(condition.field) === 'choice'"
            v-model="condition.value"
            class="condition-value-wide"
            placeholder="请选择"
            clearable
          >
            <el-option
              v-for="option in getChoiceOptions(condition.field)"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
          <el-date-picker
            v-else-if="getFieldType(condition.field) === 'date'"
            v-model="condition.value"
            class="condition-value-wide"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
          />
          <el-input
            v-else
            v-model="condition.value"
            class="condition-value-wide"
            placeholder="请输入筛选值"
            clearable
            @keyup.enter="handleSearch"
          />
          <el-button
            circle
            type="danger"
            @click="handleRemoveFilter(condition.id)"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>

      <div class="sort-builder">
        <span class="sort-label">排序</span>
        <el-select
          v-model="sortState.field"
          class="sort-field"
          placeholder="选择排序字段"
          clearable
          @change="handleSearch"
          @clear="handleSearch"
        >
          <el-option
            v-for="field in sortableFields"
            :key="field.value"
            :label="field.label"
            :value="field.value"
          />
        </el-select>
        <el-select
          v-model="sortState.direction"
          class="sort-direction"
          :disabled="!sortState.field"
          @change="handleSearch"
        >
          <el-option label="升序" value="asc" />
          <el-option label="降序" value="desc" />
        </el-select>
      </div>

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
                <p v-if="customer.alias">别名：{{ customer.alias }}</p>
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

            <div class="card-section">
              <span>上次联系</span>
              <el-tag
                :class="{ 'contact-tag-purple': getContactTagType(customer.last_contacted_at) === 'purple' }"
                :type="getContactTagType(customer.last_contacted_at) === 'purple' ? undefined : getContactTagType(customer.last_contacted_at)"
                size="small"
              >
                {{ formatLastContact(customer.last_contacted_at) }}
              </el-tag>
            </div>

            <div class="revenue-grid">
              <div>
                <span>去年营收</span>
                <strong>{{ formatCurrency(customer.last_year_revenue) }}</strong>
              </div>
              <div>
                <span>上季度营收</span>
                <small v-if="customer.last_quarter_revenue_label">{{ customer.last_quarter_revenue_label }}</small>
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
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete, Download, Plus, Refresh, Search, Upload } from '@element-plus/icons-vue'
import { downloadCustomerImportTemplate, getCustomers, importCustomers } from '../api/customer'
import { importCustomerRevenues } from '../api/customerRevenue'
import { exportWorkbook } from '../api/export'
import {
  clearCustomerListFilterAndSort,
  getCustomerListStorage,
  loadCustomerListState,
  saveCustomerListState
} from '../utils/customerListState'
import CustomerDialog from '../components/CustomerDialog.vue'

const router = useRouter()
const customerListStorage = getCustomerListStorage()
const savedCustomerListState = loadCustomerListState(customerListStorage)
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
const filterConditions = ref(savedCustomerListState.filterConditions)
const sortState = ref(savedCustomerListState.sortState)

const filterFields = [
  { label: '客户名称', value: 'client_name', type: 'text' },
  { label: '别名', value: 'alias', type: 'text' },
  { label: '业务模式', value: 'business_model', type: 'choice' },
  { label: '区域', value: 'area', type: 'text' },
  { label: '城市', value: 'city', type: 'text' },
  { label: '客户等级', value: 'level', type: 'choice' },
  { label: 'X 轴评分', value: 'score_x', type: 'number' },
  { label: 'Y 轴评分', value: 'score_y', type: 'number' },
  { label: 'Z 轴评分', value: 'score_z', type: 'number' },
  { label: '潜在贡献', value: 'potential_contribution', type: 'number' },
  { label: '去年营收', value: 'last_year_revenue', type: 'number' },
  { label: '上季度营收', value: 'last_quarter_revenue', type: 'number' },
  { label: '状态', value: 'status', type: 'choice' },
  { label: '地址', value: 'address', type: 'text' },
  { label: '备注', value: 'remark', type: 'text' },
  { label: '创建时间', value: 'created_at', type: 'date' },
  { label: '更新时间', value: 'updated_at', type: 'date' }
]

const sortableFields = filterFields.filter((field) => !['address', 'remark'].includes(field.value))

const operatorOptions = {
  text: [
    { label: '包含', value: 'contains' },
    { label: '等于', value: 'eq' }
  ],
  choice: [
    { label: '等于', value: 'eq' }
  ],
  number: [
    { label: '大于等于', value: 'gte' },
    { label: '小于等于', value: 'lte' },
    { label: '等于', value: 'eq' },
    { label: '区间', value: 'between' }
  ],
  date: [
    { label: '晚于等于', value: 'gte' },
    { label: '早于等于', value: 'lte' },
    { label: '等于', value: 'eq' },
    { label: '区间', value: 'between' }
  ]
}

const choiceOptions = {
  business_model: [
    { label: 'Hunting', value: 'Hunting' },
    { label: 'Farming', value: 'Farming' }
  ],
  level: [
    { label: 'Level A', value: 'A' },
    { label: 'Level B', value: 'B' },
    { label: 'Level C', value: 'C' },
    { label: 'Level D', value: 'D' },
    { label: 'Level X', value: 'X' }
  ],
  status: [
    { label: 'Active', value: 'active' },
    { label: 'Inactive', value: 'inactive' }
  ]
}

const searchParams = ref(savedCustomerListState.searchParams)

const getCurrentCustomerListState = () => ({
  searchParams: searchParams.value,
  filterConditions: filterConditions.value,
  sortState: sortState.value
})

const applyCustomerListState = (state) => {
  searchParams.value = { ...state.searchParams }
  filterConditions.value = state.filterConditions.map((condition) => ({
    ...condition,
    value: Array.isArray(condition.value) ? [...condition.value] : condition.value
  }))
  sortState.value = { ...state.sortState }
}

const persistCustomerListState = () => {
  saveCustomerListState(customerListStorage, getCurrentCustomerListState())
}

const getLevelType = (level) => {
  const types = {
    A: 'danger',
    B: 'primary',
    C: 'success',
    D: 'info',
    X: 'warning'
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

const getContactDaysAgo = (value) => {
  if (!value) {
    return Number.POSITIVE_INFINITY
  }
  const contactedDate = new Date(value)
  const today = new Date()
  contactedDate.setHours(0, 0, 0, 0)
  today.setHours(0, 0, 0, 0)
  return Math.floor((today - contactedDate) / 86400000)
}

const getContactTagType = (value) => {
  const days = getContactDaysAgo(value)
  if (!Number.isFinite(days) || days > 183) {
    return 'info'
  }
  if (days > 90) {
    return 'danger'
  }
  if (days > 30) {
    return 'warning'
  }
  if (days > 14) {
    return 'success'
  }
  return 'purple'
}

const formatLastContact = (value) => {
  if (!value) {
    return '从未联系'
  }
  const days = getContactDaysAgo(value)
  const dateText = new Date(value).toLocaleDateString('zh-CN')
  if (days <= 0) {
    return `${dateText}（今天）`
  }
  return `${dateText}（${days} 天前）`
}

const getFieldConfig = (field) => {
  return filterFields.find((item) => item.value === field) ?? filterFields[0]
}

const getFieldType = (field) => {
  return getFieldConfig(field).type
}

const getOperators = (condition) => {
  return operatorOptions[getFieldType(condition.field)] ?? operatorOptions.text
}

const getChoiceOptions = (field) => {
  return choiceOptions[field] ?? []
}

const emptyFilterCondition = () => ({
  id: `${Date.now()}-${Math.random()}`,
  field: 'client_name',
  operator: 'contains',
  value: ''
})

const resetConditionValue = (condition) => {
  condition.value = condition.operator === 'between' ? ['', ''] : ''
}

const handleAddFilter = () => {
  filterConditions.value.push(emptyFilterCondition())
}

const handleRemoveFilter = (id) => {
  filterConditions.value = filterConditions.value.filter((condition) => condition.id !== id)
  handleSearch()
}

const handleFilterFieldChange = (condition) => {
  const operators = getOperators(condition)
  condition.operator = operators[0]?.value ?? 'contains'
  resetConditionValue(condition)
}

const handleFilterOperatorChange = (condition) => {
  resetConditionValue(condition)
}

const hasFilterValue = (condition) => {
  if (condition.operator === 'between' && Array.isArray(condition.value)) {
    return condition.value.some((value) => String(value ?? '').trim() !== '')
  }
  return String(condition.value ?? '').trim() !== ''
}

const buildCustomFilters = () => {
  return filterConditions.value
    .filter((condition) => condition.field && condition.operator && hasFilterValue(condition))
    .map((condition) => ({
      field: condition.field,
      operator: condition.operator,
      value: condition.value
    }))
}

const fetchCustomers = async () => {
  persistCustomerListState()
  loading.value = true
  try {
    const params = { ...searchParams.value }
    const filters = buildCustomFilters()
    if (filters.length) {
      params.filters = JSON.stringify(filters)
    }
    if (sortState.value.field) {
      params.ordering = `${sortState.value.direction === 'desc' ? '-' : ''}${sortState.value.field}`
    }
    const response = await getCustomers(params)
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

const handleResetFilters = () => {
  searchParams.value.search = ''
  searchParams.value.page = 1
  filterConditions.value = []
  sortState.value = {
    field: '',
    direction: 'desc'
  }
  fetchCustomers()
}

const handleClearFilterAndSort = () => {
  applyCustomerListState(clearCustomerListFilterAndSort(getCurrentCustomerListState()))
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

watch(
  () => [searchParams.value, filterConditions.value, sortState.value],
  () => {
    persistCustomerListState()
  },
  { deep: true }
)
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

.filter-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-builder {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 14px;
}

.sort-builder {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
}

.sort-label {
  color: #4b5563;
  font-size: 14px;
}

.sort-field {
  width: 220px;
}

.sort-direction {
  width: 110px;
}

.condition-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
}

.condition-field {
  width: 150px;
  flex: 0 0 150px;
}

.condition-operator {
  width: 120px;
  flex: 0 0 120px;
}

.condition-value {
  width: 160px;
  flex: 1 1 140px;
}

.condition-value-wide {
  min-width: 220px;
  flex: 1 1 220px;
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

.revenue-grid small {
  font-size: 11px;
  color: #909399;
  line-height: 1.2;
}

.revenue-grid strong {
  font-size: 15px;
  color: #111827;
}

.contact-tag-purple {
  color: #7e22ce;
  background-color: #f3e8ff;
  border-color: #d8b4fe;
}

.pagination {
  justify-content: center;
  margin-top: 4px;
}

@media (max-width: 768px) {
  .filter-actions {
    justify-content: flex-start;
    margin-top: 12px;
  }

  .condition-row {
    align-items: stretch;
    flex-direction: column;
  }

  .condition-field,
  .condition-operator,
  .condition-value,
  .condition-value-wide,
  .sort-field,
  .sort-direction {
    width: 100%;
    flex: 1 1 auto;
  }

  .sort-builder {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
