# 基于机器学习的高考志愿智能推荐平台

## 一、项目概述

本系统是一个面向高考考生的志愿填报辅助平台，基于 Django + Vue 3 前后端分离架构，结合历年录取数据与机器学习算法，为考生提供院校查询、专业查询、智能推荐、专业倾向测评、志愿填报管理等功能。系统支持多角色（高考生、教师、家长、数据管理员、系统管理员），并提供数据采集、模型训练等后台管理能力。

## 二、技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue 3 + Composition API | 3.4 |
| UI 组件库 | Element Plus | 2.7 |
| 前端构建 | Vite | 5.2 |
| 状态管理 | Pinia | 2.1 |
| 图表 | ECharts + vue-echarts | 5.5 |
| 后端框架 | Django + Django REST Framework | 4.2 / 3.15 |
| 认证 | JWT (djangorestframework-simplejwt) | 5.3 |
| 数据库 | MySQL 8.0 / SQLite（开发） | - |
| 大数据处理 | PySpark | 3.5 |
| 机器学习 | scikit-learn、NumPy、Pandas | 1.5 / 1.26 / 2.2 |
| AI 分析 | 通义千问 API (qwen-turbo) | - |

## 三、项目结构

```
gaokao_zhiyuan/
├── backend/                          # Django 后端
│   ├── config/                       # 项目配置
│   │   ├── settings.py               # Django 配置（数据库、JWT、CORS等）
│   │   ├── urls.py                   # 主路由
│   │   └── wsgi.py                   # WSGI 入口
│   ├── apps/                         # 业务模块
│   │   ├── users/                    # 用户管理（注册、登录、JWT认证、角色管理）
│   │   ├── universities/             # 院校数据（院校、专业、分数线、招生计划）
│   │   ├── recommendation/           # 智能推荐（冲稳保推荐、专业测评、AI分析）
│   │   ├── volunteer/                # 志愿填报（志愿表管理、志愿项CRUD）
│   │   ├── crawler/                  # 数据采集（爬虫任务管理、模拟爬取）
│   │   └── system/                   # 系统管理（日志、权限、配置、模型训练）
│   ├── spark_jobs/                   # Spark 大数据处理
│   │   └── data_clean.py            # 数据清洗、趋势分析、特征构建
│   ├── init_data.py                  # 演示数据初始化脚本
│   ├── manage.py                     # Django 管理脚本
│   └── requirements.txt              # Python 依赖
├── frontend/                         # Vue 3 前端
│   ├── src/
│   │   ├── api/                      # API 接口封装
│   │   ├── layout/                   # 布局组件（侧边栏+顶栏）
│   │   ├── router/                   # 路由配置
│   │   ├── stores/                   # Pinia 状态管理
│   │   ├── styles/                   # 全局样式
│   │   ├── utils/                    # 工具函数（axios封装）
│   │   └── views/                    # 页面组件
│   │       ├── Login.vue             # 登录页
│   │       ├── Register.vue          # 注册页
│   │       ├── Dashboard.vue         # 首页概览
│   │       ├── Profile.vue           # 个人中心
│   │       ├── university/           # 院校查询、院校详情
│   │       ├── major/                # 专业查询
│   │       ├── recommend/            # 智能推荐、专业测评
│   │       ├── volunteer/            # 志愿填报、志愿详情
│   │       └── admin/                # 管理后台（用户、日志、爬虫、模型）
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
└── README.md
```

## 四、功能模块说明

### 4.1 用户管理模块

- 支持五种角色：高考生、教师、家长、数据管理员、系统管理员
- JWT Token 认证，access_token 有效期 1 天，refresh_token 7 天
- 注册、登录、个人信息修改、密码修改
- 管理员可管理用户（启用/禁用、重置密码）

### 4.2 院校查询模块

- 院校列表：支持按省份、层次、类型、985/211/双一流筛选，支持名称搜索
- 院校详情：展示院校基本信息、开设专业、近年录取分数线
- 院校对比：选择多所院校进行数据对比
- 省份列表接口：动态获取有数据的省份

### 4.3 专业查询模块

- 专业列表：支持按专业名称/代码搜索、按学科门类和所属院校筛选
- 专业详情：弹窗展示专业代码、学制、学位、就业率、平均薪资、简介等

### 4.4 智能推荐模块

- 冲稳保推荐：输入分数、省份、科类，基于历年录取分数线计算录取概率，按冲（20%-45%）、稳（45%-75%）、保（75%+）三个梯度推荐院校
- 录取概率算法：基于用户分数与院校近三年平均最低分的差值，通过分段函数计算概率
- AI 智能分析：调用通义千问 API 对推荐方案进行专业点评和风险提示
- 推荐历史：记录每次推荐结果，支持回溯查看

### 4.5 专业倾向测评模块

- 10 道测评题目，覆盖逻辑思维、艺术创造、商业管理、社会服务、自然探索、语言表达六个维度
- 提交后计算各维度得分，确定最强倾向维度
- 根据测评结果匹配数据库中对应学科门类的院校和专业（最多15条），展示院校名称、985/211标签、专业名、就业率、薪资等

### 4.6 志愿填报模块

- 创建志愿表：填写分数、省份、科类
- 添加志愿项：选择院校和专业，设置志愿序号和冲稳保等级
- 志愿表状态管理：草稿 → 已提交 → 已分析
- 志愿分析：对志愿表进行梯度合理性分析

### 4.7 数据采集模块（管理员）

- 爬虫任务管理：查看任务列表、启动任务、停止任务、查看运行日志
- 支持院校信息采集和分数线数据采集两种任务类型
- 任务状态实时轮询更新（等待中 → 运行中 → 成功/失败）
- 爬取数据存储为原始数据 + 清洗后数据

### 4.8 系统管理模块（管理员）

- 操作日志：记录用户操作行为，支持按用户、操作类型、模块筛选
- 数据权限：按角色配置各模块的查看、编辑、删除、导出权限
- 系统配置：站点名称、最大志愿数、当前高考年份等可配置项
- 模型训练：启动推荐模型训练，查看训练日志和准确率

### 4.9 Spark 大数据处理模块

- 分数线数据清洗：去空值、去重、范围校验、字段标准化
- 分数线趋势分析：按院校+省份+科类聚合，计算平均分、最低分、最高分
- 推荐特征构建：聚合多年数据生成推荐模型输入特征

## 五、数据库设计

### 核心数据表

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| users | 用户表 | username, role, phone, province, score, subject_type, subjects |
| universities | 院校表 | name, code, province, level, type, is_985, is_211, ranking, employment_rate |
| majors | 专业表 | university_id(FK), name, code, category, duration, degree, employment_rate, avg_salary |
| admission_scores | 录取分数线 | university_id(FK), major_id(FK), year, province, subject_type, min_score, min_rank |
| enrollment_plans | 招生计划 | university_id(FK), major_id(FK), year, province, plan_count, tuition |
| recommend_records | 推荐记录 | user_id(FK), university_id(FK), level(冲/稳/保), probability |
| assessment_questions | 测评题目 | content, option_a/b/c/d, category(维度) |
| assessment_results | 测评结果 | user_id(FK), answers(JSON), result(JSON), recommended_majors |
| volunteer_forms | 志愿表 | user_id(FK), name, score, province, status |
| volunteer_items | 志愿项 | form_id(FK), order, university_id(FK), major_id(FK), level, probability |
| crawler_tasks | 爬虫任务 | name, task_type, status, total_count, success_count, log |
| crawler_data | 爬取数据 | task_id(FK), data_type, raw_data(JSON), cleaned_data(JSON) |
| operation_logs | 操作日志 | user_id(FK), action, module, detail, ip_address |
| data_permissions | 数据权限 | role, module, can_view, can_edit, can_delete, can_export |
| system_configs | 系统配置 | key, value, description |
| model_train_logs | 模型训练日志 | name, status, accuracy, params(JSON), log |

## 六、API 接口一览

### 用户认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/users/auth/register/ | 用户注册 |
| POST | /api/users/auth/login/ | 用户登录 |
| GET | /api/users/auth/info/ | 获取当前用户信息 |
| PUT | /api/users/auth/update_profile/ | 更新个人信息 |
| POST | /api/users/auth/change_password/ | 修改密码 |

### 院校数据
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/universities/list/ | 院校列表（支持筛选搜索） |
| GET | /api/universities/list/{id}/ | 院校详情 |
| GET | /api/universities/list/compare/ | 院校对比 |
| GET | /api/universities/list/provinces/ | 省份列表 |
| GET | /api/universities/majors/ | 专业列表 |
| GET | /api/universities/scores/ | 分数线列表 |
| GET | /api/universities/scores/trend/ | 分数线趋势 |
| GET | /api/universities/plans/ | 招生计划列表 |

### 智能推荐
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/recommendation/recommend/smart_match/ | 智能匹配推荐 |
| POST | /api/recommendation/recommend/ai_analyze/ | AI智能分析 |
| GET | /api/recommendation/recommend/history/ | 推荐历史 |
| GET | /api/recommendation/assessment/questions/ | 获取测评题目 |
| POST | /api/recommendation/assessment/submit/ | 提交测评 |
| GET | /api/recommendation/assessment/my_results/ | 我的测评结果 |

### 志愿填报
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | /api/volunteer/forms/ | 志愿表列表/创建 |
| GET/PUT/DELETE | /api/volunteer/forms/{id}/ | 志愿表详情/修改/删除 |
| GET/POST | /api/volunteer/items/ | 志愿项列表/创建 |

### 数据采集
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/crawler/tasks/ | 任务列表 |
| POST | /api/crawler/tasks/{id}/start/ | 启动任务 |
| POST | /api/crawler/tasks/{id}/stop/ | 停止任务 |
| GET | /api/crawler/tasks/{id}/logs/ | 查看任务日志 |

### 系统管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/system/dashboard/overview/ | 仪表盘概览 |
| GET | /api/system/dashboard/score_distribution/ | 分数分布统计 |
| GET | /api/system/logs/ | 操作日志列表 |
| GET/PUT | /api/system/permissions/ | 数据权限管理 |
| GET/PUT | /api/system/configs/ | 系统配置管理 |
| GET | /api/system/model-train/ | 模型训练列表 |
| POST | /api/system/model-train/{id}/start_train/ | 启动模型训练 |

## 七、环境搭建与运行

### 7.1 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0（生产环境）或 SQLite（开发环境）

### 7.2 后端启动

```bash
# 进入后端目录
cd gaokao_zhiyuan/backend

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py makemigrations users universities recommendation volunteer crawler system
python manage.py migrate

# 初始化演示数据
python init_data.py

# 启动开发服务器（端口8090）
python manage.py runserver 8090
```

### 7.3 前端启动

```bash
# 进入前端目录
cd gaokao_zhiyuan/frontend

# 安装依赖
npm install

# 启动开发服务器（端口5180）
npm run dev
```

### 7.4 访问地址

- 前端页面：http://localhost:5180/
- 后端API：http://127.0.0.1:8090/api/
- 前端已配置代理，`/api` 请求自动转发到后端 8090 端口

### 7.5 数据库配置

开发环境默认使用 SQLite，生产环境切换 MySQL 需修改 `backend/config/settings.py` 中的 `DATABASES` 配置：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gaokao_zhiyuan',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

## 八、测试账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 高考生 | student1 | 123456 | 广东考生，620分，物理类 |
| 高考生 | student2 | 123456 | 北京考生，580分，物理类 |
| 高考生 | student3 | 123456 | 浙江考生，650分，物理类 |
| 教师 | teacher1 | 123456 | 广东教师 |
| 家长 | parent1 | 123456 | 北京家长 |
| 数据管理员 | dataadmin | 123456 | 可管理数据采集和模型训练 |
| 系统管理员 | sysadmin | 123456 | 拥有全部权限 |

## 九、推荐算法说明

### 录取概率计算

系统基于考生分数与目标院校近三年平均最低录取分数的差值，通过分段函数计算录取概率：

| 分差范围 | 概率计算公式 | 概率区间 |
|----------|-------------|----------|
| ≥ 30分 | 80 + diff × 0.5 | 80% - 95% |
| 10 ~ 30分 | 60 + diff × 1.0 | 70% - 90% |
| 0 ~ 10分 | 40 + diff × 2.0 | 40% - 60% |
| -10 ~ 0分 | 20 + diff × 2.0 | 0% - 40% |
| -30 ~ -10分 | 10 + diff × 0.5 | 5% - 15% |
| < -30分 | 5 + diff × 0.1 | 2% - 5% |

### 推荐梯度划分

- 冲刺院校（rush）：录取概率 20% - 45%
- 稳妥院校（stable）：录取概率 45% - 75%
- 保底院校（safe）：录取概率 ≥ 75%

每个梯度最多推荐 10 所院校，按录取概率降序排列。

### 专业倾向测评

测评覆盖六个维度，每个维度对应推荐的学科门类：

| 测评维度 | 推荐学科门类 | 推荐专业方向 |
|----------|-------------|-------------|
| 逻辑思维 | 工学、理学 | 计算机科学与技术、数学、物理学 |
| 语言表达 | 文学、法学 | 汉语言文学、新闻学、法学 |
| 艺术创造 | 艺术学、文学 | 设计学、美术学、音乐学 |
| 社会服务 | 医学、教育学 | 医学、教育学、社会工作 |
| 商业管理 | 管理学、经济学 | 工商管理、金融学、市场营销 |
| 自然探索 | 理学、农学 | 生物科学、环境科学、地理学 |

## 十、角色权限说明

| 功能模块 | 高考生 | 教师 | 家长 | 数据管理员 | 系统管理员 |
|----------|--------|------|------|-----------|-----------|
| 首页概览 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 院校查询 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 专业查询 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 智能推荐 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 专业测评 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 志愿填报 | ✓ | - | - | - | ✓ |
| 用户管理 | - | - | - | - | ✓ |
| 操作日志 | - | - | - | - | ✓ |
| 数据采集 | - | - | - | ✓ | ✓ |
| 模型训练 | - | - | - | ✓ | ✓ |
