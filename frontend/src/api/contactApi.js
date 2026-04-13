import axios from 'axios'

const API_BASE_URL = '/api'

export function getContacts(customerId) {
  return axios.get(`${API_BASE_URL}/contacts/`, {
    params: { customer: customerId }
  })
}

export function createContact(customerId, data) {
  return axios.post(`${API_BASE_URL}/contacts/`, {
    ...data,
    customer: customerId
  })
}

export function updateContact(id, data) {
  return axios.put(`${API_BASE_URL}/contacts/${id}/`, data)
}

export function deleteContact(id) {
  return axios.delete(`${API_BASE_URL}/contacts/${id}/`)
}
