<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑客户' : '新增客户'"
    width="700px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="120px"
    >
      <el-form-item label="客户名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入客户名称" />
      </el-form-item>

      <el-form-item label="别名">
        <el-input v-model="formData.alias" placeholder="请输入别名" />
      </el-form-item>

      <el-form-item label="业务模式" prop="business_model">
        <el-select v-model="formData.business_model" placeholder="请选择业务模式" style="width: 100%">
          <el-option label="Hunting" value="Hunting" />
          <el-option label="Farming" value="Farming" />
        </el-select>
      </el-form-item>

      <el-form-item label="区域" prop="region">
        <el-input v-model="formData.region" placeholder="请输入区域" />
      </el-form-item>

      <el-form-item label="城市" prop="city">
        <el-input v-model="formData.city" placeholder="请输入城市" />
      </el-form-item>

      <el-form-item label="地址">
        <el-input v-model="formData.address" placeholder="请输入详细地址" />
      </el-form-item>

      <el-divider content-position="left">三维评分</el-divider>

      <el-form-item label="X轴描述">
        <el-input v-model="formData.score_x_desc" placeholder="请输入X轴评分描述" />
      </el-form-item>

      <el-form-item label="X轴评分" prop="score_x">
        <el-slider v-model="formData.score_x" :min="0" :max="100" show-input />
      </el-form-item>

      <el-form-item label="Y轴描述">
        <el-input v-model="formData.score_y_desc" placeholder="请输入Y轴评分描述" />
      </el-form-item>

      <el-form-item label="Y轴评分" prop="score_y">
        <el-slider v-model="formData.score_y" :min="0" :max="100" show-input />
      </el-form-item>

      <el-form-item label="Z轴描述">
        <el-input v-model="formData.score_z_desc" placeholder="请输入Z轴评分描述" />
      </el-form-item>

      <el-form-item label="Z轴评分" prop="score_z">
        <el-slider v-model="formData.score_z" :min="0" :max="100" show-input />
      </el-form-item>

      <el-form-item label="客户等级">
        <el-tag :type="levelType" size="large">{{ currentLevel }}</el-tag>
      </el-form-item>

      <el-divider content-position="left">其他信息</el-divider>

      <el-form-item label="客户策略">
        <el-input
          v-model="formData.strategy"
          type="textarea"
          :rows="3"
          placeholder="请输入客户策略"
        />
      </el-form-item>

      <el-form-item label="潜在贡献">
        <el-input v-model="formData.potential_contribution" placeholder="请输入潜在贡献" />
      </el-form-item>

      <el-form-item label="备注">
        <el-input
          v-model="formData.notes"
          type="textarea"
          :rows="3"
          placeholder="请输入备注"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createCustomer, updateCustomer } from '../api/customer'
import { calculateLevel } from '../utils/level'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  customer: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'success'])

const formRef = ref(null)
const loading = ref(false)

const isEdit = computed(() => !!props.customer)

const formData = ref({
  name: '',
  alias: '',
  business_model: '',
  region: '',
  city: '',
  address: '',
  score_x: 0,
  score_y: 0,
  score_z: 0,
  score_x_desc: '',
  score_y_desc: '',
  score_z_desc: '',
  strategy: '',
  potential_contribution: '',
  notes: ''
})

const rules = {
  name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
  business_model: [{ required: true, message: '请选择业务模式', trigger: 'change' }],
  region: [{ required: true, message: '请输入区域', trigger: 'blur' }],
  city: [{ required: true, message: '请输入城市', trigger: 'blur' }],
  score_x: [{ required: true, message: '请输入X轴评分', trigger: 'blur' }],
  score_y: [{ required: true, message: '请输入Y轴评分', trigger: 'blur' }],
  score_z: [{ required: true, message: '请输入Z轴评分', trigger: 'blur' }]
}

// 计算当前等级
const currentLevel = computed(() => {
  return calculateLevel(formData.value.score_x, formData.value.score_y, formData.value.score_z)
})

// 等级对应的标签类型
const levelType = computed(() => {
  const types = {
    A: 'danger',
    B: 'primary',
    C: 'success',
    D: 'info'
  }
  return types[currentLevel.value]
})

// 监听customer变化，更新表单数据
watch(() => props.customer, (newVal) => {
  if (newVal) {
    formData.value = { ...newVal }
  } else {
    resetForm()
  }
}, { immediate: true })

const handleClose = () => {
  emit('update:visible', false)
  resetForm()
}

const resetForm = () => {
  formData.value = {
    name: '',
    alias: '',
    business_model: '',
    region: '',
    city: '',
    address: '',
    score_x: 0,
    score_y: 0,
    score_z: 0,
    score_x_desc: '',
    score_y_desc: '',
    score_z_desc: '',
    strategy: '',
    potential_contribution: '',
    notes: ''
  }
  formRef.value?.clearValidate()
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true

    const data = {
      ...formData.value,
      level: currentLevel.value
    }

    if (isEdit.value) {
      await updateCustomer(props.customer.id, data)
      ElMessage.success('更新客户成功')
    } else {
      await createCustomer(data)
      ElMessage.success('创建客户成功')
    }

    emit('success')
    handleClose()
  } catch (error) {
    if (error.response) {
      ElMessage.error('操作失败：' + (error.response.data.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}
</script>
