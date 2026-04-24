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
        <h1 class="brand-slogan">数据驱动，科学填报</h1>
        <p class="brand-desc">基于历年录取数据与机器学习算法，为你提供精准的院校推荐和志愿填报方案</p>
        <div class="brand-features">
          <div class="feature-item">
            <div class="feature-dot"></div>
            <span>覆盖全国 2800+ 院校数据</span>
          </div>
          <div class="feature-item">
            <div class="feature-dot"></div>
            <span>智能冲稳保梯度推荐</span>
          </div>
          <div class="feature-item">
            <div class="feature-dot"></div>
            <span>专业兴趣测评匹配</span>
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
          <h2>欢迎回来</h2>
          <p>登录你的账号以继续使用</p>
        </div>
        <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleLogin" size="large">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" :prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" :prefix-icon="Lock" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" class="submit-btn" @click="handleLogin">登 录</el-button>
          </el-form-item>
        </el-form>
        <div class="form-footer">
          还没有账号？<router-link to="/register">立即注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await userStore.login(form)
    if (res.code === 200) {
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      ElMessage.error(res.message || '登录失败')
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

  svg {
    width: 42px;
    height: 42px;
    flex-shrink: 0;
  }

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

.deco-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  right: -100px;
}

.deco-2 {
  width: 300px;
  height: 300px;
  bottom: -80px;
  left: -60px;
}

.deco-3 {
  width: 200px;
  height: 200px;
  bottom: 20%;
  right: 10%;
  background: rgba(79, 209, 197, 0.05);
}

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
  margin-top: 20px;

  a {
    color: #2c5364;
    text-decoration: none;
    font-weight: 500;

    &:hover {
      color: #4fd1c5;
    }
  }
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e2e8f0;
  padding: 4px 12px;

  &:hover {
    box-shadow: 0 0 0 1px #cbd5e0;
  }

  &.is-focus {
    box-shadow: 0 0 0 2px #2c5364;
  }
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #203a43, #2c5364);
  border: none;

  &:hover {
    background: linear-gradient(135deg, #2c5364, #4fd1c5);
  }
}

@media (max-width: 900px) {
  .auth-brand {
    display: none;
  }

  .auth-form-side {
    width: 100%;
  }
}
</style>
