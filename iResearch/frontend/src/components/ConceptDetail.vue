<template>
  <div class="concept-detail">
    <div v-if="loading" class="text-center p-4">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
    </div>
    
    <div v-else-if="!concept" class="text-muted text-center p-4">
      请选择一个概念查看详情
    </div>
    
    <div v-else>
      <!-- 概念基本信息 -->
      <div class="mb-4">
        <h5>{{ concept.term }}</h5>
        <div v-if="concept.category" class="mb-2">
          <span class="badge bg-primary">{{ concept.category }}</span>
        </div>
        <div v-if="concept.last_used" class="text-muted small">
          最近使用：{{ concept.last_used }}
        </div>
      </div>
      
      <!-- 概念图片 -->
      <div v-if="concept.image_path" class="mb-3">
        <img 
          :src="`/uploads/${concept.image_path.split('/').pop()}`" 
          class="img-fluid rounded"
          style="max-height: 200px;"
          :alt="concept.term"
        >
      </div>
      
      <!-- 编辑表单 -->
      <form @submit.prevent="saveConcept">
        <div class="mb-3">
          <label class="form-label">概念术语</label>
          <input 
            type="text" 
            class="form-control" 
            v-model="form.term"
            :disabled="isViewer"
            required
          >
        </div>
        
        <div class="mb-3">
          <label class="form-label">通俗解释</label>
          <textarea
            class="form-control"
            rows="4"
            v-model="form.plain_def"
            :disabled="isViewer"
            placeholder="请输入概念的通俗解释..."
            v-autoresize
          ></textarea>
        </div>

        <div class="mb-3">
          <label class="form-label">案例/例子</label>
          <textarea
            class="form-control"
            rows="3"
            v-model="form.examples"
            :disabled="isViewer"
            placeholder="请输入相关的案例或例子..."
            v-autoresize
          ></textarea>
        </div>
        
        <div class="mb-3">
          <label class="form-label">主分类</label>
          <select 
            class="form-select" 
            v-model="form.category_id"
            :disabled="isViewer"
          >
            <option value="">未分类</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
        </div>
        
        <!-- 操作按钮 -->
        <div class="d-grid gap-2" v-if="!isViewer">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
            {{ saving ? '保存中...' : '保存' }}
          </button>
          
          <button type="button" class="btn btn-outline-success" @click="markAsUsed" :disabled="marking">
            <span v-if="marking" class="spinner-border spinner-border-sm me-2"></span>
            {{ marking ? '标记中...' : '标记为已使用' }}
          </button>
          
          <router-link 
            :to="`/concept/${concept.id}/edit`" 
            class="btn btn-outline-info"
          >
            详细编辑
          </router-link>
        </div>
      </form>
      
      <!-- 浏览者只读显示 -->
      <div v-if="isViewer" class="readonly-content">
        <div class="mb-3">
          <label class="form-label">通俗解释</label>
          <div class="form-control-plaintext">{{ concept.plain_def || '暂无描述' }}</div>
        </div>
        
        <div class="mb-3">
          <label class="form-label">机制原理</label>
          <div class="form-control-plaintext">{{ concept.mechanism || '暂无描述' }}</div>
        </div>
        
        <div class="mb-3">
          <label class="form-label">案例/例子</label>
          <div class="form-control-plaintext">{{ concept.examples || '暂无描述' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConceptDetail',
  props: {
    conceptId: [Number, String],
    currentUser: Object
  },
  emits: ['concept-updated'],
  data() {
    return {
      concept: null,
      categories: [],
      loading: false,
      saving: false,
      marking: false,
      form: {
        term: '',
        plain_def: '',
        mechanism: '',
        examples: '',
        category_id: null
      }
    }
  },
  computed: {
    isViewer() {
      return this.currentUser.role === 'viewer'
    }
  },
  watch: {
    conceptId(newId) {
      if (newId) {
        this.loadConcept()
        // 自动标记为已使用（延迟1秒）
        setTimeout(() => {
          this.autoMarkAsUsed()
        }, 1000)
      }
    }
  },
  async mounted() {
    await this.loadCategories()
    if (this.conceptId) {
      await this.loadConcept()
    }
  },
  methods: {
    async loadConcept() {
      if (!this.conceptId) return
      
      this.loading = true
      
      try {
        const response = await this.$axios.get(`/concept/${this.conceptId}`)
        this.concept = response.data
        
        // 更新表单数据
        this.form = {
          term: this.concept.term || '',
          plain_def: this.concept.plain_def || '',
          mechanism: this.concept.mechanism || '',
          examples: this.concept.examples || '',
          category_id: this.concept.category_id
        }
        
      } catch (error) {
        console.error('加载概念详情失败:', error)
        this.$toast?.error('加载概念详情失败')
      } finally {
        this.loading = false
      }
    },
    
    async loadCategories() {
      try {
        const response = await this.$axios.get('/categories/flat')
        this.categories = response.data.items
      } catch (error) {
        console.error('加载分类列表失败:', error)
      }
    },
    
    async saveConcept() {
      if (this.isViewer) return
      
      this.saving = true
      
      try {
        await this.$axios.post(`/concept/${this.conceptId}/quick_update`, this.form)
        
        // 更新本地数据
        Object.assign(this.concept, this.form)
        
        this.$toast?.success('保存成功')
        this.$emit('concept-updated')
        
      } catch (error) {
        console.error('保存概念失败:', error)
        this.$toast?.error('保存概念失败')
      } finally {
        this.saving = false
      }
    },
    
    async markAsUsed() {
      this.marking = true
      
      try {
        await this.$axios.post(`/concept/${this.conceptId}/quick_update`, { last_used: true })
        
        // 更新本地数据
        this.concept.last_used = new Date().toISOString().split('T')[0]
        
        this.$toast?.success('已标记为使用')
        this.$emit('concept-updated')
        
      } catch (error) {
        console.error('标记使用失败:', error)
        this.$toast?.error('标记使用失败')
      } finally {
        this.marking = false
      }
    },
    
    async autoMarkAsUsed() {
      // 自动标记为已使用，但不显示提示
      try {
        await this.$axios.post(`/concept/${this.conceptId}/quick_update`, { last_used: true })
        
        // 静默更新本地数据
        if (this.concept) {
          this.concept.last_used = new Date().toISOString().split('T')[0]
        }
        
        this.$emit('concept-updated')
        
      } catch (error) {
        // 静默失败，不显示错误
        console.log('自动标记使用失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.concept-detail {
  height: 100%;
  overflow-y: auto;
}

.readonly-content .form-control-plaintext {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  padding: 0.375rem 0.75rem;
  min-height: 2.25rem;
}

.img-fluid {
  max-width: 100%;
  height: auto;
}

.badge {
  font-size: 0.875em;
}
</style>
