<template>
  <div v-if="show" class="rejection-sidebar">
    <div class="sidebar-header">
      <h3>반려 사유 및 대안</h3>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>
    
    <!-- 반려 사유 -->
    <div class="rejection-reason" v-if="currentVariable">
      <h4>• 반려 사유: 부적절한 언어</h4>
      <p>변수 "<strong>{{ currentVariable }}</strong>"에 대한 대안을 선택하세요.</p>
    </div>
    
    <!-- 대안 목록 -->
    <div class="alternatives-section" v-if="currentVariable">
      <h4>대안 선택</h4>
      <div class="alternatives-list">
        <div 
          v-for="(alt, index) in currentAlternatives" 
          :key="index"
          :class="['alternative-item', { 'selected': alt.selected }]"
          @click="selectAlternative(alt)"
        >
          <div class="alternative-content">
            <p>{{ alt.text }}</p>
          </div>
          <div class="alternative-status">
            <span v-if="alt.selected" class="selected-mark">✓</span>
          </div>
        </div>
      </div>
      
      <div class="alternatives-actions">
        <button class="btn-apply" @click="applySelectedAlternative">
          선택한 대안 적용하기
        </button>
      </div>
    </div>
    
    <!-- 반려된 모든 항목 요약 -->
    <div class="rejected-summary" v-if="!currentVariable">
      <h4>반려된 항목들</h4>
      <div class="rejected-items">
        <div 
          v-for="variable in rejectedVariables" 
          :key="variable"
          class="rejected-item"
          @click="$emit('variableClick', variable)"
        >
          <span class="variable-name">{{ variable }}</span>
          <span class="click-hint">클릭하여 대안 확인</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Alternative {
  text: string
  selected: boolean
}

interface RejectionSidebarProps {
  show: boolean
  currentVariable: string
  alternatives: Alternative[]
  rejectedVariables: string[]
}

const props = defineProps<RejectionSidebarProps>()
const emit = defineEmits<{
  close: []
  variableClick: [variableName: string]
  applyAlternative: [alternative: Alternative]
}>()

const currentAlternatives = ref<Alternative[]>([])

watch(() => props.alternatives, (newAlternatives) => {
  currentAlternatives.value = JSON.parse(JSON.stringify(newAlternatives))
}, { immediate: true })

// 대안 선택
const selectAlternative = (alternative: Alternative) => {
  // 다른 대안들의 선택 해제
  currentAlternatives.value.forEach(alt => {
    if (alt !== alternative) {
      alt.selected = false
    }
  })
  // 현재 대안 선택/해제
  alternative.selected = !alternative.selected
}

// 선택한 대안 적용
const applySelectedAlternative = () => {
  const selectedAlternative = currentAlternatives.value.find(alt => alt.selected)
  if (selectedAlternative) {
    emit('applyAlternative', selectedAlternative)
  }
}
</script>

<style scoped>
.rejection-sidebar {
  width: 20rem;
  min-width: 20rem;
  height: auto;
  background: white;
  border-radius: 0.6rem;
  padding: 1rem;
  box-shadow: 0 0.1rem 0.4rem rgba(0, 0, 0, 0.1);
  border: 0.05rem solid #e0e0e0;
  overflow-y: auto;
  align-self: center;
  flex-shrink: 0;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
  padding-bottom: 0.6rem;
  border-bottom: 0.1rem solid #e0e0e0;
}

.sidebar-header h3 {
  margin: 0;
  color: #1a1a1a;
  font-size: 1.1rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-btn:hover {
  background: #f5f5f5;
}

.rejection-reason {
  margin-bottom: 0.8rem;
  padding: 0.6rem;
  background: #fff3e0;
  border-radius: 0.4rem;
  border-left: 0.2rem solid #ff9800;
}

.rejection-reason h4 {
  margin: 0 0 0.3rem 0;
  color: #e65100;
  font-size: 0.9rem;
}

.rejection-reason p {
  margin: 0;
  color: #795548;
  font-size: 0.8rem;
}

.alternatives-section {
  margin-bottom: 0.8rem;
}

.alternatives-section h4 {
  margin: 0 0 0.6rem 0;
  color: #333;
  font-size: 0.9rem;
}

.alternatives-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 0.8rem;
}

.alternative-item {
  padding: 0.5rem;
  border: 0.1rem solid #e0e0e0;
  border-radius: 0.4rem;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.alternative-item:hover {
  border-color: #1976d2;
  background: #f8f9fa;
}

.alternative-item.selected {
  border-color: #4caf50;
  background: #e8f5e8;
}

.alternative-content p {
  margin: 0;
  color: #333;
  font-size: 0.95rem;
}

.alternative-status {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
}

.selected-mark {
  color: #4caf50;
  font-weight: bold;
  font-size: 1.2rem;
}

.alternatives-actions {
  padding-top: 0.6rem;
  border-top: 0.05rem solid #e0e0e0;
}

.btn-apply {
  width: 100%;
  background: #1976d2;
  color: white;
  border: none;
  padding: 0.6rem;
  border-radius: 0.3rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-apply:hover {
  background: #1565c0;
}

.btn-apply:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.rejected-summary {
  margin-top: 0.8rem;
}

.rejected-summary h4 {
  margin: 0 0 0.6rem 0;
  color: #333;
  font-size: 0.9rem;
}

.rejected-items {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.rejected-item {
  padding: 0.5rem;
  border: 0.1rem solid #ffebee;
  border-radius: 0.4rem;
  background: #fff5f5;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rejected-item:hover {
  border-color: #f44336;
  background: #ffebee;
}

.variable-name {
  font-weight: 500;
  color: #c62828;
}

.click-hint {
  font-size: 0.8rem;
  color: #666;
  font-style: italic;
}
</style>
