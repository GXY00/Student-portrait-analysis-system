<template>
  <div class="dashboard-content">
    <div class="dashboard-header">
      <div class="dashboard-title">个人信息管理</div>
    </div>
    <div class="container">
      <div v-if="roleId === 3" class="admin-message-container">
        <div class="admin-message">您的身份是系统管理员，请前往用户管理进行具体操作</div>
      </div>
      <div v-else class="profile-list">
        <div class="profile-item">
          <span class="label">姓名</span>
          <span class="value">{{ userInfo.name }}</span>
        </div>

        <div class="profile-item">
          <span class="label">学号/工号</span>
          <span class="value">{{ userInfo.studentId }}</span>
        </div>

        <div class="profile-item">
          <span class="label">性别</span>
          <span class="value">{{ userInfo.gender }}</span>
        </div>

        <div class="profile-item">
          <span class="label">年级</span>
          <span class="value">{{ userInfo.grade }}</span>
        </div>

        <div class="profile-item">
          <span class="label">班级</span>
          <span class="value">{{ userInfo.class }}</span>
        </div>

        <div class="profile-item" :class="{ 'editing': isEditingPassword }">
          <span class="label">密码</span>
          <div class="password-value-container">
            <span v-if="!isEditingPassword" class="value password-text">{{ isPasswordVisible ? userInfo.password : '*************' }}</span>
            <div v-else class="password-edit-group">
              <input type="password" v-model="oldPassword" class="password-input" placeholder="请输入原密码" />
              <input :type="isPasswordVisible ? 'text' : 'password'" v-model="newPassword" class="password-input" placeholder="请输入新密码" />
              <input type="password" v-model="confirmPassword" class="password-input" placeholder="请确认新密码" />
            </div>
            <button class="icon-btn" @click="togglePasswordVisibility" title="显示/隐藏密码" v-if="!isEditingPassword || newPassword">
              <svg v-if="isPasswordVisible" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                <circle cx="12" cy="12" r="3"></circle>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                <line x1="1" y1="1" x2="23" y2="23"></line>
              </svg>
            </button>
            <button class="change-pwd-btn" @click="changePassword">
              {{ isEditingPassword ? '确认修改' : '修改密码' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 确认弹窗 -->
    <div v-if="showConfirmModal" class="modal-overlay">
      <div class="modal-content">
        <h3>确认修改密码</h3>
        <p>您确定要将密码修改为 "{{ newPassword }}" 吗？</p>
        <div class="modal-actions">
          <button class="modal-btn cancel" @click="cancelUpdate">取消</button>
          <button class="modal-btn confirm" @click="confirmUpdate">确认</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserProfile',
  data () {
    return {
      isPasswordVisible: false,
      isEditingPassword: false,
      oldPassword: '',
      newPassword: '',
      confirmPassword: '',
      showConfirmModal: false,
      roleId: null,
      userInfo: {
        name: '',
        username: '',
        studentId: '',
        gender: '',
        grade: '',
        class: '',
        password: ''
      }
    }
  },
  mounted () {
    this.fetchUserInfo()
  },
  methods: {
    fetchUserInfo () {
      const username = localStorage.getItem('username')
      if (!username) {
        // 如果没有用户名，可能需要重新登录或使用默认值
        // 这里假设已经登录
        return
      }
      fetch('/api/v1/user/detail', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username })
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            this.userInfo = data.data
            this.roleId = data.data.role_id
          } else {
            console.error('Failed to fetch user info:', data.msg)
          }
        })
        .catch(error => {
          console.error('Error fetching user info:', error)
        })
    },
    togglePasswordVisibility () {
      this.isPasswordVisible = !this.isPasswordVisible
    },
    changePassword () {
      // 直接跳转到忘记密码页面
      this.$router.push('/forgot-password')
    }
  }
}
</script>

<style scoped>
.dashboard-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  width: 100%;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background-color: transparent;
}

.dashboard-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.container {
  background-color: #fff;
  border-radius: 4px;
  flex: 1; /* 占满剩余高度 */
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  min-height: 400px; /* 最小高度保证 */
  padding: 10px;
}

.profile-list {
  padding: 20px 40px;
  max-width: 800px;
}

.profile-item {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  font-size: 16px;
}

.label {
  width: 100px;
  color: #333;
  font-weight: 500;
}

.value {
  color: #333;
  font-weight: 500;
}

.password-value-container {
  display: flex;
  align-items: center;
}

.password-text {
  margin-right: 15px;
  min-width: 120px;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  margin-right: 20px;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  color: #4169e1;
}

.change-pwd-btn {
  background-color: #4169e1;
  color: white;
  border: none;
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.change-pwd-btn:hover {
  background-color: #3154b3;
}

.password-input {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  margin-right: 15px;
  min-width: 150px;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 400px;
  max-width: 90%;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 18px;
  color: #333;
}

.modal-content p {
  margin-bottom: 24px;
  color: #666;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.modal-btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: background-color 0.2s;
}

.modal-btn.cancel {
  background-color: #f5f5f5;
  color: #666;
}

.modal-btn.cancel:hover {
  background-color: #e0e0e0;
}

.modal-btn.confirm {
  background-color: #4169e1;
  color: white;
}

.modal-btn.confirm:hover {
  background-color: #3154b3;
}

.password-edit-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-right: 15px;
}

.password-edit-group .password-input {
  margin-right: 0;
  width: 250px;
}

.admin-message-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  min-height: 300px;
}

.admin-message {
  font-size: 20px;
  color: #666;
  font-weight: 500;
  text-align: center;
}
</style>
