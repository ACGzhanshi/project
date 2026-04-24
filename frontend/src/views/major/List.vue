<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <span class="page-title">专业信息查询</span>
      </div>
      <el-form :inline="true" :model="query" class="filter-form" @submit.prevent="loadData">
        <el-form-item label="专业名称">
          <el-input v-model="query.search" placeholder="搜索专业名称或代码" clearable @clear="loadData" style="width: 200px" />
        </el-form-item>
        <el-form-item label="学科门类">
          <el-select v-model="query.category" placeholder="全部" clearable @change="loadData" style="width: 150px">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属院校">
          <el-select
            v-model="query.university"
            placeholder="输入院校名称搜索"
            clearable
            filterable
            remote
            :remote-method="searchUniversities"
            :loading="uniLoading"
            @change="loadData"
            style="width: 200px"
          >
            <el-option v-for="u in universities" :key="u.id" :label="u.name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="page-card">
      <el-table :data="majors" v-loading="loading" stripe>
        <el-table-column prop="name" label="专业名称" min-width="160" />
        <el-table-column prop="code" label="专业代码" width="120" />
        <el-table-column prop="university_name" label="所属院校" min-width="160" />
        <el-table-column prop="category" label="学科门类" width="100" />
        <el-table-column prop="duration" label="学制" width="70" align="center">
          <template #default="{ row }">{{ row.duration }}年</template>
        </el-table-column>
        <el-table-column prop="degree" label="授予学位" width="110" />
        <el-table-column prop="employment_rate" label="就业率" width="90" align="center">
          <template #default="{ row }">
            <span v-if="row.employment_rate">{{ row.employment_rate }}%</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="avg_salary" label="平均薪资" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.avg_salary">¥{{ row.avg_salary }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="query.page"
          :page-size="10"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadData"
        />
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" :title="currentMajor?.name" width="560px">
      <el-descriptions :column="2" border v-if="currentMajor">
        <el-descriptions-item label="专业名称">{{ currentMajor.name }}</el-descriptions-item>
        <el-descriptions-item label="专业代码">{{ currentMajor.code }}</el-descriptions-item>
        <el-descriptions-item label="所属院校">{{ currentMajor.university_name }}</el-descriptions-item>
        <el-descriptions-item label="学科门类">{{ currentMajor.category }}</el-descriptions-item>
        <el-descriptions-item label="学制">{{ currentMajor.duration }}年</el-descriptions-item>
        <el-descriptions-item label="授予学位">{{ currentMajor.degree || '-' }}</el-descriptions-item>
        <el-descriptions-item label="就业率">{{ currentMajor.employment_rate ? currentMajor.employment_rate + '%' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="平均薪资">{{ currentMajor.avg_salary ? '¥' + currentMajor.avg_salary : '-' }}</el-descriptions-item>
        <el-descriptions-item label="专业简介" :span="2">{{ currentMajor.description || '暂无简介' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getMajorList, getUniversityList } from '@/api/university'

const loading = ref(false)
const majors = ref([])
const total = ref(0)
const universities = ref([])
const categories = ['工学', '理学', '经济学', '管理学', '文学', '法学', '医学', '教育学', '艺术学', '哲学', '历史学', '农学']
const detailVisible = ref(false)
const currentMajor = ref(null)

const query = reactive({
  search: '',
  category: '',
  university: '',
  page: 1
})

async function loadData() {
  loading.value = true
  try {
    const params = { page: query.page }
    if (query.search) params.search = query.search
    if (query.category) params.category = query.category
    if (query.university) params.university = query.university
    const res = await getMajorList(params)
    if (res.code === 200) {
      majors.value = res.data.results || res.data
      total.value = res.data.count || majors.value.length
    } else {
      // DRF 默认分页格式
      majors.value = res.results || []
      total.value = res.count || 0
    }
  } catch (e) { /* ignore */ }
  finally { loading.value = false }
}

const uniLoading = ref(false)

// 远程搜索院校方法
async function searchUniversities(queryStr) {
  uniLoading.value = true
  try {
    // 将用户输入的字符作为 search 参数发给后端
    const res = await getUniversityList({ search: queryStr, page_size: 50 })
    if (res.code === 200) {
      universities.value = res.data?.results || res.data || []
    } else {
      universities.value = res.results || []
    }
  } catch (e) { /* ignore */ }
  finally { uniLoading.value = false }
}

// 初始加载时不带搜索词，只加载前50个占位
function loadUniversities() {
  searchUniversities('')
}

function resetQuery() {
  query.search = ''
  query.category = ''
  query.university = ''
  query.page = 1
  loadData()
}

function showDetail(row) {
  currentMajor.value = row
  detailVisible.value = true
}

onMounted(() => {
  loadData()
  loadUniversities()
})
</script>

<style scoped lang="scss">
.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.text-muted {
  color: #a0aec0;
}
</style>
