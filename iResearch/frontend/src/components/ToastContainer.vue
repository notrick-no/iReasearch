<template>
  <div class="toast-container position-fixed top-0 end-0 p-3">
    <div 
      v-for="toast in toasts" 
      :key="toast.id"
      class="toast show"
      :class="toast.type"
      role="alert"
    >
      <div class="toast-header">
        <i :class="getIconClass(toast.type)" class="me-2"></i>
        <strong class="me-auto">{{ getTitle(toast.type) }}</strong>
        <button 
          type="button" 
          class="btn-close" 
          @click="removeToast(toast.id)"
        ></button>
      </div>
      <div class="toast-body">
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ToastContainer',
  data() {
    return {
      toasts: [],
      nextId: 1
    }
  },
  methods: {
    show(message, type = 'info') {
      const toast = {
        id: this.nextId++,
        message,
        type: `alert-${type}`,
        timer: null
      }
      
      this.toasts.push(toast)
      
      // 自动移除
      toast.timer = setTimeout(() => {
        this.removeToast(toast.id)
      }, 3000)
    },
    
    removeToast(id) {
      const index = this.toasts.findIndex(t => t.id === id)
      if (index > -1) {
        const toast = this.toasts[index]
        if (toast.timer) {
          clearTimeout(toast.timer)
        }
        this.toasts.splice(index, 1)
      }
    },
    
    getIconClass(type) {
      const icons = {
        'alert-success': 'bi bi-check-circle-fill text-success',
        'alert-danger': 'bi bi-exclamation-triangle-fill text-danger',
        'alert-warning': 'bi bi-exclamation-triangle-fill text-warning',
        'alert-info': 'bi bi-info-circle-fill text-info'
      }
      return icons[type] || icons['alert-info']
    },
    
    getTitle(type) {
      const titles = {
        'alert-success': '成功',
        'alert-danger': '错误',
        'alert-warning': '警告',
        'alert-info': '提示'
      }
      return titles[type] || titles['alert-info']
    }
  },
  mounted() {
    // 将 toast 方法添加到全局
    this.$root.$toast = {
      success: (msg) => this.show(msg, 'success'),
      error: (msg) => this.show(msg, 'danger'),
      warning: (msg) => this.show(msg, 'warning'),
      info: (msg) => this.show(msg, 'info')
    }
  }
}
</script>

<style scoped>
.toast-container {
  z-index: 1055;
}

.toast {
  min-width: 300px;
}
</style>
