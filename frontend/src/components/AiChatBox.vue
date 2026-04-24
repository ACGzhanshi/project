<template>
  <div class="ai-chat-wrapper">
    <div class="chat-fab" @click="isOpen = !isOpen" v-if="!isOpen">
      <el-icon :size="24" color="#fff"><ChatDotRound /></el-icon>
      <span class="fab-text">AI 顾问</span>
    </div>

    <div
      class="chat-panel"
      v-show="isOpen"
      ref="chatPanelRef"
      :style="{ left: position.x + 'px', top: position.y + 'px' }"
    >
      <div class="chat-header" @mousedown="startDrag">
        <span style="font-weight: bold; color: #fff;">志愿填报 AI 顾问</span>
        <el-icon @mousedown.stop @click.stop="isOpen = false" class="close-icon"><Close /></el-icon>
      </div>

      <div class="chat-messages" ref="msgContainer">
        <div v-for="(msg, index) in messageList" :key="index" :class="['msg-bubble', msg.role]">
          <div class="msg-content">{{ msg.content }}</div>
        </div>
        <div v-if="loading" class="msg-bubble ai loading">
          <div class="msg-content">AI 正在思考...</div>
        </div>
      </div>

      <div class="chat-input-area">
        <el-input
          v-model="inputText"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 4 }"
          resize="none"
          placeholder="提问... (Enter 发送，Shift+Enter 换行)"
          @keydown.enter.exact.prevent="sendMessage"
          @keydown.enter.shift.exact="() => {}"
          :disabled="loading"
          class="custom-textarea"
        />
        <el-button @click="sendMessage" :loading="loading" type="primary" class="send-btn">
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { ChatDotRound, Close } from '@element-plus/icons-vue'
import { sendAiChat } from '@/api/recommendation'

const props = defineProps({
  pageContext: { type: String, default: '' }
})

const isOpen = ref(false)
const loading = ref(false)
const inputText = ref('')
const messageList = ref([
  { role: 'ai', content: '您好！我是您的专属志愿填报顾问。您可以向我询问关于当前院校或志愿填报的任何问题。你可以拖动我的头部，也可以拖拽我的右下角来调整我的大小哦！' }
])
const msgContainer = ref(null)

// ================= 🚀 核心逻辑 1：自由拖拽 =================
const chatPanelRef = ref(null)
const position = ref({ x: 0, y: 0 }) // 面板的绝对坐标
const isDragging = ref(false)
let dragOffset = { x: 0, y: 0 }      // 鼠标点击位置距离面板左上角的偏差

// 组件挂载时，根据用户屏幕分辨率，将对话框默认放置在右下角
onMounted(() => {
  position.value = {
    x: Math.max(20, window.innerWidth - 420), // 靠右
    y: Math.max(20, window.innerHeight - 600) // 靠下
  }
})

const startDrag = (e) => {
  isDragging.value = true
  // 记录鼠标按下时的相对位置偏差
  dragOffset.x = e.clientX - position.value.x
  dragOffset.y = e.clientY - position.value.y

  // 将监听器绑定在 document 上，防止鼠标移动过快脱离面板导致拖拽断开
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

const onDrag = (e) => {
  if (!isDragging.value) return

  // 计算新坐标
  let newX = e.clientX - dragOffset.x
  let newY = e.clientY - dragOffset.y

  // 边界保护：防止面板被完全拖拽出屏幕边缘找不回来
  const panelWidth = chatPanelRef.value?.offsetWidth || 380
  const panelHeight = chatPanelRef.value?.offsetHeight || 550

  newX = Math.max(0, Math.min(newX, window.innerWidth - panelWidth))
  newY = Math.max(0, Math.min(newY, window.innerHeight - panelHeight))

  position.value = { x: newX, y: newY }
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}
// ==========================================================

const scrollToBottom = async () => {
  await nextTick()
  if (msgContainer.value) {
    msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!inputText.value.trim() || loading.value) return

  const userMsg = inputText.value
  messageList.value.push({ role: 'user', content: userMsg })
  inputText.value = ''
  scrollToBottom()

  loading.value = true
  try {
    const res = await sendAiChat({
      message: userMsg,
      context: props.pageContext
    })

    if (res.code === 200) {
      messageList.value.push({ role: 'ai', content: res.data.reply })
    } else {
      messageList.value.push({ role: 'ai', content: '抱歉，服务出现了一点问题。' })
    }
  } catch (error) {
    messageList.value.push({ role: 'ai', content: '网络连接失败，请稍后再试。' })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
.ai-chat-wrapper {
  z-index: 9999;
}

/* 唤醒按钮依然固定在右下角 */
.chat-fab {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: linear-gradient(135deg, #1890ff, #36cfc9);
  border-radius: 30px;
  padding: 10px 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
  transition: transform 0.2s;
  z-index: 9999;
}
.chat-fab:hover { transform: scale(1.05); }
.fab-text { color: #fff; font-weight: bold; }

/* 🚀 核心优化 2：绝对定位 + CSS原生改变大小属性 */
.chat-panel {
  position: fixed; /* 必须使用 fixed 脱离文档流 */
  width: 380px;
  height: 550px;
  min-width: 300px; /* 限制缩小的下限 */
  min-height: 400px;
  max-width: 90vw;  /* 限制放大的上限 */
  max-height: 90vh;
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(0,0,0,0.25); /* 加深阴影使其浮在最上层 */
  background: #fff;
  display: flex;
  flex-direction: column;

  /* 神奇的 CSS：这两句代码直接开启浏览器的右下角拉伸功能 */
  resize: both;
  overflow: hidden;
  z-index: 10000;
}

.chat-header {
  background: linear-gradient(135deg, #1890ff, #36cfc9);
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: grab; /* 鼠标悬停显示“可抓取”手势 */
  user-select: none; /* 防止拖拽时误选中文本 */
}
.chat-header:active {
  cursor: grabbing; /* 鼠标按下时变成“紧紧抓取”手势 */
}

.close-icon {
  cursor: pointer;
  color: #fff;
  font-size: 18px;
  transition: transform 0.2s;
}
.close-icon:hover { transform: scale(1.2); }

.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.msg-bubble {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}
.msg-bubble.user { align-self: flex-end; background-color: #1890ff; color: #fff; border-bottom-right-radius: 0; }
.msg-bubble.ai { align-self: flex-start; background-color: #fff; color: #333; border: 1px solid #e4e7ed; border-bottom-left-radius: 0; }
.msg-bubble.loading { color: #909399; font-style: italic; }

.chat-input-area {
  padding: 12px;
  padding-right: 20px; /* 给右下角的伸缩手柄留出一点空间 */
  border-top: 1px solid #ebeef5;
  background: #fff;
  display: flex;
  align-items: flex-end;
  gap: 8px;
}
.custom-textarea {
  flex: 1;
}
:deep(.el-textarea__inner::-webkit-resizer) {
  display: none;
}
.send-btn {
  margin-bottom: 2px;
}
</style>