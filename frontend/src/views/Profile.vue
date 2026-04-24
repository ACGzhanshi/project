<template>
  <div>
    <div class="page-card">
      <div class="page-header"><span class="page-title">个人中心</span></div>
      <el-form :model="form" label-width="90px" style="max-width:500px">
        <el-form-item label="用户名">
          <el-input :value="userStore.userInfo?.username" disabled />
        </el-form-item>
        <el-form-item label="角色">
          <el-input :value="roleLabel[userStore.userInfo?.role]" disabled />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="省份">
          <el-input v-model="form.province" />
        </el-form-item>
        <el-form-item label="高考分数" v-if="userStore.role === 'student'">
          <el-input-number v-model="form.score" :min="0" :max="750" />
        </el-form-item>
        <el-form-item label="科目类型" v-if="userStore.role === 'student'">
          <el-radio-group v-model="form.subject_type">
            <el-radio value="物理类">物理类</el-radio>
            <el-radio value="历史类">历史类</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存修改</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="page-card">
      <div class="page-header"><span class="page-title">修改密码</span></div>
      <el-form :model="pwdForm" label-width="90px" style="max-width:500px">
        <el-form-item label="原密码">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="warning" :loading="changingPwd" @click="handleChangePwd">修改密码</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { updateProfile, changePassword } from '@/api/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const saving = ref(false)
const changingPwd = ref(false)
const roleLabel = { student: '高考生', teacher: '教师', parent: '家长', data_admin: '数据管理员', sys_admin: '系统管理员' }
const form = reactive({ phone: '', province: '', score: null, subject_type: '' })
const pwdForm = reactive({ old_password: '', new_password: '' })

onMounted(() => {
  const u = userStore.userInfo
  if (u) {
    form.phone = u.phone || ''
    form.province = u.province || ''
    form.score = u.score
    form.subject_type = u.subject_type || ''
  }
})

async function handleSave() {
  saving.value = true
  try {
    const res = await updateProfile(form)
    if (res.code === 200) {
      ElMessage.success('保存成功')
      userStore.fetchUserInfo()
    }
  } catch (e) { /* ignore */ }
  finally { saving.value = false }
}

async function handleChangePwd() {
  if (!pwdForm.old_password || !pwdForm.new_password) return ElMessage.warning('请填写密码')
  changingPwd.value = true
  try {
    const res = await changePassword(pwdForm)
    if (res.code === 200) {
      ElMessage.success('密码修改成功')
      pwdForm.old_password = ''
      pwdForm.new_password = ''
    }
  } catch (e) { /* ignore */ }
  finally { changingPwd.value = false }
}
</script>
