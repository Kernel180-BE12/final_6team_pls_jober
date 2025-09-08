<template>
  <div class="chat-component">
    <!-- 채팅 메시지 영역 -->
    <div class="chat-messages">
      <div 
        v-for="(message, index) in chatMessages" 
        :key="index"
        :class="['message', message.type]"
      >
        <div class="message-content">
          <p>{{ message.text }}</p>
        </div>
        <div class="message-time">{{ message.time }}</div>
      </div>
    </div>
    
    <!-- 입력 필드 -->
    <div class="input-field">
      <input 
        v-model="inputMessage"
        type="text" 
        placeholder="발송하고 싶은 내용을 입력하세요"
        class="message-input"
        :disabled="isModifying"
        @keyup.enter="sendMessage"
      />
      <button class="btn-send" :disabled="isModifying" @click="sendMessage">Enter</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface ChatComponentProps {
  isModifying: boolean
}

const props = defineProps<ChatComponentProps>()

// 채팅 관련 변수들
const inputMessage = ref('')
const chatMessages = ref([
  {
    type: 'bot',
    text: '안녕하세요! 템플릿 수정에 도움이 필요하시면 언제든 말씀해주세요.',
    time: '방금 전'
  }
])

// 메시지 전송
const sendMessage = () => {
  if (inputMessage.value.trim() === '') return
  
  // 사용자 메시지 추가
  const userMessage = {
    type: 'user',
    text: inputMessage.value,
    time: new Date().toLocaleTimeString('ko-KR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }
  chatMessages.value.push(userMessage)
  
  // 입력창 초기화
  inputMessage.value = ''
  
  // 봇 응답 (고정된 답변)
  setTimeout(() => {
    const botResponses = [
      '네, 말씀해주세요. 어떤 부분을 도와드릴까요?',
      '좋은 질문이네요! 더 자세히 설명드리겠습니다.',
      '이해했습니다. 해당 기능을 구현해드리겠습니다.',
      '도움이 되었다니 기쁩니다. 다른 궁금한 점이 있으시면 언제든 말씀해주세요.',
      '템플릿 수정에 대해 궁금한 점이 있으시면 편하게 문의해주세요.'
    ]
    
    const randomResponse = botResponses[Math.floor(Math.random() * botResponses.length)]
    
    const botMessage = {
      type: 'bot',
      text: randomResponse,
      time: new Date().toLocaleTimeString('ko-KR', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    }
    chatMessages.value.push(botMessage)
  }, 1000)
}
</script>

<style scoped>
.chat-component {
  margin-top: 0.8rem;
  display: flex;
  flex-direction: column;
  height: 15rem;
}

.input-field {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  margin-top: auto;
  padding-top: 0.8rem;
}

.message-input {
  flex: 1;
  padding: 0.5rem;
  border: 0.05rem solid #ddd;
  border-radius: 0.2rem;
  font-size: 1rem;
}

.btn-send {
  background-color: #1976d2;
  color: white;
  border: none;
  padding: 0.5rem;
  border-radius: 0.2rem;
  cursor: pointer;
  font-size: 1rem;
}

/* 채팅 메시지 영역 스타일 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  border: 0.05rem solid #e0e0e0;
  border-radius: 0.4rem;
  padding: 0.8rem;
  background-color: #f8f9fa;
  margin-bottom: 0.8rem;
}

.chat-messages::-webkit-scrollbar {
  width: 0.3rem;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 0.15rem;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 0.15rem;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.message {
  margin-bottom: 0.8rem;
  display: flex;
  flex-direction: column;
}

.message.user {
  align-items: flex-end;
}

.message.bot {
  align-items: flex-start;
}

.message-content {
  max-width: 80%;
  padding: 0.6rem 0.8rem;
  border-radius: 0.9rem;
  position: relative;
}

.message.user .message-content {
  background-color: #1976d2;
  color: white;
  border-bottom-right-radius: 0.2rem;
}

.message.bot .message-content {
  background-color: #e9ecef;
  color: #333;
  border-bottom-left-radius: 0.2rem;
}

.message-content p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.message-time {
  font-size: 0.75rem;
  color: #666;
  margin-top: 0.2rem;
  padding: 0 0.2rem;
}

.message.user .message-time {
  text-align: right;
}

.message.bot .message-time {
  text-align: left;
}
</style>
