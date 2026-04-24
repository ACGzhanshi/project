<template>
  <div class="page-card">
    <el-tabs v-model="activeTab">

      <el-tab-pane label="院校管理" name="university">
        <div class="table-header">
          <el-form :inline="true" :model="uQuery" class="filter-form">
            <el-form-item label="院校名称">
              <el-input v-model="uQuery.search" placeholder="搜索名称/代码" clearable @clear="handleUSearch" @keyup.enter="handleUSearch" style="width: 160px" />
            </el-form-item>
            <el-form-item label="省份">
              <el-select v-model="uQuery.province" placeholder="全部" clearable @change="handleUSearch" style="width: 120px">
                <el-option v-for="p in provinceList" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
            <el-form-item label="层次">
              <el-select v-model="uQuery.level" placeholder="全部" clearable @change="handleUSearch" style="width: 120px">
                <el-option v-for="l in levelList" :key="l" :label="l" :value="l" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleUSearch">查询</el-button>
              <el-button @click="resetUQuery">重置</el-button>
              <el-button type="success" @click="handleAddU">添加院校</el-button>
            </el-form-item>
          </el-form>
        </div>

        <el-table :data="uList" v-loading="loading" stripe border>
          <el-table-column prop="code" label="代码" width="80" />
          <el-table-column prop="name" label="院校名称" min-width="150" />
          <el-table-column prop="province" label="省份" width="80" />
          <el-table-column prop="level" label="层次" width="100" />
          <el-table-column label="操作" width="150" align="center" fixed="right">
            <template #default="{ row }">
              <el-button text type="primary" @click="handleEditU(row)">编辑</el-button>
              <el-button text type="danger" @click="handleDeleteU(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-box">
          <el-pagination v-model:current-page="uQuery.page" v-model:page-size="uQuery.page_size" :total="uTotal" layout="total, prev, pager, next" @current-change="fetchUList" />
        </div>
      </el-tab-pane>

      <el-tab-pane label="专业管理" name="major">
        <div class="table-header">
          <el-form :inline="true" :model="mQuery" class="filter-form">
            <el-form-item label="所属院校">
              <el-select
                v-model="mQuery.university"
                filterable remote clearable
                placeholder="输入院校信息搜索"
                :remote-method="searchFilterUniversities"
                :loading="uSelectLoading"
                @change="handleMSearch"
                style="width: 180px"
              >
                <el-option v-for="u in filterUniversities" :key="u.id" :label="u.name" :value="u.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="学科门类">
              <el-select v-model="mQuery.category" placeholder="全部" clearable @change="handleMSearch" style="width: 120px">
                <el-option v-for="c in categoryList" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
            <el-form-item label="专业名称">
              <el-input v-model="mQuery.search" placeholder="搜专业名称/代码" clearable @clear="handleMSearch" @keyup.enter="handleMSearch" style="width: 150px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleMSearch">查询</el-button>
              <el-button type="success" @click="handleAddM">添加专业</el-button>
            </el-form-item>
          </el-form>
        </div>

        <el-table :data="mList" v-loading="loading" stripe border>
          <el-table-column prop="university_name" label="所属院校" min-width="150" />
          <el-table-column prop="name" label="专业名称" min-width="150" />
          <el-table-column prop="code" label="代码" width="100" />
          <el-table-column prop="category" label="门类" width="100" />
          <el-table-column label="操作" width="150" align="center" fixed="right">
            <template #default="{ row }">
              <el-button text type="primary" @click="handleEditM(row)">编辑</el-button>
              <el-button text type="danger" @click="handleDeleteM(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-box">
          <el-pagination v-model:current-page="mQuery.page" v-model:page-size="mQuery.page_size" :total="mTotal" layout="total, prev, pager, next" @current-change="fetchMList" />
        </div>
      </el-tab-pane>

      <el-tab-pane label="分数线与计划" name="scores">
        <div class="table-header">
          <el-form :inline="true" :model="sQuery" class="filter-form">
            <el-form-item label="年份">
              <el-select v-model="sQuery.year" placeholder="全部" clearable @change="handleSSearch" style="width: 90px">
                <el-option v-for="y in [2025, 2024, 2023, 2022]" :key="y" :label="y" :value="y" />
              </el-select>
            </el-form-item>
            <el-form-item label="省份">
              <el-select v-model="sQuery.province" placeholder="全部" clearable @change="handleSSearch" style="width: 90px">
                <el-option v-for="p in provinceList" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
            <el-form-item label="院校">
              <el-select
                v-model="sQuery.university"
                filterable remote clearable
                placeholder="输入院校过滤"
                :remote-method="searchFilterUniversities"
                :loading="uSelectLoading"
                @change="handleSSearch"
                style="width: 160px"
              >
                <el-option v-for="u in filterUniversities" :key="u.id" :label="u.name" :value="u.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="专业">
              <el-input v-model="sQuery.search" placeholder="搜专业名称" clearable @keyup.enter="handleSSearch" style="width: 140px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSSearch">查询</el-button>
              <el-button type="success" @click="handleAddS">添加记录</el-button>
            </el-form-item>
          </el-form>
        </div>

        <el-table :data="sList" v-loading="loading" border stripe>
          <el-table-column prop="year" label="年份" width="70" />
          <el-table-column prop="university_name" label="院校" min-width="130" />
          <el-table-column prop="major_name" label="专业" min-width="150" />
          <el-table-column prop="province" label="生源地" width="80" />
          <el-table-column prop="subject_type" label="科类" width="80" />
          <el-table-column prop="plan_count" label="计划人数" width="90">
            <template #default="{row}"><b style="color: #409EFF">{{ row.plan_count || '-' }}</b></template>
          </el-table-column>
          <el-table-column prop="min_score" label="最低分" width="80" />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{row}">
              <el-button text type="primary" @click="handleEditS(row)">编辑</el-button>
              <el-button text type="danger" @click="handleDeleteS(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-box">
          <el-pagination v-model:current-page="sQuery.page" :total="sTotal" layout="total, prev, pager, next" @current-change="fetchSList" />
        </div>
      </el-tab-pane>

    </el-tabs>

    <el-dialog :title="isEditU ? '编辑院校' : '添加院校'" v-model="uDialogVisible" width="650px">
      <el-form :model="uForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12"><el-form-item label="名称"><el-input v-model="uForm.name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="代码"><el-input v-model="uForm.code" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="省份"><el-input v-model="uForm.province" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="层次"><el-input v-model="uForm.level" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="特色标签">
          <el-checkbox v-model="uForm.is_985">985</el-checkbox>
          <el-checkbox v-model="uForm.is_211">211</el-checkbox>
          <el-checkbox v-model="uForm.is_double_first">双一流</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUForm">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog :title="isEditM ? '编辑专业' : '添加专业'" v-model="mDialogVisible" width="650px">
      <el-form :model="mForm" label-width="100px">
        <el-form-item label="所属院校" required>
          <el-select
            v-model="mForm.university"
            filterable remote
            placeholder="输入院校信息搜索"
            :remote-method="searchFilterUniversities"
            :loading="uSelectLoading"
            style="width: 100%"
          >
            <el-option v-for="u in filterUniversities" :key="u.id" :label="u.name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12"><el-form-item label="专业名称" required><el-input v-model="mForm.name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="专业代码"><el-input v-model="mForm.code" /></el-form-item></el-col>
          <el-col :span="12">
            <el-form-item label="学科门类">
              <el-select v-model="mForm.category" style="width: 100%">
                <el-option v-for="c in categoryList" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学制(年)">
              <el-input-number v-model="mForm.duration" :min="1" :max="8" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12"><el-form-item label="学费"><el-input v-model="mForm.tuition" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="选科要求"><el-input v-model="mForm.major_group" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="mDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitMForm">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog :title="isEditS ? '编辑录取记录' : '添加录取记录'" v-model="sDialogVisible" width="650px">
      <el-form :model="sForm" label-width="100px">
        <el-form-item label="所属院校" required>
          <el-select
            v-model="sForm.university"
            filterable remote
            placeholder="输入院校信息搜索 (先选院校再选专业)"
            :remote-method="searchFilterUniversities"
            :loading="uSelectLoading"
            style="width: 100%"
            @change="handleSFormUniversityChange"
          >
            <el-option v-for="u in filterUniversities" :key="u.id" :label="u.name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="录取专业" required>
          <el-select
            v-model="sForm.major"
            filterable remote
            placeholder="输入专业信息搜索"
            :remote-method="searchSFormMajors"
            :loading="mSelectLoading"
            style="width: 100%"
          >
            <el-option v-for="m in sFormMajorOptions" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="生源省份" required>
              <el-select v-model="sForm.province" style="width: 100%">
                <el-option v-for="p in provinceList" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12"><el-form-item label="录取年份" required><el-input-number v-model="sForm.year" :min="2010" style="width: 100%"/></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="科类"><el-input v-model="sForm.subject_type" placeholder="如：物理类"/></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="批次"><el-input v-model="sForm.batch" placeholder="如：本科批"/></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="计划人数"><el-input-number v-model="sForm.plan_count" :min="0" style="width: 100%"/></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="最低分"><el-input-number v-model="sForm.min_score" :min="0" style="width: 100%"/></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="最低位次"><el-input-number v-model="sForm.min_rank" :min="0" style="width: 100%"/></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="sDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitSForm">保存</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getUniversityList, createUniversity, updateUniversity, deleteUniversity,
  getMajorList, createMajor, updateMajor, deleteMajor,
  getUniversityProvinces,
  getScoreList, createScore, updateScore, deleteScore // 确保 api.js 里有 createScore
} from '@/api/university'

const activeTab = ref('university')
const loading = ref(false)

const provinceList = ref([])
const levelList = ['本科(普通)', '专科(高职)', '中外合作办学', '独立学院']
const categoryList = ['哲学', '经济学', '法学', '教育学', '文学', '历史学', '理学', '工学', '农学', '医学', '军事学', '管理学', '艺术学', '交叉学科']

// ================= 全局组件：远程搜学校 =================
const uSelectLoading = ref(false)
const filterUniversities = ref([])
async function searchFilterUniversities(query) {
  if (!query) return
  uSelectLoading.value = true
  try {
    const res = await getUniversityList({ search: query, page_size: 30 })
    filterUniversities.value = res.data?.results || res.results || res.data || []
  } finally { uSelectLoading.value = false }
}

// ================= 全局组件：表单内搜专业 =================
const mSelectLoading = ref(false)
const sFormMajorOptions = ref([])
async function searchSFormMajors(query) {
  if (!query) return
  mSelectLoading.value = true
  try {
    // 限制只搜索当前选中院校的专业，防止选错
    const params = { search: query, page_size: 30 }
    if (sForm.university) params.university = sForm.university
    const res = await getMajorList(params)
    sFormMajorOptions.value = res.data?.results || res.results || res.data || []
  } finally { mSelectLoading.value = false }
}
function handleSFormUniversityChange() {
  sForm.major = null // 切换学校时，清空已选专业
  sFormMajorOptions.value = []
}


// ================= 1. 院校逻辑 =================
const uList = ref([])
const uTotal = ref(0)
const uQuery = reactive({ search: '', province: '', level: '', page: 1, page_size: 10 })
const uDialogVisible = ref(false)
const isEditU = ref(false)
const uForm = reactive({ id: null, name: '', code: '', province: '', level: '', is_985: false, is_211: false, is_double_first: false })

function handleUSearch() { uQuery.page = 1; fetchUList() }
function resetUQuery() { Object.assign(uQuery, { search: '', province: '', level: '', page: 1 }); fetchUList() }
async function fetchUList() {
  loading.value = true
  try {
    const res = await getUniversityList(uQuery)
    uList.value = res.results || res.data || []
    uTotal.value = res.count || 0
  } finally { loading.value = false }
}
function handleAddU() { isEditU.value = false; Object.assign(uForm, { id: null, name: '', code: '', province: '', level: '', is_985: false, is_211: false, is_double_first: false }); uDialogVisible.value = true }
function handleEditU(row) { isEditU.value = true; Object.assign(uForm, row); uDialogVisible.value = true }
async function submitUForm() {
  try {
    isEditU.value ? await updateUniversity(uForm.id, uForm) : await createUniversity(uForm)
    ElMessage.success('保存成功'); uDialogVisible.value = false; fetchUList()
  } catch (error) { ElMessage.error('保存失败') }
}
async function handleDeleteU(row) {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await deleteUniversity(row.id)
  ElMessage.success('删除成功'); fetchUList()
}

// ================= 2. 专业逻辑 =================
const mList = ref([])
const mTotal = ref(0)
const mQuery = reactive({ search: '', university: '', category: '', page: 1, page_size: 10 })
const mDialogVisible = ref(false)
const isEditM = ref(false)
const mForm = reactive({ id: null, university: null, name: '', code: '', category: '', duration: 4, tuition: '', major_group: '' })

function handleMSearch() { mQuery.page = 1; fetchMList() }
function resetMQuery() { Object.assign(mQuery, { search: '', university: '', category: '', page: 1 }); filterUniversities.value = []; fetchMList() }
async function fetchMList() {
  loading.value = true
  try {
    const res = await getMajorList(mQuery)
    mList.value = res.results || res.data || []
    mTotal.value = res.count || 0
  } finally { loading.value = false }
}
function handleAddM() {
  isEditM.value = false;
  Object.assign(mForm, { id: null, university: null, name: '', code: '', category: '', duration: 4, tuition: '', major_group: '' });
  filterUniversities.value = [];
  mDialogVisible.value = true
}
function handleEditM(row) {
  isEditM.value = true;
  Object.assign(mForm, row);
  // 为下拉框提供默认显示文字
  filterUniversities.value = [{ id: row.university, name: row.university_name }];
  mDialogVisible.value = true
}
async function submitMForm() {
  if (!mForm.university || !mForm.name) return ElMessage.warning('请填写必填项（院校和专业名称）')
  try {
    isEditM.value ? await updateMajor(mForm.id, mForm) : await createMajor(mForm)
    ElMessage.success('保存成功'); mDialogVisible.value = false; fetchMList()
  } catch (error) { ElMessage.error('保存失败') }
}
async function handleDeleteM(row) {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await deleteMajor(row.id)
  ElMessage.success('删除成功'); fetchMList()
}

// ================= 3. 分数线/计划逻辑 =================
const sList = ref([])
const sTotal = ref(0)
const sQuery = reactive({ search: '', university: '', year: '', province: '', page: 1, page_size: 10 })
const sDialogVisible = ref(false)
const isEditS = ref(false)
const sForm = reactive({
  id: null, university: null, major: null, year: new Date().getFullYear(),
  province: '', subject_type: '', batch: '', plan_count: null, min_score: null, min_rank: null
})

function handleSSearch() { sQuery.page = 1; fetchSList() }
function resetSQuery() { Object.assign(sQuery, { search: '', university: '', year: '', province: '', page: 1 }); filterUniversities.value = []; fetchSList() }
async function fetchSList() {
  loading.value = true
  try {
    const res = await getScoreList(sQuery)
    sList.value = res.results || res.data || []
    sTotal.value = res.count || 0
  } finally { loading.value = false }
}
function handleAddS() {
  isEditS.value = false;
  Object.assign(sForm, { id: null, university: null, major: null, year: new Date().getFullYear(), province: '', subject_type: '', batch: '', plan_count: null, min_score: null, min_rank: null });
  filterUniversities.value = [];
  sFormMajorOptions.value = [];
  sDialogVisible.value = true
}
function handleEditS(row) {
  isEditS.value = true;
  Object.assign(sForm, row);
  // 为下拉框提供默认显示文字
  filterUniversities.value = [{ id: row.university, name: row.university_name }];
  sFormMajorOptions.value = [{ id: row.major, name: row.major_name }];
  sDialogVisible.value = true
}
async function submitSForm() {
  if (!sForm.university || !sForm.major || !sForm.province || !sForm.year) return ElMessage.warning('请完整填写所属院校、专业、省份和年份')
  try {
    isEditS.value ? await updateScore(sForm.id, sForm) : await createScore(sForm)
    ElMessage.success('保存成功'); sDialogVisible.value = false; fetchSList()
  } catch (error) { ElMessage.error('保存失败') }
}
async function handleDeleteS(row) {
  await ElMessageBox.confirm('确定删除这条记录吗？', '提示', { type: 'warning' })
  await deleteScore(row.id)
  ElMessage.success('删除成功'); fetchSList()
}

// ================= 初始化 =================
onMounted(async () => {
  fetchUList()
  fetchMList()
  fetchSList()
  try {
    const pRes = await getUniversityProvinces()
    provinceList.value = pRes.data || pRes || []
  } catch(e) {}
})
</script>

<style scoped>
.table-header { margin-bottom: 20px; background-color: #f8f9fa; padding: 15px; border-radius: 4px; }
.filter-form .el-form-item { margin-bottom: 0; }
.pagination-box { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>