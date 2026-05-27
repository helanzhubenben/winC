<template>
  <div v-loading="loading" class="customer-detail">
    <el-page-header @back="handleBack" title="返回列表">
      <template #content>
        <span class="page-title">客户详情</span>
      </template>
      <template #extra>
        <el-button type="primary" @click="handleEdit">编辑</el-button>
        <el-button type="danger" @click="handleDelete">删除</el-button>
      </template>
    </el-page-header>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-tag :type="getLevelType(customer.level)" size="large">
                {{ customer.level }}
              </el-tag>
            </div>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="客户名称">
              {{ customer.name }}
            </el-descriptions-item>
            <el-descriptions-item label="别名">
              {{ customer.alias || '暂无' }}
            </el-descriptions-item>
            <el-descriptions-item label="业务模式">
              {{ customer.business_model }}
            </el-descriptions-item>
            <el-descriptions-item label="区域">
              {{ customer.region }}
            </el-descriptions-item>
            <el-descriptions-item label="城市">
              {{ customer.city }}
            </el-descriptions-item>
            <el-descriptions-item label="地址" :span="2">
              {{ customer.address || '暂无' }}
            </el-descriptions-item>
            <el-descriptions-item label="潜在贡献" :span="2">
              {{ customer.potential_contribution || '暂无' }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间" :span="2">
              {{ formatDate(customer.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间" :span="2">
              {{ formatDate(customer.updated_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>
            <span>客户策略</span>
          </template>
          <p>{{ customer.strategy || '暂无策略' }}</p>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>
            <span>备注</span>
          </template>
          <p>{{ customer.notes || '暂无备注' }}</p>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>三维评分</span>
          </template>
          <div ref="chartRef" style="width: 100%; height: 400px"></div>
        </el-card>

        <el-card style="margin-top: 20px">
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
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="position" label="职位" />
            <el-table-column prop="phone" label="电话" />
            <el-table-column prop="email" label="邮箱" />
            <el-table-column label="关键人">
              <template #default="{ row }">
                <el-tag v-if="row.is_key_person" type="success">是</el-tag>
                <el-tag v-else type="info">否</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  @click="handleEditContact(row)"
                >
                  编辑
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="handleDeleteContact(row.id)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <CustomerForm
      v-model:visible="formVisible"
      :customer="customer"
      @success="fetchCustomer"
    />

    <ContactForm
      v-model:visible="contactFormVisible"
      :contact="currentContact"
      :customer-id="Number(route.params.id)"
      @success="fetchContacts"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { getCustomer, deleteCustomer } from '../api/customer'
import { getContacts, deleteContact } from '../api/contact'
import CustomerForm from '../components/CustomerForm.vue'
import ContactForm from '../components/ContactForm.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const customer = ref({})
const contacts = ref([])
const chartRef = ref(null)
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

const formatDate = (dateString) => {
  if (!dateString) return '暂无'
  return new Date(dateString).toLocaleString('zh-CN')
}

const fetchCustomer = async () => {
  loading.value = true
  try {
    const response = await getCustomer(route.params.id)
    customer.value = response.data
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
    contacts.value = response.data
  } catch (error) {
    ElMessage.error('获取联系人列表失败')
    console.error(error)
  }
}

const initChart = () => {
  if (!chartRef.value) return

  const chart = echarts.init(chartRef.value)
  const option = {
    radar: {
      indicator: [
        { name: customer.value.score_x_desc || 'X轴', max: 100 },
        { name: customer.value.score_y_desc || 'Y轴', max: 100 },
        { name: customer.value.score_z_desc || 'Z轴', max: 100 }
      ]
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: [
              customer.value.score_x,
              customer.value.score_y,
              customer.value.score_z
            ],
            name: '三维评分'
          }
        ]
      }
    ]
  }
  chart.setOption(option)
}

const handleBack = () => {
  router.push('/customers')
}

const handleEdit = () => {
  formVisible.value = true
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm('确定要删除该客户吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteCustomer(route.params.id)
    ElMessage.success('删除成功')
    router.push('/customers')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleAddContact = () => {
  currentContact.value = null
  contactFormVisible.value = true
}

const handleEditContact = (contact) => {
  currentContact.value = contact
  contactFormVisible.value = true
}

const handleDeleteContact = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该联系人吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteContact(id)
    ElMessage.success('删除成功')
    fetchContacts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchCustomer()
  fetchContacts()
})
</script>

<style scoped>
.customer-detail {
  padding: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
