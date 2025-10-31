<template>
  <div class="login-page">
    <div class="login-container">
      <el-card class="login-card" shadow="never">
        <div class="logo">
          <h2>行业概念研究系统</h2>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          @submit.prevent="login"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              clearable
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              show-password
              clearable
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              native-type="submit"
              :loading="loading"
              style="width: 100%"
              size="default"
            >
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <el-alert
          v-if="error"
          type="error"
          :title="error"
          show-icon
          style="margin-top: 16px"
          :closable="false"
        />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios' // 假设你已安装 axios
import { ElMessage } from 'element-plus'

// 路由
const router = useRouter()

// 表单引用
const formRef = ref(null)

// 响应式数据
const form = reactive({
  username: '',
  password: ''
})

const loading = ref(false)
const error = ref('')

// 表单验证规则
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 登录方法
const login = async () => {
  if (!formRef.value) return

  // 触发表单验证
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  error.value = ''

  try {
    const response = await axios.post('/auth/login', form)

    // 保存 token 和用户信息
    localStorage.setItem('token', response.data.token)
    localStorage.setItem('user', JSON.stringify(response.data.user))

    // 跳转首页
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.error || '登录失败，请检查用户名或密码'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 已登录则跳转
onMounted(() => {
  if (localStorage.getItem('token')) {
    router.push('/')
  }
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 420px;
}

.login-card {
  border-radius: 16px;
  padding: 32px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border: none;
}

.logo h2 {
  text-align: center;
  margin-bottom: 28px;
  font-weight: 600;
  color: #333;
  font-size: 22px;
}
</style>