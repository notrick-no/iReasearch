<template>
  <div class="container py-3" style="max-width: 900px;">
    <!-- 顶部 -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold">{{ isEdit ? '编辑公司' : '新增公司' }}</h2>
      <div>
        <RouterLink to="/companies" class="btn btn-outline-secondary me-2">返回</RouterLink>
        <button
          v-if="isEdit && isEditorOrAdmin"
          class="btn btn-outline-danger"
          @click="confirmDelete"
        >删除公司</button>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" role="status"></div>
    </div>

    <!-- 编辑内容 -->
    <form v-else @submit.prevent="saveCompany" class="markdown-style">
      <!-- 关联概念 -->
      <h3>🔗 关联概念</h3>
      <div v-if="!isViewer" class="input-group mb-3" style="max-width: 400px;">
        <input
          v-model="newConceptTerm"
          type="text"
          class="form-control"
          placeholder="输入概念术语..."
          @keyup.enter="addConcept"
        />
        <button
          class="btn btn-outline-primary"
          :disabled="!newConceptTerm.trim()"
          type="button"
          @click="addConcept"
        >
          添加
        </button>
      </div>
      <div class="d-flex flex-wrap gap-2 mb-4">
        <span
          v-for="c in concepts"
          :key="c.id"
          class="badge bg-primary d-flex align-items-center"
          style="cursor: pointer"
        >
          <router-link
            :to="`/concept/${c.id}/edit`"
            class="text-white text-decoration-none me-1"
            style="flex: 1"
          >
            {{ c.term }}
          </router-link>
          <button
            v-if="!isViewer"
            type="button"
            class="btn-close btn-close-white"
            style="font-size:0.6rem"
            @click.stop="removeConcept(c.id)"
          ></button>
        </span>
      </div>


      <!-- 备注 -->
      <h3>📝 备注</h3>
      <textarea
        v-model="form.notes"
        rows="1"
        class="form-control mb-4"
        placeholder="可输入长描述..."
        :disabled="isViewer"
        v-autoresize
      ></textarea>

      <!-- 基本信息 -->
      <h3>🏢 公司信息</h3>
      <p><strong>公司名称：</strong>
        <input v-model="form.name" class="input-line" :disabled="isViewer" />
      </p>
      <p><strong>官网：</strong>
        <input v-model="form.website" class="input-line" :disabled="isViewer" />
      </p>
      <p><strong>地址：</strong>
        <input v-model="form.address" class="input-line" :disabled="isViewer" />
      </p>
      <p><strong>所属领域：</strong>
        <input v-model="form.field" class="input-line" :disabled="isViewer" />
      </p>

      <!-- 团队与融资 -->
      <h3>👥 团队与融资</h3>
      <textarea v-model="form.team_info" rows="3" class="form-control mb-3" :disabled="isViewer" v-autoresize></textarea>
      <textarea v-model="form.funding_info" rows="3" class="form-control mb-4" :disabled="isViewer" v-autoresize></textarea>

      <!-- 产品与模式 -->
      <h3>💡 产品与模式</h3>
      <textarea v-model="form.product" rows="3" class="form-control mb-3" :disabled="isViewer" v-autoresize></textarea>
      <textarea v-model="form.biz_model" rows="3" class="form-control mb-4" :disabled="isViewer" v-autoresize></textarea>

      <!-- 技术核心 -->
      <h3>⚙️ 技术核心与差异化</h3>
      <textarea v-model="form.tech_core" rows="3" class="form-control mb-3" :disabled="isViewer" v-autoresize></textarea>
      <textarea v-model="form.difference" rows="3" class="form-control mb-4" :disabled="isViewer" v-autoresize></textarea>

      <!-- 合作伙伴 -->
      <h3>🤝 合作与客户</h3>
      <textarea v-model="form.partners" rows="3" class="form-control mb-3" :disabled="isViewer" v-autoresize></textarea>
      <textarea v-model="form.clients" rows="3" class="form-control mb-4" :disabled="isViewer" v-autoresize></textarea>

      <!-- 来源 -->
      <h3>🔗 来源</h3>
      <input
        v-model="form.source_link"
        class="form-control mb-4"
        type="url"
        placeholder="来源链接"
        :disabled="isViewer"
      />

      <div v-if="!isViewer" class="text-end mt-4">
        <button type="submit" class="btn btn-primary" :disabled="saving">
          <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const axios = inject('$axios')
const toast = inject('$toast')

const loading = ref(false)
const saving = ref(false)
const concepts = ref([])
const newConceptTerm = ref('')

<<<<<<< HEAD
const notesTextarea = ref(null)

function autoResize() {
  const el = notesTextarea.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

=======
>>>>>>> codex
const form = reactive({
  name: '', website: '', address: '', field: '',
  team_info: '', funding_info: '',
  product: '', biz_model: '',
  tech_core: '', difference: '',
  partners: '', clients: '',
  notes: '', source_link: ''
})

const currentUser = reactive(JSON.parse(localStorage.getItem('user') || '{}'))
const isEdit = computed(() => !!route.params.id)
const isViewer = computed(() => currentUser.role === 'viewer')
const isEditorOrAdmin = computed(() => ['admin', 'editor'].includes(currentUser.role))

onMounted(() => { if (isEdit.value) loadCompany() })

async function loadCompany() {
  loading.value = true
  try {
    const { data } = await axios.get(`/company/${route.params.id}`)
    Object.assign(form, data)
    concepts.value = data.concepts || []
    loading.value = false
  } catch {
    toast?.error('加载公司失败')
    router.push('/companies')
  } finally {
    loading.value = false
  }
}

async function saveCompany() {
  if (isViewer.value) return
  saving.value = true
  try {
    if (isEdit.value) await axios.put(`/company/${route.params.id}`, form)
    else {
      const { data } = await axios.post('/company', form)
      router.push(`/company/${data.id}/edit`)
      return
    }
    toast?.success('保存成功')
  } catch {
    toast?.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function addConcept() {
  if (!newConceptTerm.value.trim()) return
  try {
    await axios.post(`/company/${route.params.id}/concepts`, { term: newConceptTerm.value.trim() })
    newConceptTerm.value = ''
    await loadCompany()
    toast?.success('添加成功')
  } catch {
    toast?.error('添加失败')
  }
}

async function removeConcept(id) {
  try {
    await axios.delete(`/company/${route.params.id}/concepts/${id}`)
    concepts.value = concepts.value.filter(c => c.id !== id)
  } catch {
    toast?.error('删除失败')
  }
}

function confirmDelete() {
  if (confirm(`确定删除公司「${form.name}」吗？`)) deleteCompany()
}

async function deleteCompany() {
  try {
    await axios.delete(`/company/${route.params.id}`)
    toast?.success('删除成功')
    router.push('/companies')
  } catch {
    toast?.error('删除公司失败')
  }
}
</script>

<style>
body {
  background: linear-gradient(180deg, #f8f9fb 0%, #eef1f4 100%);
  font-family: "Inter", "Noto Sans SC", system-ui, sans-serif;
  color: #334155;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.card.markdown-style {
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
  padding: 2rem 2rem 3rem;
  line-height: 1.7;
  transition: box-shadow 0.2s ease;
}

.card.markdown-style:hover {
  box-shadow: 0 6px 28px rgba(0, 0, 0, 0.07);
}

.markdown-style h2 {
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 1.5rem;
}

.markdown-style h3 {
  font-weight: 600;
  color: #334155;
  margin-top: 2rem;
  margin-bottom: 0.75rem;
}

.markdown-style p {
  margin-bottom: 0.8rem;
  font-size: 15.5px;
}

.input-line {
  border: none;
  border-bottom: 1px solid #cbd5e1;
  width: 70%;
  background: transparent;
  padding: 2px 4px;
  outline: none;
  transition: border-color 0.2s ease;
}
.input-line:focus {
  border-color: #3b82f6;
}

textarea.form-control {
  background: #f9fafb;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 15px;
  padding: 0.75rem;
  transition: border-color 0.2s ease;
}
textarea.form-control:focus {
  border-color: #3b82f6;
  background: #fff;
}

button.btn-primary {
  background: #3b82f6;
  border-color: #3b82f6;
}
button.btn-primary:hover {
  background: #2563eb;
  border-color: #2563eb;
}

.badge {
  background: #2563eb !important;
  font-weight: 500;
}

hr {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 2rem 0;
}
</style>
