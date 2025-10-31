<template>
  <div class="categories-page">
    <div class="header-section">
      <div class="title-group">
        <h2>分类与概念管理</h2>
        <el-tag v-if="totalConcepts !== null" size="small" type="info" effect="plain">
          概念总数：{{ totalConcepts }}
        </el-tag>
      </div>
      <div class="header-actions">
        <el-button
          class="refresh-btn"
          circle
          :loading="loading"
          @click="loadData"
        >
          <el-icon><Refresh /></el-icon>
        </el-button>
        <el-button type="primary" @click="showAddModal = true">
          新增分类
        </el-button>
      </div>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <h5 class="mb-0">行业分类与概念</h5>
          <span class="card-subtitle">点击概念可跳转到编辑页面</span>
        </div>
      </template>

      <div v-if="loading" class="text-center p-4">
        <el-skeleton :rows="6" animated />
      </div>

      <div v-else-if="categoryTree.length === 0" class="empty-text">
        暂无分类或概念数据
      </div>

      <el-tree
        v-else
        :data="categoryTree"
        node-key="id"
        :props="treeProps"
        :expand-on-click-node="false"
        highlight-current
        class="category-tree"
      >
        <template #default="{ data }">
          <div
            class="tree-node"
            :class="{
              'tree-node--category': data.type === 'category',
              'tree-node--concept': data.type === 'concept',
              'tree-node--virtual': data.type === 'uncategorized'
            }"
          >
            <div class="node-main">
              <el-icon v-if="data.type === 'category'"><Folder /></el-icon>
              <el-icon v-else-if="data.type === 'concept'"><Document /></el-icon>
              <el-icon v-else><Folder /></el-icon>

              <span v-if="data.type !== 'concept'" class="node-label">{{ data.label }}</span>
              <router-link
                v-else
                :to="`/concept/${data.conceptId}/edit`"
                class="concept-link"
              >
                {{ data.label }}
              </router-link>

              <el-tag
                v-if="data.type === 'concept' && data.isExtra"
                size="small"
                type="info"
                effect="plain"
                class="extra-tag"
              >
                附加
              </el-tag>

              <el-tag
                v-if="data.type === 'category'"
                size="small"
                type="success"
                effect="plain"
                :title="`主分类概念 ${data.primaryCount} 个`"
              >
                共 {{ data.totalCount }} 个概念
              </el-tag>

              <el-tag
                v-else-if="data.type === 'uncategorized'"
                size="small"
                type="warning"
                effect="plain"
              >
                {{ data.totalCount }} 个概念
              </el-tag>
            </div>

            <div v-if="data.type === 'category'" class="node-actions">
              <el-button
                type="primary"
                link
                size="small"
                @click.stop="editCategory(data.categoryId)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                link
                size="small"
                @click.stop="confirmDeleteCategory(data)"
              >
                删除
              </el-button>
            </div>
          </div>
        </template>
      </el-tree>
    </el-card>

    <el-dialog
      v-model="showAddModal"
      title="新增分类"
      width="400px"
      @close="resetForm"
    >
      <el-form @submit.prevent="addCategory" label-position="top">
        <el-form-item label="分类名称" required>
          <el-input
            v-model="newCategoryForm.name"
            placeholder="请输入分类名称"
            clearable
          />
        </el-form-item>

        <el-form-item label="上级分类">
          <el-select
            v-model="newCategoryForm.parent_id"
            placeholder="请选择上级分类"
            clearable
          >
            <el-option label="顶级分类" :value="''" />
            <el-option
              v-for="category in flatCategories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddModal = false">取消</el-button>
        <el-button
          type="primary"
          :loading="adding"
          @click="addCategory"
        >
          {{ adding ? '添加中...' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Folder, Document, Refresh } from '@element-plus/icons-vue'
import axiosBase from 'axios'

const router = useRouter()

const axios = inject('$axios', axiosBase)

const categoryTree = ref([])
const flatCategories = ref([])
const loading = ref(false)
const adding = ref(false)
const showAddModal = ref(false)
const totalConcepts = ref(0)
const newCategoryForm = ref({
  name: '',
  parent_id: ''
})

const treeProps = {
  label: 'label',
  children: 'children'
}

const createConceptNode = (concept, categoryId) => ({
  id: `concept-${concept.id}-${categoryId ?? 'none'}${concept.is_extra ? '-extra' : '-main'}`,
  label: concept.term,
  type: 'concept',
  conceptId: concept.id,
  isExtra: Boolean(concept.is_extra),
  categoryId,
  children: []
})

const transformCategory = (category) => {
  const childCategories = (category.children || []).map(transformCategory)
  const conceptNodes = (category.concepts || []).map((concept) =>
    createConceptNode(concept, category.id)
  )

  return {
    id: `category-${category.id}`,
    label: category.name,
    name: category.name,
    type: 'category',
    categoryId: category.id,
    primaryCount: category.primary_count ?? 0,
    totalCount: category.total_count ?? conceptNodes.length,
    children: [...childCategories, ...conceptNodes]
  }
}

const buildTreeData = (treeResponse) => {
  if (!treeResponse) {
    return []
  }

  const categories = (treeResponse.tree || []).map(transformCategory)
  const uncategorizedConcepts = treeResponse.uncategorized || []

  if (uncategorizedConcepts.length > 0) {
    categories.push({
      id: 'uncategorized',
      label: '未分类概念',
      type: 'uncategorized',
      totalCount: uncategorizedConcepts.length,
      primaryCount: 0,
      children: uncategorizedConcepts.map((concept) =>
        createConceptNode(concept, null)
      )
    })
  }

  return categories
}

const loadData = async () => {
  loading.value = true
  try {
    const [treeRes, flatRes] = await Promise.all([
      axios.get('/categories/with-concepts'),
      axios.get('/categories/flat')
    ])

    categoryTree.value = buildTreeData(treeRes.data)
    totalConcepts.value = treeRes.data?.total_concepts ?? 0
    flatCategories.value = flatRes.data.items || []
  } catch (error) {
    console.error('加载分类和概念数据失败:', error)
    ElMessage.error(error?.response?.data?.error || '加载分类和概念数据失败')
  } finally {
    loading.value = false
  }
}

const addCategory = async () => {
  const name = newCategoryForm.value.name.trim()
  if (!name) {
    ElMessage.warning('请输入分类名称')
    return
  }

  adding.value = true
  try {
    await axios.post('/category', {
      name,
      parent_id: newCategoryForm.value.parent_id || null
    })
    ElMessage.success('分类添加成功')
    showAddModal.value = false
    await loadData()
  } catch (error) {
    console.error('添加分类失败:', error)
    ElMessage.error('添加分类失败')
  } finally {
    adding.value = false
  }
}

const resetForm = () => {
  newCategoryForm.value = { name: '', parent_id: '' }
}

const editCategory = (id) => {
  router.push(`/category/${id}/edit`)
}

const confirmDeleteCategory = (categoryNode) => {
  if (!categoryNode?.categoryId) {
    return
  }

  ElMessageBox.confirm(
    `确定删除分类 "${categoryNode.name}" 吗？此操作不可恢复。`,
    '删除确认',
    { type: 'warning' }
  )
    .then(() => deleteCategory(categoryNode.categoryId))
    .catch(() => {})
}

const deleteCategory = async (id) => {
  try {
    await axios.delete(`/category/${id}`)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {
    console.error('删除分类失败:', error)
    ElMessage.error('删除分类失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.categories-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.refresh-btn {
  border: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.card-subtitle {
  color: var(--el-text-color-secondary);
  font-size: 0.875rem;
}

.empty-text {
  text-align: center;
  color: var(--el-text-color-secondary);
  padding: 20px;
}

.category-tree {
  margin-top: 10px;
}

.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 12px;
}

.node-main {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.node-label {
  font-weight: 500;
}

.concept-link {
  color: var(--el-color-primary);
  text-decoration: none;
}

.concept-link:hover {
  text-decoration: underline;
}

.extra-tag {
  margin-left: 4px;
}

.node-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tree-node--concept .node-actions {
  display: none;
}

.tree-node--virtual .node-actions {
  display: none;
}

@media (max-width: 768px) {
  .tree-node {
    align-items: flex-start;
    flex-direction: column;
  }

  .node-actions {
    align-self: flex-end;
  }
}
</style>