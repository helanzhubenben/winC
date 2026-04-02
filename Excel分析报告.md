# 销售周报Excel文件分析报告

## 文件概况

**文件名**: ★ 2026Fish Pool & Weekly report-Timothee.xlsx  
**工作表数量**: 9个  
**分析日期**: 2026-04-01

---

## 工作表列表

1. **使用说明** - 使用指南和说明文档
2. **General-Fishpool** - 客户池/潜在客户数据库 (341行)
3. **Weekly Report** - 周报任务跟踪 (35行)
4. **Weekly Travel Plan** - 出差计划 (2024年)
5. **Weekly Travel Plan (2)** - 出差计划 (2025年)
6. **2026Weekly Travel Plan (3)** - 出差计划 (2026年)
7. **M & S Key-Customers** - 关键客户管理
8. **Top Clients** - 顶级客户信息
9. **Weekly Travel Plan** - 出差计划汇总

---

## 核心工作表详细分析

### 1. General-Fishpool (客户池)

**规模**: 341行 × 16列

**数据结构**:

#### 基本信息区
- Nr. (编号)
- Update (更新日期)
- Client (客户名称)
- Business Model (业务模式: Farming/Hunting)
- Area (区域: East Region, South Region等)
- Address (地址)

#### 客户潜力评估 (Leveling System)
- **Level A**: X级, Y级, Z级 - 最高级别客户
- **Level B**: X级, Y级 或 Z级 - 中高级别
- **Level C**: X级, Y级, Z级 - 中级
- **Level D**: X级, Y级, Z级 - 初级

#### 评分维度
- **Description (X)**: 客户描述和业务情况
- **Score X**: 客户潜力评分 (0-100)
- **Competition Surrounding (Y)**: 竞争环境分析
- **Score Y**: 竞争评分 (0-100)
- **Key Person (Z)**: 关键联系人信息
- **Score Z**: 关系评分 (0-100)

#### 战略信息
- Level: 综合等级 (A/B/C/D)
- Client Strategy: 客户策略
- Potential Contribution (KEUR/year): 年度潜在贡献(千欧元)
- Remark: 备注

**样本客户**:
1. Brembo (Nanjing) - 布雷博南京 (Level A, 250 KEUR/year)
2. Aptiv Electronics (Suzhou) - 安波福苏州 (Level B, 20 KEUR/year)

---

### 2. Weekly Report (周报)

**规模**: 35行 × 14列

**数据结构**:

#### 客户基本信息
- Client (客户名称)
- Area (区域)
- Address (地址)

#### 任务计划
- Tasks (任务类型: Sorting & Rework, Inspection等)
- Definition (任务定义/项目名称)
- Due Date (截止日期)
- Revenue (收入预期)

#### 执行跟踪
- Actions (行动记录/进展)
- Responsibility (负责人)
- Revise date (修订日期)
- Finish Date (完成日期)
- Remark (备注)

**主要客户项目**:
- Brembo (Nanjing) - 多个分拣返工项目
- 上海保隆 (Baolong) - 分拣检验项目

---

### 3. M & S Key-Customers (关键客户)

**规模**: 23行 × 16列

**数据结构**:

#### 客户信息
- Customer (客户名称)
- Level (等级: A/B/C)
- Area (区域)
- Service Type (服务类型)
- Potential distribution (KEUR/year) (潜在收入)

#### 任务计划
- Tasks (任务描述)
- Planed date (Target) (计划日期)
- Due Date (Finish) (完成日期)
- Weekly Status (周状态)

#### 业务指标
- Opportunities (商机数)
- Enquiries (询价数)
- PO or MO (订单数)
- Hit Rate (%) (成功率)

#### 管理信息
- BD Name (商务负责人)
- Remark (备注)
- Corona Virus state & Business View points (疫情状态及业务观点)

**重点客户**:
- HHT (GZ & SZ & SH) - Level A, 25-30K EUR
- Honda-Trading - Level A, 10-12K EUR

---

### 4. Top Clients (顶级客户)

**规模**: 281行 × 大量列

**数据结构**:
- Nr. (编号)
- Update (更新日期)
- Client (客户名称)
- Business Model (Hunting/Farming)
- Area (区域)
- Level (等级)
- Potential Contribution (KEUR/year) (年度潜在贡献)
- Progress (进展)
- Phrasal Objectives (阶段目标)
- State of contract (合同状态)

---

## 客户管理系统需求分析

### 核心功能模块

#### 1. 客户信息管理
- 客户基本信息 (名称、地址、区域、业务模式)
- 客户分级系统 (A/B/C/D)
- 多维度评分 (客户潜力、竞争环境、关键人关系)
- 潜在收入预测

#### 2. 任务/项目管理
- 任务创建和分配
- 任务类型分类 (Sorting, Rework, Inspection等)
- 截止日期跟踪
- 收入预期管理
- 进度跟踪和状态更新

#### 3. 出差计划管理
- 出差日程安排
- 客户拜访记录
- 会议纪要
- 下次拜访计划

#### 4. 业务指标跟踪
- 商机数量
- 询价转化
- 订单成功率
- 收入统计

#### 5. 关键人管理
- 联系人信息
- 关系评分
- 沟通记录

### 数据字段映射

#### 客户表 (Customers)
```
- id (主键)
- name (客户名称)
- business_model (Farming/Hunting)
- area (区域)
- address (地址)
- level (A/B/C/D)
- description (描述)
- score_x (客户潜力评分)
- score_y (竞争评分)
- score_z (关系评分)
- potential_revenue (年度潜在收入)
- strategy (客户策略)
- status (状态)
- created_at
- updated_at
```

#### 联系人表 (Contacts)
```
- id
- customer_id (外键)
- name (姓名)
- position (职位)
- phone (电话)
- email (邮箱)
- relationship_score (关系评分)
- is_key_person (是否关键人)
```

#### 任务/项目表 (Tasks)
```
- id
- customer_id (外键)
- task_type (任务类型)
- definition (任务定义)
- due_date (截止日期)
- revenue (预期收入)
- actions (行动记录)
- responsibility (负责人)
- status (状态: 计划中/进行中/已完成)
- finish_date (完成日期)
- remark (备注)
```

#### 出差计划表 (Travel_Plans)
```
- id
- date (日期)
- time (时间段: AM/PM)
- customer_id (外键)
- location (地点)
- purpose (目的)
- attendees (参会人员)
- mom (会议纪要)
- next_plan (下次计划)
```

#### 业务指标表 (Business_Metrics)
```
- id
- customer_id (外键)
- period (统计周期)
- opportunities (商机数)
- enquiries (询价数)
- orders (订单数)
- hit_rate (成功率)
- actual_revenue (实际收入)
```

---

## 技术建议

### 推荐技术栈

#### 后端
- **框架**: Spring Boot (Java) 或 Django (Python)
- **数据库**: PostgreSQL 或 MySQL
- **API**: RESTful API

#### 前端
- **框架**: Vue.js 3 或 React
- **UI组件**: Element Plus 或 Ant Design
- **状态管理**: Pinia 或 Redux

#### 功能特性
- 用户认证和权限管理
- 数据导入/导出 (Excel)
- 报表生成
- 数据可视化 (图表)
- 搜索和筛选
- 移动端适配

---

## 下一步行动

1. **需求确认**: 与用户确认具体功能需求和优先级
2. **数据库设计**: 详细设计数据库表结构和关系
3. **原型设计**: 设计UI/UX原型
4. **技术选型**: 确定具体的技术栈
5. **开发计划**: 制定开发时间表和里程碑
