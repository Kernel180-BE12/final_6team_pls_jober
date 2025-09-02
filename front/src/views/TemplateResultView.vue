<template>
  <div class="template-result-container">
    <v-container class="h-100 pa-0">
      <div class="content-wrapper">
        <!-- 제목 및 설명 -->
        <div class="header-section">
          <h1 class="page-title">템플릿 생성 완료</h1>
          <p class="page-description">
            AI가 생성한 카카오 알림톡 템플릿을 확인하고 수정할 수 있습니다
          </p>
        </div>
        
        <!-- 메인 콘텐츠 영역 -->
        <div class="main-content">
          <!-- 왼쪽: 템플릿 정보 -->
          <div class="template-info-section">
            <div class="info-card">
              <h3 class="section-title">생성된 템플릿 정보</h3>
              
              <div class="template-details">
                <div class="detail-item">
                  <span class="detail-label">카테고리:</span>
                  <span class="detail-value">예약 안내</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">템플릿 유형:</span>
                  <span class="detail-value">사전 승인된 알림톡</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">적용된 변수:</span>
                  <span class="detail-value">총 4개</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">상태:</span>
                  <v-chip color="success" size="small" variant="flat">검증 대기</v-chip>
                </div>
              </div>
              
              <div class="template-description">
                <p>
                  예약 진료 일정 안내 및 도착 안내에 대한 카카오 알림톡 템플릿이 생성되었습니다. 
                  '사전 승인된 알림톡'을 기반으로 총 4개 변수가 적용되었으며, 
                  '채팅으로 수정하기'에서 자유롭게 수정하실 수 있습니다.
                </p>
              </div>
              
              <div class="action-buttons">
                <v-btn
                  color="primary"
                  size="large"
                  variant="elevated"
                  @click="goToChat"
                  class="action-btn"
                >
                  채팅으로 수정하기
                </v-btn>
                <v-btn
                  color="secondary"
                  size="large"
                  variant="outlined"
                  @click="goToLanding"
                  class="action-btn"
                >
                  새로운 템플릿 만들기
                </v-btn>
              </div>
            </div>
          </div>
          
          <!-- 오른쪽: 알림톡 미리보기 -->
          <div class="preview-section">
            <h3 class="section-title">알림톡 미리보기</h3>
            
            <div class="kakao-preview-card">
              <div class="kakao-header">
                <div class="kakao-title">
                  <v-icon color="yellow-darken-2" size="20">mdi-bell</v-icon>
                  <span>알림톡 도착</span>
                </div>
              </div>
              
              <div class="kakao-content">
                <div class="kakao-subject">예약 안내</div>
                
                <div class="kakao-message">
                  <p>안녕하세요 <span class="variable">고객님</span>.</p>
                  <p>예약 일정 안내드립니다.</p>
                  <p>▶예약자: <span class="variable">고객</span></p>
                  <p>▶예약일시: <span class="variable">2025.09.05(금) 14:30</span></p>
                  <p>예약 시간 10분 전 도착 부탁드립니다.</p>
                  <p>▶장소: <span class="variable">3층 내과 진료실</span></p>
                  <p>감사합니다.</p>
                </div>
                
                <div class="kakao-button">
                  <v-btn variant="outlined" size="small" color="grey">예약확인</v-btn>
                </div>
              </div>
            </div>
            
            <!-- 변수 정보 -->
            <div class="variables-info">
              <h4 class="variables-title">적용된 변수</h4>
              <div class="variables-list">
                <div class="variable-item">
                  <span class="variable-name">고객님</span>
                  <span class="variable-desc">고객 호칭</span>
                </div>
                <div class="variable-item">
                  <span class="variable-name">고객</span>
                  <span class="variable-desc">예약자명</span>
                </div>
                <div class="variable-item">
                  <span class="variable-name">2025.09.05(금) 14:30</span>
                  <span class="variable-desc">예약 일시</span>
                </div>
                <div class="variable-item">
                  <span class="variable-name">3층 내과 진료실</span>
                  <span class="variable-desc">진료 장소</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

// 페이지 이동
const goToChat = () => {
  router.push('/chat')
}

const goToLanding = () => {
  router.push('/')
}
</script>

<style scoped>
.template-result-container {
  height: calc(100vh - 64px);
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

.template-info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.info-card {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  height: fit-content;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 24px;
}

.template-details {
  margin-bottom: 32px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 500;
  color: #666;
}

.detail-value {
  font-weight: 600;
  color: #1a1a1a;
}

.template-description {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 32px;
}

.template-description p {
  margin: 0;
  line-height: 1.6;
  color: #555;
  font-size: 0.95rem;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-btn {
  width: 100%;
}

.preview-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.kakao-preview-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.kakao-header {
  background: #fee500;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.kakao-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1a1a1a;
}

.kakao-content {
  padding: 20px;
}

.kakao-subject {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 16px;
}

.kakao-message {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #333;
  margin-bottom: 20px;
}

.kakao-message p {
  margin: 8px 0;
}

.variable {
  color: #1976d2;
  font-weight: 500;
}

.kakao-button {
  text-align: center;
}

.variables-info {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.variables-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 20px;
}

.variables-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.variable-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #1976d2;
}

.variable-name {
  font-weight: 600;
  color: #1976d2;
}

.variable-desc {
  font-size: 0.9rem;
  color: #666;
}

/* 반응형 디자인 제거 - 고정 레이아웃 */
@media (max-width: 1200px) {
  .content-wrapper {
    padding: 30px;
    gap: 30px;
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
  
  .template-info-section,
  .preview-section {
    flex: none;
  }
  
  .content-wrapper {
    padding: 20px;
  }
  
  .page-title {
    font-size: 2rem;
  }
}

@media (max-width: 600px) {
  .content-wrapper {
    padding: 16px;
  }
  
  .info-card {
    padding: 24px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>
