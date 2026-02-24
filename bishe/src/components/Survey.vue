<!-- eslint-disable vue/valid-v-model -->
<!-- eslint-disable vue/no-unused-vars -->
<template>
  <div class="survey-container">
    <div class="survey-header">
      <h2>问卷调查系统</h2>
      <p class="desc" v-if="view === 'list'">请选择当前学期适用的问卷进行填写。</p>
      <div v-if="view === 'form'">
        <h3>{{ currentQuestionnaire.title }}</h3>
        <p class="desc">{{ currentQuestionnaire.description }}</p>
        <p class="scale-desc">评分标准：1=非常不同意 2=不同意 3=一般 4=同意 5=非常同意</p>
        <button class="btn-back" @click="view = 'list'">返回列表</button>
      </div>
    </div>

    <!-- View: Questionnaire List -->
    <div v-if="view === 'list'" class="list-view">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="filteredQuestionnaires.length === 0" class="empty">
        暂无适合您当前年级（{{ studentInfo.grade }}）的问卷。
      </div>
      <div v-else class="questionnaire-list">
        <div v-for="q in filteredQuestionnaires" :key="q.questionnaire_id" class="questionnaire-card">
          <div class="card-header">
            <span class="q-title">{{ q.title }}</span>
            <span class="q-semester tag">{{ q.semester }}</span>
          </div>
          <div class="card-body">
            <p>{{ q.description }}</p>
            <p class="time">发布时间: {{ formatDate(q.create_time) }}</p>
          </div>
          <div class="card-footer">
            <button class="btn-start" @click="selectQuestionnaire(q)">开始填写</button>
          </div>
        </div>
      </div>
    </div>

    <!-- View: Survey Form -->
    <div v-if="view === 'form'" class="survey-form">
      <div class="section">
        <h3 class="section-title">基本信息</h3>
        <div class="form-item">
          <label>学号：</label>
          <span class="value">{{ studentNo }}</span>
        </div>
        <div class="form-item">
           <label>姓名：</label>
           <span class="value">{{ studentInfo.name }}</span>
        </div>
      </div>

      <div class="section">
        <h3 class="section-title">问卷内容</h3>
        <div class="question-item" v-for="(q, index) in parsedQuestions" :key="index">
          <p class="question-text">{{ q.id ? q.id + '.' : (index + 1) + '.' }} {{ q.question }} <span class="q-type" v-if="q.type">[{{q.type}}]</span></p>

          <!-- Render based on type, defaulting to scale 1-5 -->
          <div class="options" v-if="isScaleQuestion(q.type)">
            <label v-for="n in 5" :key="n" class="radio-label">
            <input type="radio" :name="'q_' + index" :value="n" v-model="answers[q.id || index]">
            {{ n }}
          </label>
          </div>
          <div class="options-text" v-else>
             <textarea v-model="answers[q.id || index]" rows="3" placeholder="请输入您的回答"></textarea>
          </div>
        </div>
      </div>

      <div class="actions">
        <button class="btn-submit" @click="submitSurvey" :disabled="submitting">
          {{ submitting ? '提交中...' : '提交问卷' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Survey',
  data () {
    return {
      view: 'list', // 'list' or 'form'
      studentNo: '',
      studentInfo: {},
      questionnaires: [],
      currentQuestionnaire: null,
      parsedQuestions: [],
      answers: {},
      submitting: false,
      loading: false
    }
  },
  computed: {
    filteredQuestionnaires () {
      if (!this.studentInfo.grade) return []
      // Filter questionnaires where semester contains the student's grade
      // e.g. studentGrade="高二", semester="2024-2025-1(高二上)" -> Match
      return this.questionnaires.filter(q => {
        return q.semester && q.semester.includes(this.studentInfo.grade)
      })
    }
  },
  mounted () {
    this.studentNo = localStorage.getItem('username') || ''
    if (this.studentNo) {
      this.fetchStudentInfo()
    } else {
      alert('未登录，请先登录')
      this.$router.push('/login')
    }
  },
  methods: {
    formatDate (dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleString()
    },
    isScaleQuestion (type) {
      // Default to true if type is empty or explicitly scale-like
      if (!type) return true
      const scaleTypes = ['量表题', '单选题', '评分题']
      return scaleTypes.some(t => type.includes(t))
    },
    fetchStudentInfo () {
      this.loading = true
      fetch('/api/v1/user/detail', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: this.studentNo })
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            this.studentInfo = data.data
            this.fetchQuestionnaires()
          } else {
            alert('获取用户信息失败: ' + data.msg)
          }
        })
        .catch(err => {
          console.error(err)
          alert('无法获取用户信息')
        })
    },
    fetchQuestionnaires () {
      fetch('/api/v1/questionnaire/list')
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            this.questionnaires = data.data
          } else {
            alert('获取问卷列表失败: ' + data.msg)
          }
        })
        .catch(err => console.error(err))
        .finally(() => {
          this.loading = false
        })
    },
    selectQuestionnaire (q) {
      this.currentQuestionnaire = q
      try {
        // Parse content_structure
        let content = q.content_structure
        if (typeof content === 'string') {
          content = JSON.parse(content)
        }

        // Normalize content to array of objects
        // If it's array of strings (from Word), convert to objects
        if (Array.isArray(content)) {
          if (content.length > 0 && typeof content[0] === 'string') {
            this.parsedQuestions = content.map((text, idx) => ({
              id: `Q${idx + 1}`,
              question: text,
              type: '量表题' // Default for unstructured text
            }))
          } else {
            this.parsedQuestions = content
          }
        } else {
          this.parsedQuestions = []
        }

        // Initialize answers
        this.answers = {}
        this.parsedQuestions.forEach((q, idx) => {
          const key = q.id || idx
          this.$set(this.answers, key, null)
        })

        this.view = 'form'
      } catch (e) {
        console.error('Parse error:', e)
        alert('问卷内容解析失败')
      }
    },
    validate () {
      for (let i = 0; i < this.parsedQuestions.length; i++) {
        const q = this.parsedQuestions[i]
        const key = q.id || i
        if (this.answers[key] === null || this.answers[key] === '' || this.answers[key] === undefined) {
          alert(`请回答第 ${i + 1} 题`)
          return false
        }
      }
      return true
    },
    submitSurvey () {
      if (!this.validate()) return

      this.submitting = true

      const payload = {
        student_no: this.studentNo,
        answers: this.answers,
        semester: this.currentQuestionnaire.semester,
        questionnaire_id: this.currentQuestionnaire.questionnaire_id
      }

      fetch('/api/v1/survey/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            alert('问卷提交成功！')
            this.view = 'list'
            this.currentQuestionnaire = null
          } else {
            alert('提交失败: ' + data.msg)
          }
        })
        .catch(err => {
          alert('网络错误: ' + err)
        })
        .finally(() => {
          this.submitting = false
        })
    }
  }
}
</script>

<style scoped>
.survey-container {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  /* min-height: 80vh; */
  height: auto;
  overflow: visible;
}

.survey-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
  position: relative;
}

.survey-header h2 {
  color: #333;
  margin-bottom: 15px;
}

.desc {
  color: #666;
  font-size: 14px;
  margin-bottom: 10px;
}

.scale-desc {
  color: #e67e22;
  font-weight: bold;
}

.btn-back {
  position: absolute;
  left: 0;
  top: 0;
  padding: 5px 15px;
  background: #f4f4f5;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
}

/* List View Styles */
.questionnaire-list {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}

.questionnaire-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s;
  background: #fff;
}

.questionnaire-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.q-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.tag {
  background: #ecf5ff;
  color: #409eff;
  border: 1px solid #d9ecff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.card-body {
  color: #606266;
  font-size: 14px;
  margin-bottom: 20px;
  min-height: 60px;
}

.time {
  font-size: 12px;
  color: #909399;
  margin-top: 10px;
}

.card-footer {
  text-align: right;
}

.btn-start {
  background: #409eff;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-start:hover {
  background: #66b1ff;
}

.empty {
  text-align: center;
  padding: 40px;
  color: #909399;
}

/* Form View Styles */
.section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 18px;
  color: #409eff;
  margin-bottom: 20px;
  padding-left: 10px;
  border-left: 4px solid #409eff;
}

.question-item {
  margin-bottom: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.question-text {
  font-weight: 500;
  margin-bottom: 15px;
  font-size: 16px;
  line-height: 1.5;
}

.q-type {
  font-size: 12px;
  color: #909399;
  margin-left: 5px;
  font-weight: normal;
}

.options {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.radio-label {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 4px;
  background: #fff;
  border: 1px solid #dcdfe6;
}

.radio-label:hover {
  border-color: #409eff;
}

.options-text textarea {
  width: 100%;
  padding: 2px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  resize: vertical;
}

.form-item {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.form-item label {
  width: 80px;
  font-weight: bold;
}

.actions {
  text-align: center;
  margin-top: 40px;
  margin-bottom: 20px;
}

.btn-submit {
  padding: 12px 50px;
  background-color: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-submit:hover {
  background-color: #85ce61;
}

.btn-submit:disabled {
  background-color: #c2e7b0;
  cursor: not-allowed;
}
</style>
