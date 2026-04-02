import axios from 'axios'

const API_BASE_URL = '/api'

// 获取客户的联系人列表
export function getContacts(customerId) {
  return axios.get(`${API_BASE_URL}/customers/${customerId}/contacts/`)
}

// 创建联系人
export function createContact(customerId, data) {
  return axios.post(`${API_BASE_URL}/customers/${customerId}/contacts/`, data)
}

// 更新联系人
export function updateContact(id, data) {
  return axios.put(`${API_BASE_URL}/contacts/${id}/`, data)
}

// 删除联系人
export function deleteContact(id) {
  return axios.delete(`${API_BASE_URL}/contacts/${id}/`)
}
