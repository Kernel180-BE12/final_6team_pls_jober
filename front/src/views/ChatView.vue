<template>
  <div class="chat-container">
    <!-- 헤더 컴포넌트 -->
    <HeaderComponent />
    
    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <div class="content-wrapper">
        <!-- 좌우 분할 레이아웃 -->
        <div class="split-layout">
          <!-- 왼쪽: 메시지 편집/정보 -->
          <div class="left-panel">
            <div class="version-indicator">버전 1 ></div>
            
            <div class="template-content">
              <p>안녕하세요. ○○병원입니다.</p>
              <p>예약하신 진료 일정 안내드립니다.</p>
              <p>- 일시: 25.09.05(금) 14:30</p>
              <p>- 장소: ○○병원 3층 내과 진료실</p>
              <p>예약 시간 10분 전 도착 부탁드립니다.</p>
            </div>
            
            <div class="template-description">
              <p>
                예약 진료 일정 안내 및 도착 안내에 대한 카카오 알림톡 템플릿이 생성되었습니다. 
                '사전 승인된 알림톡'을 기반으로 총 4개 변수가 적용되었으며, 
                '이 카톡 발송하기'에서 자유롭게 수정하실 수 있습니다.
              </p>
            </div>
            
            <div class="input-field">
              <input 
                type="text" 
                placeholder="발송하고 싶은 내용을 입력하세요"
                class="message-input"
              />
              <button class="btn-send">↑</button>
            </div>
          </div>
          
          <!-- 오른쪽: 카카오톡 미리보기 및 수정 반려 -->
          <div class="right-panel">
            <!-- 상단 컨트롤 -->
            <div class="top-controls">
              <div class="toggle-switch">
                <label class="toggle-label">
                  <input type="checkbox" v-model="showVariables" />
                  <span class="toggle-slider"></span>
                  변수값 표시
                </label>
              </div>
              <button class="btn-send-kakao">이 카톡 발송하기</button>
            </div>
            
            <!-- 카카오톡 미리보기 -->
            <div class="kakao-preview">
              <div class="kakao-header">알림톡 도착</div>
              <div class="kakao-content">
                <div class="kakao-title">
                  <span>예약 안내</span>
                  <div class="calendar-icon">📅</div>
                </div>
                
                <div class="kakao-message">
                  <p>안녕하세요 <span class="variable">고객님</span>,</p>
                  <p>예약 일정 안내드립니다.</p>
                  <p>▶예약자: <span class="variable">고객</span></p>
                  <p>▶예약일시: <span class="variable">2025.09.05(금) 14:30</span></p>
                  <p>예약 시간 10분 전 도착 부탁드립니다.</p>
                  <p>▶장소: <span class="variable">○○병원 3층 내과 진료실</span></p>
                  <p>감사합니다.</p>
                </div>
                
                <div class="kakao-action">
                  <button class="btn-reservation">예약확인</button>
                </div>
              </div>
            </div>
            
            <!-- 수정 반려 내용 -->
            <div class="rejection-section">
              <div class="rejection-header">
                <button class="btn-complete">완료</button>
              </div>
              
              <div class="rejection-content">
                <h4 class="rejection-title">수정 반려 내용</h4>
                
                <div class="rejection-item">
                  <div class="rejection-reason">
                    <span class="bullet">•</span>
                    <span>반려 사유: 부적절 한 언어</span>
                  </div>
                  <div class="rejection-text">블라블라</div>
                  <div class="rejection-actions">
                    <button class="btn-reject">반려</button>
                    <button class="btn-approve">승인</button>
                  </div>
                </div>
                
                <div class="rejection-item">
                  <div class="rejection-reason">
                    <span class="bullet">•</span>
                    <span>반려 사유: 부적절 한 언어</span>
                  </div>
                  <div class="rejection-text">블라라라랄</div>
                  <div class="rejection-actions">
                    <button class="btn-reject">반려</button>
                    <button class="btn-approve">승인</button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 하단 정정 횟수 -->
            <div class="correction-count">
              <span class="count-text">남은 정정 횟수: 1/3</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import HeaderComponent from '@/components/HeaderComponent.vue'

const showVariables = ref(true)
</script>

<style scoped>
.chat-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  background: linear-gradient(135deg, #E3F2FD 0%, #F1F8E9 100%);
  padding: 40px 0;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.split-layout {
  display: flex;
  gap: 40px;
  height: 100%;
}

.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.version-indicator {
  background-color: #666;
  color: white;
  padding: 12px 24px;
  border-radius: 6px;
  font-weight: 500;
  text-align: center;
  cursor: pointer;
}

.template-content {
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 12px;
  font-size: 1rem;
  line-height: 1.6;
  color: #333;
}

.template-content p {
  margin: 8px 0;
}

.template-description {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  font-size: 0.95rem;
  line-height: 1.6;
  color: #555;
}

.template-description p {
  margin: 0;
}

.input-field {
  display: flex;
  gap: 12px;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
}

.btn-send {
  background-color: #1976d2;
  color: white;
  border: none;
  padding: 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.2rem;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.top-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toggle-switch {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #333;
}

.toggle-label input {
  display: none;
}

.toggle-slider {
  width: 40px;
  height: 20px;
  background-color: #ccc;
  border-radius: 10px;
  position: relative;
  transition: background-color 0.2s ease;
}

.toggle-slider:before {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  background-color: white;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: transform 0.2s ease;
}

.toggle-label input:checked + .toggle-slider {
  background-color: #1976d2;
}

.toggle-label input:checked + .toggle-slider:before {
  transform: translateX(20px);
}

.btn-send-kakao {
  background-color: #9c27b0;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.kakao-preview {
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.kakao-header {
  background-color: #fee500;
  padding: 16px 20px;
  font-weight: 600;
  color: #333;
  text-align: center;
}

.kakao-content {
  padding: 20px;
}

.kakao-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-size: 1.2rem;
  font-weight: 600;
}

.calendar-icon {
  font-size: 1.5rem;
}

.kakao-message {
  margin-bottom: 20px;
  line-height: 1.6;
}

.kakao-message p {
  margin: 8px 0;
}

.variable {
  background-color: #fff3cd;
  padding: 2px 6px;
  border-radius: 4px;
  color: #856404;
}

.kakao-action {
  text-align: center;
}

.btn-reservation {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  color: #495057;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
}

.rejection-section {
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.rejection-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e9ecef;
}

.btn-complete {
  background-color: #1976d2;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.rejection-content {
  padding: 20px;
}

.rejection-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
}

.rejection-item {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.rejection-reason {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: #666;
}

.bullet {
  color: #dc3545;
  font-weight: bold;
}

.rejection-text {
  margin-bottom: 12px;
  font-size: 0.9rem;
  color: #333;
}

.rejection-actions {
  display: flex;
  gap: 8px;
}

.btn-reject,
.btn-approve {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.btn-reject {
  background-color: #dc3545;
  color: white;
}

.btn-approve {
  background-color: #28a745;
  color: white;
}

.correction-count {
  text-align: center;
  padding: 16px;
  background-color: #e3f2fd;
  border-radius: 8px;
}

.count-text {
  font-size: 0.9rem;
  color: #1976d2;
  font-weight: 500;
}
</style>
