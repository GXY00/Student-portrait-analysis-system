<template>
  <div class="dashboard-content">
    <div class="dashboard-header">
      <div class="dashboard-title">问卷配置管理</div>
    </div>

    <!-- 操作区域 -->
    <div class="filter-container">
      <div class="action-row left">
        <button class="btn btn-blue" @click="handleAdd">新增问卷</button>
        <button class="btn btn-red" @click="handleDeleteBatch">删除问卷</button>
      </div>
    </div>

    <!-- 表格区域 -->
    <div class="table-container">
      <table class="user-table">
        <thead>
          <tr>
            <th class="checkbox-col">
              <input type="checkbox" v-model="selectAll" @change="toggleSelectAll">
            </th>
            <th>问卷标题</th>
            <th>描述</th>
            <th @click="sortByDate" class="sortable">创建时间
              <span v-if="sortOrder === 'asc'">▲</span>
              <span v-else>▼</span>
            </th>
            <th>学期</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in questionnaires" :key="item.questionnaire_id">
            <td class="checkbox-col">
              <input type="checkbox" v-model="selectedIds" :value="item.questionnaire_id">
            </td>
            <td>{{ item.title }}</td>
            <td class="desc-col" :title="item.description">{{ item.description }}</td>
            <td>{{ item.create_time }}</td>
            <td>{{ item.semester }}</td>
            <td>
              <a href="#" class="action-link" @click.prevent="viewDetails(item)">查看详情</a>
              <a href="#" class="action-link" @click.prevent="handleEdit(item)">编辑</a>
            </td>
          </tr>
          <tr v-if="questionnaires.length === 0">
            <td colspan="7" class="empty-text">暂无问卷数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新增/编辑弹窗 -->
    <div class="modal-mask" v-if="showModal">
      <div class="modal-wrapper">
        <div class="modal-container">
          <div class="modal-header">
            <h3>{{ isEdit ? '编辑问卷' : '新增问卷' }}</h3>
            <span class="close-btn" @click="closeModal">&times;</span>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>问卷名称:</label>
              <input type="text" v-model="modalForm.title" placeholder="请输入问卷名称">
              <p class="error-text" v-if="titleError">{{ titleError }}</p>
            </div>
            <div class="form-group">
              <label>问卷说明:</label>
              <textarea v-model="modalForm.description" placeholder="请输入问卷说明" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label>学期:</label>
              <select v-model="modalForm.semester">
                <option value="">请选择学期</option>
                <option v-for="s in semesters" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>上传问卷:</label>
              <input type="file" ref="fileInput" @change="handleFileChange" accept=".xlsx, .xls, .docx">
              <p class="tip" v-if="isEdit">再次上传将覆盖原问卷内容</p>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-default" @click="closeModal">取消</button>
            <button class="btn btn-blue" @click="handleSave">确定</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div class="modal-mask" v-if="showDetailModal">
      <div class="modal-wrapper">
        <div class="modal-container detail-modal">
          <div class="modal-header">
            <h3>问卷详情 - {{ currentDetail.title }}</h3>
            <span class="close-btn" @click="closeDetailModal">&times;</span>
          </div>
          <div class="modal-body detail-body">
            <div v-if="currentDetail.content_structure && currentDetail.content_structure.length > 0">

              <!-- 1. Structured Data (New Excel Parse) -->
              <div v-if="isStructured(currentDetail.content_structure)" class="survey-paper">
                 <div class="paper-header">
                    <h2 class="paper-title">{{ currentDetail.title }}</h2>
                    <p class="paper-desc">{{ currentDetail.description }}</p>
                    <p class="paper-info">学期: {{ currentDetail.semester }}</p>
                 </div>

                 <div class="paper-content">
                    <div v-for="(q, index) in currentDetail.content_structure" :key="index" class="q-item">
                        <div class="q-row">
                           <span class="q-id" v-if="q.id">{{ q.id }}</span>
                           <span class="q-text">{{ q.question }}</span>
                           <span class="q-type-label" v-if="false">[{{q.type}}]</span>
                        </div>

                        <!-- Single Choice (Likert 1-5) -->
                        <div class="q-body" v-if="isSingleChoice(q.type)">
                           <div class="scale-group">
                              <span v-for="n in 5" :key="n" class="scale-opt">
                                 <span class="checkbox-mock">□</span> {{ n }}
                              </span>
                           </div>
                        </div>

                        <!-- Fill in blank -->
                        <div class="q-body" v-else-if="isFillBlank(q.type)">
                           <div class="blank-line-wrapper">
                              {{ q.question.split(/[:：]/)[1] || '' }} __________________________
                           </div>
                        </div>

                        <div class="q-body" v-else>
                           <span class="unknown-type">[{{ q.type }}]</span>
                        </div>
                    </div>
                 </div>
              </div>

              <!-- 2. Old Excel Format (List of Lists) -->
              <div v-else-if="Array.isArray(currentDetail.content_structure[0])">
                <table class="detail-table">
                  <tbody>
                    <tr v-for="(row, rIndex) in currentDetail.content_structure" :key="rIndex">
                      <td v-for="(cell, cIndex) in row" :key="cIndex">{{ cell }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- 3. Word Format (List of Strings) -->
              <div v-else>
                <div v-for="(line, index) in currentDetail.content_structure" :key="index" class="doc-line">
                  {{ line }}
                </div>
              </div>
            </div>
            <div v-else class="empty-text">暂无内容结构</div>
          </div>
          <div class="modal-footer">
             <button class="btn btn-blue" @click="closeDetailModal">关闭</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'QuestionnaireConfig',
  data () {
    return {
      questionnaires: [],
      selectedIds: [],
      selectAll: false,

      // Modal state
      showModal: false,
      isEdit: false,
      titleError: '',
      modalForm: {
        id: null,
        title: '',
        description: '',
        semester: '',
        file: null
      },
      semesters: ['高一上', '高一下', '高二上', '高二下', '高三上', '高三下'],

      // Detail Modal state
      showDetailModal: false,
      currentDetail: {},

      sortOrder: 'desc' // 'asc' or 'desc'
    }
  },
  watch: {
    selectedIds: {
      handler (val) {
        if (val.length === this.questionnaires.length && this.questionnaires.length > 0) {
          this.selectAll = true
        } else {
          this.selectAll = false
        }
      },
      deep: true
    }
  },
  mounted () {
    this.fetchQuestionnaires()
  },
  methods: {
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
        .catch(err => {
          console.error('Fetch error:', err)
          alert('网络错误，无法获取问卷列表')
        })
    },
    toggleSelectAll () {
      if (this.selectAll) {
        this.selectedIds = this.questionnaires.map(q => q.questionnaire_id)
      } else {
        this.selectedIds = []
      }
    },

    // Add/Edit Logic
    handleAdd () {
      this.isEdit = false
      this.modalForm = {
        id: null,
        title: '',
        description: '',
        semester: '',
        file: null
      }
      // Reset file input if exists
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
      this.showModal = true
    },
    handleEdit (item) {
      this.isEdit = true
      this.modalForm = {
        id: item.questionnaire_id,
        title: item.title,
        description: item.description,
        semester: item.semester,
        file: null
      }
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
      this.showModal = true
    },
    handleFileChange (e) {
      this.modalForm.file = e.target.files[0]
    },
    closeModal () {
      this.showModal = false
    },
    handleSave () {
      if (!this.modalForm.title || !this.modalForm.semester) {
        alert('请填写问卷名称和学期')
        return
      }
      if (!this.isEdit && !this.modalForm.file) {
        alert('请上传问卷文件')
        return
      }

      const formData = new FormData()
      formData.append('title', this.modalForm.title)
      formData.append('description', this.modalForm.description || '')
      formData.append('semester', this.modalForm.semester)
      if (this.modalForm.file) {
        formData.append('file', this.modalForm.file)
      }
      if (this.isEdit) {
        formData.append('questionnaire_id', this.modalForm.id)
      }

      fetch('/api/v1/questionnaire/save', {
        method: 'POST',
        body: formData
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            alert('保存成功')
            this.closeModal()
            this.fetchQuestionnaires()
          } else {
            alert('保存失败: ' + data.msg)
          }
        })
        .catch(err => {
          console.error('Save error:', err)
          alert('保存失败: 网络错误')
        })
    },

    // Delete Logic
    handleDeleteBatch () {
      if (this.selectedIds.length === 0) {
        alert('请先选择要删除的问卷')
        return
      }

      if (!confirm(`确定要删除选中的 ${this.selectedIds.length} 个问卷吗？`)) {
        return
      }

      fetch('/api/v1/questionnaire/delete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ ids: this.selectedIds })
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            alert('删除成功')
            this.selectedIds = []
            this.selectAll = false
            this.fetchQuestionnaires()
          } else {
            alert('删除失败: ' + data.msg)
          }
        })
        .catch(err => {
          console.error('Delete error:', err)
          alert('删除失败: 网络错误')
        })
    },

    // Detail Logic
    viewDetails (item) {
      this.currentDetail = item
      this.showDetailModal = true
    },
    closeDetailModal () {
      this.showDetailModal = false
      this.currentDetail = {}
    },
    isStructured (data) {
      return data && data.length > 0 && typeof data[0] === 'object' && !Array.isArray(data[0])
    },
    isSingleChoice (type) {
      return type && type.indexOf('单选题') !== -1
    },
    isFillBlank (type) {
      return type && (type.indexOf('填空') !== -1 || type.indexOf('填空题') !== -1)
    },
    sortByDate () {
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
      this.questionnaires.sort((a, b) => {
        const dateA = new Date(a.create_time)
        const dateB = new Date(b.create_time)
        if (this.sortOrder === 'asc') {
          return dateA - dateB
        } else {
          return dateB - dateA
        }
      })
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
  padding: 20px;
  background-color: #f0f2f5;
  height: 100%;
}

.dashboard-header {
  margin-bottom: 20px;
}

.dashboard-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  padding-left: 10px;
  border-left: 4px solid #4169e1;
}

.filter-container {
  background-color: #fff;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
}

.action-row {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-default {
  background-color: #f0f0f0;
  color: #333;
}
.btn-default:hover {
  background-color: #d9d9d9;
}

.btn-blue {
  background-color: #4169e1;
  color: #fff;
}

.btn-blue:hover {
  background-color: #3da1ff;
}

.btn-red {
  background-color: #ff4d4f;
  color: #fff;
}

.btn-red:hover {
  background-color: #ff7875;
}

.table-container {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
  flex: 1; /* Fill remaining space */
  display: flex;
  flex-direction: column;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
}

.user-table th,
.user-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
  color: #333;
}

.user-table th {
  background-color: #fafafa;
  font-weight: 600;
  color: #262626;
}

.user-table tr:hover {
  background-color: #fafafa;
}

.checkbox-col {
  width: 40px;
  text-align: center;
}

.desc-col {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.action-link {
  color: #1890ff;
  text-decoration: none;
  margin-right: 10px;
  cursor: pointer;
}

.action-link:hover {
  text-decoration: underline;
}

.empty-text {
  text-align: center;
  color: #999;
  padding: 30px;
}

/* Modal Styles */
.modal-mask {
  position: fixed;
  z-index: 9998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.3s ease;
}

.modal-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
}

.modal-container {
  width: 500px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.33);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.detail-modal {
  width: 80%; /* Wider for details */
  max-width: 1200px;
  max-height: 80vh;
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.close-btn {
  font-size: 20px;
  cursor: pointer;
  color: #999;
}
.close-btn:hover {
  color: #666;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input[type="text"],
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  border-color: #4169e1;
  outline: none;
}

.form-group textarea {
  resize: vertical;
}

.tip {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #e8e8e8;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Detail Table */
.detail-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #e8e8e8;
}

.detail-table td {
  padding: 8px;
  border: 1px solid #e8e8e8;
  font-size: 13px;
}

.doc-line {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 8px;
  color: #333;
  white-space: pre-wrap;
}

/* Paper Style for Survey Preview */
.survey-paper {
  font-family: 'Times New Roman', SimSun, sans-serif;
  color: #333;
}

.paper-header {
  text-align: center;
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
  padding-bottom: 20px;
}

.paper-title {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #000;
}

.paper-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.paper-info {
  font-size: 12px;
  color: #999;
}

.paper-content {
  padding: 0 10px;
}

.q-item {
  margin-bottom: 20px;
}

.q-row {
  font-size: 16px;
  line-height: 1.5;
  margin-bottom: 8px;
}

.q-id {
  font-weight: bold;
  margin-right: 8px;
  display: inline-block;
  min-width: 30px;
}

.q-text {
  color: #333;
}

.q-body {
  padding-left: 38px; /* Indent to align with text */
}

.scale-group {
  display: flex;
  gap: 20px;
}

.scale-opt {
  display: flex;
  align-items: center;
  font-size: 14px;
  cursor: default;
}

.checkbox-mock {
  font-size: 16px;
  margin-right: 4px;
  line-height: 1;
}

.blank-line-wrapper {
  font-size: 14px;
  color: #333;
}
</style>
