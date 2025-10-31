<template>
  <div class="category-tree">
    <!-- 虚拟分类节点 -->
    <div class="list-group list-group-flush">
      <a 
        href="#" 
        class="list-group-item list-group-item-action"
        :class="{ active: selectedCategory === null }"
        @click="$emit('category-selected', null)"
      >
        <strong>全部</strong>
        <span class="badge bg-secondary ms-2">{{ treeData?.count_all || 0 }}</span>
      </a>
      
      <a 
        href="#" 
        class="list-group-item list-group-item-action"
        :class="{ active: selectedCategory === -1 }"
        @click="$emit('category-selected', -1)"
      >
        <strong>未分类</strong>
        <span class="badge bg-secondary ms-2">{{ treeData?.count_uncat || 0 }}</span>
      </a>
      
      <a 
        href="#" 
        class="list-group-item list-group-item-action"
        :class="{ active: selectedCategory === -2 }"
        @click="$emit('category-selected', -2)"
      >
        <strong>最近使用</strong>
        <span class="badge bg-secondary ms-2">{{ treeData?.count_recent || 0 }}</span>
      </a>
    </div>
    
    <!-- 实际分类树 -->
    <div class="list-group list-group-flush mt-2">
      <CategoryNode
        v-for="category in treeData?.tree || []"
        :key="category.id"
        :category="category"
        :selected-category="selectedCategory"
        :current-user="currentUser"
        @category-selected="$emit('category-selected', $event)"
        @concept-dropped="$emit('concept-dropped', $event.conceptId, $event.categoryId)"
      />
    </div>
  </div>
</template>

<script>
import CategoryNode from './CategoryNode.vue'

export default {
  name: 'CategoryTree',
  components: {
    CategoryNode
  },
  props: {
    treeData: Object,
    selectedCategory: [Number, String],
    currentUser: Object
  },
  emits: ['category-selected', 'concept-dropped']
}
</script>

<style scoped>
.category-tree {
  max-height: 100%;
  overflow-y: auto;
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
</style>
