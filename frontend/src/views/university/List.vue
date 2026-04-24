<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <span class="page-title">院校查询</span>
      </div>
      <el-form :inline="true" :model="query" class="filter-form">
        <el-form-item label="省份">
          <el-select v-model="query.province" clearable placeholder="全部" @change="fetchList">
            <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="层次">
          <el-select v-model="query.level" clearable placeholder="全部" @change="fetchList">
            <el-option label="本科" value="本科" />
            <el-option label="专科" value="专科" />
          </el-select>
        </el-form-item>
        <el-form-item label="特色">
          <el-checkbox v-model="query.is_985" @change="fetchList">985</el-checkbox>
          <el-checkbox v-model="query.is_211" @change="fetchList">211</el-checkbox>
          <el-checkbox v-model="query.is_double_first" @change="fetchList">双一流</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-input v-model="query.search" placeholder="搜索院校名称" clearable @keyup.enter="fetchList" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchList">查询</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="page-card">
      <el-table v-loading="loading" :data="list" stripe border>
        <el-table-column prop="name" label="院校名称" min-width="150" />
        <el-table-column label="所在地" width="120">
          <template #default="{ row }">
            {{ row.province }} {{ row.city }}
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="level" label="层次" width="80" />
        <el-table-column prop="ranking" label="排名" width="80" align="center" />
        <el-table-column label="标签" min-width="180">
          <template #default="{ row }">
            <el-tag v-if="row.is_985" type="danger" size="small" class="tag-gap">985</el-tag>
            <el-tag v-if="row.is_211" type="warning" size="small" class="tag-gap">211</el-tag>
            <el-tag v-if="row.is_double_first" type="success" size="small">双一流</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="$router.push(`/universities/${row.id}`)">详情</el-button>
            <el-button link type="success" @click="handleShowTrend(row)">录取趋势</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        layout="total, prev, pager, next"
        class="pagination"
        @current-change="fetchList"
      />
    </div>

    <el-dialog v-model="trendVisible" :title="`${currentUniv.name} - 录取数据趋势`" width="800px" @opened="initChart">
      <div style="margin-bottom: 20px;">
        <span style="margin-right: 10px;">选择生源地:</span>
        <el-select v-model="trendProvince" style="width: 120px" @change="loadTrendData">
          <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
        </el-select>
      </div>
      <div v-loading="trendLoading" style="height: 400px">
        <div ref="chartRef" style="width: 100%; height: 100%"></div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { getUniversityList, getProvinces, getUniversityScoreTrends } from '@/api/university'
import * as echarts from 'echarts'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const provinces = ref([])
const query = reactive({
  province: '', level: '', is_985: false, is_211: false, is_double_first: false,
  search: '', page: 1, page_size: 10
})

// --- 趋势逻辑数据 ---
const trendVisible = ref(false)
const trendLoading = ref(false)
const currentUniv = ref({})
const trendProvince = ref('北京')
const chartRef = ref(null)
let myChart = null

async function fetchList() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size, search: query.search }
    if (query.province) params.province = query.province
    if (query.level) params.level = query.level
    if (query.is_985) params.is_985 = true
    if (query.is_211) params.is_211 = true
    if (query.is_double_first) params.is_double_first = true
    const res = await getUniversityList(params)
    list.value = res.results || res.data || []
    total.value = res.count || 0
  } catch (e) { /* ignore */ }
  finally { loading.value = false }
}

function handleShowTrend(row) {
  currentUniv.value = row
  trendVisible.value = true
}

async function loadTrendData() {
  trendLoading.value = true
  try {
    const res = await getUniversityScoreTrends(currentUniv.value.id, { province: trendProvince.value })
    renderChart(res.data)
  } catch (e) {
    console.error("加载趋势失败", e)
  } finally {
    trendLoading.value = false
  }
}

function renderChart(data) {
  if (!myChart) myChart = echarts.init(chartRef.value)
  myChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { data: ['最低分', '最低位次'] },
    xAxis: { type: 'category', data: data.years },
    yAxis: [
      { type: 'value', name: '分数', min: 'dataMin' },
      { type: 'value', name: '位次', inverse: true, nameLocation: 'start' }
    ],
    series: [
      { name: '最低分', type: 'line', data: data.min_scores, smooth: true },
      { name: '最低位次', type: 'line', yAxisIndex: 1, data: data.min_ranks, smooth: true }
    ]
  })
}

function initChart() { loadTrendData() }

onMounted(async () => {
  const pRes = await getProvinces()
  provinces.value = pRes.data || []
  fetchList()
})
</script>

<style scoped>
.filter-form { margin-top: 20px; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
.tag-gap { margin-right: 5px; }
</style>