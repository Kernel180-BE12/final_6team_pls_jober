<template>
  <div class="template-create-container">
    <v-container class="h-100 pa-0">
      <div class="content-wrapper">
        <!-- 제목 및 설명 -->
        <div class="header-section">
          <h1 class="page-title">
            카카오 알림톡으로 발송할 메시지 내용을 입력하세요
          </h1>
          <p class="page-description">
            문자메시지를 보낸다고 생각하시고 메시지를 입력해주세요
          </p>
        </div>
        
        <!-- 메인 콘텐츠 영역 -->
        <div class="main-content">
          <!-- 왼쪽: 카테고리 영역 -->
          <div class="category-section">
            <h3 class="section-title">카테고리 선택</h3>
            <div class="category-grid">
              <v-btn
                v-for="category in categories"
                :key="category.id"
                :variant="selectedCategory === category.id ? 'elevated' : 'outlined'"
                :color="selectedCategory === category.id ? 'primary' : 'grey'"
                :class="['category-btn', { 'selected': selectedCategory === category.id }]"
                @click="selectCategory(category.id)"
              >
                {{ category.name }}
              </v-btn>
            </div>
          </div>
          
          <!-- 오른쪽: 텍스트 입력 영역 -->
          <div class="text-input-section">
            <h3 class="section-title">메시지 내용</h3>
            <v-textarea
              v-model="messageText"
              placeholder="발송할 메시지 내용을 입력하세요..."
              variant="outlined"
              rows="12"
              auto-grow
              class="message-textarea"
              hide-details
            />
            
            <!-- 제출 버튼 -->
            <div class="submit-section">
              <v-btn
                color="primary"
                size="large"
                variant="elevated"
                :disabled="!canSubmit"
                @click="handleSubmit"
                class="submit-btn"
              >
                템플릿 생성하기
              </v-btn>
            </div>
          </div>
        </div>
      </div>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

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
  { id: 11, name: '기타' }
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
  height: calc(100vh - 64px); /* 헤더 높이 제외 */
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #e3f2fd 0%, #f1f8e9 100%);
}

.content-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 40px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.header-section {
  text-align: center;
  margin-bottom: 40px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 16px;
  line-height: 1.3;
}

.page-description {
  font-size: 1.25rem;
  color: #666;
  margin: 0;
}

.main-content {
  display: flex;
  gap: 40px;
  flex: 1;
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
  margin-bottom: 24px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  flex: 1;
}

.category-btn {
  height: 48px;
  font-size: 0.9rem;
  font-weight: 500;
  text-transform: none;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.category-btn:hover {
  transform: translateY(-1px);
}

.category-btn.selected {
  font-weight: 600;
}

.text-input-section {
  display: flex;
  flex-direction: column;
}

.message-textarea {
  flex: 1;
  min-height: 300px;
}

.message-textarea :deep(.v-field) {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.message-textarea :deep(.v-field--focused) {
  background: rgba(255, 255, 255, 1);
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.15);
}

.submit-section {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}

.submit-btn {
  min-width: 160px;
  height: 48px;
  font-weight: 600;
  text-transform: none;
  border-radius: 8px;
}

/* 카테고리 그리드 조정 - 2줄에 맞춤 */
@media (max-width: 1400px) {
  .category-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (max-width: 1200px) {
  .category-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .content-wrapper {
    padding: 30px;
  }
  
  .main-content {
    gap: 30px;
  }
}

@media (max-width: 900px) {
  .main-content {
    flex-direction: column;
    gap: 30px;
  }
  
  .category-grid {
    grid-template-columns: repeat(6, 1fr);
  }
  
  .content-wrapper {
    padding: 20px;
  }
  
  .page-title {
    font-size: 2rem;
  }
}

@media (max-width: 600px) {
  .category-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }
  
  .category-btn {
    height: 40px;
    font-size: 0.8rem;
  }
  
  .content-wrapper {
    padding: 16px;
  }
}
</style>
