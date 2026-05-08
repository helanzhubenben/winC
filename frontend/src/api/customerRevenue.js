import axios from 'axios'

const API_BASE_URL = '/api'

export function getCustomerRevenues(params) {
  return axios.get(`${API_BASE_URL}/customer-revenues/`, { params })
}

export function createCustomerRevenue(data) {
  return axios.post(`${API_BASE_URL}/customer-revenues/`, data)
}

export function importCustomerRevenues(file) {
  const formData = new FormData()
  formData.append('file', file)
  return axios.post(`${API_BASE_URL}/customer-revenues/import/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
