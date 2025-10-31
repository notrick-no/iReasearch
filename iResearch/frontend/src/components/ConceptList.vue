<template>
  <div class="concept-list">
    <!-- 搜索和操作栏 -->
    <div class="p-3 border-bottom">
      <div class="row g-2">
        <div class="col-md-6">
          <div class="input-group">
            <input 
              type="text" 
              class="form-control" 
              placeholder="搜索概念..."
              v-model="searchInput"
              @keyup.enter="performSearch"
            >
            <button class="btn btn-outline-secondary" @click="performSearch">
              <i class="bi bi-search"></i>
            </button>
          </div>
        </div>
        
        <div class="col-md-3">
          <select class="form-select" v-model="sortBy" @change="loadConcepts">
            <option value="term">按名称排序</option>
            <option value="last_used">按最近使用排序</option>
          </select>
        </div>
        
        <div class="col-md-3" v-if="isEditorOrAdmin">
          <div class="btn-group w-100">
            <button 
              class="btn btn-outline-primary btn-sm"
              @click="showBulkMoveModal = true"
              :disabled="selectedConcepts.length === 0"
            >
              批量移动
            </button>
            <button 
              class="btn btn-outline-danger btn-sm"
              @click="confirmBulkDelete"
              :disabled="selectedConcepts.length === 0"
            >
              批量删除
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 概念列表 -->
    <div class="concept-items">
      <div v-if="loading" class="text-center p-4">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
      </div>
      
      <div v-else-if="concepts.length === 0" class="text-muted text-center p-4">
        暂无概念数据
      </div>
      
      <div v-else class="list-group list-group-flush">
        <div 
          v-for="concept in concepts" 
          :key="concept.id"
          class="list-group-item list-group-item-action"
          :class="{ active: selectedConceptId === concept.id }"
          @click="selectConcept(concept.id)"
          :draggable="isEditorOrAdmin"
          @dragstart="onDragStart($event, concept.id)"
        >
          <div class="d-flex align-items-start">
            <!-- 复选框 -->
            <div class="form-check me-3" v-if="isEditorOrAdmin" @click.stop>
              <input 
                class="form-check-input" 
                type="checkbox" 
                :value="concept.id"
                v-model="selectedConcepts"
              >
            </div>
            
            <!-- 概念信息 -->
            <div class="flex-grow-1">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h6 class="mb-1">
                    <strong>{{ concept.term }}</strong>
                    <span v-if="concept.category" class="badge bg-light text-dark ms-2">
                      {{ concept.category }}
                    </span>
                  </h6>
                  <p class="mb-1 text-muted small">
                    {{ getConceptSummary(concept.plain_def) }}
                  </p>
                </div>
                <small class="text-muted">
                  {{ concept.last_used || '-' }}
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 分页 -->
    <div class="p-3 border-top" v-if="totalPages > 1">
      <nav>
        <ul class="pagination pagination-sm justify-content-center mb-0">
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
      
      <div class="text-center text-muted small">
        第 {{ currentPage }} 页 / 共 {{ totalPages }} 页，共 {{ total }} 条记录
      </div>
    </div>
    
    <!-- 批量移动模态框 -->
    <div class="modal fade" :class="{ show: showBulkMoveModal }" :style="{ display: showBulkMoveModal ? 'block' : 'none' }">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">批量移动概念</h5>
            <button type="button" class="btn-close" @click="showBulkMoveModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">选择目标分类</label>
              <select class="form-select" v-model="bulkMoveTarget">
                <option value="">请选择分类</option>
                <option value="null">未分类</option>
                <option v-for="category in flatCategories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showBulkMoveModal = false">取消</button>
            <button type="button" class="btn btn-primary" @click="performBulkMove" :disabled="!bulkMoveTarget">
              确认移动
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConceptList',
  props: {
    categoryId: [Number, String],
    searchQuery: String,
    currentUser: Object
  },
  emits: ['concept-selected', 'search-changed', 'bulk-operation'],
  data() {
    return {
      concepts: [],
      loading: false,
      currentPage: 1,
      pageSize: 50,
      total: 0,
      sortBy: 'term',
      searchInput: '',
      selectedConcepts: [],
      showBulkMoveModal: false,
      bulkMoveTarget: '',
      flatCategories: [],
      searchTimer: null
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
    },
    isEditorOrAdmin() {
      return ['admin', 'editor'].includes(this.currentUser.role)
    }
  },
  watch: {
    categoryId() {
      this.currentPage = 1
      this.loadConcepts()
    },
    searchInput(newVal) {
      // 防抖搜索
      clearTimeout(this.searchTimer)
      this.searchTimer = setTimeout(() => {
        this.performSearch()
      }, 300)
    }
  },
  async mounted() {
    await this.loadCategories()
    await this.loadConcepts()
  },
  methods: {
    async loadConcepts() {
      this.loading = true
      
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          sort: this.sortBy
        }
        
        if (this.categoryId !== null && this.categoryId !== undefined) {
          params.cat_id = this.categoryId
        }
        
        if (this.searchInput.trim()) {
          params.q = this.searchInput.trim()
        }
        
        const response = await this.$axios.get('/concepts', { params })
        
        this.concepts = response.data.items
        this.total = response.data.total
        
        // 默认选中第一项
        if (this.concepts.length > 0 && !this.selectedConcepts.includes(this.concepts[0].id)) {
          this.$emit('concept-selected', this.concepts[0].id)
        }
        
      } catch (error) {
        console.error('加载概念列表失败:', error)
        this.$toast?.error('加载概念列表失败')
      } finally {
        this.loading = false
      }
    },
    
    async loadCategories() {
      try {
        const response = await this.$axios.get('/categories/flat')
        this.flatCategories = response.data.items
      } catch (error) {
        console.error('加载分类列表失败:', error)
      }
    },
    
    performSearch() {
      this.currentPage = 1
      this.$emit('search-changed', this.searchInput)
      this.loadConcepts()
    },
    
    selectConcept(conceptId) {
      this.$emit('concept-selected', conceptId)
    },
    
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        this.loadConcepts()
      }
    },
    
    onDragStart(event, conceptId) {
      event.dataTransfer.setData('text/plain', conceptId.toString())
    },
    
    getConceptSummary(text) {
      if (!text) return '暂无描述'
      return text.length > 100 ? text.substring(0, 100) + '...' : text
    },
    
    confirmBulkDelete() {
      if (confirm(`确定删除选中的 ${this.selectedConcepts.length} 个概念吗？此操作不可恢复。`)) {
        this.performBulkDelete()
      }
    },
    
    async performBulkDelete() {
      try {
        await this.$emit('bulk-operation', 'delete', this.selectedConcepts)
        this.selectedConcepts = []
        await this.loadConcepts()
      } catch (error) {
        console.error('批量删除失败:', error)
      }
    },
    
    async performBulkMove() {
      try {
        const targetId = this.bulkMoveTarget === 'null' ? null : parseInt(this.bulkMoveTarget)
        await this.$emit('bulk-operation', 'move', this.selectedConcepts, { category_id: targetId })
        this.selectedConcepts = []
        this.showBulkMoveModal = false
        this.bulkMoveTarget = ''
        await this.loadConcepts()
      } catch (error) {
        console.error('批量移动失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.concept-list {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.concept-items {
  flex: 1;
  overflow-y: auto;
}

.list-group-item {
  cursor: pointer;
  transition: background-color 0.2s;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.list-group-item.active {
  background-color: #0d6efd;
  border-color: #0d6efd;
  color: white;
}

.list-group-item.active .text-muted {
  color: rgba(255, 255, 255, 0.7) !important;
}

.badge {
  font-size: 0.75em;
}

.pagination {
  margin-bottom: 0;
}

.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

/* 拖拽样式 */
.list-group-item[draggable="true"] {
  cursor: move;
}

.list-group-item[draggable="true"]:hover {
  background-color: #e3f2fd;
}
</style>
