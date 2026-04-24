<template>
  <div class="university-detail-container" v-loading="loading">
    <el-page-header @back="$router.back()" class="custom-header">
      <template #content>
        <div class="header-info">
          <span class="uni-name">{{ uni.name || '加载中...' }}</span>
          <div class="tags-wrap" v-if="uni.name">
            <el-tag v-if="uni.is_985" type="danger" effect="dark" size="small">985</el-tag>
            <el-tag v-if="uni.is_211" type="warning" effect="dark" size="small">211</el-tag>
            <el-tag v-if="uni.is_double_first" type="success" effect="dark" size="small">双一流</el-tag>
            <el-tag type="info" size="small">{{ uni.type || '院校' }}</el-tag>
            <el-tag type="info" size="small">{{ uni.level || '本科' }}</el-tag>
          </div>
        </div>
      </template>
    </el-page-header>

    <el-card class="info-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span class="card-title">基本资料</span>
        </div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="院校代码">{{ uni.code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="全国排名">No.{{ uni.ranking || '-' }}</el-descriptions-item>
        <el-descriptions-item label="所在省份">{{ uni.province || '-' }}</el-descriptions-item>
        <el-descriptions-item label="所在城市">{{ uni.city || '-' }}</el-descriptions-item>
        <el-descriptions-item label="就业率">
          <span v-if="uni.employment_rate">{{ uni.employment_rate }}%</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="官方网站">
          <el-link v-if="uni.website" :href="uni.website" target="_blank" type="primary">点击访问</el-link>
          <span v-else>-</span>
        </el-descriptions-item>
      </el-descriptions>
      <div class="description-section">
        <h4 class="sub-title">院校简介</h4>
        <p class="desc-text">{{ uni.description || '暂无详细简介' }}</p>
      </div>
    </el-card>

    <el-tabs v-model="activeTab" class="detail-tabs" @tab-click="handleTabClick">

      <el-tab-pane label="录取趋势" name="trends">
        <div class="trend-filter">
          <span class="filter-label">选择生源地：</span>
          <el-select v-model="trendProvince" placeholder="请选择省份" @change="updateChart" style="width: 150px">
            <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
          </el-select>
        </div>
        <div ref="chartRef" class="score-chart"></div>
      </el-tab-pane>

      <el-tab-pane label="专业录取分数" name="admission_scores">
        <div style="margin-bottom: 20px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
          <span style="font-size: 14px; color: #606266;">录取对比：</span>
          <el-select v-model="scoreQuery.years" multiple collapse-tags placeholder="选择对比年份" style="width: 180px">
            <el-option label="2024年" :value="2024" />
            <el-option label="2023年" :value="2023" />
            <el-option label="2022年" :value="2022" />
          </el-select>

          <el-select v-model="scoreQuery.province" placeholder="生源省份" style="width: 120px">
            <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
          </el-select>

          <el-select v-model="scoreQuery.subject_type" placeholder="科类" style="width: 160px">
            <el-option-group label="新高考 (3+1+2)">
              <el-option label="物理类" value="物理类" />
              <el-option label="历史类" value="历史类" />
            </el-option-group>
            <el-option-group label="传统文理">
              <el-option label="理科" value="理科" />
              <el-option label="文科" value="文科" />
            </el-option-group>
            <el-option-group label="综合改革/其他">
              <el-option label="综合" value="综合" />
              <el-option label="不分文理" value="不分文理" />
            </el-option-group>
          </el-select>

          <el-input
            v-model="scoreQuery.search"
            placeholder="搜索专业名称"
            clearable
            style="width: 200px;"
            @keyup.enter="loadScores"
          />
          <el-button type="primary" icon="Search" @click="loadScores">查询对比</el-button>
        </div>

        <el-table :data="pagedScoreData" v-loading="scoreLoading" stripe border>
          <el-table-column prop="major_name" label="专业名称" min-width="180">
            <template #default="{row}">
              <strong>{{ row.major_name || row.major?.name || '未知专业' }}</strong>
            </template>
          </el-table-column>
          <el-table-column
             prop="major_discipline_eval"
             label="学科等级"
             width="100"
             align="center"
             sortable
             :sort-method="sortEval"
          >
           <template #default="{row}">
            <el-tag
              v-if="row.major_discipline_eval"
              :type="row.major_discipline_eval.includes('A') ? 'danger' : 'primary'"
              size="small"
              effect="dark"
            >
              {{ row.major_discipline_eval }}
            </el-tag>
            <span v-else>-</span>
           </template>
        </el-table-column>
          <el-table-column prop="year" label="年份" width="90" align="center" sortable />
          <el-table-column prop="batch" label="录取批次" width="120" />
          <el-table-column prop="min_score" label="最低分" width="90" align="center">
            <template #default="{row}">
              <span style="font-weight: bold; color: #f56c6c">{{ row.min_score }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="min_rank" label="最低位次" width="110" align="center" />
          <el-table-column prop="plan_count" label="计划数" width="90" align="center" />
        </el-table>

        <div class="pagination-wrap">
          <el-pagination
            v-model:current-page="scoreQuery.page"
            :page-size="scoreQuery.pageSize"
            :total="scoreTableData.length"
            layout="total, prev, pager, next"
            @current-change="handleScorePageChange"
            background
          />
        </div>
      </el-tab-pane>

      <el-tab-pane label="专业设置" name="majors">
        <div class="major-filter-bar">
          <el-input
            v-model="majorQuery.search"
            placeholder="搜索专业名称"
            clearable
            @input="loadMajors"
            style="width: 300px; margin-bottom: 20px;"
          >
            <template #append>
              <el-button icon="Search" @click="loadMajors" />
            </template>
          </el-input>
        </div>

        <el-table :data="majorsList" v-loading="majorsLoading" stripe border>
          <el-table-column prop="name" label="专业名称" min-width="150" />
          <el-table-column prop="discipline_eval" label="学科评估" width="100" align="center">
            <template #default="{row}">
              <el-tag v-if="row.discipline_eval && row.discipline_eval.includes('A')" type="danger" effect="dark" size="small">
                {{ row.discipline_eval }}
              </el-tag>
              <el-tag v-else-if="row.discipline_eval" type="primary" effect="plain" size="small">
                {{ row.discipline_eval }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="code" label="专业代码" width="120" />
          <el-table-column prop="category" label="门类" width="100" />
          <el-table-column prop="duration" label="学制" width="90" align="center">
            <template #default="{row}">{{ row.duration }}年</template>
          </el-table-column>
          <el-table-column prop="tuition" label="学费" width="130">
            <template #default="{row}">
              <span class="tuition-text">{{ row.tuition || '详见官网' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="major_group" label="选科要求" min-width="180" show-overflow-tooltip />
        </el-table>

        <div class="pagination-wrap">
          <el-pagination
            v-model:current-page="majorQuery.page"
            :page-size="10"
            :total="majorTotal"
            layout="total, prev, pager, next"
            @current-change="loadMajors"
            background
          />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  getUniversityDetail,
  getUniversityProvinces,
  getUniversityScoreTrends,
  getMajorList,
  getScoreList
} from '@/api/university'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { Search } from '@element-plus/icons-vue'

const route = useRoute()
const loading = ref(false)
const uni = ref({})
const provinces = ref([])
const trendProvince = ref('北京')
const chartRef = ref(null)
let myChart = null
const activeTab = ref('trends')
const evalWeight = {
  'A+': 9, 'A': 8, 'A-': 7,
  'B+': 6, 'B': 5, 'B-': 4,
  'C+': 3, 'C': 2, 'C-': 1
}
const sortEval = (a, b) => {
  const weightA = evalWeight[a.major_discipline_eval] || 0
  const weightB = evalWeight[b.major_discipline_eval] || 0
  return weightA - weightB
}
// ================= 专业设置分页状态 (完全保留原版) =================
const majorsList = ref([])
const majorTotal = ref(0)
const majorsLoading = ref(false)
const majorQuery = reactive({
  page: 1,
  search: ''
})

// ================= 新增：多年度录取分数状态 =================
const scoreLoading = ref(false)
const scoreTableData = ref([])
const scoreQuery = reactive({
  page: 1,
  pageSize: 15,
  years: [2024, 2023],
  province: '',
  subject_type: '物理类',
  search: ''
})

// 专业分数列表的前端分页处理
const pagedScoreData = computed(() => {
  const start = (scoreQuery.page - 1) * scoreQuery.pageSize
  const end = start + scoreQuery.pageSize
  return scoreTableData.value.slice(start, end)
})

// ================= 方法区 =================

async function loadDetail() {
  loading.value = true
  try {
    const res = await getUniversityDetail(route.params.id)
    uni.value = res.data || res || {}
    await loadProvinces()
  } catch (e) {
    console.error('加载院校基础信息失败', e)
  } finally {
    loading.value = false
  }
}

async function loadProvinces() {
  try {
    const res = await getUniversityProvinces()
    provinces.value = res.data || res || []

    if (provinces.value.length > 0) {
      if (uni.value.province && provinces.value.includes(uni.value.province)) {
        trendProvince.value = uni.value.province
        scoreQuery.province = uni.value.province
      } else {
        trendProvince.value = provinces.value[0]
        scoreQuery.province = provinces.value[0]
      }
      updateChart()
      if (activeTab.value === 'admission_scores') loadScores()
    }
  } catch (e) { /* ignore */ }
}

// 👑 获取专业列表 (完全保留原版逻辑和分页)
async function loadMajors() {
  if (!route.params.id) return
  majorsLoading.value = true
  try {
    const params = {
      university: route.params.id,
      page: majorQuery.page,
      search: majorQuery.search,
      page_size: 10
    }
    const res = await getMajorList(params)
    const data = res.data || res || {}
    majorsList.value = data.results || []
    majorTotal.value = data.count || 0
  } catch (e) {
    console.error('加载专业列表失败', e)
  } finally {
    majorsLoading.value = false
  }
}

// 🚀 新增：多年度录取分数对比加载逻辑
async function loadScores() {
  if (!route.params.id) return
  if (!scoreQuery.province) return

  scoreLoading.value = true
  scoreQuery.page = 1

  try {
    // 通过并发请求拉取多年度全量数据 (page_size: 2000)
    const requests = scoreQuery.years.map(year => {
      return getScoreList({
        university: route.params.id,
        year: year,
        province: scoreQuery.province,
        subject_type: scoreQuery.subject_type,
        search: scoreQuery.search,
        page_size: 2000
      })
    })

    const responses = await Promise.all(requests)

    let allData = []
    responses.forEach(res => {
      const yearData = res.results || res.data || []
      allData = allData.concat(yearData)
    })

    // 排序：同专业汇聚，年份降序
    allData.sort((a, b) => {
      const nameA = a.major_name || a.major?.name || ''
      const nameB = b.major_name || b.major?.name || ''
      if (nameA === nameB) return b.year - a.year
      return nameA.localeCompare(nameB, 'zh-Hans-CN')
    })

    scoreTableData.value = allData
  } catch (e) {
    ElMessage.error('查询录取数据失败')
  } finally {
    scoreLoading.value = false
  }
}

function handleScorePageChange(page) {
  scoreQuery.page = page
}

// 👑 绘制/更新图表 (完全保留原版逻辑)
async function updateChart() {
  await nextTick()
  if (!chartRef.value) return
  if (!myChart) myChart = echarts.init(chartRef.value)

  myChart.showLoading()
  try {
    const res = await getUniversityScoreTrends(route.params.id, { province: trendProvince.value })
    const data = res.data || res || {}
    myChart.hideLoading()

    if (data.years && data.years.length > 0) {
      const option = {
        tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
        legend: { data: ['最低分', '最低位次', '计划人数'] },
        grid: { left: '3%', right: '5%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', boundaryGap: true, data: data.years },
        yAxis: [
          { type: 'value', name: '分数', min: 'dataMin', position: 'left' },
          { type: 'value', name: '位次', inverse: true, position: 'right' }
        ],
        series: [
          { name: '最低分', type: 'line', yAxisIndex: 0, data: data.min_scores, smooth: true, symbolSize: 8, lineStyle: { width: 3, color: '#ff6b6b' }, itemStyle: { color: '#ff6b6b' }, z: 3 },
          { name: '最低位次', type: 'line', yAxisIndex: 1, data: data.min_ranks, smooth: true, symbolSize: 8, lineStyle: { width: 3, type: 'dashed', color: '#52c41a' }, itemStyle: { color: '#52c41a' }, z: 3 },
          { name: '计划人数', type: 'bar', yAxisIndex: 0, data: data.plan_counts, barMaxWidth: 40, itemStyle: { color: 'rgba(64, 158, 255, 0.25)', borderRadius: [4, 4, 0, 0] }, z: 1 }
        ]
      }
      myChart.setOption(option, true)
    } else {
      myChart.clear()
      myChart.showLoading({ text: '该省份暂无历年分数数据', showSpinner: false })
    }
  } catch (e) {
    myChart.hideLoading()
  }
}

function handleTabClick(tab) {
  if (tab.name === 'majors') loadMajors()
  if (tab.name === 'trends') updateChart()
  if (tab.name === 'admission_scores' && scoreTableData.value.length === 0) loadScores()
}

onMounted(() => {
  loadDetail()
  loadMajors()
})
</script>

<style scoped lang="scss">
.university-detail-container {
  padding: 24px;
  background-color: #f0f2f5;
  min-height: 100vh;
}

.custom-header {
  background: #fff;
  padding: 16px 24px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,21,41,0.08);
  .header-info {
    display: flex;
    align-items: center;
    gap: 16px;
    .uni-name {
      font-size: 22px;
      font-weight: 600;
      color: #1a1a1a;
    }
    .tags-wrap {
      display: flex;
      gap: 8px;
    }
  }
}

.info-card {
  .card-title {
    font-size: 16px;
    font-weight: 600;
  }
}

.description-section {
  margin-top: 24px;
  .sub-title {
    border-left: 4px solid #1890ff;
    padding-left: 12px;
    margin-bottom: 12px;
    color: #262626;
  }
  .desc-text {
    font-size: 14px;
    line-height: 1.8;
    color: #595959;
    white-space: pre-wrap;
  }
}

.detail-tabs {
  margin-top: 24px;
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  min-height: 500px;
}

.trend-filter {
  margin-bottom: 24px;
  .filter-label {
    font-size: 14px;
    color: #8c8c8c;
  }
}

.score-chart {
  height: 450px;
  width: 100%;
}

.tuition-text {
  color: #ff4d4f;
  font-weight: bold;
}

.pagination-wrap {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style>