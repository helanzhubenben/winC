# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 通用要求
- 代码注释以函数为单位进行注释，注释必须清晰。
- 代码文件开头必须由代码总体描述注释


## 项目概述

这是一个 **Fishpool 客户池管理系统**，用于 B2B 销售团队管理客户关系。系统采用前后端分离架构，实现客户三维评分（客户潜力、竞争环境、关键人关系）和自动分级功能。

## 技术栈

### Backend
- Django 5.0.3 + Django REST Framework 3.15.1
- 数据库：SQLite3（开发）/ MySQL 8.0（生产）
- Python 虚拟环境：`backend/.venv`

### Frontend
- Vue 3（组合式 API）+ Vite 5
- Element Plus + ECharts（数据可视化）
- 开发端口：5173，API 代理到 localhost:8000

## 常用命令

### Backend 开发

```bash
# 进入后端目录
cd backend

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 运行开发服务器（http://127.0.0.1:8000）
python manage.py runserver
```

### Frontend 开发

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 运行开发服务器（http://localhost:5173）
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 核心架构

### 数据模型

**Customer（客户）** - 核心实体
- 三维评分：`score_x`（客户潜力）、`score_y`（竞争环境）、`score_z`（关键人关系）
- 自动分级：`level` 字段（A/B/C/D），基于评分规则自动计算
- 业务字段：`business_model`（Hunting/Farming）、`area`、`city`、`client_strategy`、`potential_contribution`

**Contact（联系人）** - 关联实体
- 外键关联到 Customer
- `is_key_person` 标记关键联系人

### 客户等级规则（在 `frontend/src/utils/level.js` 中实现）

- **Level A**: X≥70 且 Y≥70 且 Z≥70（三项都高）
- **Level B**: 至少两项≥70
- **Level C**: X≥70（客户潜力高）
- **Level D**: 其他情况

### API 架构

RESTful API 设计，主要端点：

```
/api/customers/              # 客户 CRUD + 列表筛选
/api/customers/{id}/         # 客户详情
/api/customers/statistics/   # 统计数据（按等级/区域/业务模式）
/api/contacts/               # 联系人 CRUD
```

**筛选参数**：`level`、`area`、`city`、`business_model`、`status`、`search`、`ordering`

### 前端路由结构

```
/                           # 客户列表页（CustomerListPage.vue）
/customer/:id               # 客户详情页（CustomerDetailPage.vue）
```

### 组件架构

- **页面组件**（`views/`）：CustomerListPage、CustomerDetailPage
- **业务组件**（`components/`）：CustomerForm、CustomerDialog、ContactForm、ContactDialog
- **API 层**（`api/`）：customer.js、contact.js - 封装 Axios 请求
- **工具函数**（`utils/`）：level.js - 客户等级计算逻辑

## 开发注意事项

1. **语言**：所有界面文本使用中文，Element Plus 已配置中文语言包
2. **CORS**：后端已配置允许跨域，前端通过 Vite 代理访问 API
3. **数据库**：开发环境使用 SQLite（`backend/db.sqlite3`），生产环境需切换到 MySQL
4. **虚拟环境**：后端开发必须激活虚拟环境（`.venv`）
5. **前后端联调**：确保后端服务（8000 端口）先启动，再启动前端（5173 端口）

## 项目文档

- `backend/README.md` - 后端详细文档
- `frontend/README.md` - 前端详细文档
- `Fishpool客户池需求.md` - 核心功能需求
- `功能扩展-营收数据和跟进追踪.md` - 扩展功能规划
