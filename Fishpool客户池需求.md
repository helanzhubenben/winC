# Fishpool 客户池管理系统

## 一、功能范围

基于Excel工作表"General-Fishpool"，实现客户池管理的核心功能。

---

## 二、数据库设计

### 2.1 客户表 (customers)

```sql
CREATE TABLE customers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- 基本信息
    client_name VARCHAR(200) NOT NULL COMMENT '客户名称',
    business_model VARCHAR(20) COMMENT '业务模式: Hunting/Farming',
    area VARCHAR(100) COMMENT '区域（East Region, South Region等）',
    city VARCHAR(100) COMMENT '城市',
    address TEXT COMMENT '详细地址',
    
    -- X轴：客户潜力
    description_x TEXT COMMENT '客户描述',
    score_x INT DEFAULT 0 COMMENT '客户潜力评分 0-100',
    
    -- Y轴：竞争环境
    description_y TEXT COMMENT '竞争环境描述',
    score_y INT DEFAULT 0 COMMENT '竞争评分 0-100',
    
    -- Z轴：关键人关系
    key_person VARCHAR(200) COMMENT '关键联系人',
    score_z INT DEFAULT 0 COMMENT '关系评分 0-100',
    
    -- 分级和战略
    level VARCHAR(1) COMMENT '客户等级: A/B/C/D',
    client_strategy TEXT COMMENT '客户策略',
    potential_contribution DECIMAL(10,2) COMMENT '年度潜在贡献(KEUR)',
    
    remark TEXT COMMENT '备注',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_level (level),
    INDEX idx_area (area),
    INDEX idx_city (city),
    INDEX idx_business_model (business_model)
) COMMENT='客户信息表';
```

### 2.2 联系人表 (contacts)

```sql
CREATE TABLE contacts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL COMMENT '客户ID',
    
    name VARCHAR(100) NOT NULL COMMENT '姓名',
    position VARCHAR(100) COMMENT '职位',
    phone VARCHAR(50) COMMENT '电话',
    email VARCHAR(100) COMMENT '邮箱',
    is_key_person BOOLEAN DEFAULT FALSE COMMENT '是否关键人',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    INDEX idx_customer (customer_id)
) COMMENT='联系人表';
```

---

## 三、核心功能

### 3.1 客户列表
- 显示所有客户（卡片或表格）
- 搜索客户名称
- 筛选：
  - 按等级（A/B/C/D）
  - 按区域
  - 按业务模式（Farming/Hunting）
- 排序：按等级、按潜在贡献

### 3.2 客户详情
- 查看客户完整信息
- 三维评分雷达图
- 客户等级显示
- 联系人列表

### 3.3 客户新增/编辑
- 录入基本信息
- 设置三维评分（X/Y/Z）
- 自动计算等级
- 添加客户策略

### 3.4 联系人管理
- 添加联系人
- 编辑联系人
- 删除联系人
- 标记关键联系人

### 3.5 Excel导入导出
- 从Excel导入客户数据
- 导出客户数据到Excel

---

## 四、客户等级计算规则

```
Level A: X>=70 AND Y>=70 AND Z>=70 (三项都高)
Level B: 至少两项>=70
Level C: X>=70 (客户潜力高)
Level D: 其他情况
```

---

## 五、API接口

```
# 客户管理
GET    /api/customers              # 客户列表（支持筛选）
GET    /api/customers/{id}         # 客户详情
POST   /api/customers              # 创建客户
PUT    /api/customers/{id}         # 更新客户
DELETE /api/customers/{id}         # 删除客户

# 联系人管理
GET    /api/customers/{id}/contacts    # 联系人列表
POST   /api/customers/{id}/contacts    # 添加联系人
PUT    /api/contacts/{id}              # 更新联系人
DELETE /api/contacts/{id}              # 删除联系人

# 数据导入导出
POST   /api/customers/import       # 导入Excel
GET    /api/customers/export       # 导出Excel

# 统计
GET    /api/customers/statistics   # 客户统计
```

---

## 六、前端页面

### 6.1 客户列表页 (`/customers`)
- 顶部：搜索框 + 筛选器 + 新增按钮
- 主体：客户卡片列表
  - 客户名称
  - 等级徽章（A红/B蓝/C绿/D灰）
  - 区域
  - 三维评分（小雷达图）
  - 潜在贡献
  - 操作按钮
- 底部：分页

### 6.2 客户详情页 (`/customers/{id}`)
- 基本信息卡片
- 三维评分雷达图
- 客户策略
- 联系人列表
- 编辑/删除按钮

### 6.3 客户表单（对话框）
- 客户名称
- 业务模式（Farming/Hunting）
- 区域、地址
- X轴描述 + 评分（0-100滑块）
- Y轴描述 + 评分（0-100滑块）
- Z轴关键人 + 评分（0-100滑块）
- 客户策略
- 潜在贡献
- 自动显示计算的等级

---

## 七、技术选型

### 方案A：快速开发（推荐）
- **后端**: Django 5 + Django REST Framework
- **前端**: Vue.js 3 + Element Plus
- **数据库**: MySQL 8.0
- **开发时间**: 2周

### 方案B：企业级
- **后端**: Spring Boot 3
- **前端**: React 18 + Ant Design
- **数据库**: PostgreSQL
- **开发时间**: 3周

---

## 八、开发计划

### Week 1：后端开发
- [ ] 创建Django/Spring Boot项目
- [ ] 创建数据库表
- [ ] 实现客户CRUD API
- [ ] 实现联系人API
- [ ] 实现Excel导入导出
- [ ] API测试

### Week 2：前端开发
- [ ] 创建Vue/React项目
- [ ] 客户列表页面
- [ ] 客户详情页面
- [ ] 客户表单（新增/编辑）
- [ ] 三维评分雷达图
- [ ] 联系人管理
- [ ] Excel导入导出界面
- [ ] 整体测试

---

## 九、下一步

请选择：
1. **技术方案**：方案A（Django+Vue）或 方案B（Spring Boot+React）
2. **是否需要用户登录**：是/否

选好后立即开始创建项目！
