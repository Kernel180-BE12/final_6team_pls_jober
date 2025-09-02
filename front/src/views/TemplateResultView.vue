<template>
  <div class="template-result-page">
    <!-- 헤더 -->
    <HeaderComponent />
    
    <!-- 메인 콘텐츠 -->
    <v-main class="main-content">
      <v-container fluid class="pa-0">
        <section class="result-section">
          <v-container class="result-container">
            <v-row>
              <!-- 왼쪽 섹션: 템플릿 편집 -->
              <v-col cols="12" lg="6" class="left-section">
                <div class="edit-content">
                  <!-- 생성된 템플릿 내용 -->
                  <div class="template-box mb-6">
                    <div class="template-content">
                      <p class="template-text">
                        안녕하세요. ○○병원입니다. 예약하신 진료 일정 안내드립니다.
                      </p>
                      <ul class="template-list">
                        <li>- 일시: 25.09.05(금) 14:30</li>
                        <li>- 장소: ○○병원 3층 내과 진료실</li>
                      </ul>
                      <p class="template-text">
                        예약 시간 10분 전 도착 부탁드립니다.
                      </p>
                    </div>
                  </div>
                  
                  <!-- 버전 정보 -->
                  <div class="version-info mb-6">
                    <v-btn
                      color="#333"
                      variant="outlined"
                      class="version-btn"
                      rounded="pill"
                    >
                      버전 1 >
                    </v-btn>
                  </div>
                  
                  <!-- 생성 설명 -->
                  <div class="generation-info mb-6">
                    <p class="info-text">
                      {{ selectedCategoryName }} 카테고리에 대한 카카오 알림톡 템플릿이 생성되었습니다. 
                      '사전 승인된 알림톡'을 기반으로 총 4개 변수가 적용되었으며, 
                      '이 카톡 발송하기'에서 자유롭게 수정하실 수 있습니다.
                    </p>
                  </div>
                  
                  <!-- 추가 입력 필드 -->
                  <div class="additional-input mb-6">
                    <v-text-field
                      v-model="additionalMessage"
                      label="발송하고 싶은 내용을 입력해주세요"
                      variant="outlined"
                      class="additional-field"
                      append-inner-icon="mdi-arrow-up"
                      @click:append-inner="sendAdditionalMessage"
                    ></v-text-field>
                  </div>
                  
                  <!-- 정정 횟수 -->
                  <div class="correction-count">
                    <div class="correction-bar">
                      <div class="correction-fill" :style="{ width: correctionPercentage + '%' }"></div>
                    </div>
                    <p class="correction-text">남은 정정 횟수: {{ remainingCorrections }}/3</p>
                  </div>
                </div>
              </v-col>
              
              <!-- 오른쪽 섹션: 미리보기 -->
              <v-col cols="12" lg="6" class="right-section">
                <div class="preview-content">
                  <!-- 컨트롤 바 -->
                  <div class="control-bar mb-4">
                    <div class="toggle-section">
                      <span class="toggle-label">변수값 표시</span>
                      <v-switch
                        v-model="showVariables"
                        color="#00C851"
                        hide-details
                      ></v-switch>
                    </div>
                    <v-btn
                      color="#9C27B0"
                      variant="flat"
                      class="send-btn"
                      rounded="pill"
                      size="large"
                    >
                      이 카톡 발송하기
                    </v-btn>
                  </div>
                  
                  <!-- 메시지 미리보기 -->
                  <div class="message-preview">
                    <div class="preview-header">
                      <span class="preview-title">알림톡 도착</span>
                    </div>
                    <div class="preview-content">
                      <div class="preview-icon">
                        <v-icon icon="mdi-calendar-check" size="40" color="#00C851"></v-icon>
                      </div>
                      <h3 class="preview-main-title">예약 안내</h3>
                      <p class="preview-main-text">
                        안녕하세요 고객님. 예약 일정 안내드립니다.
                      </p>
                      <div class="preview-details">
                        <div class="detail-item">
                          <span class="detail-icon">▶</span>
                          <span class="detail-text">예약자: 고객</span>
                        </div>
                        <div class="detail-item">
                          <span class="detail-icon">▶</span>
                          <span class="detail-text">예약일시: 2025.09.05(금) 14:30</span>
                        </div>
                        <p class="detail-text">예약 시간 10분 전 도착 부탁드립니다.</p>
                        <div class="detail-item">
                          <span class="detail-icon">▶</span>
                          <span class="detail-text">장소: ○○병원 3층 내과 진료실</span>
                        </div>
                      </div>
                      <p class="preview-closing">감사합니다.</p>
                      <v-btn
                        color="#E0E0E0"
                        variant="flat"
                        class="action-btn"
                        rounded="pill"
                      >
                        예약확인
                      </v-btn>
                    </div>
                  </div>
                  
                  <!-- 하단 버튼들 -->
                  <div class="bottom-buttons mt-6">
                    <v-btn
                      color="#E0E0E0"
                      variant="flat"
                      class="bottom-btn"
                      rounded="pill"
                      size="large"
                    >
                      사용자 수정
                    </v-btn>
                    <v-btn
                      color="#E0E0E0"
                      variant="flat"
                      class="bottom-btn ml-4"
                      rounded="pill"
                      size="large"
                    >
                      제출하기
                    </v-btn>
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-container>
        </section>
      </v-container>
    </v-main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import HeaderComponent from '@/components/HeaderComponent.vue'

const route = useRoute()

// 카테고리 매핑
const categoryNames = {
  'appointment': '예약 안내',
  'marketing': '마케팅',
  'notification': '공지사항',
  'reminder': '리마인더',
  'custom': '커스텀'
}

// Reactive data
const showVariables = ref(true)
const additionalMessage = ref('')
const remainingCorrections = ref(2)

// 계산된 속성
const selectedCategory = computed(() => route.query.category as string || 'appointment')
const selectedCategoryName = computed(() => categoryNames[selectedCategory.value as keyof typeof categoryNames] || '커스텀')
const correctionPercentage = computed(() => ((3 - remainingCorrections.value) / 3) * 100)

// 추가 메시지 전송
const sendAdditionalMessage = () => {
  if (additionalMessage.value.trim()) {
    console.log('추가 메시지 전송:', additionalMessage.value)
    additionalMessage.value = ''
  }
}

onMounted(() => {
  console.log('선택된 카테고리:', selectedCategory.value)
  console.log('입력된 메시지:', route.query.message)
})
</script>

<style scoped>
.template-result-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #FFF8E1 0%, #FFFDE7 50%, #F1F8E9 100%);
}

.main-content {
  padding-top: 70px;
}

.result-section {
  padding: 2rem 0;
  min-height: calc(100vh - 70px);
}

.result-container {
  max-width: 1400px !important;
}

.left-section, .right-section {
  padding: 1rem;
}

.edit-content, .preview-content {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  padding: 2rem;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  height: 100%;
}

/* 왼쪽 섹션 스타일 */
.template-box {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #E0E0E0;
}

.template-content {
  line-height: 1.6;
}

.template-text {
  margin-bottom: 1rem;
  color: #333;
  font-size: 1rem;
}

.template-list {
  list-style: none;
  padding: 0;
  margin: 1rem 0;
}

.template-list li {
  margin-bottom: 0.5rem;
  color: #333;
  font-size: 1rem;
}

.version-btn {
  font-weight: 500;
  border-color: #333;
  color: #333;
}

.generation-info {
  background: #F5F5F5;
  padding: 1.5rem;
  border-radius: 8px;
}

.info-text {
  color: #666;
  line-height: 1.6;
  margin: 0;
  font-size: 0.95rem;
}

.additional-field {
  background: white;
}

.correction-count {
  text-align: center;
}

.correction-bar {
  width: 100%;
  height: 8px;
  background: #E0E0E0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.correction-fill {
  height: 100%;
  background: #00C851;
  transition: width 0.3s ease;
}

.correction-text {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

/* 오른쪽 섹션 스타일 */
.control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.toggle-section {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toggle-label {
  color: #333;
  font-weight: 500;
  font-size: 0.95rem;
}

.send-btn {
  font-weight: 600;
  text-transform: none;
  padding: 0 1.5rem;
}

.message-preview {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #E0E0E0;
}

.preview-header {
  background: #FFE066;
  padding: 0.75rem 1rem;
  text-align: center;
}

.preview-title {
  color: #333;
  font-weight: 600;
  font-size: 0.9rem;
}

.preview-content {
  padding: 2rem;
  text-align: center;
}

.preview-icon {
  margin-bottom: 1rem;
}

.preview-main-title {
  color: #333;
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.preview-main-text {
  color: #666;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.preview-details {
  text-align: left;
  margin-bottom: 1.5rem;
}

.detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
}

.detail-icon {
  color: #00C851;
  font-weight: bold;
  margin-right: 0.5rem;
  font-size: 1.1rem;
}

.detail-text {
  color: #333;
  line-height: 1.4;
}

.preview-closing {
  color: #666;
  margin-bottom: 1.5rem;
  font-style: italic;
}

.action-btn {
  background: #F5F5F5;
  color: #333;
  font-weight: 500;
  text-transform: none;
  padding: 0 2rem;
}

.bottom-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.bottom-btn {
  background: #F5F5F5;
  color: #333;
  font-weight: 500;
  text-transform: none;
  padding: 0 2rem;
}

/* 반응형 디자인 */
@media (max-width: 1200px) {
  .left-section, .right-section {
    margin-bottom: 2rem;
  }
}

@media (max-width: 960px) {
  .control-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .send-btn {
    width: 100%;
  }
  
  .bottom-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .bottom-btn {
    width: 200px;
  }
}

@media (max-width: 600px) {
  .edit-content, .preview-content {
    padding: 1.5rem;
  }
  
  .template-box {
    padding: 1rem;
  }
  
  .preview-content {
    padding: 1.5rem;
  }
}
</style>
