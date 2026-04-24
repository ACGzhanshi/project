<template>
  <div class="auth-page">
    <div class="auth-brand">
      <div class="brand-content">
        <div class="brand-logo">
          <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="48" height="48" rx="12" fill="rgba(255,255,255,0.15)"/>
            <path d="M24 10L14 18v14h8v-8h4v8h8V18L24 10z" fill="#fff"/>
            <circle cx="24" cy="22" r="3" fill="rgba(255,255,255,0.6)"/>
          </svg>
          <span class="brand-name">高考志愿智能推荐平台</span>
        </div>
        <h1 class="brand-slogan">开启你的升学规划之旅</h1>
        <p class="brand-desc">注册账号，获取个性化的院校推荐和志愿填报方案，让每一分都不浪费</p>
        <div class="brand-features">
          <div class="feature-item">
            <div class="feature-dot"></div>
            <span>个性化院校智能匹配</span>
          </div>
          <div class="feature-item">
            <div class="feature-dot"></div>
            <span>历年录取数据深度分析</span>
          </div>
          <div class="feature-item">
            <div class="feature-dot"></div>
            <span>一键生成志愿填报方案</span>
          </div>
        </div>
      </div>
      <div class="brand-decoration">
        <div class="deco-circle deco-1"></div>
        <div class="deco-circle deco-2"></div>
        <div class="deco-circle deco-3"></div>
      </div>
    </div>
    <div class="auth-form-side">
      <div class="auth-form-wrapper">
        <div class="form-header">
          <h2>创建账号</h2>
          <p>填写以下信息完成注册</p>
        </div>
        <el-form ref="formRef" :model="form" :rules="rules" size="large">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" :prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="请设置密码（至少6位）" :prefix-icon="Lock" show-password />
          </el-form-item>
          <el-form-item prop="role">
            <el-select v-model="form.role" placeholder="选择你的身份" style="width:100%">
              <el-option label="高考生" value="student" />
              <el-option label="教师" value="teacher" />
              <el-option label="家长" value="parent" />
            </el-select>
          </el-form-item>
          <el-form-item prop="phone">
            <el-input v-model="form.phone" placeholder="手机号（选填）" :prefix-icon="Phone" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" class="submit-btn" @click="handleRegister">注 册</el-button>
          </el-form-item>
        </el-form>
        <div class="form-footer">
          已有账号？<router-link to="/login">去登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '@/api/user'
import { ElMessage } from 'element-plus'
import { User, Lock, Phone } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '', role: 'student', phone: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: '密码至少6位', trigger: 'blur' }],
  role: [{ required: true, message: '请选择身份', trigger: 'change' }]
}

async function handleRegister() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await register(form)
    if (res.code === 200) {
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    }
  } catch (e) { /* interceptor handles */ }
  finally { loading.value = false }
}
</script>

<style scoped lang="scss">
.auth-page {
  height: 100vh;
  display: flex;
  background: #f8f9fc;
}

.auth-brand {
  flex: 1;
  background: linear-gradient(160deg, #0f2027 0%, #203a43 40%, #2c5364 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 60px;
}

.brand-content {
  position: relative;
  z-index: 2;
  max-width: 480px;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 48px;

  svg { width: 42px; height: 42px; flex-shrink: 0; }

  .brand-name {
    font-size: 16px;
    color: rgba(255, 255, 255, 0.85);
    font-weight: 500;
    letter-spacing: 1px;
  }
}

.brand-slogan {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  line-height: 1.3;
  margin-bottom: 16px;
  letter-spacing: 1px;
}

.brand-desc {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.55);
  line-height: 1.8;
  margin-bottom: 40px;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.75);
  font-size: 14px;
}

.feature-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4fd1c5;
  flex-shrink: 0;
}

.brand-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.deco-1 { width: 400px; height: 400px; top: -100px; right: -100px; }
.deco-2 { width: 300px; height: 300px; bottom: -80px; left: -60px; }
.deco-3 { width: 200px; height: 200px; bottom: 20%; right: 10%; background: rgba(79, 209, 197, 0.05); }

.auth-form-side {
  width: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: #fff;
}

.auth-form-wrapper {
  width: 100%;
  max-width: 360px;
}

.form-header {
  margin-bottom: 36px;

  h2 {
    font-size: 26px;
    font-weight: 700;
    color: #1a202c;
    margin-bottom: 8px;
  }

  p {
    font-size: 14px;
    color: #a0aec0;
  }
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  border-radius: 8px;
  letter-spacing: 4px;
}

.form-footer {
  text-align: center;
  font-size: 14px;
  color: #a0aec0;
  margin-top: 24px;

  a {
    color: #2c5364;
    text-decoration: none;
    font-weight: 500;

    &:hover { color: #4fd1c5; }
  }
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e2e8f0;
  padding: 4px 12px;

  &:hover { box-shadow: 0 0 0 1px #cbd5e0; }
  &.is-focus { box-shadow: 0 0 0 2px #2c5364; }
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #203a43, #2c5364);
  border: none;

  &:hover { background: linear-gradient(135deg, #2c5364, #4fd1c5); }
}

@media (max-width: 900px) {
  .auth-brand { display: none; }
  .auth-form-side { width: 100%; }
}
</style>
