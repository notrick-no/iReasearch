<template>
  <div class="container py-3" style="max-width: 900px;">
    <!-- 顶部 -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold">{{ isEdit ? '编辑概念' : '新增概念' }}</h2>
      <div>
        <RouterLink to="/concepts" class="btn btn-outline-secondary me-2">返回</RouterLink>
        <el-button v-if="isEdit" type="danger" plain @click="confirmDelete">删除概念</el-button>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="text-center py-5">
      <el-icon class="is-loading" style="font-size:24px;"><loading /></el-icon>
    </div>

    <!-- 编辑内容（markdown风格，纵向排布） -->
    <form v-else class="markdown-style" @submit.prevent>
      <!-- 基本信息 -->
      <h3>概念术语</h3>
      <el-input v-model="form.term" placeholder="请输入概念术语" />

            <!-- 图片（即时预览 + 上传） -->
            <h3>概念图片</h3>
      <div class="mb-3">
        <img
          v-if="imagePreviewSrc"
          :src="imagePreviewSrc"
          :alt="form.term"
          class="img-fluid rounded"
          style="max-width:100%;height:auto;"
        />
        <div v-else class="text-muted">暂无图片</div>
      </div>
      <div class="d-flex gap-2">
        <el-upload
          :auto-upload="false"
          :show-file-list="false"
          accept="image/*"
          :on-change="onPickImage"
        >
          <el-button type="primary" :loading="uploading">选择图片</el-button>
        </el-upload>
        <el-button
          type="success"
          :disabled="!pickedFile || !isEdit"
          :loading="uploading"
          @click="uploadImage"
        >
          上传并保存
        </el-button>
        <span v-if="!isEdit" class="text-muted">（请先保存概念再上传图片）</span>
      </div>

      <h3>通俗解释</h3>
      <el-input
        v-model="form.plain_def"
        type="textarea"
        :autosize="{ minRows: 1 }"
        placeholder="请输入通俗解释…"
      />

      <h3>案例/例子</h3>
      <el-input
        v-model="form.examples"
        type="textarea"
        :autosize="{ minRows: 1 }"
        placeholder="请输入案例或例子…"
      />

      <h3>主分类</h3>
      <el-select v-model="form.category_id" placeholder="未分类" clearable filterable style="max-width: 360px;">
        <el-option :value="null" label="未分类" />
        <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>

      <h3> 附加分类</h3>
      <div class="d-flex gap-2 mb-2" style="max-width: 560px;">
        <el-select v-model="newExtraCategoryId" placeholder="选择分类" clearable filterable class="flex-fill">
          <el-option
            v-for="c in availableCategories"
            :key="c.id"
            :label="c.name"
            :value="c.id"
          />
        </el-select>
        <el-button type="primary" plain :disabled="!newExtraCategoryId" @click="addExtraCategory">添加</el-button>
      </div>
      <div class="d-flex flex-wrap gap-2 mb-4">
        <el-tag
          v-for="c in extraCategories"
          :key="c.id"
          closable
          @close="removeExtraCategory(c.id)"
        >{{ c.name }}</el-tag>
        <span v-if="extraCategories.length===0" class="text-muted">暂无附加分类</span>
      </div>



      <!-- 底部操作 -->
      <div class="text-end mt-4">
        <el-button type="primary" :loading="saving" @click="saveConcept">
          {{ saving ? '保存中…' : '保存' }}
        </el-button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const axios = inject('$axios')
const toast = inject('$toast')

const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)

const concept = ref(null)
const categories = ref([])
const extraCategories = ref([])
const newExtraCategoryId = ref('')

const form = reactive({
  term: '',
  plain_def: '',
  mechanism: '',
  examples: '',
  category_id: null
})

const isEdit = computed(() => !!route.params.id)

// —— 图片预览：优先显示本地预览；无则显示服务器图片；都没有则空
const pickedFile = ref(null)                  // File
const pickedPreviewUrl = ref('')              // createObjectURL
const serverImageSrc = computed(() =>
  concept.value?.image_path
    ? `/uploads/${concept.value.image_path.split('/').pop()}`
    : ''
)
const imagePreviewSrc = computed(() => pickedPreviewUrl.value || serverImageSrc.value)

const availableCategories = computed(() => {
  const mainId = form.category_id
  const extraIds = extraCategories.value.map(c => c.id)
  return categories.value.filter(c => c.id !== mainId && !extraIds.includes(c.id))
})

onMounted(async () => {
  await loadCategories()
  if (isEdit.value) await loadConcept()
})

async function loadCategories() {
  try {
    const { data } = await axios.get('/categories/flat')
    categories.value = data.items || []
  } catch (e) {
    console.error(e)
  }
}

async function loadConcept() {
  loading.value = true
  try {
    const { data } = await axios.get(`/concept/${route.params.id}`)
    concept.value = data
    extraCategories.value = data.extra_categories || []
    Object.assign(form, {
      term: data.term || '',
      plain_def: data.plain_def || '',
      mechanism: data.mechanism || '',
      examples: data.examples || '',
      category_id: data.category_id ?? null
    })
  } catch (e) {
    console.error('加载概念失败', e)
    toast?.error('加载概念失败')
    router.push('/concepts')
  } finally {
    loading.value = false
  }
}

async function saveConcept() {
  saving.value = true
  try {
    const payload = { ...form, extra_categories: extraCategories.value.map(c => c.id) }
    if (isEdit.value) {
      await axios.put(`/concept/${route.params.id}`, payload)
    } else {
      const { data } = await axios.post('/concept', payload)
      router.push(`/concept/${data.id}/edit`)
      return
    }
    toast?.success('保存成功')
  } catch (e) {
    console.error('保存失败', e)
    toast?.error('保存失败')
  } finally {
    saving.value = false
  }
}

function addExtraCategory() {
  if (!newExtraCategoryId.value) return
  const c = categories.value.find(x => x.id == newExtraCategoryId.value)
  if (c) {
    extraCategories.value.push(c)
    newExtraCategoryId.value = ''
  }
}

function removeExtraCategory(id) {
  extraCategories.value = extraCategories.value.filter(c => c.id !== id)
}

function confirmDelete() {
  if (!isEdit.value) return
  if (confirm(`确定删除概念「${form.term || ''}」吗？此操作不可恢复。`)) {
    deleteConcept()
  }
}

async function deleteConcept() {
  try {
    await axios.post('/concepts/bulk', { ids: [route.params.id], op: 'delete' })
    toast?.success('删除成功')
    router.push('/concepts')
  } catch (e) {
    console.error('删除失败', e)
    toast?.error('删除失败')
  }
}

// —— 选图：立即生成本地预览
function onPickImage(file) {
  const raw = file?.raw
  if (!raw) return
  if (!raw.type?.startsWith('image/')) {
    toast?.error('请选择图片文件')
    return
  }
  pickedFile.value = raw
  // 释放旧URL
  if (pickedPreviewUrl.value) URL.revokeObjectURL(pickedPreviewUrl.value)
  pickedPreviewUrl.value = URL.createObjectURL(raw)
}

// —— 上传图片：成功后切到服务器地址（仍保持“立即可见”的体验）
async function uploadImage() {
  if (!isEdit.value) {
    toast?.error('请先保存概念，再上传图片')
    return
  }
  if (!pickedFile.value) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('image', pickedFile.value)
    const { data } = await axios.post(`/concept/${route.params.id}/image`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    concept.value = concept.value || {}
    concept.value.image_path = data.image_path
    // 一旦后端返回了路径，可以（可选）释放本地URL，让预览指向服务端
    if (pickedPreviewUrl.value) {
      URL.revokeObjectURL(pickedPreviewUrl.value)
      pickedPreviewUrl.value = ''
    }
    toast?.success('图片上传成功')
  } catch (e) {
    console.error('上传失败', e)
    toast?.error('上传失败')
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
/* 复用“公司编辑页”的 markdown 风格 */
.markdown-style {
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.04);
  padding: 2rem 2rem 3rem;
  line-height: 1.7;
}
.markdown-style h3 {
  font-weight: 600;
  color: #334155;
  margin-top: 2rem;
  margin-bottom: 0.75rem;
}
.container { max-width: 900px; margin: 0 auto; }
</style>
