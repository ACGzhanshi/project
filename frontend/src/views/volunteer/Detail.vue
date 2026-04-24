<template>
  <div v-loading="loading">
    <div class="page-card">
      <el-page-header @back="$router.back()">
        <template #content><span class="page-title">{{ form.name }}</span></template>
        <template #extra>
          <el-button type="primary" @click="handleAnalyze" :loading="analyzing">智能分析概率</el-button>
        </template>
      </el-page-header>
      <el-descriptions :column="4" border style="margin-top:16px">
        <el-descriptions-item label="分数">{{ form.score }}</el-descriptions-item>
        <el-descriptions-item label="省份">{{ form.province }}</el-descriptions-item>
        <el-descriptions-item label="科类">{{ form.subject_type }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag size="small">{{ form.status === 'analyzed' ? '已分析' : '草稿' }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <div class="page-card">
      <div class="page-header">
        <span class="page-title">我的志愿列表</span>
        <el-button type="primary" icon="Plus" size="small" @click="showAdd = true">添加志愿</el-button>
      </div>
      <el-table :data="items" stripe>
        <el-table-column prop="order" label="序号" width="60" />
        <el-table-column prop="university_name" label="院校" min-width="160">
          <template #default="{ row }">{{ row.university?.name || row.university_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="major_name" label="专业" min-width="150">
          <template #default="{ row }">{{ row.major?.name || row.major_name || '未选专业' }}</template>
        </el-table-column>
        <el-table-column prop="level" label="冲稳保评估" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.probability > 0" :type="levelType[row.level]" size="small">{{ levelLabel[row.level] }}</el-tag>
            <el-tag v-else type="info" size="small">缺本省招生数据</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="probability" label="录取概率" width="100">
          <template #default="{ row }">
            <span v-if="row.probability > 0" style="font-weight: bold">{{ row.probability }}%</span>
            <span v-else style="color: #999">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button type="danger" text size="small" @click="handleRemove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="page-card" v-if="analysis">
      <div class="page-header"><span class="page-title">整体梯度诊断</span></div>
      <div class="stat-cards">
        <div class="stat-card">
          <div class="stat-icon" style="background:#f56c6c"><el-icon><Top /></el-icon></div>
          <div class="stat-info"><div class="stat-value">{{ analysis.summary?.rush }}</div><div class="stat-label">冲刺</div></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#e6a23c"><el-icon><Minus /></el-icon></div>
          <div class="stat-info"><div class="stat-value">{{ analysis.summary?.stable }}</div><div class="stat-label">稳妥</div></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#67c23a"><el-icon><Bottom /></el-icon></div>
          <div class="stat-info"><div class="stat-value">{{ analysis.summary?.safe }}</div><div class="stat-label">保底</div></div>
        </div>
      </div>
      <el-alert v-for="(s, i) in analysis.suggestions" :key="i" :title="s" type="info" show-icon :closable="false" style="margin-bottom:8px" />
    </div>

    <el-dialog v-model="showAdd" title="添加志愿" width="450px">
      <el-form :model="addForm" label-width="60px">
        <el-form-item label="院校">
          <el-select v-model="addForm.university" filterable remote :remote-method="searchUni" @change="handleUniChange" placeholder="输入关键字搜索院校" style="width:100%">
            <el-option v-for="u in uniOptions" :key="u.id" :label="u.name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="专业">
          <el-select v-model="addForm.major" filterable placeholder="选择专业 (必填)" :disabled="!addForm.university" style="width:100%">
            <el-option v-for="m in majorOptions" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" @click="handleAdd">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getFormDetail, analyzeForm, addItem, removeItem } from '@/api/volunteer'
import { getUniversityList } from '@/api/university'
import request from '@/utils/request' // 引入全局请求工具用于获取全量专业
import { ElMessage } from 'element-plus'

const route = useRoute()
const loading = ref(true)
const analyzing = ref(false)
const showAdd = ref(false)
const form = ref({})
const items = ref([])
const analysis = ref(null)

const uniOptions = ref([])
const majorOptions = ref([]) // 新增：存放当前选中院校的所有专业
const addForm = ref({ university: null, major: null })

const levelLabel = { rush: '冲', stable: '稳', safe: '保' }
const levelType = { rush: 'danger', stable: 'warning', safe: 'success' }

async function fetchDetail() {
  try {
    const res = await getFormDetail(route.params.id)
    const data = res.data || res
    form.value = data
    items.value = data.items || []
    if (data.analysis) {
      try { analysis.value = typeof data.analysis === 'string' ? JSON.parse(data.analysis) : data.analysis } catch (e) { /* ignore */ }
    }
  } catch (e) { /* ignore */ }
  finally { loading.value = false }
}

async function handleAnalyze() {
  analyzing.value = true
  try {
    const res = await analyzeForm(route.params.id)
    if (res.code === 200) {
      analysis.value = res.data
      ElMessage.success('分析完成')
      fetchDetail()
    }
  } catch (e) { /* ignore */ }
  finally { analyzing.value = false }
}

async function searchUni(q) {
  if (!q) return
  try {
    const res = await getUniversityList({ search: q })
    uniOptions.value = res.results || res.data || []
  } catch (e) { /* ignore */ }
}

// 核心修复：选择院校后，无视分页限制，拉取该校所有专业
async function handleUniChange(uniId) {
  addForm.value.major = null
  majorOptions.value = []
  if (!uniId) return
  try {
    const res = await request.get('/universities/majors/', {
      params: { university: uniId, no_page: 1 }
    })

    // 🚨 终极无敌解析法：无论拦截器包了几层，只要找到数组就立刻赋值！
    if (Array.isArray(res)) {
      majorOptions.value = res; // 拦截器已经脱去外衣，直接就是数组
    } else if (res && Array.isArray(res.data)) {
      majorOptions.value = res.data; // 包在 data 里面
    } else if (res && Array.isArray(res.results)) {
      majorOptions.value = res.results; // 分页结构下的 results
    } else if (res && res.data && Array.isArray(res.data.results)) {
      majorOptions.value = res.data.results;
    } else {
      majorOptions.value = [];
    }

  } catch (e) {
    ElMessage.error('获取专业列表失败')
  }
}

async function handleAdd() {
  if (!addForm.value.university) return ElMessage.warning('请选择院校')
  if (!addForm.value.major) return ElMessage.warning('请选择专业') // 强制要求选专业，保证概率准确

  await addItem(route.params.id, {
    university: addForm.value.university,
    major: addForm.value.major
  })

  ElMessage.success('添加成功')
  showAdd.value = false
  addForm.value = { university: null, major: null } // 重置表单
  fetchDetail()
}

async function handleRemove(itemId) {
  await removeItem(route.params.id, itemId)
  ElMessage.success('删除成功')
  fetchDetail()
}

onMounted(fetchDetail)
</script>