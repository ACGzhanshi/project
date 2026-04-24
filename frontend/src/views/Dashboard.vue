<template>
  <div>
    <div class="stat-cards">
      <div class="stat-card" v-for="s in stats" :key="s.label">
        <div class="stat-icon" :style="{ background: s.color }">
          <el-icon><component :is="s.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>
    </div>
    <div class="page-card">
      <div class="page-header"><span class="page-title">分数分布</span></div>
      <div ref="chartRef" style="height:350px"></div>
    </div>

    <!-- 非管理员显示快捷功能入口 -->
    <div class="page-card" v-if="!isAdmin">
      <div class="page-header"><span class="page-title">快捷功能</span></div>
      <div class="quick-links">
        <div class="quick-link" @click="$router.push('/universities')">
          <el-icon :size="28" color="#2c5364"><OfficeBuilding /></el-icon>
          <span>院校查询</span>
        </div>
        <div class="quick-link" @click="$router.push('/majors')">
          <el-icon :size="28" color="#4fd1c5"><Reading /></el-icon>
          <span>专业查询</span>
        </div>
        <div class="quick-link" @click="$router.push('/recommend')">
          <el-icon :size="28" color="#38b2ac"><MagicStick /></el-icon>
          <span>智能推荐</span>
        </div>
        <div class="quick-link" @click="$router.push('/assessment')">
          <el-icon :size="28" color="#203a43"><Document /></el-icon>
          <span>专业测评</span>
        </div>
        <div class="quick-link" v-if="role === 'student'" @click="$router.push('/volunteer')">
          <el-icon :size="28" color="#e6a23c"><Edit /></el-icon>
          <span>志愿填报</span>
        </div>
      </div>
    </div>

    <!-- 管理员显示操作日志 -->
    <div class="page-card" v-if="isAdmin">
      <div class="page-header"><span class="page-title">最近操作</span></div>
      <el-table :data="logs" stripe size="small">
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="action" label="操作" width="100" />
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column prop="detail" label="详情" />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, markRaw } from 'vue'
import { useUserStore } from '@/stores/user'
import { getDashboardOverview, getScoreDistribution } from '@/api/system'
import { User, OfficeBuilding, DataAnalysis, TrendCharts, Reading, MagicStick, Document, Edit } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.isAdmin)
const role = computed(() => userStore.role)
const chartRef = ref()
const logs = ref([])
const stats = reactive([
  { label: '用户总数', value: 0, color: '#2c5364', icon: markRaw(User) },
  { label: '院校数量', value: 0, color: '#4fd1c5', icon: markRaw(OfficeBuilding) },
  { label: '分数线数据', value: 0, color: '#203a43', icon: markRaw(DataAnalysis) },
  { label: '推荐记录', value: 0, color: '#38b2ac', icon: markRaw(TrendCharts) },
])

onMounted(async () => {
  try {
    const res = await getDashboardOverview()
    if (res.code === 200) {
      const d = res.data
      stats[0].value = d.user_count
      stats[1].value = d.university_count
      stats[2].value = d.score_count
      stats[3].value = d.recommend_count
      logs.value = d.recent_logs || []
    }
  } catch (e) { /* ignore */ }

  try {
    const res2 = await getScoreDistribution()
    if (res2.code === 200) {
      const d = res2.data
      const chart = echarts.init(chartRef.value)
      chart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: ['<500', '500-550', '550-600', '600-650', '≥650'] },
        yAxis: { type: 'value' },
        series: [{
          type: 'bar', barWidth: '50%',
          data: [d.below_500, d.s500_550, d.s550_600, d.s600_650, d.above_650],
          itemStyle: { borderRadius: [6, 6, 0, 0], color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#2c5364' }, { offset: 1, color: '#4fd1c5' }
          ])}
        }]
      })
      window.addEventListener('resize', () => chart.resize())
    }
  } catch (e) { /* ignore */ }
})
</script>

<style scoped>
.quick-links {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
}
.quick-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 24px 16px;
  border-radius: 10px;
  background: #f7f8fc;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: #4a5568;
}
.quick-link:hover {
  background: #edf2f7;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
</style>
