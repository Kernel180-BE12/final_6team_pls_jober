<template>
  <div class="mypage-container">
    <!-- 헤더 컴포넌트 -->
    <HeaderComponent />

    <!-- 메인 콘텐츠 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 사용자 정보 섹션 -->
        <div class="user-info-section">
          <div v-if="loading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>사용자 정보를 불러오는 중...</p>
          </div>
          <div v-else-if="error" class="error-state">
            <p class="error-message">{{ error }}</p>
            <button class="btn-retry" @click="fetchUserInfo">다시 시도</button>
          </div>
          <div v-else class="user-profile">
            <div class="profile-avatar">
              <div class="avatar-icon">👤</div>
            </div>
            <div class="profile-info">
              <h2 class="user-name">{{ userInfo.name || '사용자님' }}</h2>
              <p class="user-email">{{ userInfo.email || 'user@example.com' }}</p>
            </div>
          </div>
          <div class="profile-actions">
            <button
                v-for="item in myBtn"
                :key="item.id"
                @click="item.click"
                class="btn btn-gradation02"
            >
              {{ item.text }}
            </button>
          </div>
        </div>

        <!-- 통계 섹션 -->
        <div class="stats-section">
          <h3 class="section-title">활동 통계</h3>
          <div class="template-grid">
            <div
              v-for="item in recAtivity"
              key="item.id"
              class="stat-card">
              <div class="stat-number">{{ item.num }}</div>
              <div class="stat-label">{{ item.text }}</div>
            </div>
          </div>
        </div>

        <!-- 최근 활동 섹션 -->
        <div class="recent-activity-section">
          <h3 class="section-title">최근 활동</h3>
          <div class="activity-list">
            <div
              v-for="item in ativity"
              key="item.id"
              class="activity-item">
              <div class="activity-icon">{{ item.icon }}</div>
              <div class="activity-content">
                <div class="activity-title">{{ item.text }}</div>
                <div class="activity-time">{{ item.time }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 템플릿 관리 섹션 -->
        <div class="template-management-section">
          <h3 class="section-title">내 템플릿</h3>
          <div class="template-actions">
            <button class="btn btn-gradation02" @click="goToTemplateCreate">
              새 템플릿 만들기
            </button>
            <button class="btn btn-gradation02 basic">전체 보기</button>
          </div>
          <div class="template-grid">
            <div
                v-for="item in template"
                key="item.id"
                class="template-card">
                <div class="template-icon">{{ item.icon }}</div>
                <div class="template-title">{{ item.text }}</div>
                <div class="template-date">{{ item.time }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 프로필 수정 모달 -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">
            {{ editMode === 'name' ? '이름 수정' : editMode === 'email' ? '이메일 수정' : '비밀번호 수정' }}
          </h3>
          <button class="modal-close" @click="closeEditModal">×</button>
        </div>

        <div class="modal-body">
          <div v-if="updateError" class="error-message">{{ updateError }}</div>

          <!-- 이름 수정 폼 -->
          <div v-if="editMode === 'name'" class="edit-form">
            <div class="form-group">
              <label for="name">이름</label>
              <input
                  id="name"
                  v-model="editForm.name"
                  type="text"
                  class="form-input"
                  placeholder="새로운 이름을 입력하세요"
                  :disabled="updating"
              />
            </div>
          </div>

          <!-- 이메일 수정 폼 -->
          <div v-if="editMode === 'email'" class="edit-form">
            <div class="form-group">
              <label for="email">새 이메일</label>
              <input
                  id="email"
                  v-model="editForm.email"
                  type="email"
                  class="form-input"
                  placeholder="새로운 이메일을 입력하세요"
                  :disabled="updating"
              />
            </div>
            <div class="form-group">
              <label for="currentPassword">현재 비밀번호</label>
              <input
                  id="currentPassword"
                  v-model="editForm.currentPassword"
                  type="password"
                  class="form-input"
                  placeholder="현재 비밀번호를 입력하세요"
                  :disabled="updating"
              />
            </div>
          </div>

          <!-- 비밀번호 수정 폼 -->
          <div v-if="editMode === 'password'" class="edit-form">
            <div class="form-group">
              <label for="currentPassword">현재 비밀번호</label>
              <input
                  id="currentPassword"
                  v-model="editForm.currentPassword"
                  type="password"
                  class="form-input"
                  placeholder="현재 비밀번호를 입력하세요"
                  :disabled="updating"
              />
            </div>
            <div class="form-group">
              <label for="newPassword">새 비밀번호</label>
              <input
                  id="newPassword"
                  v-model="editForm.newPassword"
                  type="password"
                  class="form-input"
                  placeholder="새 비밀번호를 입력하세요"
                  :disabled="updating"
              />
            </div>
            <div class="form-group">
              <label for="confirmPassword">새 비밀번호 확인</label>
              <input
                  id="confirmPassword"
                  v-model="editForm.confirmPassword"
                  type="password"
                  class="form-input"
                  placeholder="새 비밀번호를 다시 입력하세요"
                  :disabled="updating"
              />
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-gradation02 basic" @click="closeEditModal" :disabled="updating">취소</button>
          <button
              class="btn btn-gradation02"
              @click="editMode === 'name' ? updateName() : editMode === 'email' ? updateEmail() : updatePassword()"
              :disabled="updating"
          >
            {{ updating ? '수정 중...' : '저장' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import HeaderComponent from '../components/HeaderComponent.vue'
import { myPageApi } from '../api'

const router = useRouter()

// 사용자 정보 상태
const userInfo = ref({
  id: null as number | null,
  name: '',
  email: ''
})

const loading = ref(true)
const error = ref('')

// 모달 상태
const showEditModal = ref(false)
const editMode = ref<'name' | 'email' | 'password' | null>(null)
const updating = ref(false)
const updateError = ref('')

// 수정 폼 데이터
const editForm = ref({
  name: '',
  email: '',
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 모달 열기/닫기
function openEditModal(mode: 'name' | 'email' | 'password') {
  editMode.value = mode
  showEditModal.value = true
  updateError.value = ''
}
function closeEditModal() {
  showEditModal.value = false
  editMode.value = null
  editForm.value = { name: '', email: '', currentPassword: '', newPassword: '', confirmPassword: '' }
  updateError.value = ''
}

// 수정 버튼 목록
const myBtn = [
  { id: 1, text: "이름 수정", click: () => openEditModal('name') },
  { id: 2, text: "이메일 수정", click: () => openEditModal('email') },
  { id: 3, text: "비밀번호 수정", click: () => openEditModal('password') }
]

const recAtivity = [
  { id: 1, num: 12, text: "생성된 템플릿" },
  { id: 2, num: 8, text: "완료된 프로젝트" },
  { id: 3, num: 24, text: "총 작업 시간" },
]

const ativity = [
  { id: 1, icon: "📝", text: "마케팅 템플릿 생성", time: "2시간 전" },
  { id: 2, icon: "✅", text: "프레젠테이션 템플릿 완료", time: "1일 전" },
  { id: 3, icon: "📊", text: "데이터 분석 템플릿 생성", time: "3일 전" },
]

const template = [
  {id: 1, icon: "📋", text: "마케팅 템플릿", time: "2024.01.15"},
  {id: 2, icon: "📊", text: "데이터 분석 템플릿", time: "2024.01.12"},
  {id: 3, icon: "📝", text: "프레젠테이션 템플릿", time: "2024.01.10"},
]

// 사용자 정보 가져오기
const fetchUserInfo = async () => {
  try {
    loading.value = true
    error.value = ''
    const response = await myPageApi.getMyInfo()
    userInfo.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.message || '사용자 정보를 가져오는데 실패했습니다.'
    console.error('Failed to fetch user info:', err)
  } finally {
    loading.value = false
  }
}
onMounted(() => {
  fetchUserInfo()
})

// 업데이트 함수들
const updateName = async () => {
  try {
    updating.value = true
    updateError.value = ''
    await myPageApi.updateName(editForm.value.name)
    await fetchUserInfo()
    closeEditModal()
  } catch (err: any) {
    updateError.value = err.response?.data?.message || '이름 수정에 실패했습니다.'
  } finally {
    updating.value = false
  }
}
const updateEmail = async () => {
  try {
    updating.value = true
    updateError.value = ''
    await myPageApi.updateEmail(editForm.value.email, editForm.value.currentPassword)
    await fetchUserInfo()
    closeEditModal()
  } catch (err: any) {
    updateError.value = err.response?.data?.message || '이메일 수정에 실패했습니다.'
  } finally {
    updating.value = false
  }
}
const updatePassword = async () => {
  try {
    updating.value = true
    updateError.value = ''
    await myPageApi.updatePassword(
        editForm.value.currentPassword,
        editForm.value.newPassword,
        editForm.value.confirmPassword
    )
    closeEditModal()
  } catch (err: any) {
    updateError.value = err.response?.data?.message || '비밀번호 수정에 실패했습니다.'
  } finally {
    updating.value = false
  }
}

// 템플릿 작성 페이지 이동
const goToTemplateCreate = () => {
  router.push('/')
}
</script>

<style scoped>

.mypage-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.main-content {
  padding: 2rem 0;
}

.content-wrapper {
  max-width: 60rem;
  margin: 0 auto;
  padding: 0 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 사용자 정보 섹션 */
.user-info-section {
  background: #fff;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 0.2rem 1rem rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}

.profile-avatar {
  width: 4rem;
  height: 4rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #1976d2 0%, #8E24AA 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-icon {
  font-size: 2rem;
  color: #fff;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.user-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.user-email {
  font-size: 1rem;
  color: #666;
  margin: 0;
}

/* 섹션 공통 스타일 */
.section-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 1.2rem 0;
}

/* 통계 섹션 */
.stats-section {
  background: #fff;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 0.2rem 1rem rgba(0, 0, 0, 0.1);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
  gap: 1.2rem;
}

.stat-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 0.8rem;
  padding: 1.5rem;
  text-align: center;
  border: 0.1rem solid #e9ecef;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #1976d2;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

/* 최근 활동 섹션 */
.recent-activity-section {
  background: #fff;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 0.2rem 1rem rgba(0, 0, 0, 0.1);
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.8rem;
  border: 0.1rem solid #e9ecef;
}

.activity-icon {
  font-size: 1.5rem;
  width: 3rem;
  height: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 0.1rem 0.3rem rgba(0, 0, 0, 0.1);
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.2rem;
}

.activity-time {
  font-size: 0.9rem;
  color: #666;
}

/* 템플릿 관리 섹션 */
.template-management-section {
  background: #fff;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 0.2rem 1rem rgba(0, 0, 0, 0.1);
}

.template-actions {
  display: flex;
  gap: .5rem;
  margin-bottom: 1.5rem;
}

.btn-view-all {
  background: transparent;
  color: #1976d2;
  border: 0.1rem solid #1976d2;
  padding: 0.8rem 1.6rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-view-all:hover {
  background: #1976d2;
  color: #fff;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
  gap: 1.2rem;
}

.template-card {
  background: #f8f9fa;
  border-radius: 0.8rem;
  padding: 1.5rem;
  text-align: center;
  border: 0.1rem solid #e9ecef;
  transition: all 0.3s ease;
  cursor: pointer;
}

.template-card:hover {
  transform: translateY(-0.1rem);
  box-shadow: 0 0.2rem 0.8rem rgba(0, 0, 0, 0.1);
  border-color: #1976d2;
}

.template-icon {
  font-size: 2rem;
  margin-bottom: 0.8rem;
}

.template-title {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.template-date {
  font-size: 0.9rem;
  color: #666;
}

/* 로딩 및 에러 상태 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 0.2rem solid #e9ecef;
  border-top: 0.2rem solid #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
}

.error-message {
  color: #dc3545;
  font-size: 0.9rem;
  text-align: center;
}

.btn-retry {
  background: #1976d2;
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.3rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-retry:hover {
  background: #1565c0;
}

/* 프로필 액션 버튼들 */
.profile-actions {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.profile-actions .btn-edit-profile {
  font-size: 0.9rem;
  padding: 0.6rem 1.2rem;
}

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 1rem;
  width: 90%;
  max-width: 30rem;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 0.5rem 2rem rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 0.1rem solid #e9ecef;
}

.modal-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: #333;
}

.modal-body {
  padding: 2rem;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
}

.form-input {
  padding: 0.8rem;
  border: 0.1rem solid #ddd;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 0.2rem rgba(25, 118, 210, 0.1);
}

.form-input:disabled {
  background: #f8f9fa;
  color: #666;
  cursor: not-allowed;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  padding: 1.5rem 2rem;
  border-top: 0.1rem solid #e9ecef;
  justify-content: flex-end;
}

.btn-cancel {
  background: transparent;
  color: #666;
  border: 0.1rem solid #ddd;
  padding: 0.8rem 1.6rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #999;
}

.btn-cancel:disabled{
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
</style>
