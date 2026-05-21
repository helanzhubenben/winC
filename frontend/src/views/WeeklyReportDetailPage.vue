<template>
  <div v-loading="loading" class="weekly-report-detail">
    <el-page-header class="page-header" title="返回列表" @back="handleBack">
      <template #content>
        <span class="page-title">{{ isNew ? '新建报告' : '报告详情' }}</span>
      </template>
      <template #extra>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-page-header>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="16">
        <el-card shadow="never">
          <template #header>
            <span>基本信息</span>
          </template>

          <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
            <el-form-item label="客户名称" prop="client_name">
              <el-autocomplete
                v-model="form.client_name"
                :fetch-suggestions="searchCustomerSuggestions"
                clearable
                placeholder="输入客户名称搜索客户池"
                style="width: 100%"
                @select="handleCustomerSelect"
                @input="handleClientNameInput"
              >
                <template #default="{ item }">
                  <div class="customer-option">
                    <span>{{ item.value }}</span>
                    <small>{{ item.region || '未填写区域' }} / {{ item.city || '未填写城市' }}</small>
                  </div>
                </template>
              </el-autocomplete>
            </el-form-item>

            <el-form-item label="区域" prop="area">
              <el-input v-model="form.area" placeholder="请输入区域" />
            </el-form-item>

            <el-form-item label="地址">
              <el-input v-model="form.address" placeholder="请输入地址" />
            </el-form-item>

            <el-form-item label="任务" prop="tasks">
              <el-input
                v-model="form.tasks"
                type="textarea"
                :rows="3"
                placeholder="请输入任务描述"
              />
            </el-form-item>

            <el-form-item label="项目定义" prop="definition">
              <el-input
                v-model="form.definition"
                type="textarea"
                :rows="3"
                placeholder="请输入项目定义"
              />
            </el-form-item>

            <el-form-item label="项目状态" prop="status">
              <el-radio-group v-model="form.status">
                <el-radio label="in_progress">进行中</el-radio>
                <el-radio label="completed">已完成</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="到期日期" prop="due_date">
              <el-date-picker
                v-model="form.due_date"
                type="date"
                placeholder="选择到期日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="修订日期">
              <el-date-picker
                v-model="form.revise_date"
                type="date"
                placeholder="选择修订日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="完成日期">
              <el-date-picker
                v-model="form.finish_date"
                type="date"
                placeholder="选择完成日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="收入">
              <el-input v-model="form.revenue" placeholder="请输入收入" />
            </el-form-item>

            <el-form-item label="责任人" prop="responsibility">
              <el-input v-model="form.responsibility" placeholder="请输入责任人" />
            </el-form-item>

            <el-form-item label="备注">
              <el-input
                v-model="form.remark"
                type="textarea"
                :rows="3"
                placeholder="请输入备注"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>行动记录</span>
              <el-button type="primary" size="small" @click="handleAddAction">
                <el-icon><Plus /></el-icon>
                添加记录
              </el-button>
            </div>
          </template>

          <el-timeline v-if="form.actions && form.actions.length > 0">
            <el-timeline-item
              v-for="(action, index) in form.actions"
              :key="index"
              :timestamp="formatDateTime(action.timestamp)"
              placement="top"
            >
              <el-card shadow="hover" class="action-card">
                <div class="action-content">
                  <p><strong>行动内容：</strong>{{ action.action || action.content }}</p>
                  <p v-if="action.result"><strong>结果：</strong>{{ action.result }}</p>
                  <p v-if="action.next_step"><strong>下一步：</strong>{{ action.next_step }}</p>
                  <div class="action-meta">
                    <el-tag v-if="action.action_date" size="small">{{ action.action_date }}</el-tag>
                    <el-tag v-if="action.user" size="small" type="info">{{ action.user }}</el-tag>
                  </div>
                </div>
                <div class="action-actions">
                  <el-button link type="primary" size="small" @click="handleEditAction(index)">
                    编辑
                  </el-button>
                  <el-button link type="danger" size="small" @click="handleDeleteAction(index)">
                    删除
                  </el-button>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无行动记录" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 行动记录对话框 -->
    <el-dialog
      v-model="actionDialogVisible"
      :title="actionDialogTitle"
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getWeeklyReport,
  createWeeklyReport,
  updateWeeklyReport,
  addAction,
  updateAction,
  deleteAction
} from '../api/weeklyReport'
import { getCustomers } from '../api/customer'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const formRef = ref(null)

const isNew = computed(() => route.params.id === 'new')

const form = reactive({
  customer: null,
  client_name: '',
  area: '',
  address: '',
  tasks: '',
  definition: '',
  status: 'in_progress',
  due_date: '',
  revise_date: '',
  finish_date: '',
  revenue: '',
  responsibility: '',
  remark: '',
  actions: []
})

const rules = {
  client_name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
  tasks: [{ required: true, message: '请输入任务描述', trigger: 'blur' }],
  definition: [{ required: true, message: '请输入项目定义', trigger: 'blur' }],
  due_date: [{ required: true, message: '请选择到期日期', trigger: 'change' }],
  responsibility: [{ required: true, message: '请输入责任人', trigger: 'blur' }]
}

const actionDialogVisible = ref(false)
const actionDialogTitle = ref('添加行动记录')
const actionEditIndex = ref(-1)
const actionFormRef = ref(null)
const actionForm = reactive({
  action_date: '',
  action: '',
  result: '',
  next_step: ''
})
const selectedCustomerName = ref('')

const actionRules = {
  action_date: [{ required: true, message: '请选择行动日期', trigger: 'change' }],
  action: [{ required: true, message: '请输入行动内容', trigger: 'blur' }]
}

const loadReport = async () => {
  if (isNew.value) return

  loading.value = true
  try {
    const response = await getWeeklyReport(route.params.id)
    Object.assign(form, response.data)
    selectedCustomerName.value = form.customer ? form.client_name : ''
  } catch (error) {
    ElMessage.error('加载报告失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleBack = () => {
  router.push('/weekly-reports')
}

const handleCancel = () => {
  router.push('/weekly-reports')
}

const handleSave = async () => {
  try {
    await formRef.value.validate()

    loading.value = true
    if (isNew.value) {
      await createWeeklyReport(form)
      ElMessage.success('创建成功')
    } else {
      await updateWeeklyReport(route.params.id, form)
      ElMessage.success('保存成功')
    }
    router.push('/weekly-reports')
  } catch (error) {
    if (error !== false) {
      ElMessage.error('保存失败')
      console.error(error)
    }
  } finally {
    loading.value = false
  }
}

const searchCustomerSuggestions = async (queryString, callback) => {
  const search = String(queryString || '').trim()
  if (!search) {
    callback([])
    return
  }

  try {
    const response = await getCustomers({
      search,
      page: 1,
      page_size: 20
    })
    const results = response.data?.results ?? response.data ?? []
    callback(results.map(customer => ({
      value: customer.name,
      id: customer.id,
      region: customer.region,
      city: customer.city,
      address: customer.address
    })))
  } catch (error) {
    callback([])
    console.error(error)
  }
}

const handleCustomerSelect = (item) => {
  selectedCustomerName.value = item.value
  form.customer = item.id
  form.client_name = item.value
  form.area = item.region || ''
  form.address = item.address || ''
}

const handleClientNameInput = (value) => {
  if (value !== selectedCustomerName.value) {
    selectedCustomerName.value = ''
    form.customer = null
  }
}

const handleAddAction = () => {
  actionDialogTitle.value = '添加行动记录'
  actionEditIndex.value = -1
  actionForm.action_date = new Date().toISOString().split('T')[0]
  actionForm.action = ''
  actionForm.result = ''
  actionForm.next_step = ''
  actionDialogVisible.value = true
}

const handleEditAction = (index) => {
  actionDialogTitle.value = '编辑行动记录'
  actionEditIndex.value = index
  const action = form.actions[index]
  actionForm.action_date = action.action_date || ''
  actionForm.action = action.action || action.content || ''
  actionForm.result = action.result || ''
  actionForm.next_step = action.next_step || ''
  actionDialogVisible.value = true
}

const handleSaveAction = async () => {
  try {
    await actionFormRef.value.validate()

    if (isNew.value) {
      // 新建报告时，直接添加到本地数组
      if (actionEditIndex.value >= 0) {
        form.actions[actionEditIndex.value] = {
          ...form.actions[actionEditIndex.value],
          action_date: actionForm.action_date,
          action: actionForm.action,
          result: actionForm.result,
          next_step: actionForm.next_step
        }
      } else {
        form.actions.push({
          action_date: actionForm.action_date,
          action: actionForm.action,
          result: actionForm.result,
          next_step: actionForm.next_step,
          timestamp: new Date().toISOString()
        })
      }
      ElMessage.success('操作成功')
    } else {
      // 编辑已有报告时，调用 API
      if (actionEditIndex.value >= 0) {
        await updateAction(route.params.id, actionEditIndex.value, {
          action_date: actionForm.action_date,
          action: actionForm.action,
          result: actionForm.result,
          next_step: actionForm.next_step
        })
        ElMessage.success('更新成功')
      } else {
        await addAction(route.params.id, {
          action_date: actionForm.action_date,
          action: actionForm.action,
          result: actionForm.result,
          next_step: actionForm.next_step
        })
        ElMessage.success('添加成功')
      }
      await loadReport()
    }
    actionDialogVisible.value = false
  } catch (error) {
    if (error !== false) {
      ElMessage.error('操作失败')
      console.error(error)
    }
  }
}

const handleDeleteAction = async (index) => {
  try {
    await ElMessageBox.confirm('确定要删除这条行动记录吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    if (isNew.value) {
      form.actions.splice(index, 1)
      ElMessage.success('删除成功')
    } else {
      await deleteAction(route.params.id, index)
      ElMessage.success('删除成功')
      await loadReport()
    }
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
  loadReport()
})
</script>

<style scoped>
.weekly-report-detail {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.customer-option {
  display: flex;
  flex-direction: column;
  gap: 2px;
  line-height: 1.35;
}

.customer-option span {
  color: #111827;
}

.customer-option small {
  color: #6b7280;
}

.action-card {
  margin-bottom: 12px;
}

.action-content {
  margin-bottom: 8px;
}

.action-content p {
  margin: 0 0 8px 0;
  line-height: 1.6;
}

.action-meta {
  display: flex;
  gap: 8px;
}

.action-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>
