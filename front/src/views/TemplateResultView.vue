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
            <!-- 채팅 이력 표시 영역 -->
            <div class="chat-history-container">
              <div class="chat-history">
                <template v-for="(message, index) in chatHistory" :key="index">
                  <div :class="['chat-message', message.type]">
                    <div class="message-content">{{ message.content }}</div>
                    <div class="message-time">{{ message.time }}</div>
                  </div>
                  
                  <!-- 해당 메시지 다음에 버전 버튼 표시 -->
                  <div 
                    v-for="version in versions.filter(v => v.messageIndex === index)" 
                    :key="`version-${version.number}`"
                    class="version-creation-point"
                  >
                    <div class="version-divider">
                      <span class="version-label">버전 {{ version.number }} 생성</span>
                    </div>
                    <div class="version-buttons">
                      <button 
                        :class="['btn-version', { 'active': currentVersion === version.number }]"
                        @click="selectVersion(version.number)"
                      >
                        버전 {{ version.number }}
                      </button>
                    </div>
                  </div>
                </template>
              </div>
            </div>
            
            <!-- 채팅 입력 컨테이너 -->
            <div class="chat-input-container">
              <div class="input-field">
                <input 
                  v-model="chatInput"
                  type="text" 
                  placeholder="메시지를 입력하세요..."
                  class="message-input"
                  @keyup.enter="sendMessage"
                />
                <button class="btn-send" @click="sendMessage">↑</button>
              </div>
            </div>
          </div>
          
          <!-- 오른쪽: 카카오톡 미리보기 및 버튼들 (2/3) -->
          <div class="right-panel">
            <!-- 변수값 표시 토글 -->
            <div class="variables-toggle">
              <label class="toggle-label">
                <input type="checkbox" v-model="showVariables" />
                <span class="toggle-slider"></span>
                변수값 표시
              </label>
            </div>
            
            <!-- 카카오톡 미리보기와 반려 사이드바를 함께 관리하는 컨테이너 -->
            <div :class="['preview-and-sidebar-container', { 'with-rejection-sidebar': showRejectionSidebar }]">
              <!-- 카카오톡 미리보기 -->
              <div class="kakao-preview-wrapper">
                <KakaoPreviewComponent
                  :show-variables="showVariables"
                  :variables="editedVariables"
                  :is-modifying="isModifying"
                  :is-rejected="isRejected"
                  :rejected-variables="rejectedVariables"
                  @variable-click="handleVariableClick"
                  @update-variables="updateVariables"
                  @reject-template="rejectTemplate"
                  @submit-template="submitTemplate"
                />
              </div>
              
              <!-- 반려 사이드바 -->
              <div class="rejection-sidebar-panel" v-if="showRejectionSidebar">
                <RejectionSidebarComponent
                  :show="showRejectionSidebar"
                  :current-variable="currentVariable"
                  :alternatives="currentAlternatives"
                  :rejected-variables="rejectedVariables"
                  @close="closeRejectionSidebar"
                  @variable-click="handleVariableClick"
                  @apply-alternative="applySelectedAlternative"
                />
              </div>
            </div>
            
            <!-- 액션 버튼들 -->
            <div class="action-buttons-container">
              <div class="correction-count">남은 정정 횟수: 1/3</div>
              <div class="action-buttons">
                <button class="btn-modify" @click="toggleModification">
                  {{ isModifying ? '수정 완료' : '사용자 수정' }}
                </button>
                <button class="btn-reject" @click="rejectTemplate">반려하기</button>
                <button class="btn-submit" @click="submitTemplate">제출하기</button>
              </div>
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
import KakaoPreviewComponent from '@/components/KakaoPreviewComponent.vue'
import RejectionSidebarComponent from '@/components/RejectionSidebarComponent.vue'

const showVariables = ref(true)
const showRejectionSidebar = ref(false)
const isRejected = ref(false)
const currentVariable = ref('')
const currentAlternatives = ref<any[]>([])
const isModifying = ref(false)
const rejectedVariables = ref<string[]>([])

// 채팅 관련 변수들
const chatInput = ref('')
const currentVersion = ref(1)
const chatHistory = ref([
  {
    type: 'user',
    content: '안녕하세요! 템플릿을 만들어주세요.',
    time: '14:30'
  },
  {
    type: 'bot',
    content: '안녕하세요! 어떤 종류의 템플릿을 원하시나요?',
    time: '14:31'
  }
])

// 버전 관리
const versions = ref([
  { number: 1, template: '기본 템플릿', messageIndex: 0 }
])

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
  showRejectionSidebar.value = true
  // 모든 변수를 반려된 것으로 설정 (테스트용)
  rejectedVariables.value = ['수신자', '발신 스페이스', '쿠폰명', '사용기한', '추가 메시지']
}

// 변수 클릭 처리
const handleVariableClick = (variableName: string) => {
  if (isRejected.value && rejectedVariables.value.includes(variableName)) {
    currentVariable.value = variableName
    currentAlternatives.value = JSON.parse(JSON.stringify(variableAlternatives[variableName as keyof typeof variableAlternatives]))
    showRejectionSidebar.value = true
  }
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
const applySelectedAlternative = (alternative: any) => {
  // 여기서 실제 텍스트를 대체하는 로직을 구현할 수 있습니다
  console.log(`${currentVariable.value}를 "${alternative.text}"로 대체`)
  
  // 반려된 변수 목록에서 제거
  const index = rejectedVariables.value.indexOf(currentVariable.value)
  if (index > -1) {
    rejectedVariables.value.splice(index, 1)
  }
  
  // 모든 반려된 변수가 해결되면 반려 상태 해제
  if (rejectedVariables.value.length === 0) {
    isRejected.value = false
    showRejectionSidebar.value = false
  }
  
  currentVariable.value = ''
  currentAlternatives.value = []
}

// 반려 사이드바 닫기
const closeRejectionSidebar = () => {
  showRejectionSidebar.value = false
  isRejected.value = false
  rejectedVariables.value = []
  currentVariable.value = ''
  currentAlternatives.value = []
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

// 채팅 메시지 전송
const sendMessage = () => {
  if (!chatInput.value.trim()) return
  
  const now = new Date()
  const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  // 사용자 메시지 추가
  chatHistory.value.push({
    type: 'user',
    content: chatInput.value,
    time: timeString
  })
  
  // 챗봇 응답 (간단한 응답)
  setTimeout(() => {
    const botResponses = [
      '좋은 아이디어네요!',
      '더 구체적으로 설명해주세요.',
      '이해했습니다. 계속 진행하겠습니다.',
      '훌륭합니다!',
      '추가로 필요한 것이 있나요?'
    ]
    const randomResponse = botResponses[Math.floor(Math.random() * botResponses.length)]
    
    chatHistory.value.push({
      type: 'bot',
      content: randomResponse,
      time: timeString
    })
    
         // 3번 대화마다 새 버전 생성
     if (chatHistory.value.length % 6 === 0) {
       const newVersionNumber = Math.floor(chatHistory.value.length / 6) + 1
       versions.value.push({
         number: newVersionNumber,
         template: `버전 ${newVersionNumber} 템플릿`,
         messageIndex: chatHistory.value.length - 1
       })
     }
  }, 1000)
  
  chatInput.value = ''
}

// 버전 선택
const selectVersion = (versionNumber: number) => {
  currentVersion.value = versionNumber
  console.log(`버전 ${versionNumber} 선택됨`)
  // 여기서 해당 버전의 템플릿을 미리보기에 표시하는 로직 추가 가능
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
  padding: 2rem 0 0 0;
  overflow: auto;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.2rem;
  overflow-x: hidden;
}

.split-layout {
  display: flex;
  gap: 0;
  height: 100%;
  position: relative;
  min-width: 50rem;
}

.split-layout::after {
  content: '';
  position: absolute;
  left: calc(33.33% + 1rem);
  top: 0;
  bottom: 0;
  width: 0.1rem;
  background: linear-gradient(180deg, transparent, #e0e0e0, transparent);
  box-shadow: 0 0 0.5rem rgba(0, 0, 0, 0.1);
}

.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  padding-right: 2rem;
  min-width: 20rem;
}

.right-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  padding-left: 2rem;
  min-width: 16rem;
  overflow: auto;
}

.preview-and-sidebar-container {
  display: flex;
  gap: 1rem;
  transition: transform 0.3s ease;
  align-self: center;
}

.preview-and-sidebar-container.with-rejection-sidebar {
  transform: translateX(1rem);
}

.kakao-preview-wrapper {
  flex-shrink: 0;
  align-self: center;
}

.rejection-sidebar-panel {
  width: 14rem;
  max-width: 14rem;
  flex-shrink: 0;
  z-index: 10;
}

.variables-toggle {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 1rem;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  font-size: 0.9rem;
  color: #333;
}

.toggle-label input {
  display: none;
}

.toggle-slider {
  width: 2rem;
  height: 1rem;
  background-color: #ccc;
  border-radius: 0.5rem;
  position: relative;
  transition: background-color 0.2s ease;
}

.toggle-slider:before {
  content: '';
  position: absolute;
  width: 0.8rem;
  height: 0.8rem;
  background-color: white;
  border-radius: 50%;
  top: 0.1rem;
  left: 0.1rem;
  transition: transform 0.2s ease;
}

.toggle-label input:checked + .toggle-slider {
  background-color: #1976d2;
}

.toggle-label input:checked + .toggle-slider:before {
  transform: translateX(1rem);
}

.message-bubble {
  background-color: #f5f5f5;
  padding: 1rem;
  border-radius: 0.6rem;
  font-size: 1rem;
  line-height: 1.6;
  color: #333;
  height: 12.5rem;
}

.message-bubble p {
  margin: 0.4rem 0;
}

.version-button {
  display: flex;
  gap: 0.6rem;
  justify-content: center;
}

.btn-version {
  background-color: #666;
  color: white;
  border: none;
  padding: 0.25rem 0.6rem;
  border-radius: 0.3rem;
  font-weight: 500;
  cursor: pointer;
  flex: 1;
  max-width: 6rem;
}

.btn-version-modified {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 0.25rem 0.6rem;
  border-radius: 0.3rem;
  font-weight: 500;
  cursor: pointer;
  flex: 1;
  max-width: 6rem;
  transition: background-color 0.2s ease;
}

.btn-version-modified:hover {
  background-color: #218838;
}

.template-description {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 0.4rem;
  font-size: 0.95rem;
  line-height: 1.6;
  color: #555;
}

.template-description p {
  margin: 0;
}





/* 채팅 관련 스타일 */
.chat-history-container {
  background-color: white;
  border-radius: 0.6rem;
  padding: 1rem;
  height: 23.5rem;
  box-shadow: 0 0.1rem 0.4rem rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.chat-history {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  flex: 1;
  overflow-y: auto;
}

.chat-message {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.chat-message.user {
  align-items: flex-end;
}

.chat-message.bot {
  align-items: flex-start;
}

.message-content {
  padding: 0.6rem 0.8rem;
  border-radius: 0.9rem;
  max-width: 80%;
  word-wrap: break-word;
}

.chat-message.user .message-content {
  background-color: #1976d2;
  color: white;
}

.chat-message.bot .message-content {
  background-color: #f5f5f5;
  color: #333;
}

.message-time {
  font-size: 0.8rem;
  color: #666;
  margin: 0 0.4rem;
}

.version-creation-point {
  margin: 1rem 0;
  text-align: center;
}

.version-divider {
  position: relative;
  margin: 0.8rem 0;
}

.version-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 0.05rem;
  background: linear-gradient(90deg, transparent, #ddd, transparent);
}

.version-label {
  background: white;
  padding: 0 0.8rem;
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
  position: relative;
  z-index: 1;
}

.version-buttons {
  display: flex;
  gap: 0.4rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 0.6rem;
}

.btn-version {
  background-color: #666;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 1rem;
  font-weight: 500;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.btn-version:hover {
  background-color: #555;
}

.btn-version.active {
  background-color: #1976d2;
  transform: scale(1.05);
}

.chat-input-container {
  background-color: white;
  border-radius: 0.6rem;
  padding: 0.6rem;
  height: 3.5rem;
  box-shadow: 0 0.1rem 0.4rem rgba(0, 0, 0, 0.1);
}

.input-field {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  height: 100%;
}

.message-input {
  flex: 1;
  padding: 0.4rem 0.6rem;
  border: 0.05rem solid #ddd;
  border-radius: 1rem;
  font-size: 1rem;
  outline: none;
  height: 2rem;
}

.message-input:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 0.1rem rgba(25, 118, 210, 0.1);
}

.btn-send {
  background-color: #1976d2;
  color: white;
  border: none;
  padding: 0.4rem;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.1rem;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}

.btn-send:hover {
  background-color: #1565c0;
}

/* 액션 버튼들 스타일 */
.action-buttons-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.correction-count {
  background-color: #1976d2;
  color: white;
  padding: 0.4rem 0.8rem;
  border-radius: 1rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 0.6rem;
}

.btn-modify,
.btn-submit,
.btn-reject {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 0.2rem;
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
