<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑联系人' : '新增联系人'"
    width="500px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="姓名" prop="name">
        <el-input v-model="formData.name" placeholder="请输入姓名" />
      </el-form-item>

      <el-form-item label="职位" prop="position">
        <el-input v-model="formData.position" placeholder="请输入职位" />
      </el-form-item>

      <el-form-item label="电话" prop="phone">
        <el-input v-model="formData.phone" placeholder="请输入电话" />
      </el-form-item>

      <el-form-item label="邮箱" prop="email">
        <el-input v-model="formData.email" placeholder="请输入邮箱" />
      </el-form-item>

      <el-form-item label="关键人">
        <el-switch v-model="formData.is_key_person" />
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
import { createContact, updateContact } from '../api/contactApi'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  contact: {
    type: Object,
    default: null
  },
  customerId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update:visible', 'success'])

const formRef = ref(null)
const loading = ref(false)

const isEdit = computed(() => !!props.contact)

const formData = ref({
  name: '',
  position: '',
  phone: '',
  email: '',
  is_key_person: false
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  position: [{ required: true, message: '请输入职位', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入电话', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 监听contact变化，更新表单数据
watch(() => props.contact, (newVal) => {
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
    position: '',
    phone: '',
    email: '',
    is_key_person: false
  }
  formRef.value?.clearValidate()
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true

    if (isEdit.value) {
      await updateContact(props.contact.id, formData.value)
      ElMessage.success('更新联系人成功')
    } else {
      await createContact(props.customerId, formData.value)
      ElMessage.success('创建联系人成功')
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
