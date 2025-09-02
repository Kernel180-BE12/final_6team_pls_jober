<template>
  <div class="chat-page">
    <!-- 헤더 -->
    <HeaderComponent />
    
    <!-- 메인 콘텐츠 -->
    <v-main class="main-content">
      <v-container fluid class="pa-0">
        <section class="chat-section">
          <v-container class="chat-container">
            <v-row>
              <!-- 왼쪽 섹션: 채팅 히스토리 -->
              <v-col cols="12" lg="4" class="left-section">
                <div class="chat-sidebar">
                  <!-- 채팅 정보 -->
                  <div class="chat-info mb-6">
                    <div class="info-header">
                      <v-icon icon="mdi-chat" size="24" color="#00C851" class="mr-2"></v-icon>
                      <h3 class="info-title">템플릿 생성 채팅</h3>
                    </div>
                    <div class="info-details">
                      <p class="detail-item">
                        <span class="detail-label">카테고리:</span>
                        <span class="detail-value">{{ selectedCategoryName }}</span>
                      </p>
                      <p class="detail-item">
                        <span class="detail-label">입력 메시지:</span>
                        <span class="detail-value">{{ userMessage }}</span>
                      </p>
                    </div>
                  </div>
                  
                  <!-- 새 채팅 시작 -->
                  <div class="new-chat-section mb-6">
                    <v-btn
                      color="#00C851"
                      variant="flat"
                      class="new-chat-btn"
                      rounded="pill"
                      size="large"
                      block
                      @click="startNewChat"
                    >
                      <v-icon icon="mdi-plus" class="mr-2"></v-icon>
                      새 채팅 시작
                    </v-btn>
                  </div>
                  
                  <!-- 채팅 히스토리 -->
                  <div class="chat-history">
                    <h4 class="history-title mb-3">채팅 히스토리</h4>
                    <div class="history-list">
                      <div
                        v-for="(chat, index) in chatHistory"
                        :key="index"
                        class="history-item"
                        :class="{ active: currentChatId === chat.id }"
                        @click="selectChat(chat.id)"
                      >
                        <div class="history-icon">
                          <v-icon icon="mdi-chat-outline" size="16"></v-icon>
                        </div>
                        <div class="history-content">
                          <p class="history-preview">{{ chat.preview }}</p>
                          <span class="history-time">{{ chat.time }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </v-col>
              
              <!-- 오른쪽 섹션: 채팅 메인 -->
              <v-col cols="12" lg="8" class="right-section">
                <div class="chat-main">
                  <!-- 채팅 헤더 -->
                  <div class="chat-header mb-4">
                    <div class="header-left">
                      <h2 class="chat-title">AI 템플릿 생성기</h2>
                      <p class="chat-subtitle">{{ selectedCategoryName }} 카테고리 템플릿 생성 중...</p>
                    </div>
                    <div class="header-right">
                      <v-btn
                        icon="mdi-refresh"
                        variant="text"
                        color="#666"
                        @click="refreshChat"
                      ></v-btn>
                    </div>
                  </div>
                  
                  <!-- 채팅 메시지 영역 -->
                  <div class="chat-messages" ref="chatMessages">
                    <div
                      v-for="(message, index) in currentMessages"
                      :key="index"
                      class="message-item"
                      :class="message.type"
                    >
                      <div class="message-avatar">
                        <v-avatar
                          :color="message.type === 'user' ? '#00C851' : '#FFE066'"
                          size="40"
                        >
                          <v-icon
                            :icon="message.type === 'user' ? 'mdi-account' : 'mdi-robot'"
                            color="white"
                            size="20"
                          ></v-icon>
                        </v-avatar>
                      </div>
                      <div class="message-content">
                        <div class="message-bubble">
                          <p class="message-text">{{ message.content }}</p>
                          <span class="message-time">{{ message.time }}</span>
                        </div>
                      </div>
                    </div>
                    
                    <!-- AI가 타이핑 중일 때 표시 -->
                    <div v-if="isTyping" class="message-item ai">
                      <div class="message-avatar">
                        <v-avatar color="#FFE066" size="40">
                          <v-icon icon="mdi-robot" color="white" size="20"></v-icon>
                        </v-avatar>
                      </div>
                      <div class="message-content">
                        <div class="message-bubble typing">
                          <div class="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 메시지 입력 영역 -->
                  <div class="chat-input-section">
                    <div class="input-container">
                      <v-textarea
                        v-model="newMessage"
                        placeholder="메시지를 입력하세요..."
                        variant="outlined"
                        rows="3"
                        class="message-input"
                        :disabled="isTyping"
                        @keydown.enter.prevent="sendMessage"
                        auto-grow
                      ></v-textarea>
                      <v-btn
                        color="#00C851"
                        variant="flat"
                        class="send-btn"
                        rounded="pill"
                        :disabled="!newMessage.trim() || isTyping"
                        @click="sendMessage"
                      >
                        <v-icon icon="mdi-send" class="mr-1"></v-icon>
                        전송
                      </v-btn>
                    </div>
                    
                                         <!-- 빠른 질문 버튼들 -->
                     <div class="quick-questions mt-4">
                       <v-btn
                         v-for="question in quickQuestions"
                         :key="question"
                         variant="outlined"
                         color="#666"
                         class="quick-btn mr-2 mb-2"
                         rounded="pill"
                         size="small"
                         @click="askQuickQuestion(question)"
                         :disabled="isTyping"
                       >
                         {{ question }}
                       </v-btn>
                     </div>
                     
                     <!-- 제출하기 버튼 -->
                     <div class="submit-section mt-6">
                       <v-btn
                         color="#00C851"
                         variant="flat"
                         class="submit-btn"
                         rounded="pill"
                         size="large"
                         @click="submitTemplate"
                       >
                         <v-icon icon="mdi-check" class="mr-2"></v-icon>
                         제출하기
                       </v-btn>
                     </div>
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-container>
        </section>
      </v-container>
    </v-main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import HeaderComponent from '@/components/HeaderComponent.vue'

const route = useRoute()
const router = useRouter()

// 카테고리 매핑
const categoryNames = {
  'appointment': '예약 안내',
  'marketing': '마케팅',
  'notification': '공지사항',
  'reminder': '리마인더',
  'custom': '커스텀'
}

// Reactive data
const newMessage = ref('')
const isTyping = ref(false)
const currentChatId = ref('chat-1')
const chatMessages = ref<HTMLElement>()

// 채팅 히스토리
const chatHistory = ref([
  {
    id: 'chat-1',
    preview: '예약 안내 템플릿 생성',
    time: '방금 전'
  }
])

// 현재 채팅 메시지
const currentMessages = ref([
  {
    type: 'ai',
    content: `안녕하세요! ${categoryNames[route.query.category as keyof typeof categoryNames] || '커스텀'} 카테고리의 템플릿을 생성해드리겠습니다. 입력해주신 메시지를 바탕으로 최적화된 카카오 알림톡 템플릿을 만들어보겠습니다. 추가로 궁금한 점이나 수정하고 싶은 부분이 있으시면 언제든 말씀해 주세요!`,
    time: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
  }
])

// 빠른 질문들
const quickQuestions = [
  '더 친근한 톤으로 바꿔주세요',
  '간결하게 요약해주세요',
  '비즈니스 톤으로 수정해주세요',
  '이모티콘을 추가해주세요'
]

// 계산된 속성
const selectedCategory = computed(() => route.query.category as string || 'appointment')
const selectedCategoryName = computed(() => categoryNames[selectedCategory.value as keyof typeof categoryNames] || '커스텀')
const userMessage = computed(() => route.query.message as string || '')

// 새 채팅 시작
const startNewChat = () => {
  const newChatId = `chat-${Date.now()}`
  currentChatId.value = newChatId
  
  chatHistory.value.unshift({
    id: newChatId,
    preview: `${selectedCategoryName.value} 새 채팅`,
    time: '방금 전'
  })
  
  currentMessages.value = [
    {
      type: 'ai',
      content: `새로운 ${selectedCategoryName.value} 템플릿 생성을 시작합니다. 어떤 템플릿을 만들어드릴까요?`,
      time: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
    }
  ]
}

// 채팅 선택
const selectChat = (chatId: string) => {
  currentChatId.value = chatId
  // 실제로는 해당 채팅의 메시지를 불러와야 함
}

// 메시지 전송
const sendMessage = async () => {
  if (!newMessage.value.trim() || isTyping.value) return
  
  const userMessageObj = {
    type: 'user',
    content: newMessage.value,
    time: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
  }
  
  currentMessages.value.push(userMessageObj)
  const messageToSend = newMessage.value
  newMessage.value = ''
  
  // 스크롤을 맨 아래로
  await nextTick()
  scrollToBottom()
  
  // AI 응답 시뮬레이션
  isTyping.value = true
  setTimeout(() => {
    const aiResponse = generateAIResponse(messageToSend)
    currentMessages.value.push({
      type: 'ai',
      content: aiResponse,
      time: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
    })
    isTyping.value = false
    
    nextTick(() => {
      scrollToBottom()
    })
  }, 2000)
}

// 빠른 질문
const askQuickQuestion = (question: string) => {
  newMessage.value = question
  sendMessage()
}

// AI 응답 생성 (실제로는 AI API 호출)
const generateAIResponse = (userMessage: string): string => {
  const responses = [
    `좋은 질문이네요! "${userMessage}"에 대해 더 자세히 설명드리겠습니다.`,
    `"${userMessage}"를 반영해서 템플릿을 수정해드리겠습니다.`,
    `"${userMessage}" 요청사항을 고려하여 최적화된 템플릿을 만들어보겠습니다.`,
    `"${userMessage}"에 맞춰 템플릿을 개선해드리겠습니다.`
  ]
  
  return responses[Math.floor(Math.random() * responses.length)]
}

// 스크롤을 맨 아래로
const scrollToBottom = () => {
  if (chatMessages.value) {
    chatMessages.value.scrollTop = chatMessages.value.scrollHeight
  }
}

// 채팅 새로고침
const refreshChat = () => {
  startNewChat()
}

// 템플릿 제출
const submitTemplate = () => {
  // 성공 페이지로 이동
  router.push({ name: 'success' })
}

// 메시지 변경 감지하여 스크롤
watch(currentMessages, () => {
  nextTick(() => {
    scrollToBottom()
  })
})

onMounted(() => {
  console.log('선택된 카테고리:', selectedCategory.value)
  console.log('입력된 메시지:', userMessage.value)
  
  // 초기 AI 메시지에 사용자 입력 정보 포함
  if (userMessage.value) {
    currentMessages.value[0].content = `안녕하세요! ${selectedCategoryName.value} 카테고리의 템플릿을 생성해드리겠습니다. 

입력해주신 내용: "${userMessage.value}"

이를 바탕으로 최적화된 카카오 알림톡 템플릿을 만들어보겠습니다. 추가로 궁금한 점이나 수정하고 싶은 부분이 있으시면 언제든 말씀해 주세요!`
  }
})
</script>

<style scoped>
.chat-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #FFF8E1 0%, #FFFDE7 50%, #F1F8E9 100%);
}

.main-content {
  padding-top: 70px;
}

.chat-section {
  padding: 2rem 0;
  min-height: calc(100vh - 70px);
}

.chat-container {
  max-width: 1600px !important;
}

.left-section, .right-section {
  padding: 1rem;
}

/* 왼쪽 사이드바 스타일 */
.chat-sidebar {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  padding: 2rem;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  height: calc(100vh - 140px);
  overflow-y: auto;
}

.chat-info {
  border-bottom: 1px solid #E0E0E0;
  padding-bottom: 1.5rem;
}

.info-header {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.info-title {
  color: #333;
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.info-details {
  background: #F5F5F5;
  padding: 1rem;
  border-radius: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  color: #666;
  font-weight: 500;
}

.detail-value {
  color: #333;
  font-weight: 600;
  max-width: 150px;
  text-align: right;
  word-break: break-word;
}

.new-chat-btn {
  font-weight: 600;
  text-transform: none;
  height: 48px;
}

.chat-history {
  margin-top: 2rem;
}

.history-title {
  color: #333;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.history-item:hover {
  background: rgba(0, 200, 81, 0.1);
  border-color: rgba(0, 200, 81, 0.3);
}

.history-item.active {
  background: rgba(0, 200, 81, 0.15);
  border-color: #00C851;
}

.history-icon {
  margin-right: 0.75rem;
  color: #666;
}

.history-content {
  flex: 1;
}

.history-preview {
  color: #333;
  font-size: 0.9rem;
  margin: 0 0 0.25rem 0;
  font-weight: 500;
}

.history-time {
  color: #999;
  font-size: 0.8rem;
}

/* 오른쪽 채팅 메인 스타일 */
.chat-main {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #E0E0E0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  flex: 1;
}

.chat-title {
  color: #333;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.chat-subtitle {
  color: #666;
  font-size: 1rem;
  margin: 0;
}

.chat-messages {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message-item {
  display: flex;
  gap: 1rem;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-item.ai {
  flex-direction: row;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.message-bubble {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

.message-item.user .message-bubble {
  background: #00C851;
  color: white;
}

.message-item.ai .message-bubble {
  background: white;
  color: #333;
}

.message-text {
  margin: 0 0 0.5rem 0;
  line-height: 1.5;
  white-space: pre-wrap;
}

.message-time {
  font-size: 0.8rem;
  opacity: 0.7;
}

.message-item.user .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.message-item.ai .message-time {
  color: #999;
}

/* 타이핑 인디케이터 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 0.5rem 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #999;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 입력 영역 */
.chat-input-section {
  padding: 1.5rem 2rem;
  border-top: 1px solid #E0E0E0;
}

.input-container {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  background: white;
}

.send-btn {
  font-weight: 600;
  text-transform: none;
  height: 48px;
  padding: 0 1.5rem;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.quick-btn {
  font-size: 0.85rem;
  text-transform: none;
  border-color: #E0E0E0;
}

.submit-section {
  text-align: center;
}

.submit-btn {
  font-weight: 600 !important;
  text-transform: none !important;
  padding: 0 2rem !important;
  height: 48px !important;
  box-shadow: 0 4px 12px rgba(0, 200, 81, 0.3);
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 200, 81, 0.4);
}

/* 반응형 디자인 */
@media (max-width: 1200px) {
  .left-section, .right-section {
    margin-bottom: 2rem;
  }
  
  .chat-sidebar, .chat-main {
    height: auto;
    min-height: 500px;
  }
}

@media (max-width: 960px) {
  .chat-header {
    padding: 1rem 1.5rem;
  }
  
  .chat-messages {
    padding: 1.5rem;
  }
  
  .chat-input-section {
    padding: 1rem 1.5rem;
  }
  
  .input-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .send-btn {
    width: 100%;
  }
}

@media (max-width: 600px) {
  .chat-sidebar, .chat-main {
    padding: 1rem;
  }
  
  .chat-header {
    padding: 1rem;
  }
  
  .chat-messages {
    padding: 1rem;
  }
  
  .chat-input-section {
    padding: 1rem;
  }
  
  .message-content {
    max-width: 85%;
  }
}
</style>
