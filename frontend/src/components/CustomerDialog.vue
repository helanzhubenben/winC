<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑客户' : '新增客户'"
    width="720px"
    destroy-on-close
    @close="handleClose"
  >
    <el-form ref="formRef" :model="formData" :rules="rules" label-width="110px">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="客户名称" prop="name">
            <el-input v-model="formData.name" placeholder="请输入客户名称" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="别名">
            <el-input v-model="formData.alias" placeholder="请输入别名" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="业务模式" prop="business_model">
            <el-select
              v-model="formData.business_model"
              placeholder="请选择业务模式"
              style="width: 100%"
            >
              <el-option label="Hunting" value="Hunting" />
              <el-option label="Farming" value="Farming" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="区域" prop="region">
            <el-input v-model="formData.region" placeholder="请输入区域" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="城市" prop="city">
            <el-input v-model="formData.city" placeholder="请输入城市" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="地址">
        <el-input v-model="formData.address" placeholder="请输入详细地址" />
      </el-form-item>

      <el-divider content-position="left">三维评分</el-divider>

      <el-form-item label="X 轴描述">
        <el-input v-model="formData.score_x_desc" placeholder="请输入 X 轴说明" />
      </el-form-item>
      <el-form-item label="X 轴评分" prop="score_x">
        <el-slider v-model="formData.score_x" :min="0" :max="100" show-input />
      </el-form-item>

      <el-form-item label="Y 轴描述">
        <el-input v-model="formData.score_y_desc" placeholder="请输入 Y 轴说明" />
      </el-form-item>
      <el-form-item label="Y 轴评分" prop="score_y">
        <el-slider v-model="formData.score_y" :min="0" :max="100" show-input />
      </el-form-item>

      <el-form-item label="Z 轴描述">
        <el-input v-model="formData.score_z_desc" placeholder="请输入 Z 轴说明" />
      </el-form-item>
      <el-form-item label="Z 轴评分" prop="score_z">
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
        <el-input
          v-model="formData.potential_contribution"
          placeholder="请输入潜在贡献，如 120.50"
        />
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
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createCustomer, updateCustomer } from '../api/customer'
import { calculateLevel } from '../utils/level'

const emptyForm = () => ({
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
const formData = ref(emptyForm())

const rules = {
  name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
  business_model: [{ required: true, message: '请选择业务模式', trigger: 'change' }],
  region: [{ required: true, message: '请输入区域', trigger: 'blur' }],
  city: [{ required: true, message: '请输入城市', trigger: 'blur' }],
  score_x: [{ required: true, message: '请输入 X 轴评分', trigger: 'change' }],
  score_y: [{ required: true, message: '请输入 Y 轴评分', trigger: 'change' }],
  score_z: [{ required: true, message: '请输入 Z 轴评分', trigger: 'change' }]
}

const isEdit = computed(() => Boolean(props.customer?.id))

const currentLevel = computed(() =>
  calculateLevel(formData.value.score_x, formData.value.score_y, formData.value.score_z)
)

const levelType = computed(() => {
  const types = {
    A: 'danger',
    B: 'primary',
    C: 'success',
    D: 'info',
    X: 'warning'
  }
  return types[currentLevel.value] || 'warning'
})

watch(
  () => [props.visible, props.customer],
  ([visible, customer]) => {
    if (!visible) {
      return
    }

    formData.value = customer ? { ...emptyForm(), ...customer } : emptyForm()
  },
  { immediate: true }
)

const resetForm = () => {
  formData.value = emptyForm()
  formRef.value?.clearValidate()
}

const handleClose = () => {
  emit('update:visible', false)
  resetForm()
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true

    const payload = { ...formData.value }

    if (isEdit.value) {
      await updateCustomer(props.customer.id, payload)
      ElMessage.success('客户更新成功')
    } else {
      await createCustomer(payload)
      ElMessage.success('客户创建成功')
    }

    emit('success')
    handleClose()
  } catch (error) {
    if (error?.response?.data) {
      ElMessage.error('保存失败，请检查输入内容')
    }
  } finally {
    loading.value = false
  }
}
</script>
