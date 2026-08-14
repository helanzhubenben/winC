# Fishpool 客户池管理系统

Fishpool 是面向 B2B 销售团队的本地客户管理系统，支持客户分级、联系人管理、营收数据、周报行动记录和联系跟进。

## 普通用户快速开始

### 1. 获取安装包

只需获得一个文件，无需安装 Python、Node.js 或其他开发环境：

```text
Fishpool-Setup-1.0.1.exe
```

开发机当前生成的安装包位于：

```text
packaging/dist/Fishpool-Setup-1.0.1.exe
```

### 2. 安装

1. 双击 `Fishpool-Setup-1.0.1.exe`。
2. 在“程序安装位置”页面，建议保留默认目录：
   ```text
   C:\Users\你的用户名\AppData\Local\Programs\Fishpool
   ```
3. 在“数据保存位置”页面，选择客户数据保存目录。默认目录为：
   ```text
   C:\Users\你的用户名\AppData\Local\Fishpool
   ```
   也可以选择有写入权限的 D/E 盘文件夹，例如 `D:\FishpoolData`。
4. 完成安装后，从开始菜单或桌面快捷方式打开 `Fishpool`。

> 如果出现“没有写入权限”，请保留默认目录，或改选当前 Windows 用户有写入权限的文件夹。不要选择 `C:\Program Files`、系统目录或受公司策略保护的目录。

### 3. 首次打开

程序会自动：

1. 在所选数据目录创建空数据库 `db.sqlite3`。
2. 启动仅本机可访问的服务。
3. 在默认浏览器中打开 Fishpool。

首次安装没有预置客户数据，可通过页面中的 Excel 导入功能录入客户和营收数据。

## 数据、升级与卸载

### 数据位置

所有客户数据保存在安装时选择的数据目录中，核心文件为：

```text
<数据目录>\db.sqlite3
```

程序安装目录和数据目录彼此独立。请定期备份整个数据目录，尤其是 `db.sqlite3` 文件。

### 升级

安装新版本的 `Fishpool-Setup-x.y.z.exe` 即可升级程序。

- 安装程序默认识别并复用上次的数据目录。
- 升级只替换程序文件，不覆盖、不清空客户数据。
- 升级前建议备份数据目录。

### 卸载和重装

卸载时会询问是否同时删除本地客户数据：

- 选择“否”：保留数据库。之后重新安装会继续使用原有数据。
- 选择“是”：永久删除所选数据目录及其中的客户数据，无法恢复。

## 功能概览

- 客户信息、区域、评分和自动分级管理。
- 联系人和关键人维护。
- 客户联系记录：每天每个客户可记录一次联系时间。
- 月度营收导入、查询和图表展示。
- 周报、Action 行动记录和跟进管理。
- 客户、周报和营收数据的 Excel 导入导出。

## 开发者快速开始

### 环境要求

- Python 3.11 或更高版本。
- Node.js 20 或更高版本。

### 启动后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

后端地址：`http://127.0.0.1:8000`

### 启动前端

另开一个终端：

```powershell
cd frontend
npm ci
npm run dev
```

前端地址：`http://localhost:5173`

### 运行测试

```powershell
cd backend
.\.venv\Scripts\python.exe manage.py test customers.tests
```

### 构建 Windows 安装包

首次打包需要安装 Inno Setup 6；打包脚本会检查其是否可用。

```powershell
cd packaging
.\build-installer.ps1 -Version 1.0.2
```

生成的安装包位于：

```text
packaging\dist\Fishpool-Setup-1.0.2.exe
```

打包产物不包含开发数据库；安装后由用户首次启动时创建空数据库。

## 项目结构

```text
backend/       Django API、数据模型和本机启动器
frontend/      Vue 3 前端
packaging/     PyInstaller 与 Inno Setup 打包脚本
docs/          设计、模板和项目文档
```

更多后端和前端实现说明分别见 `backend/README.md` 与 `frontend/README.md`。
