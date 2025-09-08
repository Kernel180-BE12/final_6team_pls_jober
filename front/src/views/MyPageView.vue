<template>
  <div class="mypage-container">
    <!-- 헤더 컴포넌트 -->
    <HeaderComponent />
    
    <!-- 메인 콘텐츠 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 사용자 정보 섹션 -->
        <div class="user-info-section">
          <div class="user-profile">
            <div class="profile-avatar">
              <div class="avatar-icon">👤</div>
            </div>
            <div class="profile-info">
              <h2 class="user-name">사용자님</h2>
              <p class="user-email">user@example.com</p>
            </div>
          </div>
          <button class="btn-edit-profile">프로필 수정</button>
        </div>

        <!-- 통계 섹션 -->
        <div class="stats-section">
          <h3 class="section-title">활동 통계</h3>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-number">12</div>
              <div class="stat-label">생성된 템플릿</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">8</div>
              <div class="stat-label">완료된 프로젝트</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">24</div>
              <div class="stat-label">총 작업 시간</div>
            </div>
          </div>
        </div>

        <!-- 최근 활동 섹션 -->
        <div class="recent-activity-section">
          <h3 class="section-title">최근 활동</h3>
          <div class="activity-list">
            <div class="activity-item">
              <div class="activity-icon">📝</div>
              <div class="activity-content">
                <div class="activity-title">마케팅 템플릿 생성</div>
                <div class="activity-time">2시간 전</div>
              </div>
            </div>
            <div class="activity-item">
              <div class="activity-icon">✅</div>
              <div class="activity-content">
                <div class="activity-title">프레젠테이션 템플릿 완료</div>
                <div class="activity-time">1일 전</div>
              </div>
            </div>
            <div class="activity-item">
              <div class="activity-icon">📊</div>
              <div class="activity-content">
                <div class="activity-title">데이터 분석 템플릿 생성</div>
                <div class="activity-time">3일 전</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 템플릿 관리 섹션 -->
        <div class="template-management-section">
          <h3 class="section-title">내 템플릿</h3>
          <div class="template-actions">
            <button class="btn-create-template" @click="goToTemplateCreate">
              새 템플릿 만들기
            </button>
            <button class="btn-view-all">전체 보기</button>
          </div>
          <div class="template-grid">
            <div class="template-card">
              <div class="template-icon">📋</div>
              <div class="template-title">마케팅 템플릿</div>
              <div class="template-date">2024.01.15</div>
            </div>
            <div class="template-card">
              <div class="template-icon">📊</div>
              <div class="template-title">데이터 분석 템플릿</div>
              <div class="template-date">2024.01.12</div>
            </div>
            <div class="template-card">
              <div class="template-icon">📝</div>
              <div class="template-title">프레젠테이션 템플릿</div>
              <div class="template-date">2024.01.10</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import HeaderComponent from '../components/HeaderComponent.vue'

const router = useRouter()

const goToTemplateCreate = () => {
  router.push('/template/create')
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

.btn-edit-profile {
  background: linear-gradient(135deg, #1976d2 0%, #8E24AA 100%);
  color: #fff;
  border: none;
  padding: 0.8rem 1.6rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-edit-profile:hover {
  transform: translateY(-0.1rem);
  box-shadow: 0 0.2rem 0.8rem rgba(25, 118, 210, 0.3);
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
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.btn-create-template {
  background: linear-gradient(135deg, #1976d2 0%, #8E24AA 100%);
  color: #fff;
  border: none;
  padding: 0.8rem 1.6rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-create-template:hover {
  transform: translateY(-0.1rem);
  box-shadow: 0 0.2rem 0.8rem rgba(25, 118, 210, 0.3);
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
</style>
