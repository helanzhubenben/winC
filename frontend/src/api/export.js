import axios from 'axios'

const API_BASE_URL = '/api'

export function exportWorkbook() {
  return axios.get(`${API_BASE_URL}/export/workbook/`, {
    responseType: 'blob'
  })
}
