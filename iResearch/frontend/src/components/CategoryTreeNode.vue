<template>
  <div class="category-tree-node">
    <div class="d-flex align-items-center mb-2">
      <span class="me-2">
        <i :class="expanded ? 'bi bi-chevron-down' : 'bi bi-chevron-right'"></i>
      </span>
      
      <div class="flex-grow-1 d-flex align-items-center">
        <span class="me-2">{{ category.name }}</span>
        <span class="badge bg-secondary me-2">{{ category.count_main || 0 }}</span>
        
        <div class="btn-group btn-group-sm">
          <button 
            class="btn btn-outline-primary"
            @click="$emit('edit-category', category.id)"
          >
            编辑
          </button>
          <button 
            class="btn btn-outline-danger"
            @click="$emit('delete-category', category)"
          >
            删除
          </button>
        </div>
      </div>
    </div>
    
    <!-- 子分类 -->
    <div v-if="expanded && category.children && category.children.length > 0" class="ms-4">
      <CategoryTreeNode
        v-for="child in category.children"
        :key="child.id"
        :category="child"
        @edit-category="$emit('edit-category', $event)"
        @delete-category="$emit('delete-category', $event)"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'CategoryTreeNode',
  props: {
    category: Object
  },
  emits: ['edit-category', 'delete-category'],
  data() {
    return {
      expanded: true
    }
  },
  methods: {
    toggleExpanded() {
      this.expanded = !this.expanded
    }
  }
}
</script>

<style scoped>
.category-tree-node {
  margin-bottom: 0.5rem;
}

.badge {
  font-size: 0.75em;
}

.btn-group-sm > .btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}
</style>
