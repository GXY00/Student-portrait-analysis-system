<template>
  <div class="cluster-analysis-container">
    <div class="page-header">
      <h2>群体定位分析</h2>
      <button class="create-btn" @click="openCreateModal">
        <span class="icon">+</span> 新建分析任务
      </button>
    </div>

    <div class="main-layout">
      <!-- 左侧历史任务列表 -->
      <div class="history-sidebar">
        <div class="sidebar-title">历史任务记录</div>
        <div v-if="loadingHistory" class="loading-text">加载中...</div>
        <ul v-else class="task-list">
          <li
            v-for="task in historyTasks"
            :key="task.task_id"
            class="task-item"
            :class="{ active: currentTask && currentTask.task_id === task.task_id }"
            @click="loadTask(task)"
          >
            <div class="task-name">{{ task.task_desc }}</div>
            <div class="task-meta">
              <span class="tag">K={{ task.k_value }}</span>
              <span class="time">{{ formatDate(task.create_time) }}</span>
            </div>
          </li>
          <li v-if="historyTasks.length === 0" class="empty-list">暂无历史记录</li>
        </ul>
      </div>

      <!-- 右侧图表区域 -->
      <div class="charts-wrapper">
        <div v-if="loadingAnalysis" class="loading-overlay">
          <div class="spinner"></div>
          <p>正在进行聚类分析...</p>
        </div>

        <div v-if="currentTaskResult" class="analysis-content">
          <div class="charts-row">
            <!-- 散点图 -->
            <div class="chart-card scatter-card">
              <div class="card-header">
                <h3>群体分布图</h3>
                <span class="subtitle">点击散点查看详细画像</span>
              </div>
              <div ref="scatterChart" class="chart-body"></div>
            </div>

            <!-- 雷达图 -->
            <div class="chart-card radar-card">
              <div class="card-header">
                <h3>簇特征雷达图</h3>
                <span class="subtitle" v-if="selectedPoint">
                  当前选中: 学生ID {{ selectedPoint.student_id }} (类别 {{ selectedPoint.cluster }})
                </span>
                <span class="subtitle" v-else>展示选中学生或簇中心的特征</span>
              </div>
              <div ref="radarChart" class="chart-body"></div>
            </div>
          </div>

          <!-- 簇信息统计 -->
          <div class="clusters-info">
            <div v-for="info in currentTaskResult.clusters_info" :key="info.cluster_id" class="cluster-stat-card">
              <div class="stat-header">
                <span class="cluster-badge" :style="{ backgroundColor: colorPalette[info.cluster_id % colorPalette.length] }">
                  Cluster {{ info.cluster_id }}
                </span>
                <span class="count">{{ info.count }} 人</span>
              </div>
              <div class="stat-desc">
                占总人数 {{ ((info.count / totalStudents) * 100).toFixed(1) }}%
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="!loadingAnalysis" class="empty-state">
          <div class="empty-icon">📊</div>
          <p>请从左侧选择一个历史任务，或点击上方按钮创建新任务</p>
        </div>
      </div>
    </div>

    <!-- 新建任务弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>新建聚类分析任务</h3>
          <button class="close-btn" @click="closeCreateModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>任务描述</label>
            <input v-model="newTask.desc" type="text" placeholder="例如：2024春季期末学业心理分析">
          </div>

          <div class="form-group">
            <label>聚类数量 (K值)</label>
            <input v-model.number="newTask.k" type="number" min="2" max="10">
            <span class="help-text">建议设置为 3-6 之间</span>
          </div>

          <div class="form-group">
            <label>选择特征维度 (至少选2项)</label>
            <div class="features-grid">
              <label v-for="tag in availableFeatures" :key="tag" class="checkbox-label">
                <input type="checkbox" :value="tag" v-model="newTask.features">
                {{ tag }}
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeCreateModal">取消</button>
          <button class="btn confirm" @click="startAnalysis" :disabled="!isValidTask">开始分析</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'ClusterAnalysis',
  data () {
    return {
      historyTasks: [],
      currentTask: null,
      currentTaskResult: null,
      loadingHistory: false,
      loadingAnalysis: false,
      showCreateModal: false,

      // 新任务表单
      newTask: {
        desc: '',
        k: 4,
        features: ['平均成绩', '学习动机强度'] // 默认选中
      },

      // 可选特征（这里先硬编码常用定量标签，实际可从后端获取）
      availableFeatures: [
        '平均成绩',
        '成绩标准差',
        '偏科指数',
        '学习自律指数',
        '学习动机强度',
        '心理稳定性指数',
        '学术参与度指数',
        '学习投入强度'
      ],

      // 图表实例
      scatterChartInstance: null,
      radarChartInstance: null,

      // 选中状态
      selectedPoint: null,

      // 颜色盘
      colorPalette: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']
    }
  },
  computed: {
    isValidTask () {
      return this.newTask.desc && this.newTask.features.length >= 2 && this.newTask.k >= 2
    },
    totalStudents () {
      if (!this.currentTaskResult) return 0
      return this.currentTaskResult.points.length
    }
  },
  mounted () {
    this.fetchHistory()
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy () {
    window.removeEventListener('resize', this.handleResize)
    if (this.scatterChartInstance) this.scatterChartInstance.dispose()
    if (this.radarChartInstance) this.radarChartInstance.dispose()
  },
  methods: {
    formatDate (dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleString()
    },

    async fetchHistory () {
      this.loadingHistory = true
      try {
        const res = await fetch('http://localhost:5000/api/v1/analysis/cluster/history')
        const data = await res.json()
        if (data.code === 200) {
          this.historyTasks = data.data
        }
      } catch (error) {
        console.error('获取历史记录失败', error)
      } finally {
        this.loadingHistory = false
      }
    },

    openCreateModal () {
      this.newTask.desc = `聚类任务_${new Date().toLocaleDateString()}`
      this.showCreateModal = true
    },

    closeCreateModal () {
      this.showCreateModal = false
    },

    async startAnalysis () {
      this.closeCreateModal()
      this.loadingAnalysis = true
      this.currentTaskResult = null

      try {
        const payload = {
          task_desc: this.newTask.desc,
          k_value: this.newTask.k,
          features: this.newTask.features
        }

        const res = await fetch('http://localhost:5000/api/v1/analysis/cluster', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })
        const data = await res.json()

        if (data.code === 200) {
          this.currentTaskResult = data.data
          // 刷新历史记录并选中最新
          await this.fetchHistory()
          this.currentTask = this.historyTasks[0]

          this.$nextTick(() => {
            this.initCharts()
          })
        } else {
          alert('分析失败: ' + data.message)
        }
      } catch (error) {
        console.error('分析请求失败', error)
        alert('分析请求失败，请检查网络或后端服务')
      } finally {
        this.loadingAnalysis = false
      }
    },

    // 加载已有任务（注意：当前后端API没有提供获取特定任务结果的接口，
    // 这里为了演示，我们假设点击历史任务时，如果是刚刚创建的，直接用内存里的结果。
    // 如果是旧任务，实际应该调用一个 get_task_result 接口。
    // 由于后端只写了 create 接口返回结果，为了完整性，我建议临时复用 create 接口重新跑一次，或者仅仅展示"重新运行"
    // 为了用户体验，我们这里简单处理：点击历史任务 -> 重新运行该配置 (或者后端补充一个详情接口)
    // 鉴于后端代码已定，我们假设点击历史任务时，前端提取其配置重新请求分析接口
    // 这是一个权宜之计，但能工作）
    async loadTask (task) {
      this.currentTask = task
      // 解析 feature_desc
      const features = task.feature_desc.split(',')

      this.loadingAnalysis = true
      this.currentTaskResult = null

      try {
        // 重新调用分析接口以获取结果（因为没有单独的 get_result 接口）
        const payload = {
          task_desc: task.task_desc, // 保持原名
          k_value: task.k_value,
          features: features
        }

        // 注意：这会创建一条新的重复记录，但为了展示效果先这样做
        const res = await fetch('http://localhost:5000/api/v1/analysis/cluster', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })
        const data = await res.json()

        if (data.code === 200) {
          this.currentTaskResult = data.data
          this.$nextTick(() => {
            this.initCharts()
          })
        }
      } catch (error) {
        console.error('加载任务失败', error)
      } finally {
        this.loadingAnalysis = false
      }
    },

    initCharts () {
      if (!this.currentTaskResult) return

      this.initScatterChart()
      this.initRadarChart()
    },

    initScatterChart () {
      const dom = this.$refs.scatterChart
      if (!dom) return

      this.scatterChartInstance = echarts.init(dom)

      const points = this.currentTaskResult.points
      const k = this.currentTaskResult.k_value

      // 按簇分组数据
      const seriesData = []
      for (let i = 0; i < k; i++) {
        seriesData.push({
          name: `Cluster ${i}`,
          type: 'scatter',
          symbolSize: 10,
          data: points.filter(p => p.cluster === i).map(p => [p.x, p.y, p.student_id]),
          itemStyle: {
            color: this.colorPalette[i % this.colorPalette.length]
          }
        })
      }

      const option = {
        tooltip: {
          formatter: (params) => {
            return `Student ID: ${params.value[2]}<br/>Cluster: ${params.seriesName}`
          }
        },
        legend: {
          right: 10,
          top: 10
        },
        xAxis: { scale: true, name: 'PC1', show: false }, // 隐藏坐标轴刻度，只看分布
        yAxis: { scale: true, name: 'PC2', show: false },
        series: seriesData
      }

      this.scatterChartInstance.setOption(option)

      // 点击事件
      this.scatterChartInstance.on('click', (params) => {
        const studentId = params.value[2]
        const cluster = parseInt(params.seriesName.split(' ')[1])
        this.selectedPoint = { student_id: studentId, cluster: cluster }
        this.updateRadarChart(cluster, studentId) // 可以在这里传 studentId 进一步高亮
      })
    },

    initRadarChart () {
      const dom = this.$refs.radarChart
      if (!dom) return

      this.radarChartInstance = echarts.init(dom)
      // 默认显示 Cluster 0
      this.updateRadarChart(0)
    },

    updateRadarChart (clusterId, studentId = null) {
      if (!this.radarChartInstance) return

      const features = this.currentTaskResult.features
      const clusterInfo = this.currentTaskResult.clusters_info.find(c => c.cluster_id === clusterId)

      if (!clusterInfo) return

      // 构造雷达图指标
      // const indicator = features.map(f => ({ name: f, max: 2 })) // 假设标准化后值在 -2 到 2 之间，这里 max 设为相对值，或者动态计算

      // 实际上标准化后的值可能是负数，ECharts 雷达图处理负数不太直观，通常需要归一化或者直接显示
      // 为了展示效果，我们直接显示原始值（如果是标准化值，可能需要 shift 一下）
      // 后端返回的是 centroids (原始值吗？cluster_analysis.py 里是 df_pivot.groupby('cluster').mean()，df_pivot 是标准化前的吗？
      // 看代码：df_pivot 是原始值 (tag_value -> to_numeric)。 X_scaled 才是标准化的。
      // 所以 centroids 是原始值，非常好！

      // 动态计算 max 值以适应雷达图
      // 简单起见，取所有簇中该特征的最大值 * 1.2
      const maxValues = {}
      features.forEach(f => {
        let max = 0
        this.currentTaskResult.clusters_info.forEach(c => {
          const val = Math.abs(c.features[f])
          if (val > max) max = val
        })
        maxValues[f] = max === 0 ? 100 : max * 1.2 // 避免0
      })

      const finalIndicator = features.map(f => ({ name: f, max: maxValues[f] }))

      const data = [
        {
          value: features.map(f => clusterInfo.features[f]),
          name: `Cluster ${clusterId} 均值`,
          areaStyle: {
            color: new echarts.graphic.RadialGradient(0.1, 0.6, 1, [
              { color: 'rgba(255, 145, 124, 0.1)', offset: 0 },
              { color: 'rgba(255, 145, 124, 0.9)', offset: 1 }
            ])
          }
        }
      ]

      // 如果有选中学生，还需要获取该学生的具体数值
      // 目前后端接口只返回了 points (x, y)，没有返回每个学生的原始特征值
      // 这是一个小缺憾，为了完美，我们暂只显示簇均值。
      // 或者：前端可以在 loadTask 时把 df 数据也带回来？目前没有。
      // 暂时只显示簇均值。

      const option = {
        color: ['#FF917C'],
        tooltip: {},
        radar: {
          indicator: finalIndicator,
          shape: 'circle',
          splitNumber: 5,
          axisName: {
            color: 'rgb(238, 197, 102)'
          },
          splitLine: {
            lineStyle: {
              color: [
                'rgba(238, 197, 102, 0.1)',
                'rgba(238, 197, 102, 0.2)',
                'rgba(238, 197, 102, 0.4)',
                'rgba(238, 197, 102, 0.6)',
                'rgba(238, 197, 102, 0.8)',
                'rgba(238, 197, 102, 1)'
              ].reverse()
            }
          },
          splitArea: {
            show: false
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(238, 197, 102, 0.5)'
            }
          }
        },
        series: [
          {
            name: `Cluster ${clusterId}`,
            type: 'radar',
            lineStyle: { width: 3 },
            symbol: 'none',
            data: data
          }
        ]
      }

      this.radarChartInstance.setOption(option)
    },

    handleResize () {
      if (this.scatterChartInstance) this.scatterChartInstance.resize()
      if (this.radarChartInstance) this.radarChartInstance.resize()
    }
  }
}
</script>

<style scoped>
.cluster-analysis-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.create-btn {
  background-color: #1890ff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  transition: all 0.3s;
}

.create-btn:hover {
  background-color: #40a9ff;
}

.main-layout {
  display: flex;
  flex: 1;
  gap: 20px;
  min-height: 0; /* 防止溢出 */
}

/* Sidebar */
.history-sidebar {
  width: 280px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-title {
  padding: 15px;
  font-weight: 600;
  border-bottom: 1px solid #eee;
  background-color: #fafafa;
}

.task-list {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
  overflow-y: auto;
}

.task-item {
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.task-item:hover {
  background-color: #f5f7fa;
}

.task-item.active {
  background-color: #e6f7ff;
  border-right: 3px solid #1890ff;
}

.task-name {
  font-weight: 500;
  margin-bottom: 5px;
  color: #333;
}

.task-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}

.tag {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
}

/* Charts Area */
.charts-wrapper {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 20px;
  display: flex;
  flex-direction: column;
  position: relative;
}

.analysis-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.charts-row {
  display: flex;
  flex: 1;
  gap: 20px;
  min-height: 400px;
}

.chart-card {
  flex: 1;
  border: 1px solid #eee;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

.card-header {
  padding: 15px;
  border-bottom: 1px solid #eee;
  background: #fafafa;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
}

.subtitle {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
  display: block;
}

.chart-body {
  flex: 1;
  min-height: 300px;
}

.clusters-info {
  margin-top: 20px;
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.cluster-stat-card {
  background: #f9f9f9;
  padding: 10px 15px;
  border-radius: 6px;
  border: 1px solid #eee;
  min-width: 120px;
}

.cluster-badge {
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: bold;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.stat-desc {
  font-size: 12px;
  color: #666;
}

/* Empty State */
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #ccc;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group input[type="number"] {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-weight: normal;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  border: none;
}

.btn.cancel {
  background: #f5f5f5;
  color: #666;
}

.btn.confirm {
  background: #1890ff;
  color: white;
}

.btn.confirm:disabled {
  background: #d9d9d9;
  cursor: not-allowed;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255,255,255,0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
