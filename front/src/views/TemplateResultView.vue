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
              <div class="chat-history" ref="chatHistoryRef">
                <template v-for="(message, index) in chatHistory" :key="index">
                  <div :class="['chat-message', message.type]">
                    <div class="message-content">{{ message.content }}</div>
                    <div class="message-time">{{ message.time }}</div>
                  </div>
                  
                  <!-- 해당 메시지 다음에 버전 버튼 표시 -->
                  <div 
                    v-for="version in versions.filter((v: any) => v.messageIndex === index)" 
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
                  :is-modifying="false"
                  :is-rejected="isRejected"
                  :rejected-variables="rejectedVariables"
                  @variable-click="handleVariableClick"
                  @update-variables="updateVariables"
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
                  :validation-errors="currentVariable ? currentValidationError : validationErrors"
                  :validation-stage="validationStage"
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
                <button 
                  class="btn-submit" 
                  @click="submitTemplate"
                  :disabled="isValidating"
                >
                  <span v-if="!isValidating">제출하기</span>
                  <span v-else class="loading-content">
                    <span class="spinner"></span>
                    검증 중...
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>


  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import HeaderComponent from '@/components/HeaderComponent.vue'
import KakaoPreviewComponent from '@/components/KakaoPreviewComponent.vue'
import RejectionSidebarComponent from '@/components/RejectionSidebarComponent.vue'
import { templateApi } from '@/api'

const router = useRouter()

// 컴포넌트 refs
const chatHistoryRef = ref<HTMLElement | null>(null)

const showVariables = ref(true)
const showRejectionSidebar = ref(false)
const isRejected = ref(false)
const currentVariable = ref('')
const currentAlternatives = ref<any[]>([])
// 사용자 직접 수정 기능 제거
const rejectedVariables = ref<string[]>([])
const validationErrors = ref<any[]>([])
const currentValidationError = ref<any>(null)
const validationStage = ref<string>('') // 검증 단계 정보 추가

// 생성된 템플릿 데이터
const generatedTemplate = ref<any>(null)
const templateContent = ref('')
const templateTitle = ref('')
const templateVariables = ref<any[]>([])
const templateCategory = ref('')
const templateCategoryId = ref<number>(11) // 기본값: 기타
const userMessage = ref('')

// 채팅 관련 변수들
const chatInput = ref('')
const currentVersion = ref(1)
const chatHistory = ref<any[]>([])
const isGenerating = ref(false)
const isValidating = ref(false) // 검증 중 상태 추가

// 정정 횟수 관리 - 세션 기반
const maxCorrections = 3
const remainingCorrections = ref(maxCorrections) // 초기값을 maxCorrections로 설정, onMounted에서 세션 값으로 업데이트됨

// 세션 키 생성 함수
const getSessionKey = () => {
  // 항상 'template_modifications_new'를 사용하여 일관성 보장
  return 'template_modifications_new'
}

// 세션에서 남은 수정 횟수 가져오기
const getRemainingModifications = () => {
  try {
    const key = getSessionKey()
    const storedValue = sessionStorage.getItem(key)
    console.log(`세션에서 ${key} 키로 가져온 값:`, storedValue)
    
    if (storedValue === null || storedValue === undefined) {
      // 세션에 값이 없으면 기본값 3으로 설정하고 반환
      console.log('세션에 값이 없어서 기본값 3으로 설정')
      sessionStorage.setItem(key, maxCorrections.toString())
      return maxCorrections
    }
    
    const count = parseInt(storedValue, 10)
    if (isNaN(count) || count < 0) {
      console.log('유효하지 않은 값이므로 기본값 3으로 설정')
      sessionStorage.setItem(key, maxCorrections.toString())
      return maxCorrections
    }
    
    console.log(`세션에서 가져온 정정 횟수: ${count}`)
    return count
  } catch (error) {
    console.error('세션에서 정정 횟수를 가져오는 중 오류:', error)
    // 오류 발생 시 기본값 반환
    const key = getSessionKey()
    sessionStorage.setItem(key, maxCorrections.toString())
    return maxCorrections
  }
}

// 수정 횟수 감소
const decrementModificationCount = () => {
  try {
    const key = getSessionKey()
    const currentCount = remainingCorrections.value
    const newCount = Math.max(0, currentCount - 1)
    sessionStorage.setItem(key, newCount.toString())
    return newCount
  } catch (error) {
    console.error('정정 횟수 감소 중 오류:', error)
    return 0
  }
}


// 수정 횟수 리셋 테스트 함수들 (개발자 도구에서 사용) resetModifications() -> 3으로 리셋
const testResetModifications = () => {
  const key = getSessionKey()
  sessionStorage.setItem(key, '3')
  remainingCorrections.value = 3
  console.log('✅ 수정 횟수를 3으로 리셋했습니다.')
}

const testSetModifications = (count: number) => {
  const key = getSessionKey()
  sessionStorage.setItem(key, count.toString())
  remainingCorrections.value = count
  console.log(`✅ 수정 횟수를 ${count}로 설정했습니다.`)
}

// 전역으로 노출 (개발자 도구에서 사용 가능)
if (typeof window !== 'undefined') {
  ;(window as any).resetModifications = testResetModifications
  ;(window as any).setModifications = testSetModifications
}

// 버전 관리
const versions = ref([
  { number: 1, template: '기본 템플릿', messageIndex: 0, templateContent: '', templateTitle: '' }
])

// 각 버전의 템플릿 내용 저장
const versionTemplates = ref<Record<number, { content: string, title: string, variableList: string[] }>>({})

// 사용자가 수정할 수 있는 변수 값들
const editedVariables = ref<Record<string, string>>({})

// 컴포넌트 마운트 시 생성된 템플릿 데이터 로드
onMounted(() => {
  // 먼저 수정 횟수를 세션에서 가져와서 설정
  const sessionCorrections = getRemainingModifications()
  remainingCorrections.value = sessionCorrections
  
  const savedTemplate = sessionStorage.getItem('generatedTemplate')
  if (savedTemplate) {
    try {
      generatedTemplate.value = JSON.parse(savedTemplate)
      templateContent.value = generatedTemplate.value.templateContent
      templateTitle.value = generatedTemplate.value.templateTitle || ''
      templateVariables.value = generatedTemplate.value.variables
      templateCategory.value = generatedTemplate.value.category
      // templateCategoryId는 더 이상 사용되지 않지만, 혹시 모를 오류 방지를 위해 기본값 설정
      templateCategoryId.value = 11 
      userMessage.value = generatedTemplate.value.userMessage
      
      // 변수 값 초기화 (showVariables가 true이므로 변수값 설정)
      const initialVariables: Record<string, string> = {}
      templateVariables.value.forEach((variable: any) => {
        initialVariables[variable] = `${variable} 값`
      })
      editedVariables.value = initialVariables
      
      // 버전 1에 초기 템플릿 저장
      versionTemplates.value[1] = {
        content: templateContent.value,
        title: templateTitle.value,
        variableList: templateVariables.value
      }
      
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
      router.push('/')
    }
  } else {
    // 생성된 템플릿이 없으면 생성 페이지로 리다이렉트
    router.push('/')
  }
})
 


// 변수 클릭 처리
const handleVariableClick = (variableName: string) => {
  if (isRejected.value && rejectedVariables.value.includes(variableName)) {
    // 반려된 변수 클릭 시 - 대안 선택 사이드바 표시
    currentVariable.value = variableName
    
    // 해당 변수에 대한 검증 오류 찾기
    const variableErrors = validationErrors.value.filter(error => 
      error.variable_name === variableName || 
      (error.reason && error.reason.includes(variableName))
    )
    
    if (variableErrors.length > 0) {
      const error = variableErrors[0]
      currentValidationError.value = {
        variableName: variableName,
        errorMessage: error.reason,
        errorType: error.rule_type,
        validationStage: error.stage,
        rule: error.rule,
        suggestion: error.suggestion,
        severity: error.severity
      }
    } else {
      currentValidationError.value = null
    }
    
    // 대안 정보 설정 (백엔드에서 받은 대안)
    currentAlternatives.value = []
    showRejectionSidebar.value = true
  }
}



// 선택한 대안 적용
const applySelectedAlternative = (alternative: any) => {
  console.log(`대안 적용: ${currentVariable.value}를 "${alternative.text}"로 대체`)
  
  // 반려된 변수 목록에서 제거
  const index = rejectedVariables.value.indexOf(currentVariable.value)
  if (index > -1) {
    rejectedVariables.value.splice(index, 1)
  }
  
  // 모든 반려된 변수가 해결되면 반려 상태 해제
  if (rejectedVariables.value.length === 0) {
    isRejected.value = false
    showRejectionSidebar.value = false
  } else {
    // 다른 반려된 변수가 있으면 첫 번째로 이동
    currentVariable.value = ''
    currentAlternatives.value = []
  }
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

// 변수 업데이트
const updateVariables = (newVariables: any) => {
  editedVariables.value = { ...newVariables }
  
    // 강제로 리렌더링을 위해 nextTick 사용
    nextTick(() => {
      // 변수 업데이트 완료
    })
}

// 변수 토글 상태 변경 감지
watch(showVariables, (newValue) => {
  if (newValue && templateVariables.value.length > 0) {
    // 변수 토글을 활성화했을 때 변수값 설정
    const initialVariables: Record<string, string> = {}
      templateVariables.value.forEach((variable: any) => {
      initialVariables[variable.name] = `${variable.name} 값`
    })
    editedVariables.value = initialVariables
  }
})

// 채팅 히스토리 변경 감지하여 자동 스크롤
watch(chatHistory, () => {
  scrollToBottom()
}, { deep: true })


// 템플릿 제출
const submitTemplate = async () => {
  if (isValidating.value) return // 이미 검증 중이면 중복 실행 방지
  
  isValidating.value = true // 검증 시작
  try {
    console.log('템플릿 검증 요청 시작')
    
    // 제출 전 변수 맵 보정: 비어있으면 현재 템플릿 변수로 기본값 구성
    if (!editedVariables.value || Object.keys(editedVariables.value).length === 0) {
      const fallback: Record<string, string> = {}
        if (Array.isArray(templateVariables.value) && templateVariables.value.length > 0) {
          templateVariables.value.forEach((variableName: string) => {
          fallback[variableName] = `${variableName} 값`
        })
      } else if (templateContent.value) {
        // 변수 배열이 비어 있으면 템플릿 본문에서 변수 패턴을 파싱해 기본값 구성
        const patterns = [/\{\{([^}]+)\}\}/g, /#\{([^}]+)\}/g]
        const found = new Set<string>()
        patterns.forEach((re) => {
          let m
          while ((m = re.exec(templateContent.value)) !== null) {
            const name = (m[1] || '').trim()
            if (name) found.add(name)
          }
        })
        found.forEach((name) => { fallback[name] = `${name} 값` })
      }
      editedVariables.value = fallback
    }

    // 백엔드로 템플릿 검증 요청
    const response = await templateApi.validateTemplate(
      templateContent.value,
      editedVariables.value,
      templateCategory.value,
      userMessage.value,
      templateTitle.value
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
      
      // 백엔드에서 전달된 상세한 검증 결과 처리
      const validationResults = response.data.validation_results || []
      const stage = response.data.validationStage || '1차 검증'
      
      console.log('검증 결과:', validationResults)
      console.log('검증 단계:', stage)
      
      // 검증 결과에서 반려된 변수들과 상세 정보 추출
      const rejectedVars: string[] = []
      const detailedErrors: any[] = []
      
      validationResults.forEach((result: any) => {
        if (result.details && result.details.validation_details) {
          result.details.validation_details.forEach((detail: any) => {
            // 변수 관련 오류인 경우 반려된 변수 목록에 추가
            if (detail.variable_name && detail.severity === 'error') {
              rejectedVars.push(detail.variable_name)
            }
            
            // 모든 상세 오류 정보 저장
            detailedErrors.push({
              rule_type: detail.rule_type,
              rule: detail.rule,
              reason: detail.reason,
              suggestion: detail.suggestion,
              severity: detail.severity,
              variable_name: detail.variable_name || null,
              stage: result.stage || '1차 검증'
            })
          })
        }
      })
      
      // 중복 제거
      rejectedVariables.value = [...new Set(rejectedVars)]
      validationErrors.value = detailedErrors
      validationStage.value = stage
      isRejected.value = true
      showRejectionSidebar.value = true
      
      // 사용자에게 오류 메시지 표시 (검증 단계 포함)
      alert(`템플릿 검증 실패 (${stage}): ${response.data.message}`)
    }
  } catch (error) {
    console.error('템플릿 검증 실패:', error)
    alert('템플릿 검증 중 오류가 발생했습니다. 다시 시도해주세요.')
  } finally {
    isValidating.value = false // 검증 완료
  }
}

// 채팅 메시지 전송
const sendMessage = async () => {
  if (!chatInput.value.trim() || isGenerating.value) return
  
  // 수정 횟수 확인
  if (remainingCorrections.value <= 0) {
    alert('수정 횟수를 모두 사용했습니다. 더 이상 수정할 수 없습니다.')
    return
  }
  
  const now = new Date()
  const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  // 사용자 메시지 추가
  const userMessage = {
    type: 'user',
    content: chatInput.value,
    time: timeString
  }
  chatHistory.value.push(userMessage)
  
  // 사용자 메시지 추가 후 자동 스크롤
  scrollToBottom()
  
  const currentMessage = chatInput.value
  chatInput.value = ''
  isGenerating.value = true
  
  try {
    // 수정 횟수 감소 (성공 시에만)
    const newRemainingCount = decrementModificationCount()
    remainingCorrections.value = newRemainingCount
    
    // 백엔드 API를 통해 AI 서버에 템플릿 수정 요청
    // editedVariables를 string[] 형태로 변환
    const variableList = Object.keys(editedVariables.value)
    
    const response = await templateApi.modifyTemplate(
      templateContent.value,
      templateTitle.value,
      currentMessage,
      variableList,
      templateCategory.value,
      chatHistory.value
    )
    
    // AI 응답 추가 - 설명만 표시 (수정된 템플릿은 미리보기에서 확인)
    const explanation = response.data.explanation || '템플릿을 수정했습니다.'
    
    const botMessage = {
      type: 'bot',
      content: explanation,
      time: timeString
    }
    chatHistory.value.push(botMessage)
    
    // 봇 응답 추가 후 자동 스크롤
    scrollToBottom()
    
    // 템플릿 업데이트
    const newTemplateContent = response.data.modified_template || response.data.template_text || templateContent.value
    const templateChanged = newTemplateContent !== templateContent.value
    templateContent.value = newTemplateContent
    // 변수 처리 - 백엔드에서 variables 필드 사용
    if (response.data.variables && Array.isArray(response.data.variables)) {
      templateVariables.value = response.data.variables.map((variable: any) => 
        variable.name || variable // 문자열 배열로 변환
      )
    } else if (response.data.metadata && response.data.metadata.variablesDetected) {
      templateVariables.value = response.data.metadata.variablesDetected
    } else {
      // 응답 변수 비어 있으면 본문에서 파싱하여 변수 배열 생성
      const patterns = [/\{\{([^}]+)\}\}/g, /#\{([^}]+)\}/g]
      const found = new Set<string>()
      patterns.forEach((re) => {
        let m
        while ((m = re.exec(templateContent.value)) !== null) {
          const name = (m[1] || '').trim()
          if (name) found.add(name)
        }
      })
      templateVariables.value = Array.from(found) // 문자열 배열로 변환
    }
    // 제목 업데이트 (응답에 제목이 있다면)
    if (response.data.template_title) {
      templateTitle.value = response.data.template_title
    }
    
    // 변수 목록 업데이트: 응답 변수(없으면 파싱 결과) 기준으로 기본값 세팅
    const rebuilt: Record<string, string> = {}
    const sourceVars = (Array.isArray(response.data.variables) && response.data.variables.length > 0)
      ? response.data.variables.map((variable: any) => variable.name || variable)
      : templateVariables.value
    sourceVars.forEach((variableName: string) => {
      rebuilt[variableName] = variableName
    })
    editedVariables.value = rebuilt
    
    // 새 버전 생성
    const newVersionNumber = versions.value.length + 1
    versions.value.push({
      number: newVersionNumber,
      template: `버전 ${newVersionNumber} 템플릿`,
      messageIndex: chatHistory.value.length - 1,
      templateContent: templateContent.value,
      templateTitle: templateTitle.value
    })
    
    // 새 버전의 템플릿 내용 저장
    versionTemplates.value[newVersionNumber] = {
      content: templateContent.value,
      title: templateTitle.value,
      variableList: templateVariables.value
    }
    
    // 새 버전을 현재 선택된 버전으로 설정
    currentVersion.value = newVersionNumber
    
  } catch (error) {
    console.error('템플릿 수정 실패:', error)
    
    // 오류 발생 시 수정 횟수 복원
    const key = getSessionKey()
    const currentCount = remainingCorrections.value
    const restoredCount = Math.min(maxCorrections, currentCount + 1)
    sessionStorage.setItem(key, restoredCount.toString())
    remainingCorrections.value = restoredCount
    
    // 오류 메시지 추가
    const errorMessage = {
      type: 'bot',
      content: '죄송합니다. 템플릿 수정 중 오류가 발생했습니다. 다시 시도해주세요.',
      time: timeString
    }
    chatHistory.value.push(errorMessage)
    
    // 오류 메시지 추가 후 자동 스크롤
    scrollToBottom()
  } finally {
    isGenerating.value = false
  }
}

// 버전 선택
const selectVersion = (versionNumber: number) => {
  // 이미 선택된 버전이면 아무것도 하지 않음
  if (currentVersion.value === versionNumber) {
    return
  }
  
  currentVersion.value = versionNumber
  
  // 해당 버전의 템플릿 내용으로 업데이트
  const versionTemplate = versionTemplates.value[versionNumber]
  if (versionTemplate) {
    templateContent.value = versionTemplate.content
    templateTitle.value = versionTemplate.title
    templateVariables.value = versionTemplate.variableList
    
    // 변수 값 초기화
    const initialVariables: Record<string, string> = {}
    versionTemplate.variableList.forEach((variable: any) => {
      initialVariables[variable.name] = `${variable.name} 값`
    })
    editedVariables.value = initialVariables
    
    console.log(`버전 ${versionNumber} 템플릿으로 전환됨`)
  } else {
    console.warn(`버전 ${versionNumber}의 템플릿 데이터를 찾을 수 없습니다`)
  }
}

// 채팅 비활성화 조건 확인
const isChatDisabled = () => {
  return remainingCorrections.value <= 0 || isGenerating.value
}

// 채팅 placeholder 텍스트 결정
const getChatPlaceholder = () => {
  if (remainingCorrections.value <= 0) {
    return '정정 횟수가 모두 소진되었습니다.'
  } else if (isGenerating.value) {
    return 'AI가 응답을 생성 중입니다...'
  } else {
    return '메시지를 입력하세요...'
  }
}

// 채팅 자동 스크롤 함수
const scrollToBottom = () => {
  nextTick(() => {
    if (chatHistoryRef.value) {
      chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
    }
  })
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
  align-self: flex-start; /* 상단 정렬 */
  max-height: 80vh; /* 최대 높이 제한 */
  overflow: visible;
  margin-bottom: 1rem;
  width: 100%;
  justify-content: center;
  align-items: flex-start; /* 자식 요소들을 상단 정렬 */
}

/* 반려 사이드바가 열렸을 때의 상태 */
.preview-and-sidebar-container.with-rejection-sidebar {
  transform: translateX(-1rem);
}

/* 카카오톡 미리보기 래퍼 */
.kakao-preview-wrapper {
  flex-shrink: 0;
  align-self: flex-start; /* 상단 정렬 */
  max-height: 80vh; /* 최대 높이 제한 */
  overflow-y: auto;
  padding-right: 0.5rem;
  min-width: 20rem; /* 최소 너비 보장 */
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
  max-height: 80vh; /* 카카오 미리보기와 동일한 최대 높이 */
  flex-shrink: 0;
  z-index: 10;
  align-self: flex-start; /* 상단 정렬 */
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
.btn-submit {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 0.2rem;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s ease;
  position: relative;
  min-width: 6rem;
}

/* 제출 버튼 스타일 */
.btn-submit {
  background-color: #28a745;
}

/* 제출 버튼 호버 효과 */
.btn-submit:hover:not(:disabled) {
  background-color: #218838;
}

/* 제출 버튼 비활성화 상태 */
.btn-submit:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

/* 로딩 컨텐츠 */
.loading-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* 스피너 애니메이션 */
.spinner {
  width: 1rem;
  height: 1rem;
  border: 0.1rem solid #ffffff40;
  border-left: 0.1rem solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}


/* 수정 버튼 스타일 제거됨 */

/* 변수값 표시 토글 스타일 */
.variables-toggle {
  margin-bottom: 1rem;
  display: flex;
  justify-content: flex-start;
}

.toggle-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 0.9rem;
  color: #666;
  gap: 0.5rem;
}

.toggle-label input[type="checkbox"] {
  display: none;
}

.toggle-slider {
  position: relative;
  width: 3rem;
  height: 1.5rem;
  background-color: #ccc;
  border-radius: 1rem;
  transition: background-color 0.3s ease;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  top: 0.2rem;
  left: 0.2rem;
  width: 1.1rem;
  height: 1.1rem;
  background-color: white;
  border-radius: 50%;
  transition: transform 0.3s ease;
}

.toggle-label input[type="checkbox"]:checked + .toggle-slider {
  background-color: #4caf50;
}

.toggle-label input[type="checkbox"]:checked + .toggle-slider::before {
  transform: translateX(1.5rem);
}
</style>
