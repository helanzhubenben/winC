# Fishpool 客户池管理系统 - 后端

基于Django和Django REST Framework的客户池管理系统后端API。

## 技术栈

- Django 5.0.3
- Django REST Framework 3.15.1
- MySQL 8.0
- django-cors-headers（跨域支持）
- openpyxl（Excel导入导出）

## 项目结构

```
backend/
├── fishpool/              # Django项目配置
│   ├── __init__.py
│   ├── settings.py       # 项目设置
│   ├── urls.py           # 主路由配置
│   ├── wsgi.py
│   └── asgi.py
├── customers/            # 客户管理应用
│   ├── __init__.py
│   ├── models.py         # 数据模型
│   ├── serializers.py    # 序列化器
│   ├── views.py          # 视图集
│   ├── admin.py          # 后台管理
│   └── apps.py
├── manage.py             # Django管理脚本
└── requirements.txt      # 依赖包列表
```

## 安装步骤

### 1. 创建虚拟环境（推荐）

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv .venv

# Windows 激活
.venv\Scripts\activate

# Linux/Mac 激活
source .venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

**开发环境（推荐使用 SQLite）**

默认配置已使用 SQLite，无需额外配置。数据库文件会自动创建在 `backend/db.sqlite3`。

**生产环境（可选使用 MySQL）**

如需使用 MySQL，请先在 MySQL 中创建数据库：

```sql
CREATE DATABASE fishpool_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

然后修改 `fishpool/settings.py` 中的数据库配置，注释掉 SQLite 配置，取消注释 MySQL 配置：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fishpool_db',
        'USER': 'root',              # 修改为你的MySQL用户名
        'PASSWORD': 'your_password',  # 修改为你的MySQL密码
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```

### 4. 执行数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 创建超级管理员

```bash
python manage.py createsuperuser
```

按提示输入用户名、邮箱和密码。

### 6. 运行开发服务器

```bash
python manage.py runserver
```

服务器将在 http://127.0.0.1:8000/ 启动

## API端点

### 客户管理

- `GET /api/customers/` - 获取客户列表
- `POST /api/customers/` - 创建新客户
- `GET /api/customers/{id}/` - 获取客户详情
- `PUT /api/customers/{id}/` - 更新客户信息
- `PATCH /api/customers/{id}/` - 部分更新客户信息
- `DELETE /api/customers/{id}/` - 删除客户
- `GET /api/customers/statistics/` - 获取统计数据

### 联系人管理

- `GET /api/contacts/` - 获取联系人列表
- `POST /api/contacts/` - 创建新联系人
- `GET /api/contacts/{id}/` - 获取联系人详情
- `PUT /api/contacts/{id}/` - 更新联系人信息
- `DELETE /api/contacts/{id}/` - 删除联系人

### 查询参数

#### 客户列表筛选

- `level` - 按客户等级筛选（A/B/C/D）
- `area` - 按区域筛选
- `city` - 按城市筛选
- `business_model` - 按业务模式筛选（Hunting/Farming）
- `status` - 按状态筛选
- `search` - 搜索客户名称、地址、备注
- `ordering` - 排序字段（如：-updated_at, score_x）

示例：
```
GET /api/customers/?level=A&area=华东&ordering=-score_x
```

#### 联系人列表筛选

- `customer` - 按客户ID筛选
- `is_key_person` - 筛选关键联系人
- `search` - 搜索姓名、职位、电话、邮箱

## 数据模型

### Customer（客户）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| client_name | String | 客户名称 |
| business_model | String | 业务模式（Hunting/Farming） |
| area | String | 区域 |
| city | String | 城市 |
| address | Text | 详细地址 |
| description_x | Text | 客户描述 |
| score_x | Integer | 客户潜力评分 |
| description_y | Text | 竞争环境描述 |
| score_y | Integer | 竞争评分 |
| key_person | String | 关键联系人 |
| score_z | Integer | 关系评分 |
| level | String | 客户等级（A/B/C/D） |
| client_strategy | Text | 客户策略 |
| potential_contribution | Decimal | 年度潜在贡献(KEUR) |
| remark | Text | 备注 |
| status | String | 状态 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### Contact（联系人）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| customer | ForeignKey | 关联客户 |
| name | String | 姓名 |
| position | String | 职位 |
| phone | String | 电话 |
| email | String | 邮箱 |
| is_key_person | Boolean | 是否关键人 |
| created_at | DateTime | 创建时间 |

## 管理后台

访问 http://127.0.0.1:8000/admin/ 使用超级管理员账号登录后台管理系统。

## 注意事项

1. 确保MySQL服务已启动
2. 确保Python版本 >= 3.8
3. 生产环境需要修改 `settings.py` 中的 `SECRET_KEY` 和 `DEBUG` 设置
4. 生产环境需要配置 `ALLOWED_HOSTS`
5. 建议使用虚拟环境隔离项目依赖

## 下一步开发

- [ ] 实现Excel导入导出功能
- [ ] 添加用户认证和权限管理
- [ ] 添加操作日志记录
- [ ] 实现数据备份功能
- [ ] 添加API文档（Swagger/ReDoc）

