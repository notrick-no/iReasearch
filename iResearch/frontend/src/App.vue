<template>
  <div id="app">
    <!-- 导航栏 -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark" v-if="isLoggedIn">
      <div class="container-fluid">
        <a class="navbar-brand" href="#" @click="$router.push('/')">行业概念研究系统</a>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">仪表盘</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/knowledge">知识库</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/companies">公司</router-link>
            </li>
            
            <!-- 编辑和管理员可见的菜单 -->
            <li class="nav-item" v-if="isEditorOrAdmin">
              <router-link class="nav-link" to="/concepts">概念</router-link>
            </li>
            <li class="nav-item" v-if="isEditorOrAdmin">
              <router-link class="nav-link" to="/categories">分类</router-link>
            </li>
            
            <li class="nav-item">
              <router-link class="nav-link" to="/select">选6家</router-link>
            </li>
            
            <!-- 仅管理员可见的菜单 -->
            <li class="nav-item" v-if="isAdmin">
              <router-link class="nav-link" to="/upload">上传JSON</router-link>
            </li>
            <li class="nav-item" v-if="isAdmin">
              <router-link class="nav-link" to="/users">用户管理</router-link>
            </li>
          </ul>
          
          <!-- 用户菜单 -->
          <ul class="navbar-nav">
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                {{ currentUser.username }} ({{ getRoleName(currentUser.role) }})
              </a>
              <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="#" @click="logout">注销</a></li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    
    <!-- 主要内容区域 -->
    <main class="container-fluid" :class="{ 'mt-3': isLoggedIn }">
      <router-view />
    </main>
    
    <!-- Toast 通知 -->
    <ToastContainer />
  </div>
</template>

<script>
import ToastContainer from './components/ToastContainer.vue'

export default {
  name: 'App',
  components: {
    ToastContainer
  },
  data() {
    return {
      currentUser: JSON.parse(localStorage.getItem('user') || '{}')
    }
  },
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token')
    },
    isAdmin() {
      return this.currentUser.role === 'admin'
    },
    isEditorOrAdmin() {
      return ['admin', 'editor'].includes(this.currentUser.role)
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.currentUser = {}
      this.$router.push('/login')
    },
    getRoleName(role) {
      const roleNames = {
        'admin': '管理员',
        'editor': '编辑',
        'viewer': '浏览者'
      }
      return roleNames[role] || role
    }
  },
  mounted() {
    // 验证登录状态
    if (this.isLoggedIn) {
      this.$axios.get('/auth/me')
        .then(response => {
          this.currentUser = response.data
          localStorage.setItem('user', JSON.stringify(response.data))
        })
        .catch(() => {
          this.logout()
        })
    }
  }
}
</script>

<style>
/* 自定义样式 */
.navbar-brand {
  font-weight: bold;
}

.container-fluid {
  padding-left: 15px;
  padding-right: 15px;
}

/* 知识库三栏布局 */
.knowledge-container {
  display: flex;
  height: calc(100vh - 120px);
  gap: 15px;
}

.knowledge-sidebar {
  width: 300px;
  overflow-y: auto;
  border-right: 1px solid #dee2e6;
}

.knowledge-main {
  flex: 1;
  overflow-y: auto;
}

.knowledge-detail {
  width: 400px;
  overflow-y: auto;
  border-left: 1px solid #dee2e6;
}

/* 列表项高亮 */
.list-group-item.active {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

/* 拖拽样式 */
.draggable {
  cursor: move;
}

.drop-target {
  background-color: #f8f9fa;
  border: 2px dashed #dee2e6;
}

.drop-target.drag-over {
  background-color: #e3f2fd;
  border-color: #2196f3;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .knowledge-container {
    flex-direction: column;
    height: auto;
  }
  
  .knowledge-sidebar,
  .knowledge-detail {
    width: 100%;
    height: 300px;
  }
}
</style>
