<template>
  <div class="customer-list">
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchParams.search"
            placeholder="搜索客户名称或别名"
            clearable
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="searchParams.level"
            placeholder="客户等级"
            clearable
            @change="handleSearch"
          >
            <el-option label="Level A" value="A" />
            <el-option label="Level B" value="B" />
            <el-option label="Level C" value="C" />
            <el-option label="Level D" value="D" />
            <el-option label="Level X" value="X" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-input
            v-model="searchParams.region"
            placeholder="区域"
            clearable
            @clear="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-input
            v-model="searchParams.city"
            placeholder="城市"
            clearable
            @clear="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="searchParams.business_model"
            placeholder="业务模式"
            clearable
            @change="handleSearch"
          >
            <el-option label="Hunting" value="Hunting" />
            <el-option label="Farming" value="Farming" />
          </el-select>
        </el-col>
        <el-col :span="2">
          <el-button type="primary" @click="handleSearch">搜索</el-button>
        </el-col>
      </el-row>
      <el-row style="margin-top: 20px">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增客户
        </el-button>
      </el-row>
    </el-card>

    <div v-loading="loading" class="customer-cards">
      <el-row :gutter="20">
        <el-col
          v-for="customer in customers"
          :key="customer.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <el-card
            class="customer-card"
            shadow="hover"
            @click="handleCardClick(customer.id)"
          >
            <div class="card-header">
              <h3>{{ customer.name }}</h3>
              <p v-if="customer.alias"><strong>别名：</strong>{{ customer.alias }}</p>
              <el-tag :type="getLevelType(customer.level)" size="large">
                {{ customer.level }}
              </el-tag>
            </div>
            <div class="card-content">
              <p><strong>区域：</strong>{{ customer.region }}</p>
              <p><strong>城市：</strong>{{ customer.city }}</p>
              <p><strong>业务模式：</strong>{{ customer.business_model }}</p>
              <div class="scores">
                <el-tag>X: {{ customer.score_x }}</el-tag>
                <el-tag>Y: {{ customer.score_y }}</el-tag>
                <el-tag>Z: {{ customer.score_z }}</el-tag>
              </div>
              <p class="potential">
                <strong>潜在贡献：</strong>{{ customer.potential_contribution || '暂无' }}
              </p>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-if="!loading && customers.length === 0" description="暂无客户数据" />
    </div>

    <el-pagination
      v-if="total > 0"
      v-model:current-page="searchParams.page"
      v-model:page-size="searchParams.page_size"
      :total="total"
      :page-sizes="[12, 24, 48, 96]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSearch"
      @current-change="handleSearch"
      class="pagination"
    />

    <CustomerForm
      v-model:visible="formVisible"
      :customer="currentCustomer"
      @success="handleSearch"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCustomers } from '../api/customer'
import CustomerForm from '../components/CustomerForm.vue'

const router = useRouter()

const loading = ref(false)
const customers = ref([])
const total = ref(0)
const formVisible = ref(false)
const currentCustomer = ref(null)

const searchParams = ref({
  search: '',
  level: '',
  region: '',
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
    D: 'info',
    X: 'warning'
  }
  return types[level] || 'info'
}

const fetchCustomers = async () => {
  loading.value = true
  try {
    const response = await getCustomers(searchParams.value)
    customers.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    console.error('获取客户列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  searchParams.value.page = 1
  fetchCustomers()
}

const handleAdd = () => {
  currentCustomer.value = null
  formVisible.value = true
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
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.customer-cards {
  min-height: 400px;
  margin-bottom: 20px;
}

.customer-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.2s;
}

.customer-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
}

.card-content p {
  margin: 8px 0;
  color: #606266;
}

.scores {
  margin: 10px 0;
  display: flex;
  gap: 8px;
}

.potential {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
