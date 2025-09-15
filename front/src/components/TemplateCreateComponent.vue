<template>
  <h1 class="page-title"> 
    만들고 싶은 알림톡 템플릿 주제를 알려주세요
  </h1>
  <div class="template-create-container">
    <div class="content-wrapper">
      <!-- 텍스트 입력 + 제출 버튼 -->
      <div class="text-input-section">
        <div class="textarea-container">
          <textarea
            v-model="templateStore.userText"
            placeholder="원하는 템플릿 내용을 입력하세요..."
            class="message-textarea"
            :disabled="isGenerating"
            rows="6"
          ></textarea>
          <button 
            class="submit-arrow-btn"
            @click="handleSubmit"
            :disabled="!canSubmit"
          >
            <span v-if="isGenerating" class="loading-spinner"></span>
            <span v-else>↑</span>
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
  templateStore.userText.trim().length > 0 && !isGenerating.value
)

const emit = defineEmits<{
  (e: 'requireLogin'): void
}>()

const handleSubmit = async () => {
  if (!canSubmit.value) return

  // 로그인 여부 확인
  if (!userStore.isLoggedIn) {
    templateStore.setUserText(templateStore.userText)
    alert('로그인이 필요합니다.')
    emit('requireLogin')
    return
  }

  isGenerating.value = true
  try {
    const response = await aiApi.generateTemplate(templateStore.userText)
    templateStore.setUserText(templateStore.userText)
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
.template-create-container {
  width: 100%;
  background: #fff;
  padding: 1.5rem;
  border-radius: 0.8rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 제목 */
.header-section {
  text-align: center;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
}

/* 텍스트 입력 영역 */
.text-input-section {
  width: 100%;
}

.textarea-container {
  position: relative;
}

.message-textarea {
  width: 100%;
  min-height: 10rem;
  padding: 1.2rem;
  padding-right: 3.5rem; /* 버튼 자리 확보 */
  border: 0.1rem solid #e0e0e0;
  border-radius: 0.6rem;
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
  background: white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.message-textarea:focus {
  outline: none;
  border-color: #8E24AA;
  box-shadow: 0 0 0 0.15rem rgba(142, 36, 170, 0.1);
}

/* 제출 버튼 */
.submit-arrow-btn {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  width: 2.8rem;
  height: 2.8rem;
  border: none;
  background: #8E24AA;
  color: white;
  border-radius: 50%;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 6px rgba(142, 36, 170, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-arrow-btn:hover:not(:disabled) {
  background: #7B1FA2;
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(142, 36, 170, 0.4);
}

.submit-arrow-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
