import { createRouter, createWebHashHistory } from 'vue-router'
import CustomerList from '../views/CustomerListPage.vue'
import CustomerDetail from '../views/CustomerDetailPage.vue'
import WeeklyReportList from '../views/WeeklyReportListPage.vue'
import WeeklyReportDetail from '../views/WeeklyReportDetailPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/customers'
  },
  {
    path: '/customers',
    name: 'CustomerList',
    component: CustomerList
  },
  {
    path: '/customers/:id',
    name: 'CustomerDetail',
    component: CustomerDetail
  },
  {
    path: '/weekly-reports',
    name: 'WeeklyReportList',
    component: WeeklyReportList
  },
  {
    path: '/weekly-reports/:id',
    name: 'WeeklyReportDetail',
    component: WeeklyReportDetail
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router
