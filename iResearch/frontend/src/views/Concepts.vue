<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>概念管理</h2>
      <router-link to="/concept/new" class="btn btn-primary">
        新建概念
      </router-link>
    </div>
    
    <!-- 搜索栏 -->
    <div class="row mb-3">
      <div class="col-md-6">
        <div class="input-group">
          <input 
            type="text" 
            class="form-control" 
            placeholder="搜索概念术语..."
            v-model="searchQuery"
            @keyup.enter="loadConcepts"
          >
          <button class="btn btn-outline-secondary" @click="loadConcepts">
            <i class="bi bi-search"></i>
          </button>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="btn-group w-100">
          <button 
            class="btn btn-outline-danger btn-sm"
            @click="confirmBulkDelete"
            :disabled="selectedConcepts.length === 0"
          >
            批量删除 ({{ selectedConcepts.length }})
          </button>
        </div>
      </div>
    </div>
    
    <!-- 概念列表 -->
    <div class="card">
      <div class="card-body p-0">
        <div v-if="loading" class="text-center p-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">加载中...</span>
          </div>
        </div>
        
        <div v-else-if="concepts.length === 0" class="text-muted text-center p-4">
          暂无概念数据
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th width="50">
                  <input 
                    type="checkbox" 
                    class="form-check-input"
                    :checked="selectedConcepts.length === concepts.length"
                    @change="toggleSelectAll"
                  >
                </th>
                <!-- <th>ID</th> -->
                <th>概念术语</th>
                <th>主分类</th>
                <th>最近使用</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="concept in concepts" :key="concept.id">
                <td>
                  <input 
                    type="checkbox" 
                    class="form-check-input"
                    :value="concept.id"
                    v-model="selectedConcepts"
                  >
                </td>
                <!-- <td>{{ concept.id }}</td> -->
                <td>
                  <router-link 
                    :to="`/concept/${concept.id}/edit`" 
                    class="text-decoration-none"
                  >
                    {{ concept.term }}
                  </router-link>
                </td>
                <td>{{ concept.category || '-' }}</td>
                <td>{{ concept.last_used || '-' }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <router-link 
                      :to="`/concept/${concept.id}/edit`" 
                      class="btn btn-outline-primary"
                    >
                      编辑
                    </router-link>
                    <button 
                      class="btn btn-outline-danger"
                      @click="confirmDelete(concept)"
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
    
    <!-- 分页 -->
    <div class="d-flex justify-content-between align-items-center mt-3" v-if="totalPages > 1">
      <div class="text-muted">
        共 {{ total }} 条记录
      </div>
      
      <nav>
        <ul class="pagination pagination-sm mb-0">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <button class="page-link" @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">
              上一页
            </button>
          </li>
          
          <li class="page-item" v-for="page in visiblePages" :key="page" :class="{ active: page === currentPage }">
            <button class="page-link" @click="goToPage(page)">{{ page }}</button>
          </li>
          
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <button class="page-link" @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">
              下一页
            </button>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Concepts',
  data() {
    return {
      concepts: [],
      loading: false,
      currentPage: 1,
      pageSize: 50,
      total: 0,
      searchQuery: '',
      selectedConcepts: []
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.total / this.pageSize)
    },
    visiblePages() {
      const pages = []
      const start = Math.max(1, this.currentPage - 2)
      const end = Math.min(this.totalPages, this.currentPage + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    }
  },
  async mounted() {
    await this.loadConcepts()
  },
  methods: {
    async loadConcepts() {
      this.loading = true
      
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize
        }
        
        if (this.searchQuery.trim()) {
          params.q = this.searchQuery.trim()
        }
        
        const response = await this.$axios.get('/concepts', { params })
        
        this.concepts = response.data.items
        this.total = response.data.total
        
      } catch (error) {
        console.error('加载概念列表失败:', error)
        this.$toast?.error('加载概念列表失败')
      } finally {
        this.loading = false
      }
    },
    
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        this.loadConcepts()
      }
    },
    
    toggleSelectAll() {
      if (this.selectedConcepts.length === this.concepts.length) {
        this.selectedConcepts = []
      } else {
        this.selectedConcepts = this.concepts.map(c => c.id)
      }
    },
    
    confirmDelete(concept) {
      if (confirm(`确定删除概念"${concept.term}"吗？此操作不可恢复。`)) {
        this.deleteConcept(concept.id)
      }
    },
    
    async deleteConcept(conceptId) {
      try {
        await this.$axios.post('/concepts/bulk', {
          ids: [conceptId],
          op: 'delete'
        })
        
        this.$toast?.success('删除成功')
        await this.loadConcepts()
        
      } catch (error) {
        console.error('删除概念失败:', error)
        this.$toast?.error('删除概念失败')
      }
    },
    
    confirmBulkDelete() {
      if (this.selectedConcepts.length === 0) {
        this.$toast?.warning('请选择要删除的概念')
        return
      }
      
      if (confirm(`确定删除选中的 ${this.selectedConcepts.length} 个概念吗？此操作不可恢复。`)) {
        this.performBulkDelete()
      }
    },
    
    async performBulkDelete() {
      try {
        await this.$axios.post('/concepts/bulk', {
          ids: this.selectedConcepts,
          op: 'delete'
        })
        
        this.$toast?.success('批量删除成功')
        this.selectedConcepts = []
        await this.loadConcepts()
        
      } catch (error) {
        console.error('批量删除失败:', error)
        this.$toast?.error('批量删除失败')
      }
    }
  }
}
</script>

<style scoped>
.table-responsive {
  max-height: 600px;
  overflow-y: auto;
}

.pagination {
  margin-bottom: 0;
}

.btn-group-sm > .btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}
</style>
