<template>
  <div v-if="show" class="rejection-modal" :class="{ 'show': show }">
    <div class="modal-header">
      <h3>수정 반려 내용</h3>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>
    
    <div class="rejection-reason">
      <h4>• 반려 사유: 부적절한 언어</h4>
      <p>아래 하이라이트된 부분을 클릭하여 대체 단어/문장을 확인하세요.</p>
    </div>

    <div class="recommendations-list">
      <div 
        v-for="(rec, index) in recommendations" 
        :key="index"
        class="recommendation-item"
      >
        <div class="recommendation-content">
          <p class="placeholder-text">{{ rec.placeholder }}</p>
        </div>
        <div class="action-buttons">
          <button class="reject-btn-small" @click="rejectRecommendation(rec)">
            반려
          </button>
          <button class="approve-btn" @click="approveRecommendation(rec)">
            승인
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface RejectionModalProps {
  show: boolean
}

const props = defineProps<RejectionModalProps>()
const emit = defineEmits<{
  close: []
  approve: [rec: any]
  reject: [rec: any]
}>()

// 추천 데이터
const recommendations = ref([
  {
    placeholder: '이 영역을 어케 처리하지?',
    status: 'pending'
  }
])

// 추천 승인
const approveRecommendation = (rec: any) => {
  rec.status = 'approved'
  emit('approve', rec)
}

// 추천 반려
const rejectRecommendation = (rec: any) => {
  rec.status = 'rejected'
  emit('reject', rec)
}
</script>

<style scoped>
.rejection-modal {
  position: absolute;
  top: 0;
  right: 0;
  width: 100%;
  height: 100%;
  background: white;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  overflow-y: auto;
  padding: 24px;
  border-radius: 16px;
  border: 1px solid #e0e0e0;
  transition: transform 0.3s ease-in-out;
  transform: translateX(100%);
}

.rejection-modal.show {
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

.rejection-reason {
  margin-bottom: 20px;
  padding: 15px;
  background: #fff3e0;
  border-radius: 8px;
  border-left: 4px solid #ff9800;
}

.rejection-reason h4 {
  margin: 0 0 8px 0;
  color: #e65100;
  font-size: 1rem;
}

.rejection-reason p {
  margin: 0;
  color: #795548;
  font-size: 0.9rem;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.recommendation-item {
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.recommendation-item:hover {
  border-color: #1976d2;
  background: #f8f9fa;
}

.recommendation-content {
  margin-bottom: 12px;
}

.placeholder-text {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  font-style: italic;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.approve-btn {
  background: #4caf50;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.approve-btn:hover {
  background: #388e3c;
}

.reject-btn-small {
  background: #f44336;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.reject-btn-small:hover {
  background: #d32f2f;
}
</style>
