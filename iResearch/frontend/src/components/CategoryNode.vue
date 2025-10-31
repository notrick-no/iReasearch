<template>
  <div class="category-node">
    <a 
      href="#" 
      class="list-group-item list-group-item-action d-flex align-items-center"
      :class="{ active: selectedCategory === category.id }"
      @click="$emit('category-selected', category.id)"
      @dragover.prevent
      @drop.prevent="onDrop"
    >
      <!-- 展开/折叠按钮 -->
      <span 
        v-if="category.children && category.children.length > 0"
        class="me-2"
        @click.stop="toggleExpanded"
      >
        <i :class="expanded ? 'bi bi-chevron-down' : 'bi bi-chevron-right'"></i>
      </span>
      <span v-else class="me-2" style="width: 16px;"></span>
      
      <!-- 分类名称和计数 -->
      <span class="flex-grow-1">{{ category.name }}</span>
      <span class="badge bg-secondary ms-2">{{ category.count_main || 0 }}</span>
    </a>
    
    <!-- 子分类 -->
    <div v-if="expanded && category.children && category.children.length > 0" class="ms-3">
      <CategoryNode
        v-for="child in category.children"
        :key="child.id"
        :category="child"
        :selected-category="selectedCategory"
        :current-user="currentUser"
        @category-selected="$emit('category-selected', $event)"
        @concept-dropped="$emit('concept-dropped', $event.conceptId, $event.categoryId)"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'CategoryNode',
  props: {
    category: Object,
    selectedCategory: [Number, String],
    currentUser: Object
  },
  emits: ['category-selected', 'concept-dropped'],
  data() {
    return {
      expanded: true // 默认展开
    }
  },
  methods: {
    toggleExpanded() {
      this.expanded = !this.expanded
    },
    
    onDrop(event) {
      // 只有编辑和管理员可以拖拽
      if (!['admin', 'editor'].includes(this.currentUser.role)) {
        return
      }
      
      const conceptId = event.dataTransfer.getData('text/plain')
      if (conceptId) {
        this.$emit('concept-dropped', {
          conceptId: parseInt(conceptId),
          categoryId: this.category.id
        })
      }
    }
  }
}
</script>

<style scoped>
.category-node {
  position: relative;
}

.list-group-item {
  border-left: none;
  border-right: none;
  cursor: pointer;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.list-group-item.active {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.badge {
  font-size: 0.75em;
}

/* 拖拽目标样式 */
.list-group-item {
  transition: background-color 0.2s;
}

.list-group-item.drag-over {
  background-color: #e3f2fd !important;
  border-color: #2196f3 !important;
}
</style>
