<template>
  <div>
    <!-- 顶部标题和新增按钮 -->
    <div class="header-section">
      <h2>公司管理</h2>
      <el-button
        v-if="isEditorOrAdmin"
        type="primary"
        @click="goToNew"
      >
        新增公司
      </el-button>
    </div>

    <!-- 搜索与批量操作 -->
    <el-row :gutter="20" class="search-section">
      <el-col :span="12">
        <el-input
          v-model="searchQuery"
          placeholder="搜索公司名称或领域..."
          @keyup.enter="loadCompanies"
          clearable
        >
          <template #append>
            <el-button @click="loadCompanies">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
      </el-col>

      <el-col :span="6" v-if="isEditorOrAdmin">
        <el-button
          type="danger"
          size="default"
          :disabled="selectedCompanies.length === 0"
          @click="confirmBulkDelete"
        >
          批量删除 ({{ selectedCompanies.length }})
        </el-button>
      </el-col>
    </el-row>

    <!-- 公司列表 -->
    <el-card class="mt-4" shadow="never">
      <el-table
        v-loading="loading"
        :data="companies"
        style="width: 100%"
        :row-key="row => row.id"
        @selection-change="handleSelectionChange"
        empty-text="暂无公司数据"
        >
        <el-table-column
          v-if="isEditorOrAdmin"
          type="selection"
          width="55"
        />

        <el-table-column prop="name" label="公司名称" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="goToEdit(row.id)">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="field" label="所属领域" min-width="150">
          <template #default="{ row }">
            {{ row.field || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              link
              @click="goToEdit(row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-if="isEditorOrAdmin"
              size="small"
              type="danger"
              link
              @click="confirmDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 分页 -->
    <div class="pagination-section" v-if="totalPages > 1">
      <span class="total-text">共 {{ total }} 条记录</span>
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        :page-sizes="[50]"
        @size-change="handlePageSizeChange"
        @current-change="loadCompanies"
        small
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

// 响应式数据
const companies = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(50)
const total = ref(0)
const searchQuery = ref('')
const selectedCompanies = ref([])

// 当前用户（从 localStorage 获取）
const currentUser = JSON.parse(localStorage.getItem('user') || '{}')

// 计算属性
const isEditorOrAdmin = computed(() => {
  return ['admin', 'editor'].includes(currentUser.role)
})

const totalPages = computed(() => {
  return Math.ceil(total.value / pageSize.value)
})

// 方法
const loadCompanies = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchQuery.value.trim()) {
      params.q = searchQuery.value.trim()
    }

    const response = await axios.get('/companies', { params })
    companies.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error('加载公司列表失败:', error)
    ElMessage.error('加载公司列表失败')
  } finally {
    loading.value = false
  }
}

const goToNew = () => {
  router.push('/company/new')
}

const goToEdit = (id) => {
  router.push(`/company/${id}/edit`)
}

const handleSelectionChange = (selection) => {
  selectedCompanies.value = selection.map(item => item.id)
}

const confirmDelete = (company) => {
  ElMessageBox.confirm(
    `确定删除公司 "${company.name}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }
  )
    .then(() => deleteCompany(company.id))
    .catch(() => {})
}

const deleteCompany = async (companyId) => {
  try {
    await axios.delete(`/company/${companyId}`)
    ElMessage.success('删除成功')
    await loadCompanies()
  } catch (error) {
    console.error('删除公司失败:', error)
    ElMessage.error('删除公司失败')
  }
}

const confirmBulkDelete = () => {
  if (selectedCompanies.value.length === 0) {
    ElMessage.warning('请选择要删除的公司')
    return
  }

  ElMessageBox.confirm(
    `确定删除选中的 ${selectedCompanies.value.length} 家公司吗？此操作不可恢复。`,
    '批量删除确认',
    {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }
  )
    .then(() => performBulkDelete())
    .catch(() => {})
}

const performBulkDelete = async () => {
  try {
    await axios.post('/companies/bulk', {
      ids: selectedCompanies.value,
      op: 'delete'
    })
    ElMessage.success('批量删除成功')
    selectedCompanies.value = []
    await loadCompanies()
  } catch (error) {
    console.error('批量删除失败:', error)
    ElMessage.error('批量删除失败')
  }
}

const handlePageSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadCompanies()
}

// 初始化加载
onMounted(() => {
  loadCompanies()
})
</script>

<style scoped>
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-section {
  margin-bottom: 20px;
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.total-text {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.mt-4 {
  margin-top: 20px;
}
</style>