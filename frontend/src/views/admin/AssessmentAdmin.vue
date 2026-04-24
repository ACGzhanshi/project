<template>
  <div class="page-card">
    <div class="table-header">
      <el-form :inline="true" :model="query" class="filter-form">
        <el-form-item label="题目内容">
          <el-input v-model="query.search" placeholder="搜索题目关键字..." clearable @clear="handleSearch" @keyup.enter="handleSearch" style="width: 200px" />
        </el-form-item>
        <el-form-item label="测评维度">
          <el-input v-model="query.category" placeholder="输入维度筛选" clearable @clear="handleSearch" @keyup.enter="handleSearch" style="width: 150px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
          <el-button type="success" @click="handleAdd">添加题目</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table :data="tableData" v-loading="loading" stripe border>
      <el-table-column prop="order" label="序号" width="70" align="center" />
      <el-table-column prop="content" label="题目内容" min-width="250" />
      <el-table-column label="选项 (A/B/C/D)" min-width="300">
        <template #default="{ row }">
          <div style="font-size: 12px; line-height: 1.5;">
            <div><b>A:</b> {{ row.option_a }}</div>
            <div><b>B:</b> {{ row.option_b }}</div>
            <div><b>C:</b> {{ row.option_c }}</div>
            <div><b>D:</b> {{ row.option_d }}</div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="category" label="测评维度" width="120" align="center">
        <template #default="{ row }">
          <el-tag>{{ row.category }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" align="center" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button text type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-box">
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="fetchData" @current-change="fetchData" />
    </div>

    <el-dialog :title="isEdit ? '编辑问卷题目' : '添加问卷题目'" v-model="dialogVisible" width="650px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="题目" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="2" placeholder="输入题目内容" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12"><el-form-item label="选项 A" prop="option_a"><el-input v-model="form.option_a" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="选项 B" prop="option_b"><el-input v-model="form.option_b" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="选项 C" prop="option_c"><el-input v-model="form.option_c" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="选项 D" prop="option_d"><el-input v-model="form.option_d" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="维度" prop="category"><el-input v-model="form.category" placeholder="如：R型/理科" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="排序" prop="order"><el-input-number v-model="form.order" style="width: 100%" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getQuestionList, createQuestion, updateQuestion, deleteQuestion } from '@/api/assessment'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const query = reactive({ search: '', category: '', page: 1, page_size: 10 })

function handleSearch() { query.page = 1; fetchData() }
function resetQuery() { Object.assign(query, { search: '', category: '', page: 1 }); fetchData() }

async function fetchData() {
  loading.value = true
  try {
    const res = await getQuestionList(query)
    tableData.value = res.results || res.data || []
    total.value = res.count || 0
  } finally { loading.value = false }
}

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const form = reactive({ id: null, content: '', option_a: '', option_b: '', option_c: '', option_d: '', category: '', order: 0 })

const rules = {
  content: [{ required: true, message: '请输入题目内容', trigger: 'blur' }],
  option_a: [{ required: true, message: '选项不能为空', trigger: 'blur' }],
  category: [{ required: true, message: '请输入测评维度', trigger: 'blur' }]
}

function handleAdd() {
  isEdit.value = false
  Object.assign(form, { id: null, content: '', option_a: '', option_b: '', option_c: '', option_d: '', category: '', order: total.value + 1 })
  if (formRef.value) formRef.value.clearValidate()
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  Object.assign(form, row)
  if (formRef.value) formRef.value.clearValidate()
  dialogVisible.value = true
}

async function submitForm() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        isEdit.value ? await updateQuestion(form.id, form) : await createQuestion(form)
        ElMessage.success('保存成功')
        dialogVisible.value = false
        fetchData()
      } catch (error) { ElMessage.error('保存失败') }
    }
  })
}

async function handleDelete(row) {
  await ElMessageBox.confirm('确定永久删除该题目吗？', '警告', { type: 'warning' })
  try {
    await deleteQuestion(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) { ElMessage.error('删除失败') }
}

onMounted(() => { fetchData() })
</script>

<style scoped>
.table-header { margin-bottom: 20px; background-color: #f8f9fa; padding: 15px; border-radius: 4px; }
.pagination-box { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>