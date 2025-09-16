<template>
  <div class="template-form">
    <div class="form-header">
      <h2 class="form-title">알림톡 템플릿 생성</h2>
      <p class="form-subtitle">원하는 템플릿 내용을 입력해주세요</p>
    </div>
    
    <div class="form-content">
      <div class="input-section">
        <textarea
          v-model="templateStore.userMessage"
          placeholder="예시: 회원가입 완료 알림, 주문 배송 안내, 이벤트 참여 안내 등&#10;&#10;구체적으로 작성할수록 더 정확한 템플릿이 생성됩니다."
          class="template-textarea"
          :disabled="isGenerating"
          rows="6"
        ></textarea>
        
        <div class="input-footer">
          <span class="char-count">{{ templateStore.userMessage.length }}/500</span>
          <button 
            class="generate-btn"
            @click="handleSubmit"
            :disabled="!canSubmit"
          >
            <span v-if="isGenerating" class="loading-spinner"></span>
            <span v-else class="btn-content">
              <i class="mdi mdi-magic-staff"></i>
              템플릿 생성하기
            </span>
          </button>
        </div>
      </div>
      
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useTemplateStore } from '@/stores/template'
import { aiApi } from '@/api'

const router = useRouter()
const userStore = useUserStore()
const templateStore = useTemplateStore()

const isGenerating = ref(false)

const canSubmit = computed(() =>
  templateStore.userMessage.trim().length > 0 && !isGenerating.value
)

const emit = defineEmits<{
  (e: 'requireLogin'): void
}>()

const handleSubmit = async () => {
  if (!canSubmit.value) return

  // 로그인 여부 확인
  if (!userStore.isLoggedIn) {
    templateStore.setUserMessage(templateStore.userMessage)
    alert('로그인이 필요합니다.')
    emit('requireLogin')
    return
  }

  isGenerating.value = true
  try {
    const response = await aiApi.generateTemplate(templateStore.userMessage)
    templateStore.setUserMessage(templateStore.userMessage)
    // AI 서버의 응답(TemplateGenerationResponse)을 sessionStorage에 저장합니다.
    const responseData = response.data;

    // AI가 반환한 variables (List<Dict>)에서 이름(name)만 추출하여 문자열 배열로 변환합니다.
    const variableNames = responseData.variables.map((v: any) => v.name);

    sessionStorage.setItem('generatedTemplate', JSON.stringify({
      templateContent: responseData.template_content,
      variables: variableNames,
      category: responseData.category,
      userMessage: templateStore.userText
    }));
    router.push({
      name: 'template-result',
      state: response.data
    })
  } catch (e) {
    alert('템플릿 생성 실패. 다시 시도해주세요.')
  } finally {
    isGenerating.value = false
  }
}
</script>

<style scoped>
/* 템플릿 폼 컨테이너 */
.template-form {
  background: white;
  border-radius: 0.8rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 450px;
  display: flex;
  flex-direction: column;
}

/* 폼 헤더 */
.form-header {
  padding: 2rem 2rem 1rem 2rem;
  text-align: center;
  border-bottom: 1px solid #f0f0f0;
}

.form-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 0.5rem 0;
}

.form-subtitle {
  font-size: 1rem;
  color: #666;
  margin: 0;
}

/* 폼 콘텐츠 */
.form-content {
  padding: 2rem;
}

/* 입력 섹션 */
.input-section {
  margin-bottom: 1.5rem;
}

.template-textarea {
  width: 100%;
  min-height: 8rem;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 0.8rem;
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
  background: white;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
}

.template-textarea:focus {
  outline: none;
  border-color: #8E24AA;
  box-shadow: 0 0 0 3px rgba(142, 36, 170, 0.1);
}

.template-textarea:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

/* 입력 하단 */
.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.char-count {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

.generate-btn {
  padding: 0.8rem 1.5rem;
  border: none;
  background: linear-gradient(135deg, #8E24AA 0%, #7B1FA2 100%);
  color: white;
  border-radius: 0.6rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(142, 36, 170, 0.3);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(142, 36, 170, 0.4);
}

.generate-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
</style>
