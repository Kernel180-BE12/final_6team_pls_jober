<template>
  <div class="template-result-container">
    <!-- 헤더 컴포넌트 -->
    <HeaderComponent />
    
    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <div class="content-wrapper">
        <!-- 좌우 분할 레이아웃 -->
        <div class="split-layout">
          <!-- 왼쪽: 메시지 편집/정보 (1/3) -->
          <div class="left-panel">
            <div class="message-bubble">
              <p>안녕하세요. ○○병원입니다.</p>
              <p>예약하신 진료 일정 안내드립니다.</p>
              <p>- 일시: 25.09.05(금) 14:30</p>
              <p>- 장소: ○○병원 3층 내과 진료실</p>
              <p>예약 시간 10분 전 도착 부탁드립니다.</p>
            </div>
            
            <!-- 채팅 컴포넌트 -->
            <ChatComponent :is-modifying="isModifying" />
            
            <div class="version-button">
              <button class="btn-version">버전 1</button>
              <button class="btn-version-modified" @click="showModifiedVersion">수정된 버전</button>
            </div>
            
            <div class="template-description">
              <p>
                예약 진료 일정 안내 및 도착 안내에 대한 카카오 알림톡 템플릿이 생성되었습니다. 
                '사전 승인된 알림톡'을 기반으로 총 4개 변수가 적용되었으며, 
                '이 카톡 발송하기'에서 자유롭게 수정하실 수 있습니다.
              </p>
            </div>
            
            <!-- 사용자 수정 모드일 때 표시되는 변수 편집 컴포넌트 -->
            <VariableEditComponent 
              v-if="isModifying"
              :variables="editedVariables"
              @update="updateVariables"
            />
          </div>
          
          <!-- 오른쪽: 카카오톡 미리보기 (2/3) -->
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
            </div>
            
            <!-- 카카오톡 미리보기 -->
            <div class="kakao-preview-container">
              <div class="kakao-preview">
                <div class="kakao-header">알림톡 도착</div>
                <div class="kakao-content">
                  <div class="kakao-title">
                    <span>쿠폰 발급 안내</span>
                    <div class="coupon-icon">🎫</div>
                  </div>
                  
                                    <div class="kakao-message">
                    <p>안녕하세요, <span 
                      v-if="showVariables && !isModifying"
                      :class="['variable', { 'rejected-highlight': isRejected }]"
                      @click="isRejected && showAlternatives('수신자')"
                    >#{수신자}</span><span v-else>{{ editedVariables.recipient }}</span> 회원님!</p>
                    <p><span 
                      v-if="showVariables && !isModifying"
                      :class="['variable', { 'rejected-highlight': isRejected }]"
                      @click="isRejected && showAlternatives('발신 스페이스')"
                    >#{발신 스페이스}</span><span v-else>{{ editedVariables.sender }}</span>입니다.</p>
                    <p>회원님께 발급된 쿠폰을 안내드립니다.</p>
                    <p>▶ 쿠폰명 : <span 
                      v-if="showVariables && !isModifying"
                      :class="['variable', { 'rejected-highlight': isRejected }]"
                      @click="isRejected && showAlternatives('쿠폰명')"
                    >#{쿠폰명}</span><span v-else>{{ editedVariables.couponName }}</span></p>
                    <p>▶ 사용기한 : <span 
                      v-if="showVariables && !isModifying"
                      :class="['variable', { 'rejected-highlight': isRejected }]"
                      @click="isRejected && showAlternatives('사용기한')"
                    >#{사용기한}</span><span v-else>{{ editedVariables.expiryDate }}</span></p>
                    <p><span 
                      v-if="showVariables && !isModifying"
                      :class="['variable', { 'rejected-highlight': isRejected }]"
                      @click="isRejected && showAlternatives('추가 메시지')"
                    >#{추가 메시지 - 문의 사항은 언제든 편하게 연락주세요.}</span><span v-else>{{ editedVariables.additionalMessage }}</span></p>
                    <p class="disclaimer">* 이 메시지는 이용약관(계약서) 동의에 따라 지급된 쿠폰 안내 메시지입니다.</p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 하단 컨트롤 -->
            <div class="bottom-controls">
              <div class="correction-count">남은 정정 횟수: 1/3</div>
              <div class="action-buttons">
                <button class="btn-modify" @click="toggleModification">
                  {{ isModifying ? '수정 완료' : '사용자 수정' }}
                </button>
                <button class="btn-reject" @click="rejectTemplate">반려하기</button>
                <button class="btn-submit" @click="submitTemplate">제출하기</button>
              </div>
            </div>
            
            <!-- 반려 모달 -->
            <RejectionModalComponent
              :show="showRecommendations"
              @close="closeRecommendations"
              @approve="approveRecommendation"
              @reject="rejectRecommendation"
            />
            
            <!-- 대안 선택 모달 -->
            <AlternativesModalComponent
              :show="showAlternativesSidebar"
              :current-variable="currentVariable"
              :alternatives="currentAlternatives"
              @close="closeAlternatives"
              @apply="applySelectedAlternatives"
            />
          </div>
        </div>
      </div>
    </main>


  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import HeaderComponent from '@/components/HeaderComponent.vue'
import VariableEditComponent from '@/components/VariableEditComponent.vue'
import RejectionModalComponent from '@/components/RejectionModalComponent.vue'
import AlternativesModalComponent from '@/components/AlternativesModalComponent.vue'
import ChatComponent from '@/components/ChatComponent.vue'

const showVariables = ref(true)
const showRecommendations = ref(false)
const showAlternativesSidebar = ref(false)
const isRejected = ref(false)
const currentVariable = ref('')
const currentAlternatives = ref<any[]>([])
const isModifying = ref(false)

// 사용자가 수정할 수 있는 변수 값들
const editedVariables = ref({
  recipient: '홍길동',
  sender: '저희 회사',
  couponName: '신규 가입 축하 쿠폰',
  expiryDate: '2024년 12월 31일까지',
  additionalMessage: '문의 사항은 언제든 편하게 연락주세요.'
})



// 추천 데이터
const recommendations = ref([
  {
    placeholder: '이 영역을 어케 처리하지?',
    status: 'pending'
  }
])

// 변수별 대안 데이터
const variableAlternatives = {
  '수신자': [
    { text: '고객', selected: false },
    { text: '회원', selected: false },
    { text: '사용자', selected: false }
  ],
  '발신 스페이스': [
    { text: '저희 회사', selected: false },
    { text: '저희 팀', selected: false },
    { text: '저희', selected: false }
  ],
  '쿠폰명': [
    { text: '할인 쿠폰', selected: false },
    { text: '특별 혜택', selected: false },
    { text: '프로모션 쿠폰', selected: false }
  ],
  '사용기한': [
    { text: '유효기간', selected: false },
    { text: '사용 가능 기간', selected: false },
    { text: '만료일', selected: false }
  ],
  '추가 메시지': [
    { text: '문의사항이 있으시면 언제든 연락주세요.', selected: false },
    { text: '궁금한 점이 있으시면 편하게 문의해주세요.', selected: false },
    { text: '도움이 필요하시면 언제든 연락주세요.', selected: false }
  ]
}

// 반려하기
const rejectTemplate = () => {
  isRejected.value = true
  showRecommendations.value = true
}

// 대안 표시
const showAlternatives = (variableName: string) => {
  currentVariable.value = variableName
  currentAlternatives.value = JSON.parse(JSON.stringify(variableAlternatives[variableName as keyof typeof variableAlternatives]))
  showAlternativesSidebar.value = true
}

// 대안 선택
const selectAlternative = (alternative: any) => {
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
    // 여기서 실제 텍스트를 대체하는 로직을 구현할 수 있습니다
    console.log(`${currentVariable.value}를 "${selectedAlternative.text}"로 대체`)
    // 텍스트 대체 후 사이드바 닫기
    closeAlternatives()
  }
}

// 반려 상세 표시
const showRejectionDetails = (text: string) => {
  showRecommendations.value = true
  console.log('반려된 텍스트:', text)
}

// 추천 사이드바 닫기
const closeRecommendations = () => {
  showRecommendations.value = false
  isRejected.value = false
}

// 대안 사이드바 닫기
const closeAlternatives = () => {
  showAlternativesSidebar.value = false
  currentVariable.value = ''
  currentAlternatives.value = []
}

// 추천 승인
const approveRecommendation = (rec: any) => {
  rec.status = 'approved'
  console.log('승인됨:', rec)
}

// 추천 반려
const rejectRecommendation = (rec: any) => {
  rec.status = 'rejected'
  console.log('반려됨:', rec)
}

// 수정 모드 토글
const toggleModification = () => {
  isModifying.value = !isModifying.value
}

// 변수 업데이트
const updateVariables = (newVariables: any) => {
  editedVariables.value = { ...newVariables }
}

// 수정된 버전 표시
const showModifiedVersion = () => {
  // 여기에 수정된 버전을 보여주는 로직을 구현할 수 있습니다
  console.log('수정된 버전 표시')
  // 예: 모달 열기, 다른 템플릿 표시 등
}

// 템플릿 제출
const submitTemplate = () => {
  console.log('템플릿 제출')
  // 실제 제출 로직 구현
}
</script>

<style scoped>
.template-result-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.main-content {
  flex: 1;
  background: linear-gradient(135deg, #E3F2FD 0%, #F1F8E9 100%);
  padding: 40px 0 80px 0;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.split-layout {
  display: flex;
  gap: 0;
  height: 100%;
  position: relative;
}

.split-layout::after {
  content: '';
  position: absolute;
  left: calc(33.33% + 20px);
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, transparent, #e0e0e0, transparent);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-right: 40px;
}

.right-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-left: 40px;
}

.message-bubble {
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 12px;
  font-size: 1rem;
  line-height: 1.6;
  color: #333;
  height: 250px;
}

.message-bubble p {
  margin: 8px 0;
}

.version-button {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-version {
  background-color: #666;
  color: white;
  border: none;
  padding: 5px 12px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  flex: 1;
  max-width: 120px;
}

.btn-version-modified {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 5px 12px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  flex: 1;
  max-width: 120px;
  transition: background-color 0.2s ease;
}

.btn-version-modified:hover {
  background-color: #218838;
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

.kakao-preview-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  width: 100%;
  height: 100%;
}

.kakao-preview {
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  width: 320px;
  max-width: 320px;
  flex-shrink: 0;
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

.coupon-icon {
  font-size: 1.5rem;
  background-color: #4caf50;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kakao-message {
  margin-bottom: 20px;
  line-height: 1.6;
}

.kakao-message p {
  margin: 8px 0;
}

.highlighted-text {
  background-color: #ffeb3b;
  padding: 2px 6px;
  border-radius: 4px;
  color: #856404;
  cursor: pointer;
  text-decoration: underline;
  text-decoration-color: #f44336;
  text-decoration-thickness: 2px;
}

.highlighted-text:hover {
  background-color: #fff59d;
}

.variable {
  background-color: #fff3cd;
  padding: 2px 6px;
  border-radius: 4px;
  color: #856404;
  cursor: pointer;
  transition: all 0.2s ease;
}

.variable:hover {
  background-color: #ffeaa7;
}

.variable.rejected-highlight {
  background-color: #ffebee;
  color: #c62828;
  border: 2px solid #f44336;
  cursor: pointer;
  animation: pulse 2s infinite;
}

.variable.rejected-highlight:hover {
  background-color: #ffcdd2;
  transform: scale(1.05);
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.7); }
  70% { box-shadow: 0 0 0 10px rgba(244, 67, 54, 0); }
  100% { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0); }
}

.disclaimer {
  font-size: 0.8rem;
  color: #666;
  margin-top: 16px;
  line-height: 1.4;
}

.kakao-action {
  text-align: center;
  padding: 16px 0;
}

.bottom-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 40px;
}

.correction-count {
  background-color: #1976d2;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn-modify,
.btn-submit,
.btn-reject {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s ease;
}

.btn-submit {
  background-color: #28a745;
}

.btn-submit:hover {
  background-color: #218838;
}

.btn-reject {
  background-color: #dc3545;
}

.btn-reject:hover {
  background-color: #c82333;
}

.btn-modify:hover {
  background-color: #5a6268;
}






</style>
