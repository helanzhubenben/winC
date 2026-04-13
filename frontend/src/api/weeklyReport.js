import axios from 'axios'

const API_BASE_URL = '/api'

// 获取 Weekly Report 列表
export function getWeeklyReports(params) {
  return axios.get(`${API_BASE_URL}/weekly-reports/`, { params })
}

// 获取 Weekly Report 详情
export function getWeeklyReport(id) {
  return axios.get(`${API_BASE_URL}/weekly-reports/${id}/`)
}

// 创建 Weekly Report
export function createWeeklyReport(data) {
  return axios.post(`${API_BASE_URL}/weekly-reports/`, data)
}

// 更新 Weekly Report
export function updateWeeklyReport(id, data) {
  return axios.put(`${API_BASE_URL}/weekly-reports/${id}/`, data)
}

// 删除 Weekly Report
export function deleteWeeklyReport(id) {
  return axios.delete(`${API_BASE_URL}/weekly-reports/${id}/`)
}

// 添加行动记录
export function addAction(reportId, data) {
  return axios.post(`${API_BASE_URL}/weekly-reports/${reportId}/add-action/`, data)
}

// 更新行动记录
export function updateAction(reportId, index, data) {
  return axios.post(`${API_BASE_URL}/weekly-reports/${reportId}/actions/${index}/update/`, data)
}

// 删除行动记录
export function deleteAction(reportId, index) {
  return axios.post(`${API_BASE_URL}/weekly-reports/${reportId}/actions/${index}/delete/`)
}

// 获取客户的所有 Weekly Reports
export function getCustomerWeeklyReports(customerId) {
  return axios.get(`${API_BASE_URL}/customers/${customerId}/weekly-reports/`)
}
