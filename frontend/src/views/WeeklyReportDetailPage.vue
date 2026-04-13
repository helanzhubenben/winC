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
              <el-input v-model="form.client_name" placeholder="请输入客户名称" />
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
                  <p>{{ action.content }}</p>
                  <div class="action-meta">
                    <el-tag size="small">{{ action.user }}</el-tag>
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
      width="500px"
    >
      <el-form :model="actionForm" label-width="80px">
        <el-form-item label="内容" required>
          <el-input
            v-model="actionForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入行动记录内容"
          />
        </el-form-item>
        <el-form-item label="记录人" required>
          <el-input v-model="actionForm.user" placeholder="请输入记录人" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="actionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveAction">确定</el-button>
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

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const formRef = ref(null)

const isNew = computed(() => route.params.id === 'new')

const form = reactive({
  client_name: '',
  area: '',
  address: '',
  tasks: '',
  definition: '',
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
const actionForm = reactive({
  content: '',
  user: ''
})

const loadReport = async () => {
  if (isNew.value) return

  loading.value = true
  try {
    const response = await getWeeklyReport(route.params.id)
    Object.assign(form, response.data)
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

const handleAddAction = () => {
  actionDialogTitle.value = '添加行动记录'
  actionEditIndex.value = -1
  actionForm.content = ''
  actionForm.user = ''
  actionDialogVisible.value = true
}

const handleEditAction = (index) => {
  actionDialogTitle.value = '编辑行动记录'
  actionEditIndex.value = index
  actionForm.content = form.actions[index].content
  actionForm.user = form.actions[index].user
  actionDialogVisible.value = true
}

const handleSaveAction = async () => {
  if (!actionForm.content.trim()) {
    ElMessage.warning('请输入行动记录内容')
    return
  }
  if (!actionForm.user.trim()) {
    ElMessage.warning('请输入记录人')
    return
  }

  try {
    if (isNew.value) {
      // 新建报告时，直接添加到本地数组
      if (actionEditIndex.value >= 0) {
        form.actions[actionEditIndex.value].content = actionForm.content
        form.actions[actionEditIndex.value].user = actionForm.user
      } else {
        form.actions.push({
          content: actionForm.content,
          user: actionForm.user,
          timestamp: new Date().toISOString()
        })
      }
      ElMessage.success('操作成功')
    } else {
      // 编辑已有报告时，调用 API
      if (actionEditIndex.value >= 0) {
        await updateAction(route.params.id, actionEditIndex.value, {
          content: actionForm.content,
          user: actionForm.user
        })
        ElMessage.success('更新成功')
      } else {
        await addAction(route.params.id, {
          content: actionForm.content,
          user: actionForm.user
        })
        ElMessage.success('添加成功')
      }
      await loadReport()
    }
    actionDialogVisible.value = false
  } catch (error) {
    ElMessage.error('操作失败')
    console.error(error)
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
