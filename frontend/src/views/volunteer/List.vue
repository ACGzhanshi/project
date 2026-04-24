<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <span class="page-title">我的志愿表</span>
        <el-button type="primary" icon="Plus" @click="showCreate = true">新建志愿表</el-button>
      </div>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="name" label="志愿表名称" min-width="160">
          <template #default="{ row }">
            <router-link :to="`/volunteer/${row.id}`" class="uni-link">{{ row.name }}</router-link>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="分数" width="80" />
        <el-table-column prop="province" label="省份" width="80" />
        <el-table-column prop="subject_type" label="科类" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type" size="small">{{ statusMap[row.status]?.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="showCreate" title="新建志愿表" width="450px">
      <el-form :model="createForm" :rules="createRules" ref="createRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="createForm.name" placeholder="如：第一批志愿" />
        </el-form-item>
        <el-form-item label="分数" prop="score">
          <el-input-number v-model="createForm.score" :min="100" :max="750" style="width:100%" />
        </el-form-item>
        <el-form-item label="省份" prop="province">
          <el-input v-model="createForm.province" placeholder="如：广东" />
        </el-form-item>

        <el-form-item label="科类" prop="subject_type">
          <el-select v-model="createForm.subject_type" placeholder="请选择科类" style="width:100%">
            <el-option-group label="新高考 (3+1+2)">
              <el-option label="物理类" value="物理类" />
              <el-option label="历史类" value="历史类" />
            </el-option-group>
            <el-option-group label="传统高考 (文理分科)">
              <el-option label="理科" value="理科" />
              <el-option label="文科" value="文科" />
            </el-option-group>
            <el-option-group label="综合改革 (3+3)">
              <el-option label="综合" value="综合" />
              <el-option label="不分文理" value="不分文理" />
            </el-option-group>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEdit" title="编辑志愿表" width="450px">
      <el-form :model="editForm" :rules="createRules" ref="editRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="editForm.name" placeholder="如：第一批志愿" />
        </el-form-item>
        <el-form-item label="分数" prop="score">
          <el-input-number v-model="editForm.score" :min="100" :max="750" style="width:100%" />
        </el-form-item>
        <el-form-item label="省份" prop="province">
          <el-input v-model="editForm.province" placeholder="如：广东" />
        </el-form-item>
        <el-form-item label="科类" prop="subject_type">
          <el-select v-model="editForm.subject_type" placeholder="请选择科类" style="width:100%">
            <el-option-group label="新高考 (3+1+2)">
              <el-option label="物理类" value="物理类" />
              <el-option label="历史类" value="历史类" />
            </el-option-group>
            <el-option-group label="传统高考 (文理分科)">
              <el-option label="理科" value="理科" />
              <el-option label="文科" value="文科" />
            </el-option-group>
            <el-option-group label="综合改革 (3+3)">
              <el-option label="综合" value="综合" />
              <el-option label="不分文理" value="不分文理" />
            </el-option-group>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" :loading="editing" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getFormList, createForm as createFormApi, deleteForm, updateForm } from '@/api/volunteer'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const creating = ref(false)
const showCreate = ref(false)
const list = ref([])
const createRef = ref()
const showEdit = ref(false)
const editing = ref(false)
const editRef = ref()
const editForm = reactive({ id: null, name: '', score: null, province: '', subject_type: '' })
// 将默认值改为一个通用项或者留空
const createForm = reactive({ name: '', score: 600, province: '', subject_type: '物理类' })
const createRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  score: [{ required: true, message: '请输入分数', trigger: 'blur' }],
  province: [{ required: true, message: '请输入省份', trigger: 'blur' }],
  subject_type: [{ required: true, message: '请选择科类', trigger: 'change' }]
}
const statusMap = {
  draft: { label: '草稿', type: 'info' },
  submitted: { label: '已提交', type: 'warning' },
  analyzed: { label: '已分析', type: 'success' }
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getFormList()
    list.value = res.results || res.data || []
  } catch (e) { /* ignore */ }
  finally { loading.value = false }
}

async function handleCreate() {
  await createRef.value.validate()
  creating.value = true
  try {
    const res = await createFormApi(createForm)
    if (res.code === 200 || res.id) {
      ElMessage.success('创建成功')
      showCreate.value = false
      // 创建成功后重置表单
      createForm.name = ''
      createForm.province = ''
      fetchList()
    }
  } catch (e) { /* ignore */ }
  finally { creating.value = false }
}

async function handleDelete(id) {
  await ElMessageBox.confirm('确定删除该志愿表？', '提示', { type: 'warning' })
  await deleteForm(id)
  ElMessage.success('删除成功')
  fetchList()
}

function handleEdit(row) {
  // 浅拷贝数据，避免直接修改表格显示的数据
  editForm.id = row.id
  editForm.name = row.name
  editForm.score = row.score
  editForm.province = row.province
  editForm.subject_type = row.subject_type
  showEdit.value = true
}

// 3. 增加提交编辑的方法
async function submitEdit() {
  await editRef.value.validate()
  editing.value = true
  try {
    const res = await updateForm(editForm.id, {
      name: editForm.name,
      score: editForm.score,
      province: editForm.province,
      subject_type: editForm.subject_type
    })
    // 拦截器通常已经处理了报错，只要不抛出异常就是成功
    ElMessage.success('修改成功')
    showEdit.value = false
    fetchList() // 刷新列表
  } catch (e) {
    /* ignore */
  } finally {
    editing.value = false
  }
}

onMounted(fetchList)
</script>

<style scoped>
.uni-link { color: #667eea; text-decoration: none; font-weight: 500; }
</style>