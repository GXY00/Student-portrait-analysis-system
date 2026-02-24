<template>
  <div class="login-container">
    <div class="login-box">
      <h2 class="title">学生画像分析系统</h2>
      <div class="input-group">
        <div class="icon-wrapper">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="white">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
          </svg>
        </div>
        <input type="text" v-model="username" placeholder="请输入账号" />
      </div>

      <div class="input-group">
        <div class="icon-wrapper">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="white">
            <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3 3.1-3 1.71 0 3.1 1.29 3.1 3v2z"/>
          </svg>
        </div>
        <input type="password" v-model="password" placeholder="请输入密码" />
      </div>

      <div class="options">
        <label class="remember-me">
          <input type="checkbox" v-model="rememberMe" />
          <span>记住密码</span>
        </label>
      </div>

      <button class="login-btn" @click="handleLogin">登录</button>

      <div class="footer-links">
        <a href="#" @click.prevent="forgotPassword">忘记密码</a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data () {
    return {
      username: '',
      password: '',
      rememberMe: false
    }
  },
  mounted () {
    this.checkRemembered()
  },
  // 监听 rememberMe 变化
  watch: {
    rememberMe (val) {
      if (!val) {
        // 只有当缓存中的用户名与当前输入的用户名一致时，才清除缓存
        const remembered = localStorage.getItem('login_remembered')
        if (remembered) {
          try {
            const data = JSON.parse(remembered)
            if (this.username && data.username === this.username) {
              localStorage.removeItem('login_remembered')
            }
          } catch (e) {
            // ignore
          }
        }
      } else {
        this.saveRemembered()
      }
    },
    username () {
      if (this.rememberMe) {
        this.saveRemembered()
      }
    },
    password () {
      if (this.rememberMe) {
        this.saveRemembered()
      }
    }
  },
  methods: {
    saveRemembered () {
      if (this.username) {
        localStorage.setItem('login_remembered', JSON.stringify({
          username: this.username,
          password: this.password
        }))
      }
    },
    checkRemembered () {
      const remembered = localStorage.getItem('login_remembered')
      if (remembered) {
        try {
          const data = JSON.parse(remembered)
          this.username = data.username
          this.password = data.password
          this.rememberMe = true
        } catch (e) {
          localStorage.removeItem('login_remembered')
        }
      }
    },
    handleLogin () {
      if (!this.username || !this.password) {
        alert('请输入账号和密码')
        return
      }

      // 验证用户名格式
      if (!this.username.startsWith('Stu') && !this.username.startsWith('Tea') && !this.username.startsWith('Admin')) {
        alert('用户名格式错误，必须以 Stu, Tea 或 Admin 开头')
        return
      }

      console.log('Logging in with:', this.username, this.password)
      // 登录请求
      var myHeaders = new Headers()
      myHeaders.append('Content-Type', 'application/json')

      var raw = JSON.stringify({
        'username': this.username,
        'password': this.password
      })

      var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
      }

      // 发送登录请求
      fetch('/api/v1/user/login', requestOptions)
        .then(response => {
          if (response.ok) {
            return response.json()
          }
          throw new Error('登录失败，请检查网络或账号密码')
        })
        .then(result => {
          console.log(result)
          // 保存用户角色到 localStorage
          localStorage.setItem('userRole', result.role)
          localStorage.setItem('username', this.username)
          // alert('登录成功: ' + result.msg)
          this.$router.push('/home')
        })
        .catch(error => {
          console.log('error', error)
          alert('登录失败，请检查网络或账号密码')
        })
    },
    forgotPassword () {
      // 跳转到忘记密码页面
      console.log('Navigating to Forgot Password page')
      this.$router.push('/forgot-password')
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #2c3e50; /* 备用背景色 */
  background-image: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3)), url('https://images.unsplash.com/photo-1497366216548-37526070297c?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80');
  background-size: cover;
  background-position: center;
}

.login-box {
  background: white;
  padding: 40px;
  border-radius: 4px;
  width: 400px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.title {
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.input-group {
  display: flex;
  margin-bottom: 20px;
  background-color: #f0f0f0;
  border-radius: 2px;
}

.icon-wrapper {
  width: 50px;
  background-color: #dcdcdc;
  display: flex;
  justify-content: center;
  align-items: center;
  border-top-left-radius: 2px;
  border-bottom-left-radius: 2px;
}

.input-group input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 15px;
  outline: none;
  font-size: 14px;
  color: #666;
}

.role-group {
  margin-bottom: 20px;
  text-align: left;
}

.role-label {
  display: block;
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
}

.radio-group {
  display: flex;
  justify-content: space-between;
}

.radio-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #333;
  font-size: 14px;
}

.radio-item input {
  margin-right: 5px;
}

.options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.remember-me {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #333;
}

.remember-me input {
  margin-right: 8px;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background-color: #4169e1; /* 皇家蓝 */
  color: white;
  border: none;
  border-radius: 2px;
  font-size: 16px;
  cursor: pointer;
  margin-bottom: 20px;
  transition: background-color 0.3s;
}

.login-btn:hover {
  background-color: #3154b3;
}

.footer-links {
  margin-top: 10px;
}

.footer-links a {
  color: #4169e1;
  text-decoration: none;
  font-size: 14px;
}

.footer-links a:hover {
  text-decoration: underline;
}
</style>
