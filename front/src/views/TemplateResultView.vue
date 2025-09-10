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
                  :placeholder="getChatPlaceholder()"
                  class="message-input"
                  :disabled="isChatDisabled()"
                  @keyup.enter="sendMessage"
                />
                <button 
                  class="btn-send" 
                  :disabled="isChatDisabled() || !chatInput.trim()"
                  @click="sendMessage"
                >
                  ↑
                </button>
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
                  :template-content="templateContent"
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
                  :validation-error="currentValidationError"
                  @close="closeRejectionSidebar"
                  @variable-click="handleVariableClick"
                  @apply-alternative="applySelectedAlternative"
                />
              </div>
            </div>
            
            <!-- 액션 버튼들 -->
            <div class="action-buttons-container">
              <div class="correction-count">남은 정정 횟수: {{ remainingCorrections }}/{{ maxCorrections }}</div>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import HeaderComponent from '@/components/HeaderComponent.vue'
import KakaoPreviewComponent from '@/components/KakaoPreviewComponent.vue'
import RejectionSidebarComponent from '@/components/RejectionSidebarComponent.vue'
import { templateApi } from '@/api'

const router = useRouter()

const showVariables = ref(true)
const showRejectionSidebar = ref(false)
const isRejected = ref(false)
const currentVariable = ref('')
const currentAlternatives = ref<any[]>([])
const isModifying = ref(false)
const rejectedVariables = ref<string[]>([])
const validationErrors = ref<any[]>([])
const currentValidationError = ref<any>(null)

// 생성된 템플릿 데이터
const generatedTemplate = ref<any>(null)
const templateContent = ref('')
const templateVariables = ref<any[]>([])
const templateCategory = ref('')
const templateCategoryId = ref<number>(11) // 기본값: 기타
const userMessage = ref('')

// 채팅 관련 변수들
const chatInput = ref('')
const currentVersion = ref(1)
const chatHistory = ref<any[]>([])
const isGenerating = ref(false)

// 정정 횟수 관리
const maxCorrections = 3
const remainingCorrections = ref(maxCorrections)

// 버전 관리
const versions = ref([
  { number: 1, template: '기본 템플릿', messageIndex: 0 }
])

// 사용자가 수정할 수 있는 변수 값들
const editedVariables = ref<Record<string, string>>({
  recipient: '홍길동',
  sender: '저희 회사',
  couponName: '신규 가입 축하 쿠폰',
  expiryDate: '2024년 12월 31일까지',
  additionalMessage: '문의 사항은 언제든 편하게 연락주세요.'
})

// 컴포넌트 마운트 시 생성된 템플릿 데이터 로드
onMounted(() => {
  const savedTemplate = sessionStorage.getItem('generatedTemplate')
  if (savedTemplate) {
    try {
      generatedTemplate.value = JSON.parse(savedTemplate)
      templateContent.value = generatedTemplate.value.templateContent
      templateVariables.value = generatedTemplate.value.variables
      templateCategory.value = generatedTemplate.value.category
      templateCategoryId.value = generatedTemplate.value.categoryId || 11
      userMessage.value = generatedTemplate.value.userMessage
      
      // 변수 값 초기화
      const initialVariables: Record<string, string> = {}
      templateVariables.value.forEach((variable: any) => {
        // 변수명을 한글로 변환하여 더 친숙하게 표시
        const koreanNames: Record<string, string> = {
          'recipient': '수신자',
          'sender': '발신자',
          'couponName': '쿠폰명',
          'expiryDate': '사용기한',
          'additionalMessage': '추가 메시지'
        }
        const displayName = koreanNames[variable.name] || variable.name
        initialVariables[variable.name] = `${displayName} 값`
      })
      editedVariables.value = initialVariables
      
      // 채팅 히스토리 초기화 - 템플릿 생성 시 입력한 메시지를 첫 메시지로 설정
      const now = new Date()
      const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
      
      chatHistory.value = [
        {
          type: 'user',
          content: userMessage.value,
          time: timeString
        },
        {
          type: 'bot',
          content: `네, "${templateCategory.value}" 카테고리의 템플릿을 생성해드렸습니다. 추가로 수정하고 싶은 부분이 있으시면 말씀해주세요!`,
          time: timeString
        }
      ]
      
      console.log('생성된 템플릿 로드됨:', generatedTemplate.value)
    } catch (error) {
      console.error('템플릿 데이터 파싱 실패:', error)
      router.push('/template/create')
    }
  } else {
    // 생성된 템플릿이 없으면 생성 페이지로 리다이렉트
    router.push('/template/create')
  }
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
    // 반려된 변수 클릭 시 - 대안 선택 사이드바 표시
    currentVariable.value = variableName
    
    // 해당 변수에 대한 검증 오류 찾기
    const variableErrors = validationErrors.value.filter(error => error.variableName === variableName)
    currentValidationError.value = variableErrors.length > 0 ? variableErrors[0] : null
    
    // 대안 정보 설정 (기본값 또는 백엔드에서 받은 대안)
    currentAlternatives.value = JSON.parse(JSON.stringify(variableAlternatives[variableName as keyof typeof variableAlternatives] || []))
    showRejectionSidebar.value = true
  } else if (isModifying.value) {
    // 수정 모드에서 변수 클릭 시 - 직접 편집 가능하도록 처리
    console.log(`변수 "${variableName}" 편집 시작`)
    // KakaoPreviewComponent에서 직접 편집이 가능하도록 처리됨
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
  validationErrors.value = []
  currentVariable.value = ''
  currentAlternatives.value = []
  currentValidationError.value = null
}

// 수정 모드 토글
const toggleModification = () => {
  isModifying.value = !isModifying.value
  
  if (isModifying.value) {
    // 수정 모드 진입 시 사용자에게 안내
    console.log('수정 모드 활성화: 변수 부분을 클릭하여 편집할 수 있습니다.')
  } else {
    // 수정 모드 종료 시 변경사항 저장
    console.log('수정 모드 비활성화: 변경사항이 저장되었습니다.')
  }
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
const submitTemplate = async () => {
  try {
    console.log('템플릿 검증 요청 시작')
    
    // 백엔드로 템플릿 검증 요청
    const response = await templateApi.validateTemplate(
      templateContent.value,
      editedVariables.value,
      templateCategory.value,
      userMessage.value
    )
    
    console.log('템플릿 검증 응답:', response.data)
    
    if (response.data.success) {
      // 검증 성공 - 성공 페이지로 이동
      console.log('템플릿 검증 성공, 저장된 템플릿 ID:', response.data.templateId)
      // 성공 페이지로 이동하면서 템플릿 ID 전달
      router.push({
        path: '/success',
        query: { templateId: response.data.templateId }
      })
    } else {
      // 검증 실패 - 반려 사유 표시
      console.log('템플릿 검증 실패:', response.data.message)
      console.log('전체 검증 응답:', response.data)
      
      // 백엔드에서 전달된 반려된 변수들 사용
      const rejectedVars = response.data.rejectedVariables || []
      const errors = response.data.validationErrors || []
      console.log('반려된 변수들:', rejectedVars)
      console.log('검증 오류 상세:', errors)
      
      rejectedVariables.value = rejectedVars
      validationErrors.value = errors
      isRejected.value = true
      showRejectionSidebar.value = true
      
      // 사용자에게 오류 메시지 표시
      alert(`템플릿 검증 실패: ${response.data.message}`)
    }
  } catch (error) {
    console.error('템플릿 검증 실패:', error)
    alert('템플릿 검증 중 오류가 발생했습니다. 다시 시도해주세요.')
  }
}

// 채팅 메시지 전송
const sendMessage = async () => {
  if (!chatInput.value.trim() || isGenerating.value) return
  
  const now = new Date()
  const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  // 사용자 메시지 추가
  const userMessage = {
    type: 'user',
    content: chatInput.value,
    time: timeString
  }
  chatHistory.value.push(userMessage)
  
  const currentMessage = chatInput.value
  chatInput.value = ''
  isGenerating.value = true
  
  try {
    // 정정 횟수 감소
    remainingCorrections.value--
    
    // AI 서버에 템플릿 수정 요청
    const response = await templateApi.modifyTemplate(
      templateContent.value,
      currentMessage,
      chatHistory.value
    )
    
    // AI 응답 추가
    const botMessage = {
      type: 'bot',
      content: response.data.explanation,
      time: timeString
    }
    chatHistory.value.push(botMessage)
    
    // 템플릿 업데이트
    templateContent.value = response.data.modified_template
    templateVariables.value = response.data.variables
    
    // 변수 값 업데이트
    const updatedVariables: Record<string, string> = {}
    response.data.variables.forEach((variable: any) => {
      const koreanNames: Record<string, string> = {
        'recipient': '수신자',
        'sender': '발신자',
        'couponName': '쿠폰명',
        'expiryDate': '사용기한',
        'additionalMessage': '추가 메시지'
      }
      const displayName = koreanNames[variable.name] || variable.name
      updatedVariables[variable.name] = `${displayName} 값`
    })
    editedVariables.value = updatedVariables
    
    // 새 버전 생성
    const newVersionNumber = versions.value.length + 1
    versions.value.push({
      number: newVersionNumber,
      template: `버전 ${newVersionNumber} 템플릿`,
      messageIndex: chatHistory.value.length - 1
    })
    
    console.log('템플릿 수정 완료:', response.data)
    
  } catch (error) {
    console.error('템플릿 수정 실패:', error)
    
    // 오류 발생 시 정정 횟수 복원
    remainingCorrections.value++
    
    // 오류 메시지 추가
    const errorMessage = {
      type: 'bot',
      content: '죄송합니다. 템플릿 수정 중 오류가 발생했습니다. 다시 시도해주세요.',
      time: timeString
    }
    chatHistory.value.push(errorMessage)
  } finally {
    isGenerating.value = false
  }
}

// 버전 선택
const selectVersion = (versionNumber: number) => {
  currentVersion.value = versionNumber
  console.log(`버전 ${versionNumber} 선택됨`)
  // 여기서 해당 버전의 템플릿을 미리보기에 표시하는 로직 추가 가능
}

// 채팅 비활성화 조건 확인
const isChatDisabled = () => {
  return remainingCorrections.value <= 0 || isGenerating.value || isModifying.value
}

// 채팅 placeholder 텍스트 결정
const getChatPlaceholder = () => {
  if (remainingCorrections.value <= 0) {
    return '정정 횟수가 모두 소진되었습니다.'
  } else if (isModifying.value) {
    return '사용자 수정 모드입니다. 수정 완료 후 채팅이 가능합니다.'
  } else if (isGenerating.value) {
    return 'AI가 응답을 생성 중입니다...'
  } else {
    return '메시지를 입력하세요...'
  }
}
</script>

<style scoped>
/* 전체 컨테이너 스타일 */
.template-result-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* 메인 콘텐츠 영역 */
.main-content {
  flex: 1;
  background: linear-gradient(135deg, #E3F2FD 0%, #F1F8E9 100%);
  padding: 2rem 0 0 0;
  overflow: auto;
}

/* 콘텐츠 래퍼 */
.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.2rem;
}

/* 좌우 분할 레이아웃 */
.split-layout {
  display: flex;
  gap: 0;
  height: 100%;
  position: relative;
  min-width: 50rem;
}

/* 분할선 스타일 */
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

/* 왼쪽 패널 (채팅 영역) */
.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  padding-right: 2rem;
  width: 20rem;
}

/* 오른쪽 패널 (미리보기 영역) */
.right-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  padding-left: 2rem;
  min-width: 22rem;
  overflow: visible;
  position: relative;
}

/* 미리보기와 사이드바 컨테이너 */
.preview-and-sidebar-container {
  display: flex;
  gap: 1rem;
  transition: transform 0.3s ease;
  align-self: center;
  max-height: 80vh;
  overflow: visible;
  margin-bottom: 1rem;
  width: 100%;
  justify-content: center;
}

/* 반려 사이드바가 열렸을 때의 상태 */
.preview-and-sidebar-container.with-rejection-sidebar {
  transform: translateX(-1rem);
}

/* 카카오톡 미리보기 래퍼 */
.kakao-preview-wrapper {
  flex-shrink: 0;
  align-self: center;
  max-height: 80vh;
  overflow-y: auto;
  padding-right: 0.5rem;
}

/* 스크롤바 스타일링 */
.kakao-preview-wrapper::-webkit-scrollbar {
  width: 0.4rem;
}

.kakao-preview-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 0.2rem;
}

.kakao-preview-wrapper::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 0.2rem;
}

.kakao-preview-wrapper::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 반려 사이드바 패널 */
.rejection-sidebar-panel {
  width: 20rem;
  min-width: 20rem;
  max-width: 20rem;
  flex-shrink: 0;
  z-index: 10;
}

/* 변수값 표시 토글 */
.variables-toggle {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 1rem;
}

/* 토글 라벨 */
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

/* 토글 슬라이더 */
.toggle-slider {
  width: 2rem;
  height: 1rem;
  background-color: #ccc;
  border-radius: 0.5rem;
  position: relative;
  transition: background-color 0.2s ease;
}

/* 토글 슬라이더 내부 원형 버튼 */
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

/* 토글 활성화 상태 */
.toggle-label input:checked + .toggle-slider {
  background-color: #1976d2;
}

/* 토글 활성화 시 슬라이더 버튼 이동 */
.toggle-label input:checked + .toggle-slider:before {
  transform: translateX(1rem);
}

/* 메시지 버블 */
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

/* 버전 버튼 컨테이너 */
.version-button {
  display: flex;
  gap: 0.6rem;
  justify-content: center;
}

/* 버전 버튼 기본 스타일 */
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

/* 수정된 버전 버튼 스타일 */
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

/* 템플릿 설명 */
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





/* ===== 채팅 관련 스타일 ===== */
/* 채팅 이력 컨테이너 */
.chat-history-container {
  background-color: white;
  border-radius: 0.6rem;
  padding: 1rem;
  height: 32rem;
  box-shadow: 0 0.1rem 0.4rem rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

/* 채팅 이력 목록 */
.chat-history {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  flex: 1;
  overflow-y: auto;
}

/* 개별 채팅 메시지 */
.chat-message {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

/* 사용자 메시지 정렬 */
.chat-message.user {
  align-items: flex-end;
}

/* 봇 메시지 정렬 */
.chat-message.bot {
  align-items: flex-start;
}

/* 메시지 내용 스타일 */
.message-content {
  padding: 0.6rem 0.8rem;
  border-radius: 0.9rem;
  max-width: 80%;
  word-wrap: break-word;
}

/* 사용자 메시지 배경색 */
.chat-message.user .message-content {
  background-color: #1976d2;
  color: white;
}

/* 봇 메시지 배경색 */
.chat-message.bot .message-content {
  background-color: #f5f5f5;
  color: #333;
}

/* 메시지 시간 표시 */
.message-time {
  font-size: 0.8rem;
  color: #666;
  margin: 0 0.4rem;
}

/* 버전 생성 지점 */
.version-creation-point {
  margin: 1rem 0;
  text-align: center;
}

/* 버전 구분선 */
.version-divider {
  position: relative;
  margin: 0.8rem 0;
}

/* 버전 구분선 스타일 */
.version-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 0.05rem;
  background: linear-gradient(90deg, transparent, #ddd, transparent);
}

/* 버전 라벨 */
.version-label {
  background: white;
  padding: 0 0.8rem;
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
  position: relative;
  z-index: 1;
}

/* 버전 버튼들 */
.version-buttons {
  display: flex;
  gap: 0.4rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 0.6rem;
}

/* 버전 버튼 기본 스타일 (채팅 영역) */
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

/* 버전 버튼 호버 효과 */
.btn-version:hover {
  background-color: #555;
}

/* 활성화된 버전 버튼 */
.btn-version.active {
  background-color: #1976d2;
  transform: scale(1.05);
}

/* 채팅 입력 컨테이너 */
.chat-input-container {
  background-color: white;
  border-radius: 0.6rem;
  padding: 0.6rem;
  height: 3.5rem;
  box-shadow: 0 0.1rem 0.4rem rgba(0, 0, 0, 0.1);
}

/* 입력 필드 컨테이너 */
.input-field {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  height: 100%;
}

/* 메시지 입력 필드 */
.message-input {
  flex: 1;
  padding: 0.4rem 0.6rem;
  border: 0.05rem solid #ddd;
  border-radius: 1rem;
  font-size: 1rem;
  outline: none;
  height: 2rem;
}

/* 메시지 입력 필드 포커스 상태 */
.message-input:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 0.1rem rgba(25, 118, 210, 0.1);
}

/* 메시지 입력 필드 비활성화 상태 */
.message-input:disabled {
  background-color: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

/* 전송 버튼 */
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

/* 전송 버튼 호버 효과 */
.btn-send:hover:not(:disabled) {
  background-color: #1565c0;
}

/* 전송 버튼 비활성화 상태 */
.btn-send:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

/* ===== 액션 버튼들 스타일 ===== */
/* 액션 버튼 컨테이너 */
.action-buttons-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  position: absolute;
  bottom: -2rem;
  left: 0;
  right: 0;
  padding: 1rem 0;
  border-top: 0.05rem solid #e0e0e0;
}

/* 정정 횟수 표시 */
.correction-count {
  background-color: #1976d2;
  color: white;
  padding: 0.4rem 0.8rem;
  border-radius: 1rem;
  font-size: 0.9rem;
  font-weight: 500;
  margin-left: 1rem;
}

/* 액션 버튼들 */
.action-buttons {
  display: flex;
  gap: 0.6rem;
}

/* 공통 버튼 스타일 */
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

/* 제출 버튼 스타일 */
.btn-submit {
  background-color: #28a745;
}

/* 제출 버튼 호버 효과 */
.btn-submit:hover {
  background-color: #218838;
}

/* 반려 버튼 스타일 */
.btn-reject {
  background-color: #dc3545;
}

/* 반려 버튼 호버 효과 */
.btn-reject:hover {
  background-color: #c82333;
}

/* 수정 버튼 호버 효과 */
.btn-modify:hover {
  background-color: #5a6268;
}
</style>
