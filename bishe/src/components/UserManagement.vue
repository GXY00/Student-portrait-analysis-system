<template>
  <div class="dashboard-content">
    <div class="dashboard-header">
      <div class="dashboard-title">用户管理</div>
    </div>
    <!-- 筛选区域 -->
    <div class="filter-container">
      <div class="filter-row">
        <div class="filter-item">
          <label>精确查找</label>
          <div class="search-input-wrapper">
            <input
              v-model="filters.keyword"
              type="text"
              placeholder="用户名称"
              class="filter-input"
            >
            <i class="search-icon"><svg t="1769999134387" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4789" width="12" height="12"><path d="M959.266 879.165c0 81.582-81.582 81.582-81.582 81.582l-233.38-233.381c-60.529 43.977-134.777 70.217-215.318 70.217-202.755 0-367.117-164.362-367.117-367.117S226.23 63.349 428.985 63.349s367.117 164.362 367.117 367.117c0 80.541-26.241 154.785-70.217 215.318l233.381 233.381zM428.985 144.931c-157.697 0-285.536 127.838-285.536 285.536s127.838 285.536 285.536 285.536 285.536-127.838 285.536-285.536-127.839-285.536-285.536-285.536z" fill="#cdcdcd" p-id="4790"></path></svg></i>
          </div>
        </div>

        <div class="filter-item">
          <label>角色</label>
          <select v-model="filters.role" class="filter-select">
            <option value="">全部</option>
            <option value="student">学生</option>
            <option value="teacher">教师</option>
          </select>
        </div>

        <div class="filter-item">
          <label>性别</label>
          <select v-model="filters.gender" class="filter-select">
            <option value="">全部</option>
            <option value="male">男</option>
            <option value="female">女</option>
          </select>
        </div>

        <div class="filter-item">
          <label>年级</label>
          <select v-model="filters.grade" class="filter-select">
            <option value="">全部</option>
            <option v-for="grade in gradeOptions" :key="grade" :value="grade">{{ grade }}</option>
          </select>
        </div>

        <div class="filter-item">
          <label>班级</label>
          <select v-model="filters.class" class="filter-select">
            <option value="">全部</option>
            <option v-for="n in 10" :key="'高一'+n" :value="`高一${n}班`">高一{{ n }}班</option>
            <option v-for="n in 10" :key="'高二'+n" :value="`高二${n}班`">高二{{ n }}班</option>
            <option v-for="n in 10" :key="'高三'+n" :value="`高三${n}班`">高三{{ n }}班</option>
          </select>
        </div>
      </div>

      <div class="action-row">
        <button class="btn btn-blue" @click="handleSearch">查询</button>
        <button class="btn btn-gray" @click="handleReset">重置</button>
      </div>
    </div>

    <!-- 表格区域 -->
    <div class="table-container">
      <table class="user-table">
        <thead>
          <tr>
            <th>学号/工号</th>
            <th>姓名</th>
            <th>性别</th>
            <th>年龄</th>
            <th>年级</th>
            <th>班级</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in displayedUsers" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.name }}</td>
            <td>{{ user.gender }}</td>
            <td>{{ user.age }}</td>
            <td>{{ user.grade }}</td>
            <td>{{ user.class }}</td>
            <td>
              <a href="#" class="action-link" @click.prevent="viewDetails(user)">查看详情</a>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <div class="total-info">共 {{ totalItems }} 条</div>
        <div class="pagination-controls">
          <button
            :disabled="currentPage === 1"
            @click="changePage(currentPage - 1)"
            class="page-btn"
          >
            &lt;
          </button>

          <button
            v-for="page in totalPages"
            :key="page"
            :class="['page-btn', { active: currentPage === page }]"
            @click="changePage(page)"
          >
            {{ page }}
          </button>

          <button
            :disabled="currentPage === totalPages"
            @click="changePage(currentPage + 1)"
            class="page-btn"
          >
            &gt;
          </button>
        </div>
        <div class="jump-to">
          前往
          <input
            type="number"
            v-model.number="jumpPage"
            @keyup.enter="handleJump"
            min="1"
            :max="totalPages"
            class="jump-input"
          >
          页
        </div>
      </div>
    </div>

    <!-- 详情/编辑弹窗 -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>用户详情</h3>
          <span class="close-btn" @click="closeModal">×</span>
        </div>
        <div class="modal-body">
          <!-- 学号/工号 -->
          <div class="form-item">
            <label>学号/工号</label>
            <div class="input-group">
              <span v-if="!editModes.id" class="value-text">{{ tempUser.id }}</span>
              <input v-else v-model="editValues.id" class="modal-input" placeholder="请输入学号/工号">
              <button class="link-btn" @click="toggleEdit('id')">
                {{ editModes.id ? '取消修改' : '修改' }}
              </button>
            </div>
          </div>

          <!-- 姓名 -->
          <div class="form-item">
            <label>姓名</label>
            <div class="input-group">
              <span v-if="!editModes.name" class="value-text">{{ tempUser.name }}</span>
              <input v-else v-model="editValues.name" class="modal-input" placeholder="请输入姓名">
              <button class="link-btn" @click="toggleEdit('name')">
                {{ editModes.name ? '确认修改' : '修改' }}
              </button>
            </div>
          </div>

          <!-- 性别（下拉框） -->
          <div class="form-item">
            <label>性别</label>
            <select v-model="tempUser.gender" class="modal-select">
              <option value="男">男</option>
              <option value="女">女</option>
            </select>
          </div>

          <!-- 年龄 -->
          <div class="form-item">
            <label>年龄</label>
            <div class="input-group">
              <span v-if="!editModes.age" class="value-text">{{ tempUser.age }}</span>
              <input v-else v-model="editValues.age" type="number" class="modal-input" placeholder="请输入年龄">
              <button class="link-btn" @click="toggleEdit('age')">
                {{ editModes.age ? '确认修改' : '修改' }}
              </button>
            </div>
          </div>

          <!-- 角色（文字显示） -->
          <div class="form-item">
            <label>角色</label>
            <div class="input-group">
              <span class="value-text">{{ tempUser.role }}</span>
            </div>
          </div>

          <!-- 年级（下拉框） -->
          <div class="form-item">
            <label>年级</label>
            <select v-model="tempUser.grade" class="modal-select">
              <option v-for="g in gradeOptions" :key="g" :value="g">{{ g }}</option>
            </select>
          </div>

          <!-- 班级（下拉框） -->
          <div class="form-item">
            <label>班级</label>
            <select v-model="tempUser.class" class="modal-select">
              <option v-for="n in 10" :key="n" :value="`${n}班`">{{ n }}班</option>
            </select>
          </div>

          <!-- 密码（可编辑逻辑） -->
          <div class="form-item">
            <label>密码</label>
            <div class="input-group">
              <span v-if="!editModes.password" class="value-text">
                {{ showPassword ? tempUser.password : '*************' }}
              </span>
              <input v-else v-model="editValues.password" type="text" class="modal-input" placeholder="请输入新密码">

              <button v-if="!editModes.password" class="icon-btn" @click="showPassword = !showPassword" title="显示/隐藏">
                <svg t="1770001901569" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="6180" width="30" height="30"><path d="M512 298.666667c-162.133333 0-285.866667 68.266667-375.466667 213.333333 89.6 145.066667 213.333333 213.333333 375.466667 213.333333s285.866667-68.266667 375.466667-213.333333c-89.6-145.066667-213.333333-213.333333-375.466667-213.333333z m0 469.333333c-183.466667 0-328.533333-85.333333-426.666667-256 98.133333-170.666667 243.2-256 426.666667-256s328.533333 85.333333 426.666667 256c-98.133333 170.666667-243.2 256-426.666667 256z m0-170.666667c46.933333 0 85.333333-38.4 85.333333-85.333333s-38.4-85.333333-85.333333-85.333333-85.333333 38.4-85.333333 85.333333 38.4 85.333333 85.333333 85.333333z m0 42.666667c-72.533333 0-128-55.466667-128-128s55.466667-128 128-128 128 55.466667 128 128-55.466667 128-128 128z" fill="#8a8a8a" p-id="6181"></path></svg>
              </button>

              <button class="link-btn" @click="toggleEdit('password')">
                {{ editModes.password ? '取消修改' : '修改' }}
              </button>
            </div>
          </div>

        </div>
        <div class="modal-footer">
          <button
            class="btn-main"
            :class="{ 'btn-red': confirmStep === 1 }"
            @click="handleMainConfirm"
          >
            {{ confirmStep === 0 ? '确定' : '确认修改' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 内部确认弹窗（模拟个人信息管理逻辑） -->
    <div v-if="showInnerConfirm" class="inner-modal-overlay">
      <div class="inner-modal">
        <h3>确认修改</h3>
        <p>您确定要修改{{ currentEditLabel }}吗？</p>
        <div class="inner-modal-actions">
          <button class="btn-cancel" @click="cancelInnerEdit">取消</button>
          <button class="btn-confirm" @click="confirmInnerEdit">确认</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'UserManagement',
  data () {
    return {
      filters: {
        keyword: '',
        role: '',
        gender: '',
        grade: '',
        class: ''
      },
      gradeOptions: ['高一', '高二', '高三'],
      allUsers: [],
      currentPage: 1,
      pageSize: 15,
      jumpPage: 1,

      // 弹窗状态
      showModal: false,
      tempUser: {},
      editModes: {
        id: false,
        name: false,
        age: false,
        password: false
      },
      editValues: {
        id: '',
        name: '',
        age: '',
        password: ''
      },
      confirmStep: 0,
      showPassword: false,

      // 内部确认状态
      showInnerConfirm: false,
      pendingEditField: '',
      currentEditLabel: ''
    }
  },
  computed: {
    filteredUsers () {
      return this.allUsers.filter(user => {
        const matchKeyword = !this.filters.keyword || user.name.includes(this.filters.keyword) || user.id.includes(this.filters.keyword)
        const matchRole = !this.filters.role || user.role === this.filters.role
        const matchGender = !this.filters.gender || user.gender === (this.filters.gender === 'male' ? '男' : '女')
        const matchGrade = !this.filters.grade || user.grade === this.filters.grade
        const matchClass = !this.filters.class || user.class === this.filters.class

        return matchKeyword && matchRole && matchGender && matchGrade && matchClass
      })
    },
    totalItems () {
      return this.filteredUsers.length
    },
    totalPages () {
      return Math.ceil(this.totalItems / this.pageSize) || 1
    },
    displayedUsers () {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.filteredUsers.slice(start, end)
    }
  },
  created () {
    this.fetchUsers()
  },
  methods: {
    fetchUsers () {
      fetch('/api/v1/user/list')
        .then(response => {
          if (response.ok) {
            return response.json()
          }
          throw new Error('获取用户列表失败')
        })
        .then(data => {
          if (data.success) {
            this.allUsers = data.data
          } else {
            console.error(data.msg)
          }
        })
        .catch(error => {
          console.error('Error fetching users:', error)
          alert('获取用户列表失败，请检查网络')
        })
    },
    handleSearch () {
      this.currentPage = 1
    },
    handleReset () {
      this.filters = {
        keyword: '',
        role: '',
        gender: '',
        grade: '',
        class: ''
      }
      this.currentPage = 1
    },
    changePage (page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
      }
    },
    handleJump () {
      if (this.jumpPage >= 1 && this.jumpPage <= this.totalPages) {
        this.currentPage = this.jumpPage
      } else {
        this.jumpPage = this.currentPage
      }
    },
    viewDetails (user) {
      this.tempUser = JSON.parse(JSON.stringify(user))

      // 根据学号/工号前缀判断角色
      if (this.tempUser.id) {
        if (String(this.tempUser.id).startsWith('Tea')) {
          this.tempUser.role = '教师'
        } else if (String(this.tempUser.id).startsWith('Stu')) {
          this.tempUser.role = '学生'
        }

        // 获取用户详细信息（主要是密码）
        this.fetchUserDetail(this.tempUser.id)
      }

      // 处理班级名称，去掉年级前缀以匹配下拉框选项
      if (this.tempUser.class && this.tempUser.grade) {
        this.tempUser.class = this.tempUser.class.replace(this.tempUser.grade, '')
      }

      // 重置编辑状态
      this.editModes = { id: false, name: false, age: false, password: false }
      this.editValues = { id: '', name: '', age: '', password: '' }
      this.confirmStep = 0
      this.showPassword = false
      this.showModal = true
    },
    fetchUserDetail (username) {
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
            // 更新密码和可能的其他信息
            if (data.data.password) {
              this.tempUser.password = data.data.password
            }
            // 可以在这里同步更新其他字段以确保数据最新
          }
        })
        .catch(error => console.error('Error fetching user detail:', error))
    },
    closeModal () {
      this.showModal = false
      this.showInnerConfirm = false
    },
    toggleEdit (field) {
      if (!this.editModes[field]) {
        // 开始编辑
        this.editModes[field] = true
        this.editValues[field] = field === 'password' ? '' : this.tempUser[field]
      } else {
        // 取消编辑，回复原状
        this.editModes[field] = false
        this.editValues[field] = ''
      }
    },
    getFieldLabel (field) {
      const map = {
        id: '学号/工号',
        name: '姓名',
        age: '年龄',
        password: '密码'
      }
      return map[field] || field
    },
    confirmInnerEdit () {
      const field = this.pendingEditField
      this.tempUser[field] = this.editValues[field]
      this.editModes[field] = false
      this.showInnerConfirm = false
      // 根据指示不保存到后端
    },
    cancelInnerEdit () {
      this.showInnerConfirm = false
      // 保持编辑模式开启
    },
    handleMainConfirm () {
      if (this.confirmStep === 0) {
        this.confirmStep = 1
      } else {
        // 收集更新的数据
        const updateData = {
          id: this.tempUser.id, // 原始ID用于查找
          new_id: this.editModes.id ? this.editValues.id : undefined, // 如果修改了ID，传新ID
          role: this.tempUser.role,
          // 如果字段在编辑模式，使用编辑后的值，否则使用原值（或不传）
          // 注意：如果修改了学号/工号(ID)，这里需要特殊处理，但目前假设只传原始ID作为Key
          // 如果允许修改ID，后端需要支持 old_id 和 new_id，或者只允许改其他信息

          name: this.editModes.name ? this.editValues.name : this.tempUser.name,
          age: this.editModes.age ? this.editValues.age : this.tempUser.age,
          password: this.editModes.password ? this.editValues.password : undefined, // 密码只在修改时传

          // 下拉框直接绑定到 tempUser，所以直接取
          gender: this.tempUser.gender,
          grade: this.tempUser.grade,
          class: this.tempUser.class
        }

        // 发送更新请求
        fetch('/api/v1/user/update_info', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(updateData)
        })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              alert('更新成功')
              this.closeModal()
              // 刷新列表
              this.fetchUsers()
            } else {
              alert('更新失败: ' + data.msg)
            }
          })
          .catch(error => {
            console.error('Error updating user:', error)
            alert('更新失败，请检查网络')
          })
      }
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
  margin-bottom: 20px;
}

.dashboard-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

/* 筛选区域 */
.filter-container {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.filter-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
}

.filter-item {
  display: flex;
  align-items: center;
}

.filter-item label {
  font-weight: bold;
  margin-right: 10px;
  color: #333;
  white-space: nowrap;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-input {
  border: 1px solid #dcdfe6;
  border-radius: 20px;
  padding: 6px 30px 6px 15px;
  width: 200px;
  outline: none;
  color: #606266;
}

.search-icon {
  position: absolute;
  right: 10px;
  font-style: normal;
  color: #4169e1;
  cursor: pointer;
}

.filter-select {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 6px 10px;
  width: 120px;
  outline: none;
  background-color: #fff;
  color: #606266;
}

.action-row {
  display: flex;
  gap: 15px;
}

.btn {
  padding: 6px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-blue {
  background-color: #4169e1;
  color: #fff;
}

.btn-blue:hover {
  background-color: #3154b3;
}

.btn-gray {
  background-color: #f0f2f5;
  color: #606266;
}

.btn-gray:hover {
  background-color: #e6e8eb;
}

/* 表格区域 */
.table-container {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  flex: 1;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.user-table th, .user-table td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.user-table th {
  color: #909399;
  font-weight: normal;
}

.user-table td {
  color: #606266;
}

.action-link {
  color: #4169e1;
  text-decoration: none;
  cursor: pointer;
}

.action-link:hover {
  text-decoration: underline;
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: auto;
  gap: 15px;
  color: #606266;
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  gap: 5px;
}

.page-btn {
  border: 1px solid #dcdfe6;
  background-color: #fff;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  min-width: 30px;
}

.page-btn:hover:not(:disabled) {
  color: #4169e1;
  border-color: #4169e1;
}

.page-btn.active {
  background-color: #4169e1;
  color: #fff;
  border-color: #4169e1;
}

.page-btn:disabled {
  color: #c0c4cc;
  cursor: not-allowed;
  background-color: #f4f4f5;
}

.jump-to {
  display: flex;
  align-items: center;
  gap: 5px;
}

.jump-input {
  width: 40px;
  padding: 5px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  text-align: center;
  outline: none;
}

.jump-input:focus {
  border-color: #4169e1;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background-color: #fff;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  font-size: 24px;
  color: #909399;
  cursor: pointer;
  line-height: 1;
}

.modal-body {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.form-item {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.form-item label {
  width: 100px;
  font-weight: bold;
  color: #333;
}

.input-group {
  flex: 1;
  display: flex;
  align-items: center;
}

.value-text {
  margin-right: 10px;
  color: #606266;
  flex: 1;
}

.modal-input {
  flex: 1;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 8px;
  outline: none;
  margin-right: 10px;
}

.modal-select {
  flex: 1;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 8px;
  outline: none;
  background-color: #fff;
}

.link-btn {
  background: none;
  border: none;
  color: #4169e1;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
}

.link-btn:hover {
  text-decoration: underline;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  margin-right: 10px;
  font-size: 16px;
  padding: 0;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: center;
}

.btn-main {
  background-color: #4169e1;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 10px 40px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-main:hover {
  background-color: #3154b3;
}

.btn-red {
  background-color: #f56c6c !important;
  color: #fff !important;
}

.btn-red:hover {
  background-color: #e64242 !important;
}

/* 内部确认弹窗 */
.inner-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.3);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2100;
}

.inner-modal {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  width: 300px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.inner-modal h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
}

.inner-modal p {
  color: #606266;
  margin-bottom: 20px;
}

.inner-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-cancel {
  background-color: #fff;
  border: 1px solid #dcdfe6;
  color: #606266;
  padding: 6px 15px;
  border-radius: 3px;
  cursor: pointer;
}

.btn-confirm {
  background-color: #4169e1;
  border: none;
  color: #fff;
  padding: 6px 15px;
  border-radius: 3px;
  cursor: pointer;
}
</style>
