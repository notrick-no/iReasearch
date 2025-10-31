import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'
import App from './App.vue'
import autoResize from './directives/autoResize'
import Login from './views/Login.vue'
import Dashboard from './views/Dashboard.vue'
import Knowledge from './views/Knowledge.vue'
import Companies from './views/Companies.vue'
import CompanyEdit from './views/CompanyEdit.vue'
import Concepts from './views/Concepts.vue'
import ConceptEdit from './views/ConceptEdit.vue'
import Categories from './views/Categories.vue'
import CategoryEdit from './views/CategoryEdit.vue'
import Select from './views/Select.vue'
import Upload from './views/Upload.vue'
import Users from './views/Users.vue'

// 路由配置
const routes = [
  { path: '/login', name: 'Login', component: Login },
  { path: '/', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/knowledge', name: 'Knowledge', component: Knowledge, meta: { requiresAuth: true } },
  { path: '/companies', name: 'Companies', component: Companies, meta: { requiresAuth: true } },
  { path: '/company/new', name: 'CompanyNew', component: CompanyEdit, meta: { requiresAuth: true, requiresRole: 'editor' } },
  { path: '/company/:id/edit', name: 'CompanyEdit', component: CompanyEdit, meta: { requiresAuth: true, requiresRole: 'editor' } },
  { path: '/concepts', name: 'Concepts', component: Concepts, meta: { requiresAuth: true, requiresRole: 'editor' } },
  { path: '/concept/new', name: 'ConceptNew', component: ConceptEdit, meta: { requiresAuth: true, requiresRole: 'editor' } },
  { path: '/concept/:id/edit', name: 'ConceptEdit', component: ConceptEdit, meta: { requiresAuth: true, requiresRole: 'editor' } },
  { path: '/categories', name: 'Categories', component: Categories, meta: { requiresAuth: true, requiresRole: 'editor' } },
  { path: '/category/:id/edit', name: 'CategoryEdit', component: CategoryEdit, meta: { requiresAuth: true, requiresRole: 'editor' } },
  { path: '/select', name: 'Select', component: Select, meta: { requiresAuth: true } },
  { path: '/upload', name: 'Upload', component: Upload, meta: { requiresAuth: true, requiresRole: 'admin' } },
  { path: '/users', name: 'Users', component: Users, meta: { requiresAuth: true, requiresRole: 'admin' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 创建 Vue 应用
const app = createApp(App)
app.directive('autoresize', autoResize)

// 配置 Axios
axios.defaults.baseURL = '/api'
axios.defaults.timeout = 10000

// 将 axios 添加到 Vue 实例
app.config.globalProperties.$axios = axios

// 请求拦截器 - 添加认证头
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理认证错误
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token 过期或无效
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (router.currentRoute.value.name !== 'Login') {
        router.push('/login')
      }
    }
    return Promise.reject(error)
  }
)

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }
  
  if (to.meta.requiresRole && user.role !== to.meta.requiresRole) {
    if (to.meta.requiresRole === 'admin' && user.role !== 'admin') {
      next('/')
      return
    }
    if (to.meta.requiresRole === 'editor' && !['admin', 'editor'].includes(user.role)) {
      next('/')
      return
    }
  }
  
  next()
})

app.use(router)
app.mount('#app')
app.provide('$axios', axios)

