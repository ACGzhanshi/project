<template>
  <div class="page-card">
    <div class="page-header">
      <span class="page-title">用户管理</span>
    </div>

    <el-form :inline="true" :model="query">
      <el-form-item>
        <el-select v-model="query.role" clearable placeholder="角色筛选" @change="fetchList">
          <el-option label="高考生" value="student" />
          <el-option label="教师" value="teacher" />
          <el-option label="家长" value="parent" />
          <el-option label="数据管理员" value="data_admin" />
          <el-option label="系统管理员" value="sys_admin" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-input v-model="query.search" placeholder="搜索用户名/手机号" clearable @keyup.enter="fetchList" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleAdd">添加用户</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="role" label="角色" width="100">
        <template #default="{ row }">{{ roleLabel[row.role] }}</template>
      </el-table-column>
      <el-table-column prop="phone" label="手机号" width="130" />
      <el-table-column prop="province" label="省份" width="80" />
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button text size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button text size="small" type="warning" @click="handleToggle(row)">
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
          <el-button text size="small" @click="handleReset(row)">重置密码</el-button>
          <el-button text size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="isEdit ? '编辑用户' : '添加用户'" v-model="dialogVisible" width="500px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入唯一用户名"></el-input>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%;">
            <el-option label="高考生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="家长" value="parent" />
            <el-option label="数据管理员" value="data_admin" />
            <el-option label="系统管理员" value="sys_admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号"></el-input>
        </el-form-item>
       <el-form-item label="省份" prop="province">
  <el-select v-model="form.province" placeholder="请选择或搜索省份" filterable clearable style="width: 100%;">
    <el-option
      v-for="item in provinceList"
      :key="item"
      :label="item"
      :value="item"
    />
  </el-select>
</el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用"></el-switch>
        </el-form-item>
        <el-form-item v-if="!isEdit">
          <span style="color: #909399; font-size: 12px;">注：新建用户的默认密码为 123456</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import {
  getUserList, toggleUserStatus, resetUserPassword,
  createUser, updateUser, deleteUser
} from '@/api/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { validatePhone, validateEmail, provinceList } from '@/utils/validate'

const loading = ref(false)
const list = ref([])
const query = reactive({ role: '', search: '' })
const roleLabel = { student: '高考生', teacher: '教师', parent: '家长', data_admin: '数据管理员', sys_admin: '系统管理员' }

// 弹窗表单状态
const dialogVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const form = reactive({
  id: null,
  username: '',
  role: 'student',
  phone: '',
  province: '',
  is_active: true
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '用户名不能为空', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/, message: '只能包含中英文、数字和下划线', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '手机号不能为空', trigger: 'blur' },
    { validator: validatePhone, trigger: 'blur' } // 🚀 使用全系统通用的手机号强校验
  ],
  email: [
    { validator: validateEmail, trigger: 'blur' } // 🚀 邮箱格式校验
  ],
  // 🚨 删掉关于 score 的校验逻辑
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getUserList(query)
    list.value = res.results || res.data || []
  } catch (e) { /* ignore */ }
  finally { loading.value = false }
}

// 打开添加弹窗
function handleAdd() {
  isEdit.value = false
  dialogVisible.value = true
}

// 打开编辑弹窗
function handleEdit(row) {
  isEdit.value = true
  // 数据回显
  Object.assign(form, {
    id: row.id,
    username: row.username,
    role: row.role,
    phone: row.phone || '',
    province: row.province || '',
    is_active: row.is_active
  })
  dialogVisible.value = true
}

// 关闭弹窗重置表单
function resetForm() {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(form, { id: null, username: '', role: 'student', phone: '', province: '', is_active: true })
}

// 提交表单 (新建 / 更新)
async function submitForm() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await updateUser(form.id, form)
          ElMessage.success('更新用户信息成功')
        } else {
          await createUser(form)
          ElMessage.success('添加用户成功，默认密码为123456')
        }
        dialogVisible.value = false
        fetchList()
      } catch (error) {
        const errData = error.response?.data
        if (errData && typeof errData === 'object' && !errData.code) {
          // 提取后端抛出的第一个字段错误提示 (比如用户名已存在、手机号已存在)
          const firstKey = Object.keys(errData)[0]
          const errorMsg = Array.isArray(errData[firstKey]) ? errData[firstKey][0] : errData[firstKey]
          ElMessage.error(errorMsg || '操作失败，请检查输入格式')
        } else {
          ElMessage.error(errData?.message || '操作失败')
        }
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 删除用户
async function handleDelete(row) {
  await ElMessageBox.confirm(`确定永久删除用户 [${row.username}] 吗？此操作不可逆！`, '警告', {
    type: 'warning',
    confirmButtonText: '确定删除',
    cancelButtonText: '取消'
  })

  try {
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    fetchList()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

async function handleToggle(row) {
  await toggleUserStatus(row.id)
  ElMessage.success('操作成功')
  fetchList()
}

async function handleReset(row) {
  await ElMessageBox.confirm(`确定重置 ${row.username} 的密码为123456？`, '提示')
  await resetUserPassword(row.id)
  ElMessage.success('密码已重置')
}

onMounted(fetchList)
</script>