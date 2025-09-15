<template>
  <div class="template-create-container">
    <!-- 헤더 컴포넌트 -->
    <HeaderComponent />
    
    <!-- 메인 콘텐츠 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 제목 -->
        <div class="header-section">
          <h1 class="page-title">
            만들고 싶은 알림톡 템플릿 주제를 알려주세요
          </h1>
          <p class="page-subtitle">
            원하는 템플릿에 대한 설명을 입력하시면, AI가 카테고리 분석부터 내용 생성까지 모두 처리해 드립니다.
          </p>
        </div>
        
        <!-- 텍스트 입력 영역 -->
        <div class="text-input-section">
          <div class="textarea-container">
            <textarea
              v-model="messageText"
              placeholder="ex. 우리 서비스에 맞는 법적 고지 내용을 빠르게 작성하고 적용할 수 있는 템플릿이 필요합니다."
              class="message-textarea"
              :class="{ 'loading': isGenerating }"
              :disabled="isGenerating"
              rows="8"
            ></textarea>
            <button 
              class="submit-arrow-btn" 
              :class="{ 'loading': isGenerating }"
              @click="handleSubmit" 
              :disabled="!canSubmit"
            >
              <span v-if="isGenerating" class="loading-spinner"></span>
              <span v-else>↑</span>
            </button>
          </div>
          
          <!-- 로딩 메시지 -->
          <div v-if="isGenerating" class="loading-message">
            <div class="loading-text">AI가 템플릿을 생성하고 있습니다...</div>
            <div class="loading-subtext">잠시만 기다려주세요</div>
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
import { templateApi } from '@/api' // aiApi 대신 templateApi를 사용합니다.

const router = useRouter()

const messageText = ref('')
const isGenerating = ref(false)

// 제출 가능 여부
const canSubmit = computed(() => {
  return messageText.value.trim().length > 0 && !isGenerating.value
})

// 제출 처리
const handleSubmit = async () => {
  if (!canSubmit.value) return
  
  isGenerating.value = true
  
  try {
    console.log('템플릿 생성 요청 (사용자 메시지):', messageText.value)
    
    // 백엔드를 통해 AI 템플릿 생성 요청 (사용자 메시지만 전달)
    const response = await templateApi.generateTemplate(messageText.value)
    
    console.log('템플릿 생성 응답:', response.data)
    
    const responseData = response.data;
    const metadata = responseData.metadata || {};
    const requestInfo = metadata.request_info || {};

    // 생성된 템플릿 데이터를 세션 스토리지에 저장
    sessionStorage.setItem('generatedTemplate', JSON.stringify({
      templateContent: responseData.template_text,
      templateTitle: response.data.template_title,
      variables: metadata.variables_detected || [],
      category: requestInfo.category_sub,
      userMessage: messageText.value
    }))
    
    // 결과 페이지로 이동
    router.push('/template/result')
  } catch (error) {
    console.error('템플릿 생성 실패:', error)
    alert('템플릿 생성에 실패했습니다. 다시 시도해주세요.')
  } finally {
    isGenerating.value = false
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header-section {
  text-align: center;
  margin-bottom: 2.5rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.3;
}
.page-subtitle {
  font-size: 1.1rem;
  color: #555;
  margin-top: 0.5rem;
}

.category-btn:hover {
  background: #7B1FA2;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(142, 36, 170, 0.3);
}

.category-btn.selected {
  background: #4A148C;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(74, 20, 140, 0.4);
}

.category-btn:disabled {
  background: #e0e0e0;
  color: #9e9e9e;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.category-btn:disabled:hover {
  background: #e0e0e0;
  transform: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.text-input-section {
  width: 100%;
  max-width: 800px;
}

.textarea-container {
  position: relative;
}

.message-textarea {
  width: 100%;
  min-height: 12rem;
  padding: 1.5rem;
  padding-right: 4rem;
  border: 0.1rem solid #e0e0e0;
  border-radius: 0.8rem;
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-textarea:focus {
  outline: none;
  border-color: #8E24AA;
  box-shadow: 0 0 0 0.2rem rgba(142, 36, 170, 0.1);
}

.submit-arrow-btn {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  width: 3rem;
  height: 3rem;
  border: none;
  background: #8E24AA;
  color: white;
  border-radius: 50%;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(142, 36, 170, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-arrow-btn:hover:not(:disabled) {
  background: #7B1FA2;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(142, 36, 170, 0.4);
}

.submit-arrow-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.submit-arrow-btn.loading {
  background: #8E24AA;
  cursor: not-allowed;
}

/* 로딩 스피너 */
.loading-spinner {
  width: 1.2rem;
  height: 1.2rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 로딩 중 텍스트 영역 스타일 */
.message-textarea.loading {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.message-textarea:disabled {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

/* 로딩 메시지 */
.loading-message {
  text-align: center;
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #8E24AA, #7B1FA2);
  color: white;
  border-radius: 0.8rem;
  box-shadow: 0 4px 12px rgba(142, 36, 170, 0.3);
  animation: pulse 2s ease-in-out infinite;
}

.loading-text {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.loading-subtext {
  font-size: 0.9rem;
  opacity: 0.9;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}
</style>
