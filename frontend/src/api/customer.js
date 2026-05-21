import axios from 'axios'

const API_BASE_URL = '/api'

// 获取客户列表（支持筛选、搜索、分页）
export function getCustomers(params) {
  return axios.get(`${API_BASE_URL}/customers/`, { params })
}

export function exportCustomers(params) {
  return axios.get(`${API_BASE_URL}/customers/export/`, {
    params,
    responseType: 'blob'
  })
}

export function downloadCustomerImportTemplate() {
  return axios.get(`${API_BASE_URL}/customers/import-template/`, {
    responseType: 'blob'
  })
}

export function importCustomers(file) {
  const formData = new FormData()
  formData.append('file', file)
  return axios.post(`${API_BASE_URL}/customers/import/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function createCustomerAction(id, data) {
  return axios.post(`${API_BASE_URL}/customers/${id}/create-action/`, data)
}

// 获取客户详情
export function getCustomer(id) {
  return axios.get(`${API_BASE_URL}/customers/${id}/`)
}

// 创建客户
export function createCustomer(data) {
  return axios.post(`${API_BASE_URL}/customers/`, data)
}

// 更新客户
export function updateCustomer(id, data) {
  return axios.put(`${API_BASE_URL}/customers/${id}/`, data)
}

// 删除客户
export function deleteCustomer(id) {
  return axios.delete(`${API_BASE_URL}/customers/${id}/`)
}

// 获取统计数据
export function getStatistics() {
  return axios.get(`${API_BASE_URL}/customers/statistics/`)
}
