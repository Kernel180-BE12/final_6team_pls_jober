<template>
  <div class="template-create-container">
    <!-- 헤더 컴포넌트 -->
    <HeaderComponent />
    
    <!-- 메인 콘텐츠 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 제목 및 설명 -->
        <div class="header-section">
          <h1 class="page-title">
            만들고 싶은 알림톡 템플릿 주제를 알려주세요
          </h1>
        </div>
        
        <!-- 메인 콘텐츠 영역 -->
        <div class="main-content-area">
          <!-- 왼쪽: 카테고리 영역 -->
          <div class="category-section">
            <h3 class="section-title">카테고리 선택</h3>
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
          
          <!-- 오른쪽: 텍스트 입력 영역 -->
          <div class="text-input-section">
            <h3 class="section-title">메시지 내용</h3>
            <textarea
              v-model="messageText"
              placeholder="ex. 우리 서비스에 맞는 법적 고지 내용을 빠르게 작성하고 적용할 수 있는 템플릿이 필요합니다."
              class="message-textarea"
              rows="12"
            ></textarea>
            
            <!-- 제출 버튼 -->
            <div class="submit-section">
              <button
                class="submit-btn"
                :disabled="!canSubmit"
                @click="handleSubmit"
              >
                템플릿 생성하기
              </button>
            </div>
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
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

.header-section {
  text-align: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 0.8rem;
  line-height: 1.3;
}

.page-description {
  font-size: 1.25rem;
  color: #666;
  margin: 0;
}

.main-content-area {
  display: flex;
  gap: 2rem;
  min-height: 0;
}

.category-section,
.text-input-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 1.2rem;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.6rem;
  align-content: start;
}

.category-btn {
  height: 2.4rem;
  font-size: 0.9rem;
  font-weight: 500;
  border: 0.1rem solid #e0e0e0;
  background: white;
  color: #666;
  border-radius: 0.4rem;
  transition: all 0.2s ease;
  cursor: pointer;
}

.category-btn:hover {
  border-color: #1976d2;
  color: #1976d2;
}

.category-btn.selected {
  background: #1976d2;
  color: white;
  border-color: #1976d2;
}

.text-input-section {
  display: flex;
  flex-direction: column;
}

.message-textarea {
  flex: 1;
  min-height: 15rem;
  padding: 1rem;
  border: 0.1rem solid #e0e0e0;
  border-radius: 0.6rem;
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
}

.message-textarea:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 0.1rem rgba(25, 118, 210, 0.1);
}

.submit-section {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.2rem;
}

.submit-btn {
  background: #1976d2;
  color: white;
  border: none;
  padding: 0.8rem 1.6rem;
  border-radius: 0.4rem;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  background: #1565c0;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
