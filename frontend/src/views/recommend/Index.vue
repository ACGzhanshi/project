<template>
  <div>
    <div class="page-card">
      <div class="page-header"><span class="page-title">智能推荐</span></div>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px" style="max-width:500px">
        <el-form-item label="高考分数" prop="score">
          <el-input-number v-model="form.score" :min="100" :max="750" />
        </el-form-item>
        <el-form-item label="省份" prop="province">
          <el-select v-model="form.province" placeholder="请选择高考省份" filterable style="width: 100%;">
            <el-option
              v-for="item in provinceList"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="科类" prop="subject_type">
          <el-select v-model="form.subject_type" placeholder="请选择您的科类" clearable style="width: 100%;">
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
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleMatch">开始推荐</el-button>
          <el-button @click="handleAiAnalyze" :loading="aiLoading" :disabled="!hasResult">AI分析</el-button>
        </el-form-item>
      </el-form>
    </div>

    <template v-if="hasResult">
      <div class="page-card" v-for="(items, level) in result" :key="level">
        <div class="page-header">
          <span class="page-title">
            <el-tag :type="levelTag[level]?.type" size="large">{{ levelTag[level]?.label }}</el-tag>
          </span>
        </div>
        <el-table :data="items" stripe size="small" row-key="university_id">
          <el-table-column type="expand">
            <template #default="{ row }">
              <div style="padding:8px 48px">
                <el-table :data="row.majors || []" size="small" :show-header="true">
                  <el-table-column prop="major_name" label="专业名称" min-width="140" />
                  <el-table-column prop="category" label="学科门类" width="90" />
                  <el-table-column
                    prop="discipline_eval"
                    label="学科评估"
                    width="100"
                    align="center"
                    sortable
                    :sort-method="sortEval"
                  >
                    <template #default="{ row: m }">
                      <el-tag
                        v-if="m.discipline_eval"
                        :type="m.discipline_eval.includes('A') ? 'danger' : 'primary'"
                        size="small"
                        effect="dark"
                      >
                        {{ m.discipline_eval }}
                      </el-tag>
                      <span v-else>-</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="录取概率" width="140">
                    <template #default="{ row: m }">
                      <el-progress :percentage="m.probability" :stroke-width="12" :color="levelTag[level]?.color" />
                    </template>
                  </el-table-column>
                  <el-table-column label="就业率" width="80" align="center">
                    <template #default="{ row: m }">{{ m.employment_rate ? m.employment_rate + '%' : '-' }}</template>
                  </el-table-column>
                  <el-table-column label="薪资" width="80" align="center">
                    <template #default="{ row: m }">{{ m.avg_salary ? '¥' + m.avg_salary : '-' }}</template>
                  </el-table-column>
                </el-table>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="university_name" label="院校" min-width="160" />
          <el-table-column prop="province" label="省份" width="80" />
          <el-table-column label="标签" width="150">
            <template #default="{ row }">
              <el-tag v-if="row.is_985" size="small" type="danger">985</el-tag>
              <el-tag v-if="row.is_211" size="small" type="warning">211</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="avg_min_score" label="近年均分" width="100" />
          <el-table-column label="院校录取概率" width="140">
            <template #default="{ row }">
              <el-progress :percentage="row.probability" :stroke-width="14" :color="levelTag[level]?.color" />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </template>

    <div class="page-card" v-if="aiResult">
      <div class="page-header"><span class="page-title">AI 智能分析</span></div>
      <div style="white-space:pre-wrap;line-height:1.8">{{ aiResult }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { smartMatch, aiAnalyze } from '@/api/recommendation'
import { ElMessage } from 'element-plus'
import { provinceList } from '@/utils/validate'

const formRef = ref()
const loading = ref(false)
const aiLoading = ref(false)
const result = ref({})
const aiResult = ref('')

const form = reactive({ score: 600, province: '', subject_type: '物理类' })

const rules = {
  score: [{ required: true, message: '请输入分数', trigger: 'blur' }],
  province: [{ required: true, message: '请输入省份', trigger: 'blur' }],
  subject_type: [{ required: true, message: '请选择科类', trigger: 'change' }]
}

const levelTag = {
  rush: { label: '冲刺院校', type: 'danger', color: '#f56c6c' },
  stable: { label: '稳妥院校', type: 'warning', color: '#e6a23c' },
  safe: { label: '保底院校', type: 'success', color: '#67c23a' }
}
const hasResult = computed(() => Object.keys(result.value).length > 0)

// 🚀 新增：学科等级权重逻辑
const evalWeight = {
  'A+': 9, 'A': 8, 'A-': 7,
  'B+': 6, 'B': 5, 'B-': 4,
  'C+': 3, 'C': 2, 'C-': 1
}

const sortEval = (a, b) => {
  const weightA = evalWeight[a.discipline_eval] || 0
  const weightB = evalWeight[b.discipline_eval] || 0
  return weightA - weightB
}

async function handleMatch() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await smartMatch(form)
    if (res.code === 200) {
      result.value = res.data
      ElMessage.success('推荐完成')
    }
  } catch (e) { }
  finally { loading.value = false }
}

async function handleAiAnalyze() {
  aiLoading.value = true
  try {
    const res = await aiAnalyze({ score: form.score, province: form.province, recommendations: result.value })
    if (res.code === 200) aiResult.value = res.data.analysis
  } catch (e) { /* ignore */ }
  finally { aiLoading.value = false }
}
</script>