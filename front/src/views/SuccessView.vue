<template>
  <div class="success-container">
    <v-container class="h-100 pa-0">
      <div class="content-wrapper">
        <!-- 테스트용 버튼들 -->
        <div class="test-buttons">
          <v-btn
            color="warning"
            variant="outlined"
            @click="setRejectionMode"
            class="test-btn"
          >
            반려로 가기
          </v-btn>
          <v-btn
            color="success"
            variant="outlined"
            @click="setSuccessMode"
            class="test-btn"
          >
            축하로 가기
          </v-btn>
        </div>
        
        <!-- 축하 페이지 -->
        <div v-if="isSuccess" class="success-section">
          <div class="success-content">
            <h1 class="success-title">
              메세지를 성공적으로<br>
              전송하였습니다.
            </h1>
            
            <div class="success-emoji">
              👏 👏 👏
            </div>
            
            <div class="success-actions">
              <v-btn
                color="primary"
                size="large"
                variant="elevated"
                @click="goToLanding"
                class="action-btn"
              >
                추가 템플릿 이용
              </v-btn>
              <v-btn
                color="secondary"
                size="large"
                variant="outlined"
                @click="goToLanding"
                class="action-btn"
              >
                HOME
              </v-btn>
            </div>
          </div>
        </div>
        
        <!-- 반려 페이지 -->
        <div v-else class="rejection-section">
          <div class="rejection-content">
            <div class="rejection-header">
              <div class="rejection-icon">
                <v-icon size="80" color="warning">mdi-alert-circle</v-icon>
              </div>
              <h1 class="rejection-title">검증에 실패했습니다</h1>
              <p class="rejection-subtitle">
                다음 부적절한 부분을 수정해주세요
              </p>
            </div>
            
            <!-- 부적절한 부분 목록 -->
            <div class="issues-section">
              <h3 class="issues-title">수정이 필요한 부분</h3>
              <div class="issues-list">
                <div
                  v-for="issue in issues"
                  :key="issue.id"
                  class="issue-item"
                  :class="{ 'expanded': expandedIssue === issue.id }"
                >
                  <div class="issue-header" @click="toggleIssue(issue.id)">
                    <div class="issue-info">
                      <v-icon color="error" size="20">mdi-close-circle</v-icon>
                      <span class="issue-text">{{ issue.text }}</span>
                    </div>
                    <v-icon
                      :icon="expandedIssue === issue.id ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                      size="20"
                    />
                  </div>
                  
                  <!-- 대체 문장 추천 -->
                  <div v-if="expandedIssue === issue.id" class="issue-suggestions">
                    <p class="suggestions-title">대체 가능한 문장/단어:</p>
                    <div class="suggestions-list">
                      <v-btn
                        v-for="suggestion in issue.suggestions"
                        :key="suggestion"
                        variant="outlined"
                        color="primary"
                        size="small"
                        @click="selectSuggestion(issue.id, suggestion)"
                        class="suggestion-btn"
                      >
                        {{ suggestion }}
                      </v-btn>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 액션 버튼들 -->
            <div class="rejection-actions">
              <v-btn
                color="primary"
                size="large"
                variant="elevated"
                @click="goToChat"
                class="action-btn"
              >
                채팅으로 돌아가기
              </v-btn>
              <v-btn
                color="secondary"
                size="large"
                variant="outlined"
                @click="goToLanding"
                class="action-btn"
              >
                처음으로
              </v-btn>
            </div>
          </div>
        </div>
      </div>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 페이지 모드 (성공/반려)
const isSuccess = ref(true)

// 반려 시 확장된 이슈
const expandedIssue = ref<number | null>(null)

// 부적절한 부분 데이터
const issues = ref([
  {
    id: 1,
    text: '"고객님"이라는 표현이 너무 격식적입니다',
    suggestions: ['손님', '이용자', '고객']
  },
  {
    id: 2,
    text: '"감사합니다"가 너무 짧고 딱딱합니다',
    suggestions: ['감사드립니다', '고맙습니다', '감사합니다']
  },
  {
    id: 3,
    text: '"도착 부탁드립니다"가 명령조로 들립니다',
    suggestions: ['도착해 주시기 바랍니다', '도착하시면 됩니다', '도착 부탁드립니다']
  }
])

// 테스트용 모드 설정
const setRejectionMode = () => {
  isSuccess.value = false
}

const setSuccessMode = () => {
  isSuccess.value = true
}

// 이슈 확장/축소
const toggleIssue = (issueId: number) => {
  expandedIssue.value = expandedIssue.value === issueId ? null : issueId
}

// 대체 문장 선택
const selectSuggestion = (issueId: number, suggestion: string) => {
  console.log(`이슈 ${issueId}에 "${suggestion}" 선택됨`)
  // TODO: 실제로는 선택된 대체 문장을 적용하는 로직 구현
}

// 페이지 이동
const goToLanding = () => {
  router.push('/')
}

const goToChat = () => {
  router.push('/chat')
}
</script>

<style scoped>
.success-container {
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #e3f2fd 0%, #f1f8e9 100%);
}

.content-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.test-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 40px;
}

.test-btn {
  min-width: 120px;
}

.success-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-content {
  text-align: center;
  max-width: 600px;
}

.success-title {
  font-size: 3.5rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 40px;
  line-height: 1.3;
}

.success-emoji {
  font-size: 4rem;
  margin-bottom: 60px;
  letter-spacing: 8px;
}

.success-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.action-btn {
  min-width: 180px;
  height: 56px;
  font-size: 1.1rem;
  font-weight: 600;
  text-transform: none;
  border-radius: 8px;
}

.rejection-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rejection-content {
  max-width: 800px;
  width: 100%;
}

.rejection-header {
  text-align: center;
  margin-bottom: 48px;
}

.rejection-icon {
  margin-bottom: 24px;
}

.rejection-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #f57c00;
  margin-bottom: 16px;
}

.rejection-subtitle {
  font-size: 1.25rem;
  color: #666;
  margin: 0;
}

.issues-section {
  margin-bottom: 48px;
}

.issues-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 24px;
  text-align: center;
}

.issues-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.issue-item {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.issue-item.expanded {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.issue-header {
  padding: 20px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff3e0;
  transition: background-color 0.3s ease;
}

.issue-header:hover {
  background: #ffe0b2;
}

.issue-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.issue-text {
  font-size: 1rem;
  color: #333;
  font-weight: 500;
}

.issue-suggestions {
  padding: 20px;
  background: #fafafa;
  border-top: 1px solid #e0e0e0;
}

.suggestions-title {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 16px;
  font-weight: 500;
}

.suggestions-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.suggestion-btn {
  font-size: 0.9rem;
}

.rejection-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

/* 반응형 디자인 제거 - 고정 레이아웃 */
@media (max-width: 1200px) {
  .content-wrapper {
    padding: 30px;
  }
}

@media (max-width: 900px) {
  .content-wrapper {
    padding: 20px;
  }
  
  .success-title {
    font-size: 3rem;
  }
  
  .success-emoji {
    font-size: 3.5rem;
    letter-spacing: 6px;
  }
  
  .success-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .action-btn {
    width: 100%;
    max-width: 300px;
  }
  
  .rejection-title {
    font-size: 2rem;
  }
  
  .rejection-actions {
    flex-direction: column;
    align-items: center;
  }
}

@media (max-width: 600px) {
  .content-wrapper {
    padding: 16px;
  }
  
  .success-title {
    font-size: 2.5rem;
  }
  
  .success-emoji {
    font-size: 3rem;
    letter-spacing: 4px;
  }
  
  .test-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .test-btn {
    width: 200px;
  }
  
  .rejection-title {
    font-size: 1.8rem;
  }
}
</style>
