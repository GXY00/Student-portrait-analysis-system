<template>
  <div class="dashboard-content">
    <div class="dashboard-header">
      <div class="dashboard-title">数据导入</div>
    </div>

    <!-- 导入面板 -->
    <div class="container import-panel">
      <div class="form-row">
        <div class="form-group">
          <label>请选择文件：</label>
          <div class="input-with-button">
            <input
              type="text"
              :value="fileName"
              placeholder="文件名"
              readonly
              class="filename-input"
            />
            <input
              type="file"
              ref="fileInput"
              @change="handleFileChange"
              accept=".xlsx, .xls, .csv"
              style="display: none"
            />
            <button class="btn btn-blue" @click="triggerFileSelect">
              选择文件
            </button>
          </div>
        </div>
        <div class="form-group">
          <label>文件类型：</label>
          <select v-model="fileType" class="select-input">
            <option value="student">学生信息</option>
            <option value="teacher">教师信息</option>
            <option value="score">课程成绩</option>
          </select>
        </div>
      </div>

      <div class="form-row actions">
        <button class="btn btn-blue" @click="handleImport">导入</button>
        <button class="btn btn-gray" @click="handleReset">重置</button>
        <span class="hint-text">文件仅支持 xlsx/xls/csv 格式</span>
      </div>
    </div>

    <div class="section-title-wrapper">
      <div class="dashboard-title">数据预览</div>
    </div>

    <!-- 数据预览 -->
    <div class="container preview-panel">
      <div v-if="tableData.length > 0" class="table-wrapper">
        <table class="preview-table">
          <thead>
            <tr>
              <th v-for="(header, index) in tableHeaders" :key="index">
                {{ header }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIndex) in tableData" :key="rowIndex">
              <td v-for="(header, colIndex) in tableHeaders" :key="colIndex">
                {{ row[header] }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="empty-state">
        <div class="empty-grid">
          <div class="grid-row" v-for="i in 4" :key="i">
            <div class="grid-cell" v-for="j in 4" :key="j"></div>
          </div>
        </div>
      </div>
    </div>
    <!-- 格式错误提示弹窗 -->
    <div v-if="showFormatModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>格式错误提示</h3>
          <span class="close-btn" @click="showFormatModal = false">×</span>
        </div>
        <div class="modal-body">
          <p>您上传的文件格式不正确，请确保表头包含以下字段：</p>
          <div class="format-example">
            <p v-if="fileType === 'student'">标准格式：stu_name, student_no, gender, grade, class_id, password</p>
            <p v-else-if="fileType === 'teacher'">标准格式：tea_name, teacher_no, gender, grade, class_id, password</p>
            <p v-else-if="fileType === 'score'">标准格式：stu_name, course_id, score, semester</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-main" @click="showFormatModal = false">我知道了</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import * as XLSX from 'xlsx'

export default {
  name: 'DataImport',
  data () {
    return {
      fileName: '',
      fileType: 'student', // 默认选中学生
      tableHeaders: [],
      tableData: [],
      currentFile: null,
      showFormatModal: false
    }
  },
  methods: {
    triggerFileSelect () {
      this.$refs.fileInput.click()
    },
    handleFileChange (e) {
      const files = e.target.files
      if (files.length > 0) {
        const file = files[0]
        // 验证文件格式
        const validExts = ['.xlsx', '.xls', '.csv']
        const fileExt = file.name
          .substring(file.name.lastIndexOf('.'))
          .toLowerCase()
        if (!validExts.includes(fileExt)) {
          alert('文件格式不正确，仅支持 xlsx/xls/csv')
          return
        }
        this.fileName = file.name
        this.currentFile = file
        // 自动解析预览
        this.parseFile()
      }
    },
    parseFile () {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const data = e.target.result
          const workbook = XLSX.read(data, { type: 'binary' })
          const firstSheetName = workbook.SheetNames[0]
          const worksheet = workbook.Sheets[firstSheetName]
          const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) // header:1 返回数组数组

          if (jsonData.length > 0) {
            // 校验表头
            const headers = jsonData[0]
            const studentHeaders = ['stu_name', 'student_no', 'gender', 'grade', 'class_id', 'password']
            const teacherHeaders = ['tea_name', 'teacher_no', 'gender', 'grade', 'class_id', 'password']
            const scoreHeaders = ['stu_name', 'course_id', 'score', 'semester']

            let isValid = false
            if (this.fileType === 'student') {
              isValid = studentHeaders.every(h => headers.includes(h))
            } else if (this.fileType === 'teacher') {
              isValid = teacherHeaders.every(h => headers.includes(h))
            } else if (this.fileType === 'score') {
              isValid = scoreHeaders.every(h => headers.includes(h))
            } else {
              // 其他类型暂时放行或不需要严格校验
              isValid = true
            }

            if (!isValid) {
              this.showFormatModal = true
              this.fileName = ''
              this.currentFile = null
              this.$refs.fileInput.value = '' // 清空 input
              return
            }

            this.tableHeaders = headers
            // 其余为数据
            // 将数据转换为对象数组以便展示和上传
            const rows = jsonData.slice(1)
            this.tableData = rows.map(row => {
              const obj = {}
              headers.forEach((h, i) => {
                obj[h] = row[i]
              })
              return obj
            })
          }
        } catch (e) {
          console.error('解析出错', e)
          alert('文件解析失败')
        }
      }
      reader.readAsBinaryString(this.currentFile)
    },
    handleImport () {
      if (!this.currentFile) {
        alert('请先选择文件')
        return
      }

      if (this.tableData.length === 0) {
        alert('没有可导入的数据')
        return
      }

      // 根据类型选择接口
      let apiEndpoint = '/api/v1/import/user'
      if (this.fileType === 'score') {
        apiEndpoint = '/api/v1/import/score'
      }

      // 构造请求体，包含 data 和 type
      const payload = {
        data: this.tableData,
        type: this.fileType // 'student' or 'teacher' or 'score'
      }

      fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            alert('导入成功')
            // 清空
            this.handleReset()
          } else {
            alert('导入失败: ' + data.msg)
          }
        })
        .catch(error => {
          console.error('Import error:', error)
          alert('导入失败，请检查网络')
        })
    },
    handleReset () {
      this.fileName = ''
      this.currentFile = null
      this.tableData = []
      this.tableHeaders = []
      this.$refs.fileInput.value = ''
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

.section-title-wrapper {
  margin: 20px 0;
}

.container {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.import-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.preview-panel {
  flex: 1;
  min-height: 400px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 0;
  padding: 20px;
}

/* 表单样式 */
.form-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 40px; /* "选择文件"组和"文件类型"组之间的间距 */
}

.form-group {
  display: flex;
  align-items: center;
}

.form-group label {
  margin-right: 10px;
  font-size: 14px;
  font-weight: bold;
  color: #333;
  white-space: nowrap;
}

.input-with-button {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filename-input {
  border: 1px solid #dcdfe6;
  border-radius: 20px; /* 胶囊形状近似 */
  padding: 8px 15px;
  width: 200px;
  background-color: #fff;
  color: #606266;
  outline: none;
}

.filename-input::placeholder {
  color: #c0c4cc;
}

.select-input {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 8px 30px 8px 10px;
  min-width: 160px;
  background-color: #fff;
  cursor: pointer;
  outline: none;
}

/* 按钮 */
.btn {
  padding: 8px 24px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  outline: none;
}

.btn-blue {
  background-color: #4169e1; /* Royal Blue */
  color: #fff;
}

.btn-blue:hover {
  background-color: #3154b3;
}

.btn-gray {
  background-color: #f0f2f5;
  color: #4169e1;
  font-weight: bold;
}

.btn-gray:hover {
  background-color: #e6e8eb;
}

.actions {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 10px;
}

.hint-text {
  font-size: 14px;
  color: #333;
  font-weight: bold;
  margin-left: 20px;
}

/* 空状态网格 */
.empty-state {
  flex: 1;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  min-height: 300px;
}

.empty-grid {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.grid-row {
  flex: 1;
  display: flex;
  border-bottom: 1px solid #e8e8e8;
}

.grid-row:last-child {
  border-bottom: none;
}

.grid-cell {
  flex: 1;
  border-right: 1px solid #e8e8e8;
}

.grid-cell:last-child {
  border-right: none;
}

/* 表格 */
.table-wrapper {
  overflow: auto;
  max-height: 600px;
  width: 100%;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
}

.preview-table th,
.preview-table td {
  border: 1px solid #e8e8e8;
  padding: 12px;
  text-align: left;
  white-space: nowrap;
}

.preview-table th {
  background-color: #fafafa;
  font-weight: bold;
  color: #333;
}

.preview-table tr:hover {
  background-color: #f5f7fa;
}

/* Modal Styles */
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
  background-color: #fff;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: modal-fade-in 0.3s ease;
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
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
  color: #999;
  cursor: pointer;
  line-height: 1;
}

.close-btn:hover {
  color: #666;
}

.modal-body {
  padding: 20px;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.format-example {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
  font-family: monospace;
  color: #333;
  word-break: break-all;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  text-align: right;
}

.btn-main {
  background-color: #4169e1;
  color: #fff;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  outline: none;
}

.btn-main:hover {
  background-color: #3154b3;
}

@keyframes modal-fade-in {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
