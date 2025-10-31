<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>编辑分类</h2>
      <div>
        <router-link to="/categories" class="btn btn-outline-secondary me-2">
          返回列表
        </router-link>
        <button class="btn btn-outline-danger" @click="confirmDelete">
          删除分类
        </button>
      </div>
    </div>
    
    <div v-if="loading" class="text-center p-4">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
    </div>
    
    <div v-else>
      <div class="row">
        <!-- 基本信息 -->
        <div class="col-md-6">
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">基本信息</h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="saveCategory">
                <div class="mb-3">
                  <label class="form-label">分类名称 <span class="text-danger">*</span></label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="form.name"
                    required
                  >
                </div>
                
                <div class="mb-3">
                  <label class="form-label">上级分类</label>
                  <select class="form-select" v-model="form.parent_id">
                    <option value="">顶级分类</option>
                    <option 
                      v-for="category in availableParents" 
                      :key="category.id" 
                      :value="category.id"
                    >
                      {{ category.name }}
                    </option>
                  </select>
                </div>
                
                <div class="d-grid">
                  <button type="submit" class="btn btn-primary" :disabled="saving">
                    <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                    {{ saving ? '保存中...' : '保存' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
        
        <!-- 概念关联 -->
        <div class="col-md-6">
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">关联概念</h5>
            </div>
            <div class="card-body">
              <!-- 添加概念 -->
              <div class="mb-3">
                <div class="input-group">
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="newConceptTerm"
                    placeholder="输入概念术语..."
                    @keyup.enter="addConcept"
                  >
                  <button 
                    class="btn btn-outline-primary" 
                    type="button"
                    @click="addConcept"
                    :disabled="!newConceptTerm.trim()"
                  >
                    添加概念
                  </button>
                </div>
              </div>
              
              <!-- 概念列表 -->
              <div v-if="concepts.length === 0" class="text-muted">
                暂无关联概念
              </div>
              
              <div v-else class="list-group list-group-flush">
                <div 
                  v-for="concept in concepts" 
                  :key="concept.id"
                  class="list-group-item d-flex justify-content-between align-items-center"
                >
                  <div>
                    <strong>{{ concept.term }}</strong>
                    <span v-if="concept.is_main" class="badge bg-primary ms-2">主分类</span>
                  </div>
                  <button 
                    v-if="!concept.is_main"
                    type="button" 
                    class="btn btn-sm btn-outline-danger"
                    @click="removeConcept(concept.id)"
                  >
                    移除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 分类关系 -->
      <div class="row">
        <div class="col-md-4">
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">上位分类</h5>
            </div>
            <div class="card-body">
              <div v-if="relations.broader.length === 0" class="text-muted">
                暂无上位分类
              </div>
              
              <div v-else>
                <div 
                  v-for="relation in relations.broader" 
                  :key="relation.relation_id"
                  class="d-flex justify-content-between align-items-center mb-2"
                >
                  <span>{{ relation.name }}</span>
                  <button 
                    type="button" 
                    class="btn btn-sm btn-outline-danger"
                    @click="removeRelation(relation.relation_id)"
                  >
                    删除
                  </button>
                </div>
              </div>
              
              <div class="mt-3">
                <div class="input-group">
                  <select class="form-select" v-model="newRelation.broader">
                    <option value="">选择上位分类</option>
                    <option 
                      v-for="category in availableForRelation" 
                      :key="category.id" 
                      :value="category.id"
                    >
                      {{ category.name }}
                    </option>
                  </select>
                  <button 
                    class="btn btn-outline-primary" 
                    type="button"
                    @click="addRelation('broader')"
                    :disabled="!newRelation.broader"
                  >
                    添加
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">下位分类</h5>
            </div>
            <div class="card-body">
              <div v-if="relations.narrower.length === 0" class="text-muted">
                暂无下位分类
              </div>
              
              <div v-else>
                <div 
                  v-for="relation in relations.narrower" 
                  :key="relation.relation_id"
                  class="d-flex justify-content-between align-items-center mb-2"
                >
                  <span>{{ relation.name }}</span>
                  <button 
                    type="button" 
                    class="btn btn-sm btn-outline-danger"
                    @click="removeRelation(relation.relation_id)"
                  >
                    删除
                  </button>
                </div>
              </div>
              
              <div class="mt-3">
                <div class="input-group">
                  <select class="form-select" v-model="newRelation.narrower">
                    <option value="">选择下位分类</option>
                    <option 
                      v-for="category in availableForRelation" 
                      :key="category.id" 
                      :value="category.id"
                    >
                      {{ category.name }}
                    </option>
                  </select>
                  <button 
                    class="btn btn-outline-primary" 
                    type="button"
                    @click="addRelation('narrower')"
                    :disabled="!newRelation.narrower"
                  >
                    添加
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">相关分类</h5>
            </div>
            <div class="card-body">
              <div v-if="relations.related.length === 0" class="text-muted">
                暂无相关分类
              </div>
              
              <div v-else>
                <div 
                  v-for="relation in relations.related" 
                  :key="relation.relation_id"
                  class="d-flex justify-content-between align-items-center mb-2"
                >
                  <span>{{ relation.name }}</span>
                  <button 
                    type="button" 
                    class="btn btn-sm btn-outline-danger"
                    @click="removeRelation(relation.relation_id)"
                  >
                    删除
                  </button>
                </div>
              </div>
              
              <div class="mt-3">
                <div class="input-group">
                  <select class="form-select" v-model="newRelation.related">
                    <option value="">选择相关分类</option>
                    <option 
                      v-for="category in availableForRelation" 
                      :key="category.id" 
                      :value="category.id"
                    >
                      {{ category.name }}
                    </option>
                  </select>
                  <button 
                    class="btn btn-outline-primary" 
                    type="button"
                    @click="addRelation('related')"
                    :disabled="!newRelation.related"
                  >
                    添加
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CategoryEdit',
  data() {
    return {
      category: null,
      concepts: [],
      relations: {
        broader: [],
        narrower: [],
        related: []
      },
      flatCategories: [],
      loading: false,
      saving: false,
      newConceptTerm: '',
      newRelation: {
        broader: '',
        narrower: '',
        related: ''
      },
      form: {
        name: '',
        parent_id: ''
      }
    }
  },
  computed: {
    availableParents() {
      // 过滤掉自己和子分类，避免循环引用
      return this.flatCategories.filter(c => c.id !== this.$route.params.id)
    },
    availableForRelation() {
      // 过滤掉自己
      return this.flatCategories.filter(c => c.id !== this.$route.params.id)
    }
  },
  async mounted() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      
      try {
        const [categoryRes, conceptsRes, relationsRes, flatRes] = await Promise.all([
          this.$axios.get(`/category/${this.$route.params.id}`),
          this.$axios.get(`/category/${this.$route.params.id}/concepts`),
          this.$axios.get(`/category/${this.$route.params.id}/relations`),
          this.$axios.get('/categories/flat')
        ])
        
        this.category = categoryRes.data
        this.concepts = conceptsRes.data.items || []
        this.relations = relationsRes.data
        this.flatCategories = flatRes.data.items
        
        // 更新表单数据
        this.form = {
          name: this.category.name,
          parent_id: this.category.parent_id
        }
        
      } catch (error) {
        console.error('加载分类详情失败:', error)
        this.$toast?.error('加载分类详情失败')
        this.$router.push('/categories')
      } finally {
        this.loading = false
      }
    },
    
    async saveCategory() {
      this.saving = true
      
      try {
        await this.$axios.put(`/category/${this.$route.params.id}`, this.form)
        this.$toast?.success('保存成功')
        
      } catch (error) {
        console.error('保存分类失败:', error)
        this.$toast?.error('保存分类失败')
      } finally {
        this.saving = false
      }
    },
    
    async addConcept() {
      if (!this.newConceptTerm.trim()) return
      
      try {
        await this.$axios.post(`/category/${this.$route.params.id}/concepts`, {
          term: this.newConceptTerm.trim()
        })
        
        this.newConceptTerm = ''
        await this.loadConcepts()
        this.$toast?.success('概念添加成功')
        
      } catch (error) {
        console.error('添加概念失败:', error)
        this.$toast?.error('添加概念失败')
      }
    },
    
    async loadConcepts() {
      try {
        const response = await this.$axios.get(`/category/${this.$route.params.id}/concepts`)
        this.concepts = response.data.items || []
      } catch (error) {
        console.error('加载概念列表失败:', error)
      }
    },
    
    async removeConcept(conceptId) {
      try {
        await this.$axios.delete(`/category/${this.$route.params.id}/concepts/${conceptId}`)
        await this.loadConcepts()
        this.$toast?.success('概念移除成功')
        
      } catch (error) {
        console.error('移除概念失败:', error)
        this.$toast?.error('移除概念失败')
      }
    },
    
    async addRelation(type) {
      const categoryId = this.newRelation[type]
      if (!categoryId) return
      
      try {
        await this.$axios.post(`/category/${this.$route.params.id}/relations`, {
          predicate: type,
          object_id: categoryId
        })
        
        this.newRelation[type] = ''
        await this.loadRelations()
        this.$toast?.success('关系添加成功')
        
      } catch (error) {
        console.error('添加关系失败:', error)
        this.$toast?.error('添加关系失败')
      }
    },
    
    async loadRelations() {
      try {
        const response = await this.$axios.get(`/category/${this.$route.params.id}/relations`)
        this.relations = response.data
      } catch (error) {
        console.error('加载关系列表失败:', error)
      }
    },
    
    async removeRelation(relationId) {
      try {
        await this.$axios.delete(`/category_relation/${relationId}`)
        await this.loadRelations()
        this.$toast?.success('关系删除成功')
        
      } catch (error) {
        console.error('删除关系失败:', error)
        this.$toast?.error('删除关系失败')
      }
    },
    
    confirmDelete() {
      if (confirm(`确定删除分类"${this.category.name}"吗？此操作不可恢复。`)) {
        this.deleteCategory()
      }
    },
    
    async deleteCategory() {
      try {
        await this.$axios.delete(`/category/${this.$route.params.id}`)
        this.$toast?.success('删除成功')
        this.$router.push('/categories')
        
      } catch (error) {
        console.error('删除分类失败:', error)
        this.$toast?.error('删除分类失败')
      }
    }
  }
}
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.badge {
  font-size: 0.75em;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.text-danger {
  color: #dc3545 !important;
}

.list-group-item {
  border-left: none;
  border-right: none;
}
</style>
