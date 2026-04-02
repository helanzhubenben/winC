import { createRouter, createWebHashHistory } from 'vue-router'
import CustomerList from '../views/CustomerListPage.vue'
import CustomerDetail from '../views/CustomerDetailPage.vue'

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
