<template>
  <div class="template-create-container">
    <!-- 헤더 컴포넌트 -->
    <HeaderComponent />
    
    <!-- 메인 콘텐츠 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 제목 -->
        <div class="header-section">
          <h1 class="page-title">
            만들고 싶은 알림톡 템플릿 주제를 알려주세요
          </h1>
        </div>
        
        <!-- 카테고리 버튼들 -->
        <div class="category-section">
          <div class="category-grid">
            <button
              v-for="category in categories"
              :key="category.id"
              :class="['category-btn', { 'selected': selectedCategory === category.id }]"
              @click="selectCategory(category.id)"
            >
              {{ category.name }}
            </button>
          </div>
        </div>
        
        <!-- 텍스트 입력 영역 -->
        <div class="text-input-section">
          <div class="textarea-container">
            <textarea
              v-model="messageText"
              placeholder="ex. 우리 서비스에 맞는 법적 고지 내용을 빠르게 작성하고 적용할 수 있는 템플릿이 필요합니다."
              class="message-textarea"
              rows="8"
            ></textarea>
            <button class="submit-arrow-btn" @click="handleSubmit" :disabled="!canSubmit">
              ↑
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import HeaderComponent from '@/components/HeaderComponent.vue'

const router = useRouter()

// 카테고리 데이터
const categories = [
  { id: 1, name: '공지사항' },
  { id: 2, name: '이벤트' },
  { id: 3, name: '안내' },
  { id: 4, name: '마케팅' },
  { id: 5, name: '고객서비스' },
  { id: 6, name: '주문확인' },
  { id: 7, name: '배송안내' },
  { id: 8, name: '결제완료' },
  { id: 9, name: '예약확정' },
  { id: 10, name: '취소안내' },
  { id: 11, name: '기타' },
  { id: 12, name: '없음' }
]

const selectedCategory = ref<number | null>(null)
const messageText = ref('')

// 제출 가능 여부
const canSubmit = computed(() => {
  return selectedCategory.value !== null && messageText.value.trim().length > 0
})

// 카테고리 선택
const selectCategory = (categoryId: number) => {
  selectedCategory.value = selectedCategory.value === categoryId ? null : categoryId
}

// 제출 처리
const handleSubmit = async () => {
  if (!canSubmit.value) return
  
  try {
    // TODO: 템플릿 생성 로직 구현
    console.log('템플릿 생성:', {
      category: selectedCategory.value,
      message: messageText.value
    })
    
    // 결과 페이지로 이동
    router.push('/template/result')
  } catch (error) {
    console.error('템플릿 생성 실패:', error)
  }
}
</script>

<style scoped>
.template-create-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #E3F2FD 0%, #F1F8E9 100%);
}

.main-content {
  flex: 1;
  padding: 2rem 0;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header-section {
  text-align: center;
  margin-bottom: 3rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 0.8rem;
  line-height: 1.3;
}

.category-section {
  width: 100%;
  margin-bottom: 3rem;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 1rem;
  max-width: 800px;
  margin: 0 auto;
}

.category-btn {
  height: 3rem;
  font-size: 1rem;
  font-weight: 500;
  border: none;
  background: #8E24AA;
  color: white;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(142, 36, 170, 0.2);
}

.category-btn:hover {
  background: #7B1FA2;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(142, 36, 170, 0.3);
}

.category-btn.selected {
  background: #4A148C;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(74, 20, 140, 0.4);
}

.text-input-section {
  width: 100%;
  max-width: 800px;
}

.textarea-container {
  position: relative;
}

.message-textarea {
  width: 100%;
  min-height: 12rem;
  padding: 1.5rem;
  padding-right: 4rem;
  border: 0.1rem solid #e0e0e0;
  border-radius: 0.8rem;
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-textarea:focus {
  outline: none;
  border-color: #8E24AA;
  box-shadow: 0 0 0 0.2rem rgba(142, 36, 170, 0.1);
}

.submit-arrow-btn {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  width: 3rem;
  height: 3rem;
  border: none;
  background: #8E24AA;
  color: white;
  border-radius: 50%;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(142, 36, 170, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-arrow-btn:hover:not(:disabled) {
  background: #7B1FA2;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(142, 36, 170, 0.4);
}

.submit-arrow-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
