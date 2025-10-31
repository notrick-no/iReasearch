<template>
  <div>
    <h2 class="mb-4">仪表盘</h2>
    
    <!-- 统计卡片 -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h4>{{ stats.companies }}</h4>
                <p class="mb-0">公司总数</p>
              </div>
              <div class="align-self-center">
                <i class="bi bi-building" style="font-size: 2rem;"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card bg-success text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h4>{{ stats.concepts }}</h4>
                <p class="mb-0">概念总数</p>
              </div>
              <div class="align-self-center">
                <i class="bi bi-lightbulb" style="font-size: 2rem;"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card bg-info text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h4>{{ stats.categories }}</h4>
                <p class="mb-0">分类总数</p>
              </div>
              <div class="align-self-center">
                <i class="bi bi-tags" style="font-size: 2rem;"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card bg-warning text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h4>{{ stats.users }}</h4>
                <p class="mb-0">用户总数</p>
              </div>
              <div class="align-self-center">
                <i class="bi bi-people" style="font-size: 2rem;"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 最近公司 -->
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">最近新增的公司</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">加载中...</span>
              </div>
            </div>
            
            <div v-else-if="recentCompanies.length === 0" class="text-muted text-center">
              暂无数据
            </div>
            
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <!-- <th>ID</th> -->
                    <th>公司名称</th>
                    <th>所属领域</th>
                    <th>创建时间</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="company in recentCompanies" :key="company.id">
                    <!-- <td>{{ company.id }}</td> -->
                    <td>
                      <router-link 
                        :to="`/company/${company.id}/edit`" 
                        class="text-decoration-none"
                      >
                        {{ company.name }}
                      </router-link>
                    </td>
                    <td>{{ company.field || '-' }}</td>
                    <td>{{ company.created_at }}</td>
                    <td>
                      <router-link 
                        :to="`/company/${company.id}/edit`" 
                        class="btn btn-sm btn-outline-primary"
                      >
                        查看
                      </router-link>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      stats: {
        companies: 0,
        concepts: 0,
        categories: 0,
        users: 0
      },
      recentCompanies: [],
      loading: true
    }
  },
  async mounted() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      
      try {
        // 并行加载数据
        const [companiesRes, conceptsRes, categoriesRes, usersRes] = await Promise.all([
          this.$axios.get('/companies?page_size=1'),
          this.$axios.get('/concepts?page_size=1'),
          this.$axios.get('/categories/flat'),
          this.$axios.get('/users')
        ])
        
        // 更新统计信息
        this.stats.companies = companiesRes.data.total
        this.stats.concepts = conceptsRes.data.total
        this.stats.categories = categoriesRes.data.items.length
        this.stats.users = usersRes.data.items.length
        
        // 加载最近公司
        const recentRes = await this.$axios.get('/companies?page_size=10')
        this.recentCompanies = recentRes.data.items
        
      } catch (error) {
        console.error('加载仪表盘数据失败:', error)
        this.$toast?.error('加载数据失败')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

.table-responsive {
  max-height: 400px;
  overflow-y: auto;
}
</style>
