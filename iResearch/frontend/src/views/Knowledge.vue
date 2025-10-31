<template>
  <div>
    <h2 class="mb-3">知识库</h2>
    
    <div class="knowledge-container">
      <!-- 左栏：分类树 -->
      <div class="knowledge-sidebar">
        <div class="card h-100">
          <div class="card-header">
            <h6 class="mb-0">分类导航</h6>
          </div>
          <div class="card-body p-0">
            <CategoryTree 
              :tree-data="categoryTree"
              :selected-category="selectedCategory"
              :current-user="currentUser"
              @category-selected="onCategorySelected"
              @concept-dropped="onConceptDropped"
            />
          </div>
        </div>
      </div>
      
      <!-- 中栏：概念列表 -->
      <div class="knowledge-main">
        <div class="card h-100">
          <div class="card-header">
            <ConceptList 
              :category-id="selectedCategory"
              :search-query="searchQuery"
              :current-user="currentUser"
              @concept-selected="onConceptSelected"
              @search-changed="onSearchChanged"
              @bulk-operation="onBulkOperation"
            />
          </div>
          <div class="card-body p-0">
            <!-- 概念列表内容在 ConceptList 组件中 -->
          </div>
        </div>
      </div>
      
      <!-- 右栏：概念详情 -->
      <div class="knowledge-detail">
        <div class="card h-100">
          <div class="card-header">
            <h6 class="mb-0">概念详情</h6>
          </div>
          <div class="card-body">
            <ConceptDetail 
              :concept-id="selectedConceptId"
              :current-user="currentUser"
              @concept-updated="onConceptUpdated"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CategoryTree from '../components/CategoryTree.vue'
import ConceptList from '../components/ConceptList.vue'
import ConceptDetail from '../components/ConceptDetail.vue'

export default {
  name: 'Knowledge',
  components: {
    CategoryTree,
    ConceptList,
    ConceptDetail
  },
  data() {
    return {
      categoryTree: null,
      selectedCategory: null,
      selectedConceptId: null,
      searchQuery: '',
      currentUser: JSON.parse(localStorage.getItem('user') || '{}')
    }
  },
  async mounted() {
    await this.loadCategoryTree()
  },
  methods: {
    async loadCategoryTree() {
      try {
        const response = await this.$axios.get('/categories/tree')
        this.categoryTree = response.data
      } catch (error) {
        console.error('加载分类树失败:', error)
        this.$toast?.error('加载分类树失败')
      }
    },
    
    onCategorySelected(categoryId) {
      this.selectedCategory = categoryId
      this.searchQuery = '' // 切换分类时清空搜索
    },
    
    onSearchChanged(query) {
      this.searchQuery = query
    },
    
    onConceptSelected(conceptId) {
      this.selectedConceptId = conceptId
    },
    
    async onConceptDropped(conceptId, categoryId) {
      try {
        await this.$axios.post(`/concept/${conceptId}/move`, { category_id: categoryId })
        
        // 刷新分类树计数
        await this.loadCategoryTree()
        
        this.$toast?.success('概念移动成功')
        
      } catch (error) {
        console.error('移动概念失败:', error)
        this.$toast?.error('移动概念失败')
      }
    },
    
    async onBulkOperation(operation, conceptIds, payload) {
      try {
        await this.$axios.post('/concepts/bulk', {
          ids: conceptIds,
          op: operation,
          payload: payload
        })
        
        // 刷新分类树
        await this.loadCategoryTree()
        
        this.$toast?.success('批量操作成功')
        
      } catch (error) {
        console.error('批量操作失败:', error)
        this.$toast?.error('批量操作失败')
      }
    },
    
    onConceptUpdated() {
      // 概念更新后刷新分类树计数
      this.loadCategoryTree()
    }
  }
}
</script>

<style scoped>
.knowledge-container {
  display: flex;
  height: calc(100vh - 200px);
  gap: 15px;
}

.knowledge-sidebar {
  width: 300px;
  min-width: 300px;
}

.knowledge-main {
  flex: 1;
  min-width: 0;
}

.knowledge-detail {
  width: 400px;
  min-width: 400px;
}

@media (max-width: 1200px) {
  .knowledge-container {
    flex-direction: column;
    height: auto;
  }
  
  .knowledge-sidebar,
  .knowledge-detail {
    width: 100%;
    min-width: auto;
  }
  
  .knowledge-sidebar {
    height: 300px;
  }
  
  .knowledge-detail {
    height: 400px;
  }
}
</style>
