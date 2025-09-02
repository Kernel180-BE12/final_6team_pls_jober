<template>
  <div class="chat-container">
    <v-container class="h-100 pa-0">
      <div class="content-wrapper">
        <!-- 왼쪽: 채팅 내역 -->
        <div class="chat-section">
          <div class="chat-header">
            <h2 class="section-title">AI와의 대화</h2>
            <div class="chat-status">
              <v-chip
                :color="canEdit ? 'success' : 'warning'"
                size="small"
                variant="flat"
              >
                {{ canEdit ? '수정 가능' : '수정 불가' }}
              </v-chip>
              <span class="edit-count">남은 수정 횟수: {{ remainingEdits }}/3</span>
            </div>
          </div>
          
          <div class="chat-messages">
            <div
              v-for="message in chatMessages"
              :key="message.id"
              :class="['message', message.type]"
            >
              <div class="message-avatar">
                <v-icon v-if="message.type === 'user'" color="primary">mdi-account</v-icon>
                <v-icon v-else color="success">mdi-robot</v-icon>
              </div>
              <div class="message-content">
                <div class="message-text">{{ message.text }}</div>
                <div class="message-time">{{ message.time }}</div>
              </div>
            </div>
          </div>
          
          <!-- 채팅 입력창 (수정 가능할 때만 표시) -->
          <div v-if="canEdit" class="chat-input-section">
            <v-textarea
              v-model="newMessage"
              placeholder="메시지를 입력하세요..."
              variant="outlined"
              rows="3"
              auto-grow
              hide-details
              class="chat-textarea"
            />
            <div class="input-actions">
              <v-btn
                color="primary"
                variant="elevated"
                @click="sendMessage"
                :disabled="!newMessage.trim()"
                class="send-btn"
              >
                전송
              </v-btn>
            </div>
          </div>
          
          <!-- 수정 불가 상태일 때 표시 -->
          <div v-else class="chat-disabled">
            <v-alert
              type="warning"
              variant="tonal"
              class="mb-4"
            >
              수정 횟수를 모두 사용했거나 사용자 직접 수정 모드입니다.
            </v-alert>
          </div>
        </div>
        
        <!-- 오른쪽: 알림톡 미리보기 -->
        <div class="preview-section">
          <div class="preview-header">
            <h2 class="section-title">알림톡 미리보기</h2>
            <div class="preview-actions">
              <v-btn
                color="secondary"
                variant="outlined"
                size="small"
                @click="toggleVariableView"
                class="action-btn"
              >
                {{ showVariables ? '전체 보기' : '변수만 보기' }}
              </v-btn>
            </div>
          </div>
          
          <!-- 알림톡 카드 -->
          <div class="kakao-preview-card">
            <div class="kakao-header">
              <div class="kakao-title">
                <v-icon color="yellow-darken-2" size="20">mdi-bell</v-icon>
                <span>알림톡 도착</span>
              </div>
            </div>
            
            <div class="kakao-content">
              <div class="kakao-subject">예약 안내</div>
              
              <div class="kakao-message">
                <div v-if="!showVariables">
                  <p>안녕하세요 <span class="variable">고객님</span>.</p>
                  <p>예약 일정 안내드립니다.</p>
                  <p>▶예약자: <span class="variable">고객</span></p>
                  <p>▶예약일시: <span class="variable">2025.09.05(금) 14:30</span></p>
                  <p>예약 시간 10분 전 도착 부탁드립니다.</p>
                  <p>▶장소: <span class="variable">3층 내과 진료실</span></p>
                  <p>감사합니다.</p>
                </div>
                <div v-else>
                  <p>안녕하세요 <span class="variable-highlight">고객님</span>.</p>
                  <p>예약 일정 안내드립니다.</p>
                  <p>▶예약자: <span class="variable-highlight">고객</span></p>
                  <p>▶예약일시: <span class="variable-highlight">2025.09.05(금) 14:30</span></p>
                  <p>예약 시간 10분 전 도착 부탁드립니다.</p>
                  <p>▶장소: <span class="variable-highlight">3층 내과 진료실</span></p>
                  <p>감사합니다.</p>
                </div>
              </div>
              
              <div class="kakao-button">
                <v-btn variant="outlined" size="small" color="grey">예약확인</v-btn>
              </div>
            </div>
          </div>
          
          <!-- 하단 액션 버튼들 -->
          <div class="preview-actions-bottom">
            <v-btn
              color="warning"
              variant="outlined"
              @click="enableUserEdit"
              :disabled="!canEdit"
              class="action-btn"
            >
              사용자 직접 수정
            </v-btn>
            
            <v-btn
              color="success"
              variant="elevated"
              @click="submitTemplate"
              class="action-btn"
            >
              제출
            </v-btn>
          </div>
        </div>
      </div>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 채팅 관련 상태
const newMessage = ref('')
const remainingEdits = ref(3)
const canEdit = ref(true)
const showVariables = ref(false)

// 채팅 메시지 데이터
const chatMessages = ref([
  {
    id: 1,
    type: 'ai',
    text: '안녕하세요! 카카오 알림톡 템플릿을 만들어드리겠습니다. 어떤 종류의 메시지를 보내고 싶으신가요?',
    time: '14:30'
  },
  {
    id: 2,
    type: 'user',
    text: '병원 예약 안내 메시지를 만들어주세요.',
    time: '14:31'
  },
  {
    id: 3,
    type: 'ai',
    text: '병원 예약 안내 메시지를 생성했습니다. 예약자, 예약일시, 장소 등의 정보를 포함한 템플릿이 준비되었습니다.',
    time: '14:32'
  }
])

// 변수 보기 토글
const toggleVariableView = () => {
  showVariables.value = !showVariables.value
}

// 메시지 전송
const sendMessage = () => {
  if (!newMessage.value.trim() || !canEdit.value) return
  
  // 사용자 메시지 추가
  chatMessages.value.push({
    id: Date.now(),
    type: 'user',
    text: newMessage.value,
    time: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
  })
  
  // AI 응답 시뮬레이션
  setTimeout(() => {
    chatMessages.value.push({
      id: Date.now() + 1,
      type: 'ai',
      text: '메시지를 수정했습니다. 다른 부분도 수정이 필요하신가요?',
      time: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
    })
    
    // 수정 횟수 감소
    if (remainingEdits.value > 0) {
      remainingEdits.value--
      if (remainingEdits.value === 0) {
        canEdit.value = false
      }
    }
  }, 1000)
  
  newMessage.value = ''
}

// 사용자 직접 수정 모드 활성화
const enableUserEdit = () => {
  canEdit.value = false
  remainingEdits.value = 0
}

// 템플릿 제출
const submitTemplate = () => {
  // 검증 결과 페이지로 이동
  router.push('/success')
}
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.content-wrapper {
  height: 100%;
  display: flex;
  gap: 24px;
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

.chat-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background: #fafafa;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 12px 0;
}

.chat-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.edit-count {
  font-size: 0.9rem;
  color: #666;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
}

.message.user .message-content {
  text-align: right;
}

.message-text {
  background: #e3f2fd;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 0.95rem;
  line-height: 1.4;
  word-break: break-word;
}

.message.user .message-text {
  background: #1976d2;
  color: white;
}

.message-time {
  font-size: 0.8rem;
  color: #999;
  margin-top: 4px;
}

.chat-input-section {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  background: #fafafa;
}

.chat-textarea {
  margin-bottom: 12px;
}

.chat-textarea :deep(.v-field) {
  background: white;
  border-radius: 8px;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
}

.send-btn {
  min-width: 80px;
}

.chat-disabled {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  background: #fafafa;
}

.preview-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.preview-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background: #fafafa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-actions {
  display: flex;
  gap: 8px;
}

.kakao-preview-card {
  flex: 1;
  margin: 20px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  background: white;
}

.kakao-header {
  background: #fee500;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.kakao-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1a1a1a;
}

.kakao-content {
  padding: 20px;
}

.kakao-subject {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 16px;
}

.kakao-message {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #333;
  margin-bottom: 20px;
}

.kakao-message p {
  margin: 8px 0;
}

.variable {
  color: #1976d2;
  font-weight: 500;
}

.variable-highlight {
  background: #fff3cd;
  color: #856404;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.kakao-button {
  text-align: center;
}

.preview-actions-bottom {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  background: #fafafa;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.action-btn {
  min-width: 120px;
}

/* 반응형 디자인 제거 - 고정 레이아웃 */
@media (max-width: 1200px) {
  .content-wrapper {
    padding: 20px;
    gap: 20px;
  }
}

@media (max-width: 900px) {
  .content-wrapper {
    flex-direction: column;
    gap: 20px;
  }
  
  .chat-section,
  .preview-section {
    flex: none;
  }
}
</style>
