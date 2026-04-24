<template>
  <div class="page-card">
    <div class="page-header"><span class="page-title">模型训练</span></div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="name" label="模型名称" min-width="160" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType[row.status]" size="small">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="accuracy" label="准确率" width="100">
        <template #default="{ row }">{{ row.accuracy ? row.accuracy + '%' : '-' }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" text size="small" :loading="row._training" @click="handleTrain(row)">
            {{ row.status === 'training' ? '训练中' : '开始训练' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTrainList, startTrain } from '@/api/system'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const list = ref([])
const statusType = { pending: 'info', training: 'warning', success: 'success', failed: 'danger' }

async function fetchList() {
  loading.value = true
  try {
    const res = await getTrainList()
    list.value = (res.results || res.data || []).map(i => ({ ...i, _training: false }))
  } catch (e) { /* ignore */ }
  finally { loading.value = false }
}

async function handleTrain(row) {
  row._training = true
  try {
    const res = await startTrain(row.id)
    ElMessage.success(res.message || '训练已启动')
    setTimeout(fetchList, 2000)
  } catch (e) { /* ignore */ }
  finally { row._training = false }
}

onMounted(fetchList)
</script>
