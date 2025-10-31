<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>上传JSON</h2>
    </div>
    
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">批量导入数据</h5>
          </div>
          <div class="card-body">
            <div class="mb-4">
              <h6>JSON格式说明：</h6>
              <p class="text-muted">
                请上传包含公司数据的JSON文件，格式如下：
              </p>
              <pre class="bg-light p-3 rounded"><code>[
  {
    "company_name": "公司A",
    "website": "https://example.com",
    "address": "地址信息",
    "team_info": "团队信息",
    "funding_info": "融资信息",
    "product_service": "产品服务",
    "biz_model": "商业模式",
    "partners": "合作伙伴",
    "clients": "客户信息",
    "field": "所属领域",
    "detail": "详细备注",
    "source": "来源链接",
    "explain": {
      "概念术语1": "该概念的通俗解释...",
      "概念术语2": "概念2的解释..."
    }
  }
]</code></pre>
            </div>
            
            <form @submit.prevent="uploadFile">
              <div class="mb-3">
                <label class="form-label">选择JSON文件</label>
                <input 
                  type="file" 
                  class="form-control" 
                  accept=".json"
                  @change="onFileSelected"
                  ref="fileInput"
                >
                <div class="form-text">
                  支持.json格式文件，文件大小不超过5MB
                </div>
              </div>
              
              <div v-if="selectedFile" class="mb-3">
                <div class="alert alert-info">
                  <i class="bi bi-file-earmark-text me-2"></i>
                  已选择文件：{{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
                </div>
              </div>
              
              <div class="d-grid">
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="!selectedFile || uploading"
                >
                  <span v-if="uploading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ uploading ? '上传中...' : '开始上传' }}
                </button>
              </div>
            </form>
            
            <!-- 上传进度 -->
            <div v-if="uploading" class="mt-4">
              <div class="progress">
                <div 
                  class="progress-bar" 
                  :style="{ width: uploadProgress + '%' }"
                ></div>
              </div>
              <div class="text-center mt-2">
                <small class="text-muted">上传进度：{{ uploadProgress }}%</small>
              </div>
            </div>
            
            <!-- 上传结果 -->
            <div v-if="uploadResult" class="mt-4">
              <div class="alert" :class="uploadResult.success ? 'alert-success' : 'alert-danger'">
                <h6>{{ uploadResult.success ? '上传成功' : '上传失败' }}</h6>
                <div v-if="uploadResult.success">
                  <p>成功导入 {{ uploadResult.companies_added }} 家公司</p>
                  <p>成功导入 {{ uploadResult.concepts_added }} 个概念</p>
                  <div v-if="uploadResult.errors && uploadResult.errors.length > 0">
                    <p>错误信息：</p>
                    <ul class="mb-0">
                      <li v-for="error in uploadResult.errors" :key="error">{{ error }}</li>
                    </ul>
                  </div>
                </div>
                <div v-else>
                  <p>{{ uploadResult.error }}</p>
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
  name: 'Upload',
  data() {
    return {
      selectedFile: null,
      uploading: false,
      uploadProgress: 0,
      uploadResult: null
    }
  },
  methods: {
    onFileSelected(event) {
      const file = event.target.files[0]
      
      if (!file) {
        this.selectedFile = null
        return
      }
      
      // 检查文件类型
      if (!file.name.toLowerCase().endsWith('.json')) {
        this.$toast?.error('请选择JSON格式文件')
        this.$refs.fileInput.value = ''
        return
      }
      
      // 检查文件大小（5MB限制）
      if (file.size > 5 * 1024 * 1024) {
        this.$toast?.error('文件大小不能超过5MB')
        this.$refs.fileInput.value = ''
        return
      }
      
      this.selectedFile = file
      this.uploadResult = null
    },
    
    async uploadFile() {
      if (!this.selectedFile) {
        this.$toast?.warning('请选择要上传的文件')
        return
      }
      
      this.uploading = true
      this.uploadProgress = 0
      this.uploadResult = null
      
      try {
        const formData = new FormData()
        formData.append('file', this.selectedFile)
        
        const response = await this.$axios.post('/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            this.uploadProgress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
          }
        })
        
        this.uploadResult = {
          success: true,
          ...response.data
        }
        
        this.$toast?.success('上传完成')
        
      } catch (error) {
        console.error('上传失败:', error)
        
        this.uploadResult = {
          success: false,
          error: error.response?.data?.error || '上传失败'
        }
        
        this.$toast?.error('上传失败')
        
      } finally {
        this.uploading = false
        this.uploadProgress = 0
      }
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
  }
}
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

pre {
  font-size: 0.875rem;
  max-height: 300px;
  overflow-y: auto;
}

.progress {
  height: 1rem;
}

.alert ul {
  margin-bottom: 0;
}

.form-text {
  font-size: 0.875rem;
  color: #6c757d;
}
</style>
