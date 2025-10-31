<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>{{ isEdit ? '编辑概念' : '新建概念' }}</h2>
      <div>
        <router-link to="/concepts" class="btn btn-outline-secondary me-2">
          返回列表
        </router-link>
        <button 
          v-if="isEdit" 
          class="btn btn-outline-danger"
          @click="confirmDelete"
        >
          删除概念
        </button>
      </div>
    </div>
    
    <div v-if="loading" class="text-center p-4">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
    </div>
    
    <div v-else>
      <form @submit.prevent="saveConcept">
        <div class="row">
          <!-- 基本信息 -->
          <div class="col-md-8">
            <div class="card mb-4">
              <div class="card-header">
                <h5 class="mb-0">基本信息</h5>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <label class="form-label">概念术语 <span class="text-danger">*</span></label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="form.term"
                    required
                  >
                </div>
                
                <div class="mb-3">
                  <label class="form-label">通俗解释</label>
                  <textarea 
                    class="form-control" 
                    rows="4"
                    v-model="form.plain_def"
                    placeholder="请输入概念的通俗解释..."
                  ></textarea>
                </div>
                
                <div class="mb-3">
                  <label class="form-label">机制原理</label>
                  <textarea 
                    class="form-control" 
                    rows="4"
                    v-model="form.mechanism"
                    placeholder="请输入机制的详细原理..."
                  ></textarea>
                </div>
                
                <div class="mb-3">
                  <label class="form-label">案例/例子</label>
                  <textarea 
                    class="form-control" 
                    rows="4"
                    v-model="form.examples"
                    placeholder="请输入相关的案例或例子..."
                  ></textarea>
                </div>
                
                <div class="mb-3">
                  <label class="form-label">主分类</label>
                  <select class="form-select" v-model="form.category_id">
                    <option value="">未分类</option>
                    <option v-for="category in categories" :key="category.id" :value="category.id">
                      {{ category.name }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 图片和附加分类 -->
          <div class="col-md-4">
            <!-- 概念图片 -->
            <div class="card mb-4">
              <div class="card-header">
                <h5 class="mb-0">概念图片</h5>
              </div>
              <div class="card-body">
                <div v-if="concept?.image_path" class="mb-3">
                  <img 
                    :src="`/uploads/${concept.image_path.split('/').pop()}`" 
                    class="img-fluid rounded"
                    :alt="form.term"
                  >
                </div>
                
                <div v-else class="text-muted text-center mb-3">
                  暂无图片
                </div>
                
                <div class="d-grid">
                  <input 
                    type="file" 
                    class="form-control" 
                    accept="image/*"
                    @change="uploadImage"
                    ref="imageInput"
                  >
                </div>
              </div>
            </div>
            
            <!-- 附加分类 -->
            <div class="card mb-4">
              <div class="card-header">
                <h5 class="mb-0">附加分类</h5>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <div class="input-group">
                    <select class="form-select" v-model="newExtraCategoryId">
                      <option value="">选择分类</option>
                      <option 
                        v-for="category in availableCategories" 
                        :key="category.id" 
                        :value="category.id"
                      >
                        {{ category.name }}
                      </option>
                    </select>
                    <button 
                      class="btn btn-outline-primary" 
                      type="button"
                      @click="addExtraCategory"
                      :disabled="!newExtraCategoryId"
                    >
                      添加
                    </button>
                  </div>
                </div>
                
                <div v-if="extraCategories.length === 0" class="text-muted">
                  暂无附加分类
                </div>
                
                <div v-else>
                  <div 
                    v-for="category in extraCategories" 
                    :key="category.id"
                    class="d-flex justify-content-between align-items-center mb-2"
                  >
                    <span class="badge bg-secondary">{{ category.name }}</span>
                    <button 
                      type="button" 
                      class="btn btn-sm btn-outline-danger"
                      @click="removeExtraCategory(category.id)"
                    >
                      <i class="bi bi-x"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 保存按钮 -->
        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConceptEdit',
  data() {
    return {
      concept: null,
      categories: [],
      extraCategories: [],
      loading: false,
      saving: false,
      uploading: false,
      newExtraCategoryId: '',
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
    isEdit() {
      return !!this.$route.params.id
    },
    availableCategories() {
      // 过滤掉主分类和已添加的附加分类
      const mainCategoryId = this.form.category_id
      const extraCategoryIds = this.extraCategories.map(c => c.id)
      
      return this.categories.filter(c => 
        c.id !== mainCategoryId && !extraCategoryIds.includes(c.id)
      )
    }
  },
  async mounted() {
    await this.loadCategories()
    if (this.isEdit) {
      await this.loadConcept()
    }
  },
  methods: {
    async loadConcept() {
      this.loading = true
      
      try {
        const response = await this.$axios.get(`/concept/${this.$route.params.id}`)
        this.concept = response.data
        this.extraCategories = response.data.extra_categories || []
        
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
        this.$router.push('/concepts')
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
      this.saving = true
      
      try {
        const updateData = {
          ...this.form,
          extra_categories: this.extraCategories.map(c => c.id)
        }
        
        if (this.isEdit) {
          await this.$axios.put(`/concept/${this.$route.params.id}`, updateData)
        } else {
          const response = await this.$axios.post('/concept', this.form)
          this.$router.push(`/concept/${response.data.id}/edit`)
          return
        }
        
        this.$toast?.success('保存成功')
        
      } catch (error) {
        console.error('保存概念失败:', error)
        this.$toast?.error('保存概念失败')
      } finally {
        this.saving = false
      }
    },
    
    async uploadImage(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // 检查文件类型
      if (!file.type.startsWith('image/')) {
        this.$toast?.error('请选择图片文件')
        return
      }
      
      this.uploading = true
      
      try {
        const formData = new FormData()
        formData.append('image', file)
        
        const response = await this.$axios.post(`/concept/${this.$route.params.id}/image`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        // 更新本地数据
        this.concept.image_path = response.data.image_path
        
        this.$toast?.success('图片上传成功')
        
      } catch (error) {
        console.error('上传图片失败:', error)
        this.$toast?.error('上传图片失败')
      } finally {
        this.uploading = false
        // 清空文件输入
        this.$refs.imageInput.value = ''
      }
    },
    
    addExtraCategory() {
      if (!this.newExtraCategoryId) return
      
      const category = this.categories.find(c => c.id == this.newExtraCategoryId)
      if (category) {
        this.extraCategories.push(category)
        this.newExtraCategoryId = ''
      }
    },
    
    removeExtraCategory(categoryId) {
      this.extraCategories = this.extraCategories.filter(c => c.id !== categoryId)
    },
    
    confirmDelete() {
      if (confirm(`确定删除概念"${this.concept.term}"吗？此操作不可恢复。`)) {
        this.deleteConcept()
      }
    },
    
    async deleteConcept() {
      try {
        await this.$axios.post('/concepts/bulk', {
          ids: [this.$route.params.id],
          op: 'delete'
        })
        
        this.$toast?.success('删除成功')
        this.$router.push('/concepts')
        
      } catch (error) {
        console.error('删除概念失败:', error)
        this.$toast?.error('删除概念失败')
      }
    }
  }
}
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.img-fluid {
  max-width: 100%;
  height: auto;
}

.badge {
  font-size: 0.875rem;
}

.form-label {
  font-weight: 500;
}

.text-danger {
  color: #dc3545 !important;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}
</style>
