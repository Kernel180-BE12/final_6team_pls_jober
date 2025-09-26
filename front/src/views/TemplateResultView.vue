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
              <div class="kakao-preview-wrapper" ref="kakaoPreviewRef">
                <KakaoPreviewComponent
                  :template-content="getPreviewTemplateContent()"
                  :template-title="templateTitle"
                  :show-variables="showVariables"
                  :variables="editedVariables"
                  :is-rejected="isRejected"
                  :problem-areas="problemAreas"
                  :rejected-variables="rejectedVariables"
                  :highlighted-problem-area="currentProblemArea"
                  :modified-areas="Array.from(modifiedAreas)"
                  @problem-area-click="handleProblemAreaClick"
                  @update-variables="updateVariables"
                  @submit-template="handlePrimary"
                />
              </div>
              
              <!-- 반려 사이드바 -->
              <div class="rejection-sidebar-panel" v-if="showRejectionSidebar">
                <RejectionSidebarComponent
                  :show="showRejectionSidebar"
                  :current-problem-area="currentProblemArea"
                  :alternatives="currentAlternatives"
                  :problem-areas="problemAreas"
                  :validation-stage="validationStage"
                  :total-errors="totalErrors"
                  :total-warnings="totalWarnings"
                  :alimtalk-height="alimtalkHeight"
                  @close="closeRejectionSidebar"
                  @problem-area-click="handleProblemAreaClick"
                  @apply-alternative="applyAlternativeToTemplate"
                />
              </div>
            </div>
            
            <!-- 액션 버튼들 -->
            <div class="action-buttons-container">
              <div class="correction-count">남은 정정 횟수: {{ remainingCorrections }}/{{ maxCorrections }}</div>
              <div class="action-buttons">
                <button
                  class="btn-submit"
                  @click="handlePrimary"
                  :disabled="isBusy"
                >
                  <span v-if="!isBusy">{{ primaryLabel }}</span>
                  <span v-else class="loading-content">
                    <span class="spinner"></span>
                    {{ stage === 'edit' ? '저장 중...' : '검증/제출 중...' }}
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
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import HeaderComponent from '@/components/HeaderComponent.vue'
import KakaoPreviewComponent from '@/components/KakaoPreviewComponent.vue'
import RejectionSidebarComponent from '@/components/RejectionSidebarComponent.vue'
import { templateApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 컴포넌트 refs
const chatHistoryRef = ref<HTMLElement | null>(null)
const kakaoPreviewRef = ref<HTMLElement | null>(null)
const alimtalkHeight = ref<number>(0)

const showVariables = ref(true)
const showRejectionSidebar = ref(false)
const isRejected = ref(false)
const currentProblemArea = ref<any>(null)
const currentAlternatives = ref<any[]>([])
const problemAreas = ref<any[]>([])  // 문제 영역 목록
const validationStage = ref<string>('') // 검증 단계 정보 추가
const totalErrors = ref(0)
const totalWarnings = ref(0)
const rejectedVariables = ref<string[]>([]) // 반려된 변수 목록
const modifiedAreas = ref<Set<string>>(new Set()) // 수정된 영역 ID 추적

const templateContent = ref('')
const templateTitle = ref('')
const templateVariables = ref<any[]>([])
const templateCategory = ref('')
const templateCategoryId = ref<number | null>(null) // 백엔드에서 카테고리 이름으로 처리
const userMessage = ref('')

// 채팅 관련 변수들
const chatInput = ref('')
const currentVersion = ref(1)
const chatHistory = ref<any[]>([])
const isGenerating = ref(false)
const isValidating = ref(false) // 검증 중 상태 추가
const isSaving = ref(false) // 저장 중 상태 추가

// 단계 플래그: 채팅수정(edit) vs 검증(validate)
type Stage = 'edit' | 'validate'
// 기본은 채팅 단계. 검증 화면이라면 라우트로 'validate'를 주입해도 됨.
const stage = ref<Stage>(
  (router.currentRoute.value.query.stage as Stage) || 'edit'
)

// 공통 버튼 레이블/상태
const primaryLabel = computed(() => stage.value === 'edit' ? '저장하기' : '제출하기')
const isBusy = computed(() => stage.value === 'edit' ? isSaving.value : isValidating.value)

// 공통 버튼 핸들러
const handlePrimary = () => {
  if (stage.value === 'edit') return saveTemplate()
  else return submitTemplate()
}

// 정정 횟수 관리 - 세션 기반
const maxCorrections = 10 // 수정 횟수 10번으로 설정
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
      // 세션에 값이 없으면 기본값 10으로 설정하고 반환
      console.log('세션에 값이 없어서 기본값 10으로 설정')
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


// 수정 횟수 리셋 테스트 함수들 (개발자 도구에서 사용) resetModifications() -> 10으로 리셋
const testResetModifications = () => {
  const key = getSessionKey()
  sessionStorage.setItem(key, '10')
  remainingCorrections.value = 10
  console.log('✅ 수정 횟수를 리셋했습니다.')
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
const editedVariables = ref<string[]>([])

// 저장된 템플릿 ID
const savedTemplateId = ref<string | null>(null)

// 컴포넌트 마운트 시 생성된 템플릿 데이터 로드
onMounted(() => {
  // 먼저 수정 횟수를 세션에서 가져와서 설정
  const sessionCorrections = getRemainingModifications()
  remainingCorrections.value = sessionCorrections
  
  const savedTemplate = sessionStorage.getItem('generatedTemplate')
  if (savedTemplate) {
    try {
      const generatedTemplate = JSON.parse(savedTemplate)
      templateContent.value = generatedTemplate.templateContent
      templateTitle.value = generatedTemplate.templateTitle || ''
      templateVariables.value = generatedTemplate.variables
      templateCategory.value = generatedTemplate.category
      // templateCategoryId는 백엔드에서 카테고리 이름으로 처리되므로 null로 설정
      templateCategoryId.value = null
      userMessage.value = generatedTemplate.userMessage
      
      // 변수명 초기화
      editedVariables.value = [...templateVariables.value]
      
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
      
      console.log('생성된 템플릿 로드됨:', generatedTemplate)
      
      // 템플릿 로드 후 알림톡 높이 측정
      measureAlimtalkHeight()
    } catch (error) {
      console.error('템플릿 데이터 파싱 실패:', error)
      router.push('/')
    }
  } else {
    // 생성된 템플릿이 없으면 생성 페이지로 리다이렉트
    router.push('/')
  }
})



// 문제 영역 클릭 처리
const handleProblemAreaClick = (problemArea: any) => {
  if (isRejected.value) {
    // 문제 영역 클릭 시 - 대안 선택 사이드바 표시
    currentProblemArea.value = problemArea
    
    // 대안 정보 설정 (백엔드에서 받은 대안)
    currentAlternatives.value = problemArea.alternatives?.map((alt: string) => ({
      text: alt,
      selected: false
    })) || []
    
    showRejectionSidebar.value = true
  }
}




// ID 마커 기반 편집 시스템 - 문제 영역을 마커로 감싸고 대안 적용
const applyAlternativeToTemplate = (alternative: any, problemArea: any) => {
  console.log('=== ID 마커 기반 대안 적용 시작 ===')
  console.log('받은 이벤트 데이터:', { alternative, problemArea })
  console.log('대안 텍스트:', alternative.text)
  console.log('문제 영역 ID:', problemArea.area_id)
  console.log('문제 텍스트:', problemArea.problem_text)
  console.log('현재 템플릿 내용:', templateContent.value)
  
  try {
    // 대안 텍스트에서 실제 수정 내용 추출
    const alternativeText = alternative.text
    const modifiedText = extractModifiedTextFromAlternative(alternativeText)
    console.log('추출된 수정 텍스트:', modifiedText)
    
    if (!modifiedText) {
      console.warn('수정할 텍스트를 추출할 수 없습니다:', alternativeText)
      alert('대안 텍스트를 처리할 수 없습니다. 다시 시도해주세요.')
      return
    }
    
    // 범용적인 불릿 포인트 삭제 처리
    if (modifiedText.startsWith('REMOVE_') && modifiedText.endsWith('_BULLET')) {
      const bulletType = modifiedText.replace('REMOVE_', '').replace('_BULLET', '')
      console.log(`${bulletType} 불릿 포인트 삭제 처리`)
      const removeSuccessful = removeBulletPoint(bulletType, problemArea)
      if (removeSuccessful) {
        console.log(`✅ ${bulletType} 불릿 포인트 삭제 성공!`)
        
        // 수정된 영역을 추적에 추가
        modifiedAreas.value.add(problemArea.area_id)
        console.log('수정된 영역 추가됨:', problemArea.area_id)
        
        // 해당 문제 영역을 해결된 것으로 처리
        const areaIndex = problemAreas.value.findIndex(area => area.area_id === problemArea.area_id)
        if (areaIndex > -1) {
          problemAreas.value.splice(areaIndex, 1)
          console.log('문제 영역 제거됨:', problemArea.area_id)
        }
        
        // 모든 문제 영역이 해결되면 반려 상태 해제
        if (problemAreas.value.length === 0) {
          isRejected.value = false
          showRejectionSidebar.value = false
          console.log('모든 문제 영역 해결됨, 반려 상태 해제')
        }
        
        // 사용자에게 성공 메시지 표시
        setTimeout(() => {
          alert(`✅ ${bulletType} 불릿 포인트가 성공적으로 삭제되었습니다!`)
        }, 100)
        return
      } else {
        console.error(`❌ ${bulletType} 불릿 포인트 삭제 실패`)
        setTimeout(() => {
          alert(`❌ ${bulletType} 불릿 포인트 삭제에 실패했습니다. 수동으로 수정해주세요.`)
        }, 100)
        return
      }
    }
    
    // ID 마커 기반 교체 시도
    const replacementSuccessful = applyWithMarkerSystem(problemArea, modifiedText)
    
    if (replacementSuccessful) {
      console.log('✅ ID 마커 기반 템플릿 수정 성공!')
      console.log('수정된 템플릿 내용:', templateContent.value)
      
      // 수정된 영역을 추적에 추가
      modifiedAreas.value.add(problemArea.area_id)
      console.log('수정된 영역 추가됨:', problemArea.area_id)
      
      // 해당 문제 영역을 해결된 것으로 처리
      const areaIndex = problemAreas.value.findIndex(area => area.area_id === problemArea.area_id)
      if (areaIndex > -1) {
        problemAreas.value.splice(areaIndex, 1)
        console.log('문제 영역 제거됨:', problemArea.area_id)
      }
      
      // 모든 문제 영역이 해결되면 반려 상태 해제
      if (problemAreas.value.length === 0) {
        isRejected.value = false
        showRejectionSidebar.value = false
        console.log('모든 문제 영역 해결됨, 반려 상태 해제')
      }
      
      // 사용자에게 성공 메시지 표시
      setTimeout(() => {
        alert('✅ 대안이 성공적으로 적용되었습니다!')
      }, 100)
      
    } else {
      console.error('❌ ID 마커 기반 교체 실패')
      console.log('문제 영역 정보:', problemArea)
      console.log('수정할 텍스트:', modifiedText)
      console.log('현재 템플릿:', templateContent.value)
      
      // 사용자에게 실패 메시지 표시
      setTimeout(() => {
        alert('❌ 대안 적용에 실패했습니다. 수동으로 수정해주세요.')
      }, 100)
    }
    
  } catch (error) {
    console.error('대안 적용 중 오류 발생:', error)
    setTimeout(() => {
      alert('대안 적용 중 오류가 발생했습니다. 다시 시도해주세요.')
    }, 100)
  }
}

// ID 마커 기반 편집 시스템 구현 (다중 수정 지원)
const applyWithMarkerSystem = (problemArea: any, modifiedText: string): boolean => {
  console.log('=== ID 마커 기반 편집 시스템 시작 (다중 수정 지원) ===')
  
  const markerId = problemArea.area_id || `ERR${Date.now()}`
  const originalText = problemArea.problem_text
  
  console.log('마커 ID:', markerId)
  console.log('원본 텍스트:', originalText)
  console.log('수정할 텍스트:', modifiedText)
  console.log('현재 템플릿에 마커 존재 여부:', templateContent.value.includes(`⟦${markerId}⟧`))
  
  // 1. 다중 수정을 위한 마커 업데이트 시도 (기존 마커가 있는 경우)
  if (templateContent.value.includes(`⟦${markerId}⟧`)) {
    console.log('기존 마커 발견, 다중 수정 모드')
    const updateResult = updateMarkerForMultipleEdits(problemArea, modifiedText)
    if (updateResult) {
      console.log('✅ 다중 수정 마커 업데이트 성공')
      return true
    }
  }
  
  // 2. ID 마커로 감싸기 시도 (새로운 마커 생성)
  const markerResult = tryMarkerWrapping(markerId, originalText, modifiedText, problemArea)
  if (markerResult.success) {
    console.log('✅ ID 마커 기반 교체 성공')
    templateContent.value = markerResult.template
    return true
  }
  
  // 3. 백업 앵커 시스템 시도
  const anchorResult = tryContextAnchorSystem(problemArea, modifiedText)
  if (anchorResult.success) {
    console.log('✅ 백업 앵커 시스템 교체 성공')
    templateContent.value = anchorResult.template
    return true
  }
  
  console.log('❌ 모든 교체 방법 실패')
  return false
}

// ID 마커로 감싸기 (권장 최우선 방법)
const tryMarkerWrapping = (markerId: string, originalText: string, modifiedText: string, problemArea?: any): { success: boolean, template: string } => {
  console.log('=== ID 마커로 감싸기 시도 ===')
  console.log('마커 ID:', markerId)
  console.log('원본 텍스트:', originalText)
  console.log('수정된 텍스트:', modifiedText)
  
  const template = templateContent.value
  const markerStart = `⟦${markerId}⟧`
  const markerEnd = `⟦/${markerId}⟧`
  
  // 1. 이미 마커가 있는지 확인
  const existingMarkerPattern = new RegExp(`⟦${markerId}⟧([^⟦]*)⟦/${markerId}⟧`, 'g')
  if (existingMarkerPattern.test(template)) {
    console.log('기존 마커 발견, 마커 내부만 교체')
    const newTemplate = template.replace(existingMarkerPattern, `${markerStart}${modifiedText}${markerEnd}`)
    return { success: true, template: newTemplate }
  }
  
  // 2. 원본 텍스트를 마커로 감싸기 (정확한 매칭)
  if (template.includes(originalText)) {
    console.log('원본 텍스트를 마커로 감싸기')
    const newTemplate = template.replace(originalText, `${markerStart}${modifiedText}${markerEnd}`)
    return { success: true, template: newTemplate }
  }
  
  // 3. 정규화된 텍스트 매칭 시도 (공백 차이 무시)
  const normalizedOriginal = originalText.replace(/\s+/g, ' ').trim()
  const normalizedTemplate = template.replace(/\s+/g, ' ')
  
  if (normalizedTemplate.includes(normalizedOriginal)) {
    console.log('정규화된 텍스트 매칭으로 마커 적용')
    // 원본 템플릿에서 해당 부분을 찾아서 교체
    const regex = new RegExp(originalText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')
    const newTemplate = template.replace(regex, `${markerStart}${modifiedText}${markerEnd}`)
    return { success: true, template: newTemplate }
  }
  
  // 4. 위치 기반으로 마커 삽입 시도
  if (problemArea && problemArea.start_position !== undefined && problemArea.end_position !== undefined) {
    console.log('위치 기반 마커 삽입 시도')
    const beforeText = template.substring(0, problemArea.start_position)
    const afterText = template.substring(problemArea.end_position)
    const newTemplate = beforeText + `${markerStart}${modifiedText}${markerEnd}` + afterText
    return { success: true, template: newTemplate }
  }
  
  // 5. 키워드 기반 삽입 시도
  const keywords = originalText.split(/\s+/).filter(word => word.length > 2)
  if (keywords.length > 0) {
    console.log('키워드 기반 마커 삽입 시도:', keywords)
    for (const keyword of keywords) {
      if (template.includes(keyword)) {
        const regex = new RegExp(`\\b${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'g')
        const newTemplate = template.replace(regex, `${markerStart}${modifiedText}${markerEnd}`)
        return { success: true, template: newTemplate }
      }
    }
  }
  
  console.log('ID 마커로 감싸기 실패')
  return { success: false, template: template }
}

// 백업 앵커 시스템 (내용 기반 앵커링)
const tryContextAnchorSystem = (problemArea: any, modifiedText: string): { success: boolean, template: string } => {
  console.log('=== 백업 앵커 시스템 시도 ===')
  
  const template = templateContent.value
  const originalText = problemArea.problem_text
  
  // 1. 문맥 기반 매칭 시도
  if (problemArea.search_methods) {
    const contextResult = tryContextBasedMatching(problemArea, modifiedText)
    if (contextResult.success) {
      return contextResult
    }
  }
  
  // 2. 정확한 텍스트 매칭 시도
  if (template.includes(originalText)) {
    console.log('정확한 텍스트 매칭 성공')
    const newTemplate = template.replace(originalText, modifiedText)
    return { success: true, template: newTemplate }
  }
  
  
  console.log('백업 앵커 시스템 실패')
  return { success: false, template: template }
}

// 문맥 기반 매칭
const tryContextBasedMatching = (problemArea: any, modifiedText: string): { success: boolean, template: string } => {
  console.log('=== 문맥 기반 매칭 시도 ===')
  
  const template = templateContent.value
  const searchMethods = problemArea.search_methods
  
  if (!searchMethods) {
    return { success: false, template: template }
  }
  
  const exactText = searchMethods.exact_text
  const contextBefore = searchMethods.context_before || ''
  const contextAfter = searchMethods.context_after || ''
  
  // 1. 문맥 + 정확한 텍스트 매칭
  if (exactText && (contextBefore || contextAfter)) {
    const fullPattern = contextBefore + exactText + contextAfter
    if (template.includes(fullPattern)) {
      console.log('문맥 + 정확한 텍스트 매칭 성공')
      const newTemplate = template.replace(fullPattern, contextBefore + modifiedText + contextAfter)
      return { success: true, template: newTemplate }
    }
  }
  
  // 2. 정확한 텍스트만 매칭
  if (exactText && template.includes(exactText)) {
    console.log('정확한 텍스트 매칭 성공')
    const newTemplate = template.replace(exactText, modifiedText)
    return { success: true, template: newTemplate }
  }
  
  return { success: false, template: template }
}




// 대안 텍스트에서 실제 수정될 텍스트 추출 (제약사항 태그와 설명 제거)
const extractModifiedTextFromAlternative = (alternativeText: string): string | null => {
  console.log('=== 대안 텍스트 추출 시작 ===')
  console.log('원본 대안 텍스트:', alternativeText)
  
  // 1. 제약사항 태그 제거 (⟦constraint_...⟧...⟦/constraint_...⟧)
  let cleanText = alternativeText.replace(/⟦constraint_[^⟦]+⟧([^⟦]*)⟦\/constraint_[^⟦]+⟧/g, '$1')
  
  // 2. 기타 마커 태그들 제거
  cleanText = cleanText.replace(/⟦[^⟦]+⟧([^⟦]*)⟦\/[^⟦]+⟧/g, '$1')
  
  // 3. 스마트 설명형 텍스트 제거 (패턴 기반)
  cleanText = removeExplanatoryText(cleanText)
  
  // 4. 고객에게 보이면 안 되는 메시지 패턴 제거
  cleanText = removeInternalMessages(cleanText)
  
  // 5. 범용적인 불릿 포인트 특별 처리
  const bulletResult = handleBulletPointAlternative(cleanText)
  if (bulletResult) {
    console.log('불릿 포인트 관련 대안 처리 결과:', bulletResult)
    return bulletResult
  }
  
  // 6. 콜론(:) 기반 추출 시도
  const colonIndex = cleanText.indexOf(':')
  if (colonIndex !== -1) {
    const extractedText = cleanText.substring(colonIndex + 1).trim()
    console.log('콜론 기반 추출 결과:', extractedText)
    
    // 추출된 텍스트가 의미있는 내용인지 확인
    if (isMeaningfulContent(extractedText)) {
      console.log('콜론 기반 추출 성공:', extractedText)
      return extractedText
    }
  }
  
  // 7. 다양한 패턴으로 추출 시도
  const patterns = [
    /대안\d+-\d+:\s*(.+)/,  // "대안1-1: 텍스트" 형식
    /대안\d+:\s*(.+)/,      // "대안1: 텍스트" 형식
    /실제 수정될 텍스트 예시[:\s]*["']([^"']+)["']/,
    /실제 수정될 텍스트 예시[:\s]*([^-\n]+)/,
    /예시[:\s]*["']([^"']+)["']/,
    /수정[:\s]*["']([^"']+)["']/,
    /^(.+)$/  // 마지막으로 전체 텍스트를 그대로 사용
  ]
  
  for (let i = 0; i < patterns.length; i++) {
    const pattern = patterns[i]
    const match = cleanText.match(pattern)
    if (match && match[1]) {
      const extractedText = match[1].trim()
      console.log(`패턴 ${i + 1}으로 추출된 텍스트:`, extractedText)
      
      // 의미있는 내용인지 확인
      if (isMeaningfulContent(extractedText)) {
        console.log(`패턴 ${i + 1} 추출 성공:`, extractedText)
        return extractedText
      }
    }
  }
  
  // 8. 정리된 텍스트가 의미있는 내용인지 확인
  const finalText = cleanText.trim()
  if (isMeaningfulContent(finalText)) {
    console.log('정리된 텍스트 반환:', finalText)
    return finalText
  }
  
  // 9. 모든 방법이 실패하면 원본 텍스트를 그대로 반환 (최후의 수단)
  console.log('모든 패턴 실패, 원본 텍스트 반환:', alternativeText)
  return alternativeText.trim()
}

// 범용적인 불릿 포인트 삭제 함수
const removeBulletPoint = (bulletType: string, problemArea: any): boolean => {
  console.log(`=== ${bulletType} 불릿 포인트 삭제 시작 ===`)
  console.log('문제 영역:', problemArea)
  
  const template = templateContent.value
  const problemText = problemArea.problem_text || ''
  
  console.log('현재 템플릿:', template)
  console.log('문제 텍스트:', problemText)
  
  // 불릿 포인트 타입별 키워드 매핑
  const bulletTypeKeywords: Record<string, string[]> = {
    '할인율': ['할인율', '할인'],
    '문의': ['문의', '연락처', '전화', '번호'],
    '장소': ['장소', '위치', '지점', '매장'],
    '기간': ['기간', '일정', '날짜', '시간'],
    '테마': ['테마', '주제', '이벤트']
  }
  
  const keywords = bulletTypeKeywords[bulletType] || [bulletType.toLowerCase()]
  console.log(`${bulletType} 키워드:`, keywords)
  
  // 1. 키워드별 불릿 포인트 패턴들 생성
  const bulletPatterns = keywords.map((keyword: string) => [
    new RegExp(`•\\s*${keyword}[:\\s]*[^\\n]*\\n?`, 'g'),           // "• 키워드: ..."
    new RegExp(`•\\s*${keyword}[^•\\n]*\\n?`, 'g'),                // "• 키워드..." (더 넓은 범위)
  ]).flat()
  
  let newTemplate = template
  let foundAndRemoved = false
  
  // 2. 각 패턴으로 불릿 포인트 찾아서 삭제
  for (const pattern of bulletPatterns) {
    if (pattern.test(newTemplate)) {
      console.log(`${bulletType} 불릿 포인트 패턴 발견:`, pattern)
      newTemplate = newTemplate.replace(pattern, '')
      foundAndRemoved = true
      console.log(`${bulletType} 불릿 포인트 삭제됨`)
    }
  }
  
  // 3. 문제 텍스트가 포함된 줄 전체 삭제 시도
  if (!foundAndRemoved && problemText) {
    console.log('문제 텍스트 기반 삭제 시도')
    const lines = newTemplate.split('\n')
    const filteredLines = lines.filter(line => {
      const normalizedLine = line.replace(/\s+/g, ' ').trim()
      const normalizedProblem = problemText.replace(/\s+/g, ' ').trim()
      
      // 문제 텍스트가 포함된 줄이거나 해당 키워드 관련 줄인지 확인
      const containsProblem = normalizedLine.includes(normalizedProblem)
      const isKeywordLine = keywords.some((keyword: string) => 
        normalizedLine.toLowerCase().includes(keyword.toLowerCase())
      )
      
      if (containsProblem || isKeywordLine) {
        console.log('삭제할 줄 발견:', line)
        return false
      }
      return true
    })
    
    if (filteredLines.length < lines.length) {
      newTemplate = filteredLines.join('\n')
      foundAndRemoved = true
      console.log('문제 텍스트 기반 삭제 완료')
    }
  }
  
  // 4. 템플릿 업데이트
  if (foundAndRemoved) {
    // 연속된 빈 줄 정리
    newTemplate = newTemplate
      .replace(/\n\s*\n\s*\n/g, '\n\n')  // 연속된 빈 줄을 2개로 제한
      .replace(/\n\s*\n$/, '\n')         // 마지막 빈 줄 제거
      .trim()
    
    templateContent.value = newTemplate
    console.log(`✅ ${bulletType} 불릿 포인트 삭제 성공`)
    console.log('수정된 템플릿:', newTemplate)
    return true
  }
  
  console.log(`❌ ${bulletType} 불릿 포인트를 찾을 수 없음`)
  return false
}

// 범용적인 불릿 포인트 대안 처리
const handleBulletPointAlternative = (text: string): string | null => {
  console.log('=== 범용 불릿 포인트 대안 처리 시작 ===')
  console.log('입력 텍스트:', text)
  
  // 불릿 포인트 타입별 매핑
  const bulletPointTypes = {
    '할인율': {
      keywords: ['할인율', '할인'],
      removePatterns: [
        /구체적인\s*할인율은\s*언급하지\s*않는다?/i,
        /할인율은\s*언급하지\s*않는다?/i,
        /구체적인\s*할인율은\s*말하지\s*않는다?/i,
        /할인율은\s*말하지\s*않는다?/i,
        /할인율\s*제거/i,
        /할인율\s*삭제/i,
        /할인율\s*부분\s*삭제/i,
        /할인율\s*부분\s*제거/i,
        /할인율.*삭제/i,
        /할인율.*제거/i
      ],
      modifyPatterns: [
        /방법이나\s*혜택을\s*강조하되/i,
        /혜택을\s*강조하되/i,
        /방법을\s*강조하되/i,
        /혜택을\s*강조/i,
        /방법을\s*강조/i,
        /강조하되/i
      ],
      defaultModify: '• 혜택: 다양한 할인 혜택을 제공합니다'
    },
    '문의': {
      keywords: ['문의', '연락처', '전화', '번호'],
      removePatterns: [
        /문의.*없어야\s*한다/i,
        /문의.*삭제/i,
        /문의.*제거/i,
        /문의.*없애/i,
        /연락처.*없어야\s*한다/i,
        /전화.*없어야\s*한다/i,
        /번호.*없어야\s*한다/i
      ],
      modifyPatterns: [
        /문의.*추가/i,
        /연락처.*추가/i,
        /전화.*추가/i,
        /번호.*추가/i
      ],
      defaultModify: '• 문의: 고객센터로 연락해주세요'
    },
    '장소': {
      keywords: ['장소', '위치', '지점', '매장'],
      removePatterns: [
        /장소.*없어야\s*한다/i,
        /장소.*삭제/i,
        /장소.*제거/i,
        /위치.*없어야\s*한다/i,
        /지점.*없어야\s*한다/i,
        /매장.*없어야\s*한다/i
      ],
      modifyPatterns: [
        /장소.*추가/i,
        /위치.*추가/i,
        /지점.*추가/i,
        /매장.*추가/i
      ],
      defaultModify: '• 장소: 자세한 위치는 문의해주세요'
    },
    '기간': {
      keywords: ['기간', '일정', '날짜', '시간'],
      removePatterns: [
        /기간.*없어야\s*한다/i,
        /기간.*삭제/i,
        /기간.*제거/i,
        /일정.*없어야\s*한다/i,
        /날짜.*없어야\s*한다/i,
        /시간.*없어야\s*한다/i
      ],
      modifyPatterns: [
        /기간.*추가/i,
        /일정.*추가/i,
        /날짜.*추가/i,
        /시간.*추가/i
      ],
      defaultModify: '• 기간: 자세한 일정은 문의해주세요'
    },
    '테마': {
      keywords: ['테마', '주제', '이벤트'],
      removePatterns: [
        /테마.*없어야\s*한다/i,
        /테마.*삭제/i,
        /테마.*제거/i,
        /주제.*없어야\s*한다/i,
        /이벤트.*없어야\s*한다/i
      ],
      modifyPatterns: [
        /테마.*추가/i,
        /주제.*추가/i,
        /이벤트.*추가/i
      ],
      defaultModify: '• 테마: 특별한 이벤트를 진행합니다'
    }
  }
  
  // 각 불릿 포인트 타입별로 처리
  for (const [type, config] of Object.entries(bulletPointTypes)) {
    console.log(`${type} 타입 처리 시도`)
    
    // 키워드가 포함되어 있는지 확인
    const hasKeyword = config.keywords.some(keyword => 
      text.toLowerCase().includes(keyword.toLowerCase())
    )
    
    if (!hasKeyword) {
      continue
    }
    
    console.log(`${type} 키워드 발견`)
    
    // 제거 지시 확인
    const hasRemoveInstruction = config.removePatterns.some(pattern => pattern.test(text))
    if (hasRemoveInstruction) {
      console.log(`${type} 제거 지시 감지됨`)
      return `REMOVE_${type.toUpperCase()}_BULLET`
    }
    
    // 수정 지시 확인
    const hasModifyInstruction = config.modifyPatterns.some(pattern => pattern.test(text))
    if (hasModifyInstruction) {
      console.log(`${type} 수정 지시 감지됨`)
      return config.defaultModify
    }
    
    // 특정 내용 추출 시도
    for (const keyword of config.keywords) {
      const pattern = new RegExp(`${keyword}[:\s]*([^.]*)`, 'i')
      const match = text.match(pattern)
      if (match && match[1]) {
        const extractedText = match[1].trim()
        if (extractedText && extractedText.length > 0) {
          console.log(`${type} 관련 텍스트 추출:`, extractedText)
          return `• ${type}: ${extractedText}`
        }
      }
    }
  }
  
  console.log('범용 불릿 포인트 특별 처리 없음')
  return null
}

// 고객에게 보이면 안 되는 내부 메시지 제거
const removeInternalMessages = (text: string): string => {
  console.log('=== 내부 메시지 제거 시작 ===')
  console.log('원본 텍스트:', text)
  
  // 고객에게 보이면 안 되는 패턴들
  const internalPatterns = [
    // 할인율 관련 내부 메시지
    /할인율[:\s]*~[^.]*\./g,
    /할인율[:\s]*고객이[^.]*\./g,
    /할인율[:\s]*고객들에게[^.]*\./g,
    /할인율[:\s]*보이면[^.]*\./g,
    /할인율[:\s]*안되는[^.]*\./g,
    /할인율[:\s]*메시지가[^.]*\./g,
    /할인율[:\s]*구체적인[^.]*\./g,
    /할인율[:\s]*언급하지[^.]*\./g,
    /할인율[:\s]*강조하되[^.]*\./g,
    /할인율[:\s]*참여할[^.]*\./g,
    /할인율[:\s]*방법이나[^.]*\./g,
    /할인율[:\s]*혜택을[^.]*\./g,
    
    // 기타 내부 지시사항
    /고객이[^.]*\./g,
    /고객들에게[^.]*\./g,
    /보이면[^.]*\./g,
    /안되는[^.]*\./g,
    /메시지가[^.]*\./g,
    /구체적인[^.]*\./g,
    /언급하지[^.]*\./g,
    /강조하되[^.]*\./g,
    /참여할[^.]*\./g,
    /방법이나[^.]*\./g,
    /혜택을[^.]*\./g,
    
    // 기술적 설명
    /이\s*내용이[^.]*\./g,
    /이\s*부분이[^.]*\./g,
    /이\s*텍스트가[^.]*\./g,
    /이\s*문장이[^.]*\./g,
    /미리보기에[^.]*\./g,
    /사용자가\s*보는건[^.]*\./g,
    /사용자에게\s*보이는[^.]*\./g,
    /화면에\s*표시되는[^.]*\./g,
    
    // 작업 지시사항
    /잘하자\s*/g,
    /주의하자\s*/g,
    /기억하자\s*/g,
    /명심하자\s*/g,
    /주의\s*/g,
    /기억\s*/g,
    /명심\s*/g
  ]
  
  let cleanedText = text
  internalPatterns.forEach(pattern => {
    cleanedText = cleanedText.replace(pattern, '')
  })
  
  // 연속된 공백과 줄바꿈 정리
  cleanedText = cleanedText
    .replace(/\s+/g, ' ')
    .replace(/\n\s*\n/g, '\n')
    .trim()
  
  console.log('정리된 텍스트:', cleanedText)
  console.log('================================')
  
  return cleanedText
}

// 설명형 텍스트를 제거하는 스마트한 함수
const removeExplanatoryText = (text: string): string => {
  // 설명형 텍스트 패턴들 (더 범용적)
  const explanatoryPatterns = [
    // 작업 설명 패턴
    /[^.]*를\s*(삭제|제거|변경|수정|교체|대체)하고[^.]*\.\s*/g,
    /[^.]*로\s*(변경|수정|교체|대체)합니다[^.]*\.\s*/g,
    /[^.]*를\s*(삭제|제거|변경|수정|교체|대체)합니다[^.]*\.\s*/g,
    
    // 과정 설명 패턴
    /변경될\s*부분[^.]*\.\s*/g,
    /실제\s*적용되어야\s*할\s*부분[^.]*\.\s*/g,
    /수정되어야\s*할\s*부분[^.]*\.\s*/g,
    /교체되어야\s*할\s*부분[^.]*\.\s*/g,
    
    // 메타 설명 패턴
    /과정이나[^.]*\.\s*/g,
    /태그나[^.]*\.\s*/g,
    /미리보기에[^.]*\.\s*/g,
    /사용자가\s*보는건[^.]*\.\s*/g,
    /사용자에게\s*보이는[^.]*\.\s*/g,
    /화면에\s*표시되는[^.]*\.\s*/g,
    
    // 지시사항 패턴
    /잘하자\s*/g,
    /주의하자\s*/g,
    /기억하자\s*/g,
    /명심하자\s*/g,
    
    // 기술적 설명 패턴
    /이\s*내용이[^.]*\.\s*/g,
    /이\s*부분이[^.]*\.\s*/g,
    /이\s*텍스트가[^.]*\.\s*/g,
    /이\s*문장이[^.]*\.\s*/g,
    
    // 조건부 설명 패턴
    /만약[^.]*\.\s*/g,
    /만약에[^.]*\.\s*/g,
    /경우에[^.]*\.\s*/g,
    /상황에[^.]*\.\s*/g,
    
    // 시간/순서 설명 패턴
    /먼저[^.]*\.\s*/g,
    /그다음[^.]*\.\s*/g,
    /그리고[^.]*\.\s*/g,
    /또한[^.]*\.\s*/g,
    /추가로[^.]*\.\s*/g,
    
    // 목적 설명 패턴
    /목적으로[^.]*\.\s*/g,
    /위해[^.]*\.\s*/g,
    /위해서[^.]*\.\s*/g,
    /때문에[^.]*\.\s*/g,
    
    // 결과 설명 패턴
    /결과적으로[^.]*\.\s*/g,
    /최종적으로[^.]*\.\s*/g,
    /따라서[^.]*\.\s*/g,
    /그러므로[^.]*\.\s*/g,
    
    // 예시 설명 패턴
    /예를\s*들어[^.]*\.\s*/g,
    /예시로[^.]*\.\s*/g,
    /예시는[^.]*\.\s*/g,
    /예시가[^.]*\.\s*/g,
    
    // 비교 설명 패턴
    /기존의[^.]*\.\s*/g,
    /원래의[^.]*\.\s*/g,
    /이전의[^.]*\.\s*/g,
    /과거의[^.]*\.\s*/g,
    /새로운[^.]*\.\s*/g,
    /다른[^.]*\.\s*/g,
    
    // 일반적인 설명 패턴
    /이것은[^.]*\.\s*/g,
    /저것은[^.]*\.\s*/g,
    /그것은[^.]*\.\s*/g,
    /이런[^.]*\.\s*/g,
    /저런[^.]*\.\s*/g,
    /그런[^.]*\.\s*/g
  ]
  
  let cleanedText = text
  explanatoryPatterns.forEach(pattern => {
    cleanedText = cleanedText.replace(pattern, '')
  })
  
  return cleanedText.trim()
}

// 의미있는 내용인지 판단하는 함수
const isMeaningfulContent = (text: string): boolean => {
  if (!text || text.length < 2) return false
  
  // 특수문자만 있는 경우 제외
  if (/^[^\w가-힣]*$/.test(text)) return false
  
  // 설명형 키워드가 포함된 경우 제외
  const explanatoryKeywords = [
    '삭제', '제거', '변경', '수정', '교체', '대체',
    '과정', '태그', '미리보기', '사용자', '화면',
    '잘하자', '주의', '기억', '명심',
    '먼저', '그다음', '그리고', '또한', '추가로',
    '목적', '위해', '때문에', '결과', '최종',
    '예를', '예시', '기존', '원래', '이전',
    '이것은', '저것은', '그것은', '이런', '저런'
  ]
  
  const hasExplanatoryKeyword = explanatoryKeywords.some(keyword => 
    text.includes(keyword)
  )
  
  if (hasExplanatoryKeyword) return false
  
  // 실제 내용으로 보이는 패턴 확인
  const contentPatterns = [
    /안녕하세요/,  // 인사말
    /고객님/,      // 고객 호칭
    /회원님/,      // 회원 호칭
    /브랜드/,      // 브랜드 언급
    /상품/,        // 상품 언급
    /행사/,        // 행사 언급
    /할인/,        // 할인 언급
    /쿠폰/,        // 쿠폰 언급
    /이벤트/,      // 이벤트 언급
    /특별/,        // 특별 언급
    /다양한/,      // 다양한 언급
    /사랑스러운/,  // 감정 표현
    /컬러/,        // 컬러 언급
    /패턴/,        // 패턴 언급
    /네덜란드/,    // 국가명
    /오일릴리/,    // 브랜드명
    /이월행사/     // 특정 행사명
  ]
  
  // 실제 내용 패턴이 포함된 경우 유효
  const hasContentPattern = contentPatterns.some(pattern => 
    pattern.test(text)
  )
  
  return hasContentPattern
}

// 마커 제거 및 최종 본문 확정 (제출 시에만 사용)
const removeAllMarkers = (): string => {
  console.log('=== 모든 마커 제거 및 최종 본문 확정 ===')
  
  let template = templateContent.value
  
  // 모든 마커 패턴 제거 (⟦ID⟧내용⟦/ID⟧ → 내용)
  const markerPattern = /⟦([^⟦]+)⟧([^⟦]*)⟦\/\1⟧/g
  template = template.replace(markerPattern, '$2')
  
  // 추가 정리: 설명형 텍스트 제거
  template = removeExplanatoryText(template)
  
  console.log('마커 제거 완료')
  console.log('최종 템플릿:', template)
  
  return template
}

// 미리보기용 템플릿 내용 (마커 제거, 사용자에게 보이는 깔끔한 버전)
const getPreviewTemplateContent = (): string => {
  let content = templateContent.value
  
  console.log('=== 미리보기 템플릿 내용 생성 ===')
  console.log('원본 템플릿:', content)
  
  // 마커 제거 (⟦ID⟧내용⟦/ID⟧ → 내용)
  const markerPattern = /⟦([^⟦]+)⟧([^⟦]*)⟦\/\1⟧/g
  content = content.replace(markerPattern, '$2')
  
  // 고객에게 보이면 안 되는 내부 메시지 제거
  content = removeInternalMessages(content)
  
  // 설명성 텍스트 제거
  content = removeExplanatoryText(content)
  
  // 템플릿 구조 정리 (줄바꿈과 공백 정리)
  content = content
    .replace(/\n\s*\n\s*\n/g, '\n\n')  // 연속된 빈 줄을 2개로 제한
    .replace(/[ \t]+/g, ' ')           // 연속된 공백을 하나로
    .replace(/\n[ \t]+/g, '\n')        // 줄 시작의 공백 제거
    .replace(/[ \t]+\n/g, '\n')        // 줄 끝의 공백 제거
    .trim()
  
  console.log('정리된 미리보기 템플릿:', content)
  console.log('================================')
  
  return content
}


// 문맥 기반 위치 찾기
const findContextBasedPosition = (problemArea: any): { start: number, end: number } | null => {
  const template = templateContent.value
  const searchMethods = problemArea.search_methods
  
  if (!searchMethods) return null
  
  const exactText = searchMethods.exact_text
  const contextBefore = searchMethods.context_before || ''
  const contextAfter = searchMethods.context_after || ''
  
  // 문맥 + 정확한 텍스트로 위치 찾기
  if (exactText && (contextBefore || contextAfter)) {
    const fullPattern = contextBefore + exactText + contextAfter
    const matchIndex = template.indexOf(fullPattern)
    if (matchIndex !== -1) {
      const start = matchIndex + contextBefore.length
      const end = start + exactText.length
      console.log('문맥 기반 위치 찾기 성공:', { start, end })
      return { start, end }
    }
  }
  
  // 정확한 텍스트만으로 위치 찾기
  if (exactText) {
    const matchIndex = template.indexOf(exactText)
    if (matchIndex !== -1) {
      const start = matchIndex
      const end = matchIndex + exactText.length
      console.log('정확한 텍스트 위치 찾기 성공:', { start, end })
      return { start, end }
    }
  }
  
  return null
}

// 안정적인 위치 찾기 (다중 수정을 위한 백업 함수)
const findStablePosition = (problemArea: any): { start: number, end: number } | null => {
  console.log('=== 안정적인 위치 찾기 시작 ===')
  
  // 1. 문맥 기반 위치 찾기 시도
  const contextPosition = findContextBasedPosition(problemArea)
  if (contextPosition) {
    console.log('문맥 기반 위치 찾기 성공')
    return contextPosition
  }
  
  // 2. 문제 텍스트 직접 매칭 시도
  const template = templateContent.value
  const problemText = problemArea.problem_text
  
  if (problemText && template.includes(problemText)) {
    const matchIndex = template.indexOf(problemText)
    const start = matchIndex
    const end = matchIndex + problemText.length
    console.log('문제 텍스트 직접 매칭 성공:', { start, end })
    return { start, end }
  }
  
  // 3. 위치 정보가 있다면 사용
  if (problemArea.start_position !== undefined && problemArea.end_position !== undefined) {
    const start = problemArea.start_position
    const end = problemArea.end_position
    console.log('위치 정보 사용:', { start, end })
    return { start, end }
  }
  
  // 4. 템플릿 중간 위치에 삽입 (최후의 수단)
  const middlePosition = Math.floor(template.length / 2)
  console.log('중간 위치에 삽입:', { start: middlePosition, end: middlePosition })
  return { start: middlePosition, end: middlePosition }
}

// 다중 수정 시 마커 업데이트
const updateMarkerForMultipleEdits = (problemArea: any, modifiedText: string): boolean => {
  console.log('=== 다중 수정을 위한 마커 업데이트 ===')
  
  const markerId = problemArea.area_id || `ERR${Date.now()}`
  const template = templateContent.value
  
  // 기존 마커가 있는지 확인하고 업데이트
  const markerPattern = new RegExp(`⟦${markerId}⟧([^⟦]*)⟦/${markerId}⟧`, 'g')
  if (markerPattern.test(template)) {
    console.log('기존 마커 업데이트')
    const newTemplate = template.replace(markerPattern, `⟦${markerId}⟧${modifiedText}⟦/${markerId}⟧`)
    templateContent.value = newTemplate
    return true
  }
  
  // 새 마커 생성
  const position = findStablePosition(problemArea)
  if (position) {
    console.log('새 마커 생성')
    const beforeText = template.substring(0, position.start)
    const afterText = template.substring(position.end)
    const newTemplate = beforeText + `⟦${markerId}⟧${modifiedText}⟦/${markerId}⟧` + afterText
    templateContent.value = newTemplate
    return true
  }
  
  return false
}

// 버전 선택
const selectVersion = (versionNumber: number) => {
  currentVersion.value = versionNumber
}

// 반려 사이드바 닫기
const closeRejectionSidebar = () => {
  showRejectionSidebar.value = false
  isRejected.value = false
  problemAreas.value = []
  currentProblemArea.value = null
  currentAlternatives.value = []
  totalErrors.value = 0
  totalWarnings.value = 0
}

// 변수 업데이트
const updateVariables = (newVariables: any) => {
  editedVariables.value = Array.isArray(newVariables) ? newVariables : [...newVariables]
  
  // 강제로 리렌더링을 위해 nextTick 사용
  nextTick(() => {
    // 변수 업데이트 완료
  })
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

// 알림톡 높이 측정 함수
const measureAlimtalkHeight = () => {
  nextTick(() => {
    if (kakaoPreviewRef.value) {
      alimtalkHeight.value = kakaoPreviewRef.value.offsetHeight
      console.log('알림톡 높이 측정:', alimtalkHeight.value)
    }
  })
}


// 변수 토글 상태 변경 감지
watch(showVariables, (newValue) => {
  if (newValue && templateVariables.value.length > 0) {
    // 변수 토글을 활성화했을 때 변수명 설정
    editedVariables.value = [...templateVariables.value]
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
    
    // 제출 전 변수 배열 보정: 비어있으면 현재 템플릿 변수로 기본값 구성
    if (!editedVariables.value || editedVariables.value.length === 0) {
      const fallback: string[] = []
      if (Array.isArray(templateVariables.value) && templateVariables.value.length > 0) {
        fallback.push(...templateVariables.value)
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
        fallback.push(...Array.from(found))
      }
      editedVariables.value = fallback
    }
    // 마커 제거 후 최종 템플릿 확정
    const finalTemplate = removeAllMarkers()
    
    // 백엔드로 템플릿 검증 요청
    const response = await templateApi.validateTemplate(
      finalTemplate,
      editedVariables.value,
      templateCategory.value,
      userMessage.value,
      templateTitle.value
    )
    
    console.log('템플릿 검증 응답:', response.data)
    console.log('응답 구조 확인:', {
      success: response.data.success,
      problem_areas: response.data.problem_areas,
      validation_stage: response.data.validation_stage,
      total_errors: response.data.total_errors,
      total_warnings: response.data.total_warnings
    })
    
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
      
      // 백엔드에서 전달된 문제 영역 처리
      const problemAreasData = response.data.problem_areas || []
      const validationStageData = response.data.validation_stage || '검증'
      const totalErrorsData = response.data.total_errors || 0
      const totalWarningsData = response.data.total_warnings || 0
      
      console.log('문제 영역:', problemAreasData)
      console.log('검증 단계:', validationStageData)
      console.log('총 오류:', totalErrorsData, '총 경고:', totalWarningsData)
      
      // 문제 영역 정보 저장 (position 정보 포함)
      problemAreas.value = problemAreasData.map((area: any) => ({
        ...area,
        start_position: area.start_position || area.startPosition,
        end_position: area.end_position || area.endPosition
      }))
      validationStage.value = validationStageData
      totalErrors.value = totalErrorsData
      totalWarnings.value = totalWarningsData
      
      // 반려된 변수 추출 (변수 사용 규칙 오류가 있는 경우)
      const rejectedVars: string[] = []
      problemAreasData.forEach((area: any) => {
        if (area.error_type === 'variable_usage' && area.problem_text) {
          // 변수명 추출 (예: #{변수명} 형태)
          const variableMatches = area.problem_text.match(/#\{([^}]+)\}/g)
          if (variableMatches) {
            variableMatches.forEach((match: string) => {
              const varName = match.replace(/#\{|\}/g, '')
              if (!rejectedVars.includes(varName)) {
                rejectedVars.push(varName)
              }
            })
          }
        }
      })
      rejectedVariables.value = rejectedVars
      
      console.log('반려된 변수:', rejectedVars)
      
      // 반려 상태 설정
      isRejected.value = true
      showRejectionSidebar.value = true
      
      // 사용자에게 친화적인 안내 메시지 표시 (비동기 처리)
      setTimeout(() => {
        alert(`템플릿 수정이 필요합니다 📝\n\n${validationStage.value}에서 ${totalErrors.value}개 오류, ${totalWarnings.value}개 경고가 발견되었습니다.\n오른쪽 사이드바에서 상세 내용과 수정 방법을 확인해주세요.`)
      }, 100)
    }
  } catch (error) {
    console.error('템플릿 검증 실패:', error)
    setTimeout(() => {
      alert('템플릿 검증 중 오류가 발생했습니다. 다시 시도해주세요.')
    }, 100)
  } finally {
    isValidating.value = false // 검증 완료
  }
}

// 수정 완료 후 템플릿 저장 (저장 → 검증 순서)
const saveTemplate = async () => {
  try {
    console.log('템플릿 저장 요청 시작')
    isSaving.value = true
    
    // 사용자 상태 디버깅
    console.log('=== 템플릿 저장 요청 전 사용자 상태 확인 ===')
    console.log('사용자 상태:', {
      isLoggedIn: userStore.isLoggedIn,
      hasToken: !!userStore.accessToken,
      accountId: userStore.accountId,
      userName: userStore.userName,
      email: userStore.email,
      role: userStore.role,
      loginType: userStore.loginType,
      token: userStore.accessToken ? `${userStore.accessToken.substring(0, 20)}...` : 'null',
      tokenLength: userStore.accessToken ? userStore.accessToken.length : 0
    })
    
    // localStorage에서 직접 토큰 확인
    const storedToken = localStorage.getItem('access_token')
    console.log('localStorage 토큰 상태:', {
      hasStoredToken: !!storedToken,
      storedTokenLength: storedToken ? storedToken.length : 0,
      storedToken: storedToken ? `${storedToken.substring(0, 20)}...` : 'null'
    })
    
    // 로그인 상태 확인
    if (!userStore.isLoggedIn || !userStore.accessToken) {
      console.error('사용자가 로그인되지 않았거나 토큰이 없음')
      
      // 사용자 정보 복원 시도
      userStore.restoreUser()
      
      if (!userStore.isLoggedIn || !userStore.accessToken) {
        console.error('사용자 정보 복원 실패')
        alert('템플릿을 저장하려면 로그인이 필요합니다. 로그인 페이지로 이동합니다.')
        router.push('/')
        return
      } else {
        console.log('사용자 정보 복원 성공')
      }
    }
    
    // 제출 전 변수 배열 보정: 비어있으면 현재 템플릿 변수로 기본값 구성
    if (!editedVariables.value || editedVariables.value.length === 0) {
      const fallback: string[] = []
      if (Array.isArray(templateVariables.value) && templateVariables.value.length > 0) {
        fallback.push(...templateVariables.value)
      } else if (templateContent.value) {
        // 변수 배열이 비어 있으면 템플릿 본문에서 변수 패턴을 파싱해 기본값 구성
        const patterns = [/\{\{([^}]+)\}\}/g, /#\{([^}]+)\}/g, /\{([^}]+)\}/g]
        const found = new Set<string>()
        patterns.forEach((re) => {
          let m
          while ((m = re.exec(templateContent.value)) !== null) {
            const name = (m[1] || '').trim()
            if (name) found.add(name)
          }
        })
        fallback.push(...Array.from(found))
      }
      console.log('변수 추출 결과:', fallback)
      editedVariables.value = fallback
    }
    
    console.log('저장 시 변수 목록:', editedVariables.value)

    // 1단계: 먼저 템플릿 저장
    console.log('1단계: 템플릿 저장 시작')
    const saveResponse = await templateApi.saveTemplate(
      templateContent.value,
      editedVariables.value,
      templateCategory.value,
      userMessage.value,
      templateTitle.value
    )
    
    console.log('템플릿 저장 응답:', saveResponse.data)
    
    if (!saveResponse.data.success) {
      console.error('템플릿 저장 실패:', saveResponse.data.message)
      alert('템플릿 저장에 실패했습니다: ' + saveResponse.data.message)
      return
    }
    
    const templateId = saveResponse.data.templateId
    console.log('템플릿 저장 성공, 저장된 템플릿 ID:', templateId)
    savedTemplateId.value = templateId // 저장된 템플릿 ID 저장
    
    // 저장 성공 후 검증 단계로 전환
    stage.value = 'validate'
    
    // 검증 프로세스 시작
    await submitTemplate()
    
  } catch (error: any) {
    console.error('템플릿 저장 중 오류 발생:', error)
    alert('템플릿 저장 중 오류가 발생했습니다. 다시 시도해주세요.')
  } finally {
    isSaving.value = false // 저장 완료
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
    // 변수명 배열 (이미 string[] 형태)
    const variableList = editedVariables.value
    
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
    const sourceVars = (Array.isArray(response.data.variables) && response.data.variables.length > 0)
      ? response.data.variables.map((variable: any) => variable.name || variable)
      : templateVariables.value
    editedVariables.value = [...sourceVars]
    
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


// 채팅 자동 스크롤 함수
const scrollToBottom = () => {
  nextTick(() => {
    if (chatHistoryRef.value) {
      chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
    }
  })
}

// 템플릿 내용이나 변수 변경 시 높이 재측정
watch([templateContent, templateTitle, editedVariables, showVariables], () => {
  measureAlimtalkHeight()
}, { deep: true })

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
.btn-submit,
.btn-validate,
.btn-reject {
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
