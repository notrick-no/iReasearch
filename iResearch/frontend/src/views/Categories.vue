<template>
  <div>
    <!-- 顶部标题和新增按钮 -->
    <div class="header-section">
      <h2>分类管理</h2>
      <el-button type="primary" @click="showAddModal = true">
        新增分类
      </el-button>
    </div>

    <!-- 分类树 -->
    <el-card>
      <template #header>
        <h5 class="mb-0">分类树结构</h5>
      </template>

      <div v-if="loading" class="text-center p-4">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="!categoryTree || categoryTree.length === 0" class="empty-text">
        暂无分类数据
      </div>

      <el-tree
        v-else
        :data="categoryTree"
        node-key="id"
        default-expand-all
        :props="{ label: 'name', children: 'children' }"
        class="category-tree"
      >
        <!-- 自定义节点内容 -->
        <template #default="{ node, data }">
          <span class="custom-node">
            {{ node.label }}
            <el-button
              type="primary"
              link
              size="small"
              @click.stop="editCategory(data.id)"
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
          </span>
        </template>
      </el-tree>
    </el-card>

    <!-- 新增分类对话框 -->
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const router = useRouter()

// 响应式数据
const categoryTree = ref([])
const flatCategories = ref([])
const loading = ref(false)
const adding = ref(false)
const showAddModal = ref(false)
const newCategoryForm = ref({
  name: '',
  parent_id: ''
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const [treeRes, flatRes] = await Promise.all([
      axios.get('/categories/tree'),
      axios.get('/categories/flat')
    ])
    categoryTree.value = treeRes.data.tree || []
    flatCategories.value = flatRes.data.items || []
  } catch (error) {
    console.error('加载分类数据失败:', error)
    ElMessage.error('加载分类数据失败')
  } finally {
    loading.value = false
  }
}

// 新增分类
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

// 重置表单
const resetForm = () => {
  newCategoryForm.value = { name: '', parent_id: '' }
}

// 编辑分类
const editCategory = (id) => {
  router.push(`/category/${id}/edit`)
}

// 删除分类
const confirmDeleteCategory = (category) => {
  ElMessageBox.confirm(
    `确定删除分类 "${category.name}" 吗？此操作不可恢复。`,
    '删除确认',
    { type: 'warning' }
  )
    .then(() => deleteCategory(category.id))
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

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.empty-text {
  text-align: center;
  color: var(--el-text-color-secondary);
  padding: 20px;
}

.category-tree {
  margin-top: 10px;
}

.custom-node {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}
</style>