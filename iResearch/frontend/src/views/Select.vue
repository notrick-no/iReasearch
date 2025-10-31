<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>选6家公司</h2>
      <button 
        class="btn btn-success"
        @click="exportCSV"
        :disabled="selectedCompanies.length === 0"
      >
        导出CSV ({{ selectedCompanies.length }})
      </button>
    </div>
    
    <!-- 搜索栏 -->
    <div class="row mb-3">
      <div class="col-md-6">
        <div class="input-group">
          <input 
            type="text" 
            class="form-control" 
            placeholder="搜索公司名称或领域..."
            v-model="searchQuery"
            @keyup.enter="loadCompanies"
          >
          <button class="btn btn-outline-secondary" @click="loadCompanies">
            <i class="bi bi-search"></i>
          </button>
        </div>
      </div>
      
      <div class="col-md-6">
        <div class="alert alert-info mb-0">
          <i class="bi bi-info-circle me-2"></i>
          已选择 {{ selectedCompanies.length }} 家公司，建议最多选择6家
        </div>
      </div>
    </div>
    
    <!-- 公司列表 -->
    <div class="card">
      <div class="card-body p-0">
        <div v-if="loading" class="text-center p-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">加载中...</span>
          </div>
        </div>
        
        <div v-else-if="companies.length === 0" class="text-muted text-center p-4">
          暂无公司数据
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th width="50">
                  <input 
                    type="checkbox" 
                    class="form-check-input"
                    :checked="selectedCompanies.length === companies.length"
                    @change="toggleSelectAll"
                  >
                </th>
                <th>ID</th>
                <th>公司名称</th>
                <th>所属领域</th>
                <th>创建时间</th>
                <th>关联概念</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="company in companies" :key="company.id">
                <td>
                  <input 
                    type="checkbox" 
                    class="form-check-input"
                    :value="company.id"
                    v-model="selectedCompanies"
                    :disabled="selectedCompanies.length >= 6 && !selectedCompanies.includes(company.id)"
                  >
                </td>
                <td>{{ company.id }}</td>
                <td>{{ company.name }}</td>
                <td>{{ company.field || '-' }}</td>
                <td>{{ company.created_at }}</td>
                <td>
                  <span class="badge bg-primary">{{ getCompanyConceptCount(company.id) }}</span>
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
  name: 'Select',
  data() {
    return {
      companies: [],
      companyDetails: {},
      loading: false,
      currentPage: 1,
      pageSize: 50,
      total: 0,
      searchQuery: '',
      selectedCompanies: []
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
    await this.loadCompanies()
  },
  methods: {
    async loadCompanies() {
      this.loading = true
      
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize
        }
        
        if (this.searchQuery.trim()) {
          params.q = this.searchQuery.trim()
        }
        
        const response = await this.$axios.get('/companies', { params })
        
        this.companies = response.data.items
        this.total = response.data.total
        
        // 加载选中公司的详细信息
        await this.loadSelectedCompanyDetails()
        
      } catch (error) {
        console.error('加载公司列表失败:', error)
        this.$toast?.error('加载公司列表失败')
      } finally {
        this.loading = false
      }
    },
    
    async loadSelectedCompanyDetails() {
      // 只加载选中公司的详细信息
      const promises = this.selectedCompanies.map(async (companyId) => {
        if (!this.companyDetails[companyId]) {
          try {
            const response = await this.$axios.get(`/company/${companyId}`)
            this.companyDetails[companyId] = response.data
          } catch (error) {
            console.error(`加载公司${companyId}详情失败:`, error)
          }
        }
      })
      
      await Promise.all(promises)
    },
    
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        this.loadCompanies()
      }
    },
    
    toggleSelectAll() {
      if (this.selectedCompanies.length === this.companies.length) {
        this.selectedCompanies = []
      } else {
        this.selectedCompanies = this.companies.slice(0, 6).map(c => c.id)
      }
    },
    
    getCompanyConceptCount(companyId) {
      const company = this.companyDetails[companyId]
      return company?.concepts?.length || 0
    },
    
    async exportCSV() {
      if (this.selectedCompanies.length === 0) {
        this.$toast?.warning('请选择要导出的公司')
        return
      }
      
      try {
        // 确保所有选中公司的详细信息都已加载
        await this.loadSelectedCompanyDetails()
        
        // 生成CSV内容
        const csvContent = this.generateCSV()
        
        // 创建并下载文件
        this.downloadCSV(csvContent, 'selected_companies.csv')
        
        this.$toast?.success('导出成功')
        
      } catch (error) {
        console.error('导出CSV失败:', error)
        this.$toast?.error('导出CSV失败')
      }
    },
    
    generateCSV() {
      const headers = [
        'name', 'website', 'address', 'team_info', 'funding_info',
        'product_service', 'biz_model', 'partners', 'clients',
        'field', 'notes', 'core_concepts', 'concept_explanations'
      ]
      
      // 添加BOM以支持中文
      let csv = '\uFEFF'
      
      // 添加表头
      csv += headers.join(',') + '\n'
      
      // 添加数据行
      this.selectedCompanies.forEach(companyId => {
        const company = this.companyDetails[companyId]
        if (!company) return
        
        const row = [
          this.escapeCSV(company.name || ''),
          this.escapeCSV(company.website || ''),
          this.escapeCSV(company.address || ''),
          this.escapeCSV(company.team_info || ''),
          this.escapeCSV(company.funding_info || ''),
          this.escapeCSV(company.product || ''),
          this.escapeCSV(company.biz_model || ''),
          this.escapeCSV(company.partners || ''),
          this.escapeCSV(company.clients || ''),
          this.escapeCSV(company.field || ''),
          this.escapeCSV(company.notes || ''),
          this.escapeCSV(this.getCoreConcepts(company)),
          this.escapeCSV(this.getConceptExplanations(company))
        ]
        
        csv += row.join(',') + '\n'
      })
      
      return csv
    },
    
    getCoreConcepts(company) {
      if (!company.concepts || company.concepts.length === 0) {
        return ''
      }
      return company.concepts.map(c => c.term).join('；')
    },
    
    getConceptExplanations(company) {
      if (!company.concepts || company.concepts.length === 0) {
        return ''
      }
      return company.concepts.map(c => `【${c.term}】${c.plain_def || ''}`).join('；')
    },
    
    escapeCSV(field) {
      if (field === null || field === undefined) {
        return ''
      }
      
      const str = String(field)
      if (str.includes(',') || str.includes('"') || str.includes('\n')) {
        return '"' + str.replace(/"/g, '""') + '"'
      }
      return str
    },
    
    downloadCSV(content, filename) {
      const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      
      if (link.download !== undefined) {
        const url = URL.createObjectURL(blob)
        link.setAttribute('href', url)
        link.setAttribute('download', filename)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
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

.badge {
  font-size: 0.75em;
}

.alert {
  margin-bottom: 0;
}

.form-check-input:disabled {
  opacity: 0.5;
}
</style>
