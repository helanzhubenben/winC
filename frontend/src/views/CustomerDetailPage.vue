<template>
  <div v-loading="loading" class="customer-detail">
    <el-page-header class="page-header" title="返回列表" @back="handleBack">
      <template #content>
        <span class="page-title">{{ customer.name || '客户详情' }}</span>
      </template>
      <template #extra>
        <el-button type="primary" @click="handleEdit">编辑</el-button>
        <el-button type="danger" @click="handleDelete">删除</el-button>
      </template>
    </el-page-header>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-tag :type="getLevelType(customer.level)" size="large">
                {{ customer.level || 'D' }}
              </el-tag>
            </div>
          </template>

          <el-descriptions :column="2" border>
            <el-descriptions-item label="客户名称">
              {{ customer.name || '暂无' }}
            </el-descriptions-item>
            <el-descriptions-item label="业务模式">
              {{ customer.business_model || '暂无' }}
            </el-descriptions-item>
            <el-descriptions-item label="区域">
              {{ customer.region || '暂无' }}
            </el-descriptions-item>
            <el-descriptions-item label="城市">
              {{ customer.city || '暂无' }}
            </el-descriptions-item>
            <el-descriptions-item :span="2" label="地址">
              {{ customer.address || '暂无' }}
            </el-descriptions-item>
            <el-descriptions-item :span="2" label="潜在贡献">
              {{ customer.potential_contribution || '暂无' }}
            </el-descriptions-item>
            <el-descriptions-item :span="2" label="创建时间">
              {{ formatDate(customer.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item :span="2" label="更新时间">
              {{ formatDate(customer.updated_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="stack-card" shadow="never">
          <template #header>
            <span>客户策略</span>
          </template>
          <p class="paragraph">{{ customer.strategy || '暂无客户策略' }}</p>
        </el-card>

        <el-card class="stack-card" shadow="never">
          <template #header>
            <span>备注</span>
          </template>
          <p class="paragraph">{{ customer.notes || '暂无备注' }}</p>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card shadow="never">
          <template #header>
            <span>三维评分</span>
          </template>
          <div ref="chartRef" class="chart"></div>
        </el-card>

        <el-card class="stack-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>联系人列表</span>
              <el-button type="primary" size="small" @click="handleAddContact">
                <el-icon><Plus /></el-icon>
                新增联系人
              </el-button>
            </div>
          </template>

          <el-table :data="contacts" stripe>
            <el-table-column prop="name" label="姓名" min-width="120" />
            <el-table-column prop="position" label="职位" min-width="120" />
            <el-table-column prop="phone" label="电话" min-width="140" />
            <el-table-column prop="email" label="邮箱" min-width="180" />
            <el-table-column label="关键人" width="92">
              <template #default="{ row }">
                <el-tag :type="row.is_key_person ? 'success' : 'info'">
                  {{ row.is_key_person ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleEditContact(row)">
                  编辑
                </el-button>
                <el-button type="danger" link @click="handleDeleteContact(row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!contacts.length" description="暂无联系人" />
        </el-card>
      </el-col>
    </el-row>

    <CustomerDialog
      v-model:visible="formVisible"
      :customer="customer"
      @success="fetchCustomer"
    />

    <ContactDialog
      v-model:visible="contactFormVisible"
      :contact="currentContact"
      :customer-id="Number(route.params.id)"
      @success="fetchContacts"
    />
  </div>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { deleteCustomer, getCustomer } from '../api/customer'
import { deleteContact, getContacts } from '../api/contactApi'
import CustomerDialog from '../components/CustomerDialog.vue'
import ContactDialog from '../components/ContactDialog.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const customer = ref({})
const contacts = ref([])
const chartRef = ref(null)
const chartInstance = ref(null)
const formVisible = ref(false)
const contactFormVisible = ref(false)
const currentContact = ref(null)

const getLevelType = (level) => {
  const types = {
    A: 'danger',
    B: 'primary',
    C: 'success',
    D: 'info'
  }
  return types[level] || 'info'
}

const formatDate = (value) => {
  if (!value) {
    return '暂无'
  }
  return new Date(value).toLocaleString('zh-CN')
}

const initChart = () => {
  if (!chartRef.value) {
    return
  }

  chartInstance.value?.dispose()
  chartInstance.value = echarts.init(chartRef.value)
  chartInstance.value.setOption({
    tooltip: {},
    radar: {
      radius: '62%',
      indicator: [
        { name: customer.value.score_x_desc || 'X 轴', max: 100 },
        { name: customer.value.score_y_desc || 'Y 轴', max: 100 },
        { name: customer.value.score_z_desc || 'Z 轴', max: 100 }
      ]
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: [
              customer.value.score_x || 0,
              customer.value.score_y || 0,
              customer.value.score_z || 0
            ],
            areaStyle: {
              color: 'rgba(64, 158, 255, 0.22)'
            },
            lineStyle: {
              color: '#409eff'
            },
            itemStyle: {
              color: '#409eff'
            },
            name: '评分'
          }
        ]
      }
    ]
  })
}

const fetchCustomer = async () => {
  loading.value = true
  try {
    const response = await getCustomer(route.params.id)
    customer.value = response.data ?? {}
    await nextTick()
    initChart()
  } catch (error) {
    ElMessage.error('获取客户详情失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchContacts = async () => {
  try {
    const response = await getContacts(route.params.id)
    const results = response.data?.results ?? response.data ?? []
    contacts.value = Array.isArray(results) ? results : []
  } catch (error) {
    contacts.value = []
    ElMessage.error('获取联系人失败')
    console.error(error)
  }
}

const handleBack = () => {
  router.push('/customers')
}

const handleEdit = () => {
  formVisible.value = true
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm('确定删除当前客户吗？', '提示', {
      type: 'warning'
    })
    await deleteCustomer(route.params.id)
    ElMessage.success('客户删除成功')
    router.push('/customers')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('客户删除失败')
    }
  }
}

const handleAddContact = () => {
  currentContact.value = null
  contactFormVisible.value = true
}

const handleEditContact = (contact) => {
  currentContact.value = { ...contact }
  contactFormVisible.value = true
}

const handleDeleteContact = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除当前联系人吗？', '提示', {
      type: 'warning'
    })
    await deleteContact(id)
    ElMessage.success('联系人删除成功')
    fetchContacts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('联系人删除失败')
    }
  }
}

watch(
  () => route.params.id,
  () => {
    fetchCustomer()
    fetchContacts()
  }
)

onMounted(() => {
  fetchCustomer()
  fetchContacts()
})

onUnmounted(() => {
  chartInstance.value?.dispose()
})
</script>

<style scoped>
.customer-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  padding: 18px 20px;
  background: #fff;
  border-radius: 18px;
  border: 1px solid #ebeef5;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.stack-card {
  margin-top: 20px;
}

.chart {
  width: 100%;
  height: 360px;
}

.paragraph {
  margin: 0;
  line-height: 1.7;
  color: #4b5563;
  white-space: pre-wrap;
}
</style>
