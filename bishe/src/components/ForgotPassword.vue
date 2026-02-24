<template>
  <div class="forgot-container">
    <div class="header">
      <span class="breadcrumb">
        <router-link to="/">登录</router-link>
        <span class="separator">></span>
        <span class="current">忘记/修改密码</span>
      </span>
    </div>

    <div class="content-wrapper">
      <!-- 步骤条 -->
      <div class="stepper">
        <div class="step-item" :class="{ active: currentStep >= 1 }">
          <div class="step-circle" :class="{ active: currentStep >= 1 }">1</div>
          <span class="step-text" :class="{ active: currentStep >= 1 }">确认账号</span>
        </div>
        <div class="step-line"></div>
        <div class="step-item" :class="{ active: currentStep >= 2 }">
          <div class="step-circle" :class="{ active: currentStep >= 2 }">2</div>
          <span class="step-text" :class="{ active: currentStep >= 2 }">重置密码</span>
        </div>
        <div class="step-line"></div>
        <div class="step-item" :class="{ active: currentStep >= 3 }">
          <div class="step-circle" :class="{ active: currentStep >= 3 }">3</div>
          <span class="step-text" :class="{ active: currentStep >= 3 }">重置成功</span>
        </div>
      </div>

      <!-- 步骤内容 -->
      <div class="step-content">
        <!-- 步骤 1: 确认账号 -->
        <div v-if="currentStep === 1" class="form-step">
          <div class="form-group">
            <input
              type="text"
              v-model="account"
              placeholder="请输入账号"
              class="input-field"
            />
          </div>
          <button class="btn-primary" @click="handleNext">确认</button>
        </div>

        <!-- 步骤 2: 重置密码 -->
        <div v-if="currentStep === 2" class="form-step">
          <div class="form-row">
            <label>新密码：</label>
            <input
              type="password"
              v-model="newPassword"
              placeholder="避免使用容易猜测的序列"
              class="input-field"
            />
          </div>
          <div class="form-row">
            <label>确认密码：</label>
            <input
              type="password"
              v-model="confirmPassword"
              placeholder="输入确认密码"
              class="input-field"
            />
          </div>
          <div class="form-row">
            <label>验证码：</label>
            <div style="display: flex; align-items: center; width: 100%;">
              <input
                type="text"
                v-model="captchaCode"
                placeholder="请输入验证码"
                class="input-field"
                style="margin-right: 10px;"
              />
              <div @click="refreshCaptcha" title="点击刷新验证码" style="cursor: pointer;">
                <img :src="captchaUrl" alt="验证码" style="height: 45px; border-radius: 4px;" />
              </div>
            </div>
          </div>
          <div class="button-group">
            <button class="btn-secondary" @click="handlePrev">返回上一步</button>
            <button class="btn-primary" @click="handleNext">确认修改</button>
          </div>
        </div>

        <!-- 步骤 3: 重置成功 -->
        <div v-if="currentStep === 3" class="form-step success-step">
          <div class="success-icon">✓</div>
          <div class="success-text">密码重置成功</div>
          <button class="btn-primary" @click="handleFinish">返回登录</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ForgotPassword',
  data () {
    return {
      currentStep: 1,
      account: '',
      newPassword: '',
      confirmPassword: '',
      captchaCode: '',
      captchaUrl: '',
      correctCaptcha: ''
    }
  },
  mounted () {
    this.refreshCaptcha()
  },
  methods: {
    refreshCaptcha () {
      fetch('/api/v1/captcha?t=' + new Date().getTime())
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok')
          }
          return response.json()
        })
        .then(data => {
          this.captchaUrl = data.img
          this.correctCaptcha = data.code
        })
        .catch(error => {
          console.error('Failed to fetch captcha:', error)
        })
    },
    handlePrev () {
      if (this.currentStep > 1) {
        this.currentStep--
      }
    },
    handleNext () {
      if (this.currentStep === 1) {
        if (!this.account) {
          alert('请输入账号')
          return
        }

        // Check if user exists
        fetch('/api/v1/user/check_exist', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ username: this.account })
        })
          .then(res => res.json())
          .then(data => {
            if (data.exists) {
              this.currentStep = 2
            } else {
              alert('用户不存在，请重新输入')
            }
          })
          .catch(err => {
            console.error(err)
            alert('系统错误，请稍后重试')
          })
      } else if (this.currentStep === 2) {
        if (!this.newPassword || !this.confirmPassword) {
          alert('请输入新密码和确认密码')
          return
        }
        if (this.newPassword !== this.confirmPassword) {
          alert('两次输入的密码不一致')
          return
        }
        // Password validation
        // At least 8 characters, include uppercase, lowercase, and numbers
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/
        if (!passwordRegex.test(this.newPassword)) {
          alert('密码至少包含8个字符，且必须包含大小写字母和数字')
          return
        }

        if (!this.captchaCode) {
          alert('请输入验证码')
          return
        }

        // 弹出再次确认窗口
        if (confirm('确认修改密码吗？')) {
          // Call reset password API
          fetch('/api/v1/user/reset_password', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              username: this.account,
              new_password: this.newPassword,
              captcha_code: this.captchaCode
            })
          })
            .then(res => res.json())
            .then(data => {
              if (data.success) {
                this.currentStep = 3
              } else {
                alert(data.msg || '修改失败')
                this.refreshCaptcha()
                this.captchaCode = ''
              }
            })
            .catch(err => {
              console.error(err)
              alert('系统错误，请稍后重试')
              this.refreshCaptcha()
            })
        }
      }
    },
    handleFinish () {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.forgot-container {
  min-height: 100vh;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  padding: 40px;
}

.header {
  margin-bottom: 40px;
}

.breadcrumb {
  font-size: 14px;
  color: #333;
  font-weight: bold;
}

.breadcrumb a {
  text-decoration: none;
  color: #333;
}

.separator {
  margin: 0 5px;
  color: #999;
}

.current {
  color: #666;
}

.content-wrapper {
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

/* 步骤条样式 */
.stepper {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  padding: 20px 0;
  margin-bottom: 60px;
  border-radius: 4px;
}

.step-item {
  display: flex;
  align-items: center;
  position: relative;
}

.step-circle {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1px solid #ccc;
  color: #ccc;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  margin-right: 8px;
}

.step-text {
  color: #ccc;
  font-size: 16px;
}

.step-item.active .step-circle {
  border-color: #4169e1;
  color: #4169e1;
  border-width: 2px;
}

.step-item.active .step-text {
  color: #4169e1;
  font-weight: bold;
}

.step-line {
  width: 100px;
  height: 1px;
  background-color: #e0e0e0;
  margin: 0 20px;
}

/* 表单内容样式 */
.step-content {
  display: flex;
  justify-content: center;
}

.form-step {
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.form-group {
  width: 100%;
  margin-bottom: 30px;
}

.form-row {
  width: 100%;
  display: flex;
  align-items: center;
  margin-bottom: 25px;
}

.form-row label {
  width: 80px;
  text-align: right;
  margin-right: 15px;
  font-size: 14px;
  color: #333;
  font-weight: bold;
}

.text-row {
  font-size: 14px;
}

.student-id {
  font-weight: bold;
  margin-right: 20px;
}

.link-modify {
  color: #4169e1;
  text-decoration: none;
  font-size: 12px;
}

.input-field {
  flex: 1;
  width: 100%;
  box-sizing: border-box;
  height: 45px;
  border: 1px solid #e0e0e0;
  border-radius: 25px;
  padding: 0 20px;
  font-size: 14px;
  outline: none;
}

.input-field:focus {
  border-color: #4169e1;
}

.button-group {
  width: 100%;
  display: flex;
  justify-content: space-between;
  gap: 15px;
  margin-top: 10px;
}

.btn-primary {
  width: 100%;
  height: 50px;
  background-color: #4169e1;
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
}

.button-group .btn-primary {
  flex: 1;
  width: auto;
}

.btn-secondary {
  flex: 1;
  height: 50px;
  background-color: #fff;
  color: #4169e1;
  border: 1px solid #4169e1;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
}

.btn-secondary:hover {
  background-color: #f0f5ff;
}

.btn-primary:hover {
  background-color: #3154b3;
}

/* 成功页面样式 */
.success-step {
  text-align: center;
}

.success-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #4caf50;
  color: white;
  font-size: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.success-text {
  font-size: 18px;
  color: #333;
  margin-bottom: 30px;
}
</style>
