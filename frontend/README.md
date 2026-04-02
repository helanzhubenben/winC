# Fishpool 客户池管理系统 - 前端

这是一个基于 Vue.js 3 + Element Plus 构建的客户池管理系统前端项目。

## 技术栈

- Vue 3 (组合式 API)
- Element Plus (UI 组件库)
- Vue Router (路由管理)
- Axios (HTTP 请求)
- ECharts (数据可视化)
- Vite (构建工具)

## 功能特性

- 客户列表展示（支持搜索、筛选、分页）
- 客户详情查看
- 客户信息的增删改查
- 三维评分可视化（雷达图）
- 客户等级自动计算（A/B/C/D）
- 联系人管理
- 响应式设计

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 请求封装
│   │   ├── customer.js   # 客户相关 API
│   │   └── contact.js    # 联系人相关 API
│   ├── components/       # 公共组件
│   │   ├── CustomerForm.vue   # 客户表单
│   │   └── ContactForm.vue    # 联系人表单
│   ├── views/            # 页面组件
│   │   ├── CustomerList.vue   # 客户列表页
│   │   └── CustomerDetail.vue # 客户详情页
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── utils/            # 工具函数
│   │   └── level.js      # 等级计算
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── vite.config.js        # Vite 配置
└── package.json          # 项目依赖
```

## 安装依赖

```bash
npm install
```

## 运行项目

```bash
npm run dev
```

项目将在 http://localhost:5173 启动

## 配置说明

### API 代理配置

在 `vite.config.js` 中配置了 API 代理，将 `/api` 请求代理到后端服务器：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

### 客户等级规则

- Level A: X>=70 AND Y>=70 AND Z>=70
- Level B: 至少两项>=70
- Level C: X>=70
- Level D: 其他

### 等级颜色

- Level A: 红色 (#F56C6C)
- Level B: 蓝色 (#409EFF)
- Level C: 绿色 (#67C23A)
- Level D: 灰色 (#909399)

## 构建生产版本

```bash
npm run build
```

## 预览生产版本

```bash
npm run preview
```

## 注意事项

1. 确保后端服务已启动（http://localhost:8000）
2. 后端需要配置 CORS 允许前端跨域访问
3. 所有文本使用中文
4. 使用 Element Plus 中文语言包
