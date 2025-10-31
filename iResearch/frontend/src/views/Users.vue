<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>用户管理</h2>
      <button class="btn btn-primary" @click="showAddModal = true">
        新增用户
      </button>
    </div>
    
    <!-- 用户列表 -->
    <div class="card">
      <div class="card-body p-0">
        <div v-if="loading" class="text-center p-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">加载中...</span>
          </div>
        </div>
        
        <div v-else-if="users.length === 0" class="text-muted text-center p-4">
          暂无用户数据
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>邮箱</th>
                <th>角色</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.email || '-' }}</td>
                <td>
                  <span class="badge" :class="getRoleBadgeClass(user.role)">
                    {{ getRoleName(user.role) }}
                  </span>
                </td>
                <td>{{ user.created_at }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button 
                      class="btn btn-outline-primary"
                      @click="editUser(user)"
                    >
                      编辑
                    </button>
                    <button 
                      class="btn btn-outline-warning"
                      @click="resetPassword(user)"
                    >
                      重置密码
                    </button>
                    <button 
                      v-if="user.id !== currentUser.id"
                      class="btn btn-outline-danger"
                      @click="confirmDelete(user)"
                    >
                      删除
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- 新增用户模态框 -->
    <div class="modal fade" :class="{ show: showAddModal }" :style="{ display: showAddModal ? 'block' : 'none' }">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">新增用户</h5>
            <button type="button" class="btn-close" @click="showAddModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addUser">
              <div class="mb-3">
                <label class="form-label">用户名 <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="newUserForm.username"
                  required
                >
              </div>
              
              <div class="mb-3">
                <label class="form-label">邮箱</label>
                <input 
                  type="email" 
                  class="form-control" 
                  v-model="newUserForm.email"
                >
              </div>
              
              <div class="mb-3">
                <label class="form-label">密码 <span class="text-danger">*</span></label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="newUserForm.password"
                  required
                >
              </div>
              
              <div class="mb-3">
                <label class="form-label">角色</label>
                <select class="form-select" v-model="newUserForm.role">
                  <option value="viewer">浏览者</option>
                  <option value="editor">编辑</option>
                  <option value="admin">管理员</option>
                </select>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showAddModal = false">取消</button>
            <button type="button" class="btn btn-primary" @click="addUser" :disabled="adding">
              <span v-if="adding" class="spinner-border spinner-border-sm me-2"></span>
              {{ adding ? '添加中...' : '添加' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 编辑用户模态框 -->
    <div class="modal fade" :class="{ show: showEditModal }" :style="{ display: showEditModal ? 'block' : 'none' }">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">编辑用户</h5>
            <button type="button" class="btn-close" @click="showEditModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateUser">
              <div class="mb-3">
                <label class="form-label">用户名</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="editUserForm.username"
                  disabled
                >
              </div>
              
              <div class="mb-3">
                <label class="form-label">邮箱</label>
                <input 
                  type="email" 
                  class="form-control" 
                  v-model="editUserForm.email"
                >
              </div>
              
              <div class="mb-3">
                <label class="form-label">角色</label>
                <select class="form-select" v-model="editUserForm.role">
                  <option value="viewer">浏览者</option>
                  <option value="editor">编辑</option>
                  <option value="admin">管理员</option>
                </select>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showEditModal = false">取消</button>
            <button type="button" class="btn btn-primary" @click="updateUser" :disabled="updating">
              <span v-if="updating" class="spinner-border spinner-border-sm me-2"></span>
              {{ updating ? '更新中...' : '更新' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 重置密码模态框 -->
    <div class="modal fade" :class="{ show: showResetModal }" :style="{ display: showResetModal ? 'block' : 'none' }">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">重置密码</h5>
            <button type="button" class="btn-close" @click="showResetModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="performResetPassword">
              <div class="mb-3">
                <label class="form-label">用户：{{ resetUser?.username }}</label>
              </div>
              
              <div class="mb-3">
                <label class="form-label">新密码 <span class="text-danger">*</span></label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="resetPasswordForm.password"
                  required
                >
              </div>
              
              <div class="mb-3">
                <label class="form-label">确认密码 <span class="text-danger">*</span></label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="resetPasswordForm.confirmPassword"
                  required
                >
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showResetModal = false">取消</button>
            <button type="button" class="btn btn-warning" @click="performResetPassword" :disabled="resetting">
              <span v-if="resetting" class="spinner-border spinner-border-sm me-2"></span>
              {{ resetting ? '重置中...' : '重置密码' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Users',
  data() {
    return {
      users: [],
      loading: false,
      adding: false,
      updating: false,
      resetting: false,
      showAddModal: false,
      showEditModal: false,
      showResetModal: false,
      currentUser: JSON.parse(localStorage.getItem('user') || '{}'),
      newUserForm: {
        username: '',
        email: '',
        password: '',
        role: 'viewer'
      },
      editUserForm: {
        id: null,
        username: '',
        email: '',
        role: 'viewer'
      },
      resetUser: null,
      resetPasswordForm: {
        password: '',
        confirmPassword: ''
      }
    }
  },
  async mounted() {
    await this.loadUsers()
  },
  methods: {
    async loadUsers() {
      this.loading = true
      
      try {
        const response = await this.$axios.get('/users')
        this.users = response.data.items
        
      } catch (error) {
        console.error('加载用户列表失败:', error)
        this.$toast?.error('加载用户列表失败')
      } finally {
        this.loading = false
      }
    },
    
    async addUser() {
      if (!this.newUserForm.username.trim() || !this.newUserForm.password.trim()) {
        this.$toast?.warning('请填写用户名和密码')
        return
      }
      
      this.adding = true
      
      try {
        await this.$axios.post('/users', this.newUserForm)
        
        this.$toast?.success('用户添加成功')
        this.showAddModal = false
        this.newUserForm = {
          username: '',
          email: '',
          password: '',
          role: 'viewer'
        }
        await this.loadUsers()
        
      } catch (error) {
        console.error('添加用户失败:', error)
        this.$toast?.error('添加用户失败')
      } finally {
        this.adding = false
      }
    },
    
    editUser(user) {
      this.editUserForm = {
        id: user.id,
        username: user.username,
        email: user.email || '',
        role: user.role
      }
      this.showEditModal = true
    },
    
    async updateUser() {
      this.updating = true
      
      try {
        await this.$axios.put(`/users/${this.editUserForm.id}`, {
          email: this.editUserForm.email,
          role: this.editUserForm.role
        })
        
        this.$toast?.success('用户更新成功')
        this.showEditModal = false
        await this.loadUsers()
        
      } catch (error) {
        console.error('更新用户失败:', error)
        this.$toast?.error('更新用户失败')
      } finally {
        this.updating = false
      }
    },
    
    resetPassword(user) {
      this.resetUser = user
      this.resetPasswordForm = {
        password: '',
        confirmPassword: ''
      }
      this.showResetModal = true
    },
    
    async performResetPassword() {
      if (!this.resetPasswordForm.password.trim()) {
        this.$toast?.warning('请输入新密码')
        return
      }
      
      if (this.resetPasswordForm.password !== this.resetPasswordForm.confirmPassword) {
        this.$toast?.warning('两次输入的密码不一致')
        return
      }
      
      this.resetting = true
      
      try {
        await this.$axios.put(`/users/${this.resetUser.id}`, {
          password: this.resetPasswordForm.password
        })
        
        this.$toast?.success('密码重置成功')
        this.showResetModal = false
        this.resetUser = null
        
      } catch (error) {
        console.error('重置密码失败:', error)
        this.$toast?.error('重置密码失败')
      } finally {
        this.resetting = false
      }
    },
    
    confirmDelete(user) {
      if (confirm(`确定删除用户"${user.username}"吗？此操作不可恢复。`)) {
        this.deleteUser(user.id)
      }
    },
    
    async deleteUser(userId) {
      try {
        await this.$axios.delete(`/users/${userId}`)
        this.$toast?.success('删除成功')
        await this.loadUsers()
        
      } catch (error) {
        console.error('删除用户失败:', error)
        this.$toast?.error('删除用户失败')
      }
    },
    
    getRoleName(role) {
      const roleNames = {
        'admin': '管理员',
        'editor': '编辑',
        'viewer': '浏览者'
      }
      return roleNames[role] || role
    },
    
    getRoleBadgeClass(role) {
      const classes = {
        'admin': 'bg-danger',
        'editor': 'bg-warning',
        'viewer': 'bg-secondary'
      }
      return classes[role] || 'bg-secondary'
    }
  }
}
</script>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.badge {
  font-size: 0.75em;
}

.btn-group-sm > .btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.text-danger {
  color: #dc3545 !important;
}

.table-responsive {
  max-height: 600px;
  overflow-y: auto;
}
</style>
