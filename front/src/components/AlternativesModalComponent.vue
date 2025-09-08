<template>
  <div v-if="show" class="alternatives-modal" :class="{ 'show': show }">
    <div class="modal-header">
      <h3>{{ currentVariable }} 대안 선택</h3>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>
    
    <div class="alternatives-list">
      <div 
        v-for="(alt, index) in currentAlternatives" 
        :key="index"
        class="alternative-item"
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
      <button class="btn-apply" @click="applySelectedAlternatives">
        선택한 대안 적용하기
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Alternative {
  text: string
  selected: boolean
}

interface AlternativesModalProps {
  show: boolean
  currentVariable: string
  alternatives: Alternative[]
}

const props = defineProps<AlternativesModalProps>()
const emit = defineEmits<{
  close: []
  apply: [alternative: Alternative]
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
const applySelectedAlternatives = () => {
  const selectedAlternative = currentAlternatives.value.find(alt => alt.selected)
  if (selectedAlternative) {
    emit('apply', selectedAlternative)
  }
}
</script>

<style scoped>
.alternatives-modal {
  position: absolute;
  top: 0;
  right: 0;
  width: 100%;
  height: 100%;
  background: white;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  z-index: 1001;
  overflow-y: auto;
  padding: 24px;
  border-radius: 16px;
  border: 1px solid #e0e0e0;
  transition: transform 0.3s ease-in-out;
  transform: translateX(100%);
}

.alternatives-modal.show {
  transform: translateX(0);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  color: #1a1a1a;
  font-size: 1.3rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-btn:hover {
  background: #f5f5f5;
}

.alternatives-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}

.alternative-item {
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
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
  top: 10px;
  right: 10px;
}

.selected-mark {
  color: #4caf50;
  font-weight: bold;
  font-size: 1.2rem;
}

.alternatives-actions {
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.btn-apply {
  width: 100%;
  background: #1976d2;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 6px;
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
</style>
